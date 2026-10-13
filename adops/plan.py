"""조정안 생성: 진단 지표 + 규칙 → 변경(Change) 목록과 근거 문장.

- 규칙이 걸린 개체마다 새 값을 계산하고(반올림·규칙 하한/상한 적용), 근거 문장과 예상 영향을 붙인다.
- 같은 개체·같은 필드에 규칙이 둘 이상 걸리면 위쪽 규칙만 쓴다(충돌 기록).
- 여기서는 아무것도 반영하지 않는다. 결과는 planned 상태로 감사 로그에 저장된다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from adops.audit import AuditStore
from adops.diagnose import WINDOW, AccountDiagnosis
from adops.metrics import format_metric, signed_won, won
from adops.models import Change, EntityType, Run, RunStatus
from adops.rules.engine import Action, RuleMatch, RuleSet, evaluate

PLANNER = "system:planner"


@dataclass
class PlanResult:
    run: Run
    conflicts: list[str] = field(default_factory=list)  # 우선순위에 밀린 규칙
    noops: list[str] = field(default_factory=list)  # 계산 결과 값이 그대로라 뺀 것


def _round(value: float, step: int) -> int:
    step = max(step, 1)
    return int((Decimal(str(value)) / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * step)


def compute_after(action: Action, before: Any) -> tuple[Any, str]:
    """새 값과(있으면) 보정 메모를 돌려준다."""
    if action.op == "pause":
        return "PAUSED", ""
    if action.op == "set":
        value = action.value
    else:
        pct = float(action.value or 0) / 100
        value = before * (1 + pct if action.op == "increase_pct" else 1 - pct)
    if isinstance(value, str):
        return value, ""
    after = _round(float(value), action.round_to)
    memo = ""
    if action.max is not None and after > action.max:
        after, memo = int(action.max), f"규칙 상한 {won(action.max)}으로 맞춤"
    if action.min is not None and after < action.min:
        after, memo = int(action.min), f"규칙 하한 {won(action.min)}으로 맞춤"
    return after, memo


def estimate_impact(match: RuleMatch, before: Any, after: Any) -> str:
    """사람이 승인할 때 볼 '예상 영향' 한 줄. 최근 7일 실적으로 단순 계산한 값이다."""
    m = match.metrics
    f = match.rule.action.field
    if f == "status":
        daily = (m.get("spend_7d") or 0) / WINDOW
        return f"지출 {signed_won(-daily)}/일 (최근 7일 평균)"
    diff = after - before
    if f == "daily_budget":
        text = f"최대 지출 {signed_won(diff)}/일"
        if diff > 0 and m.get("lost_impr_est_7d"):
            text += f" · 노출 손실(추정) {m['lost_impr_est_7d'] / WINDOW:,.0f}회/일 일부 회복"
        elif diff > 0 and m.get("roas_7d"):
            text += f" · 같은 ROAS면 매출 {signed_won(diff * m['roas_7d'] / 100)}/일 (단순 추정)"
        return text
    text = f"클릭당 최대 {signed_won(diff)}"
    if diff < 0 and m.get("spend_7d"):
        text += f" · 7일 무전환 비용 {won(m['spend_7d'])}"
    elif diff > 0 and m.get("avg_rank_7d"):
        text += f" · 평균 {format_metric('avg_rank_7d', m['avg_rank_7d'])}에서 순위 상승 기대"
    return text


def build_plan(diag: AccountDiagnosis, ruleset: RuleSet, store: AuditStore, rules_file: str = "",
               actor: str = PLANNER) -> PlanResult:
    run_id = store.next_run_id(diag.ops_date, diag.platform)
    run = Run(run_id=run_id, account_id=diag.account_id, platform=diag.platform, ops_date=diag.ops_date,
              created_at=datetime.now().astimezone().isoformat(timespec="seconds"), rules_file=rules_file)
    result = PlanResult(run=run)
    taken: dict[tuple[str, str], str] = {}
    for match in evaluate(ruleset, diag.entities, diag.metrics):
        action, entity = match.rule.action, match.entity
        key = (entity.id, action.field)
        if key in taken:
            result.conflicts.append(f"{entity.name}: '{match.rule.name}'은(는) 우선순위가 높은 '{taken[key]}'에 밀림")
            continue
        before = entity.fields.get(action.field)
        if before is None:
            continue
        after, memo = compute_after(action, before)
        if after == before:
            result.noops.append(f"{entity.name}: '{match.rule.name}' 계산 결과가 현재 값과 같음")
            continue
        taken[key] = match.rule.name
        evidence = list(match.evidence) + ([memo] if memo else [])
        seq = len(run.changes) + 1
        run.changes.append(Change(
            change_id=f"{run_id}-C{seq:02d}",
            run_id=run_id,
            seq=seq,
            account_id=diag.account_id,
            platform=diag.platform,
            entity_id=entity.id,
            entity_type=EntityType(entity.type),
            entity_name=entity.name,
            field=action.field,
            before=before,
            after=after,
            rule_id=match.rule.id,
            rule_name=match.rule.name,
            reason=" ".join(match.reason_text().split()),
            evidence=evidence,
            risk=match.rule.risk,
            impact=estimate_impact(match, before, after),
        ))
    if not run.changes:
        run.status = RunStatus.EMPTY
    store.save_run(run, actor)
    for text in result.conflicts:
        store.log(run_id, None, actor, "rule_conflict", text)
    return result
