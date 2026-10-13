"""YAML 규칙 엔진.

규칙 = 대상 개체 + 조건(지표·비교·임계값, all/any 중첩) + 액션(증액·감액·지정·중지) + 근거 문장 틀.
안전장치(guardrails)도 같은 파일에 두어, 마케터가 규칙과 한도를 한곳에서 고친다.
"""
from __future__ import annotations

import operator
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from adops.metrics import METRICS, format_metric, metrics_for
from adops.models import Entity, EntityType, Platform, Risk

DEFAULTS_DIR = Path(__file__).parent / "defaults"
DEFAULT_RULE_FILES = {
    Platform.SEARCHAD_LIKE: DEFAULTS_DIR / "searchad.yaml",
    Platform.META_LIKE: DEFAULTS_DIR / "meta.yaml",
}

OPS: dict[str, Callable[[Any, Any], bool]] = {
    ">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le, "==": operator.eq, "!=": operator.ne,
}


class RuleError(ValueError):
    """규칙 파일 오류(사람이 읽을 수 있는 메시지)."""


class Condition(BaseModel):
    metric: str
    op: Literal[">", ">=", "<", "<=", "==", "!="]
    value: float

    @field_validator("metric")
    @classmethod
    def _known_metric(cls, v: str) -> str:
        if v not in METRICS:
            raise ValueError(f"알 수 없는 지표 '{v}'. 사용 가능: {', '.join(sorted(METRICS))}")
        return v

    def describe(self) -> str:
        label = METRICS[self.metric].label
        return f"{label} {self.op} {format_metric(self.metric, self.value)}"


class ConditionGroup(BaseModel):
    all: list[Condition | ConditionGroup] | None = None
    any: list[Condition | ConditionGroup] | None = None

    @model_validator(mode="after")
    def _one_of(self) -> ConditionGroup:
        if bool(self.all) == bool(self.any):
            raise ValueError("조건 묶음에는 all 또는 any 중 하나만, 비어 있지 않게 써야 합니다")
        return self

    def conditions(self) -> list[Condition]:
        out: list[Condition] = []
        for c in self.all or self.any or []:
            out += c.conditions() if isinstance(c, ConditionGroup) else [c]
        return out


class Action(BaseModel):
    field: Literal["daily_budget", "bid", "status"]
    op: Literal["increase_pct", "decrease_pct", "set", "pause"]
    value: float | str | None = None
    round_to: int = 1
    min: float | None = None
    max: float | None = None

    @model_validator(mode="after")
    def _check(self) -> Action:
        if self.op in ("increase_pct", "decrease_pct"):
            if not isinstance(self.value, int | float) or not 0 < self.value <= 100:
                raise ValueError(f"{self.op}의 value는 0 초과 100 이하 숫자(%)여야 합니다")
            if self.field == "status":
                raise ValueError("status 필드에는 increase_pct/decrease_pct를 쓸 수 없습니다")
        if self.op == "pause" and self.field != "status":
            raise ValueError("pause는 field: status 와 함께 씁니다")
        if self.op == "set" and self.value is None:
            raise ValueError("set에는 value가 필요합니다")
        return self


class Rule(BaseModel):
    id: str
    name: str
    entity: EntityType
    when: ConditionGroup
    action: Action
    risk: Risk = Risk.MEDIUM
    reason: str | None = None
    enabled: bool = True

    @model_validator(mode="after")
    def _metrics_fit_entity(self) -> Rule:
        allowed = set(metrics_for(self.entity))
        bad = [c.metric for c in self.when.conditions() if c.metric not in allowed]
        if bad:
            raise ValueError(f"'{self.entity}' 규칙에서 쓸 수 없는 지표: {bad} (사용 가능: {sorted(allowed)})")
        return self


class Bound(BaseModel):
    min: float | None = None
    max: float | None = None


class Guardrails(BaseModel):
    max_change_pct: float = Field(30, gt=0, le=100, description="변경 1건의 변경 폭 상한(%)")
    max_changes_per_day: int = Field(10, ge=1, description="계정당 하루 반영 건수 상한")
    cooldown_days: int = Field(0, ge=0, description="같은 개체를 다시 바꾸기 전에 기다릴 날 수")
    max_retries: int = Field(2, ge=0, le=5, description="일시 오류 재시도 횟수")
    bounds: dict[str, Bound] = Field(default_factory=dict, description="필드별 절대 하한·상한")


class RuleSet(BaseModel):
    version: int = 1
    platform: Platform
    guardrails: Guardrails = Field(default_factory=Guardrails)
    rules: list[Rule]

    @model_validator(mode="after")
    def _unique_ids(self) -> RuleSet:
        ids = [r.id for r in self.rules]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"규칙 id가 중복됩니다: {dupes}")
        return self


def load_rules(path: Path | str) -> RuleSet:
    path = Path(path)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RuleError(f"{path.name}: YAML 문법 오류 — {exc}") from exc
    try:
        return RuleSet.model_validate(raw)
    except ValidationError as exc:
        lines = [f"{path.name}: 규칙 파일 검증 실패"]
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"])
            lines.append(f"  - {loc}: {err['msg']}")
        raise RuleError("\n".join(lines)) from exc


def default_rules(platform: Platform) -> RuleSet:
    return load_rules(DEFAULT_RULE_FILES[Platform(platform)])


# ------------------------------------------------------------------ 평가

class RuleMatch(BaseModel):
    rule: Rule
    entity: Entity
    metrics: dict[str, float | None]
    evidence: list[str]

    def reason_text(self) -> str:
        if self.rule.reason:
            values = _FormatDict({k: format_metric(k, v) for k, v in self.metrics.items()})
            return self.rule.reason.format_map(values)
        return " · ".join(self.evidence)


class _FormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "?"


def _eval(node: Condition | ConditionGroup, metrics: dict[str, float | None], evidence: list[str]) -> bool:
    if isinstance(node, Condition):
        actual = metrics.get(node.metric)
        if actual is None:
            return False  # 값이 없는 지표는 조건 불충족으로 본다
        ok = OPS[node.op](actual, node.value)
        if ok:
            evidence.append(f"{METRICS[node.metric].label} {format_metric(node.metric, actual)} "
                            f"({node.op} {format_metric(node.metric, node.value)})")
        return ok
    if node.all:
        return all(_eval(c, metrics, evidence) for c in node.all)
    return any(_eval(c, metrics, evidence) for c in node.any or [])


def evaluate(ruleset: RuleSet, entities: dict[str, Entity],
             metrics: dict[str, dict[str, float | None]]) -> list[RuleMatch]:
    """규칙 순서대로 평가한다. 파일 위쪽 규칙이 우선순위가 높다. 중지된 개체는 건너뛴다."""
    matches: list[RuleMatch] = []
    for rule in ruleset.rules:
        if not rule.enabled:
            continue
        targets = sorted((e for e in entities.values() if e.type == rule.entity and e.active), key=lambda e: e.name)
        for entity in targets:
            m = metrics.get(entity.id)
            if not m:
                continue
            evidence: list[str] = []
            if _eval(rule.when, m, evidence):
                matches.append(RuleMatch(rule=rule, entity=entity, metrics=m, evidence=evidence))
    return matches
