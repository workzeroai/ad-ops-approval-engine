"""규칙 엔진: 파일 검증, 조건 평가(all/any 중첩), 근거 문장."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from adops.models import Entity, EntityType, Platform
from adops.rules import RuleError, RuleSet, default_rules, evaluate, load_rules

ROOT = Path(__file__).resolve().parents[1]


def _entity(eid: str, etype=EntityType.KEYWORD, status="ACTIVE", **fields) -> Entity:
    return Entity(id=eid, account_id="acc", platform=Platform.SEARCHAD_LIKE, type=etype, name=eid,
                  fields={"status": status, **fields}, updated_at=date(2026, 1, 1))


def _ruleset(rules: list[dict], platform="searchad_like") -> RuleSet:
    return RuleSet.model_validate({"platform": platform, "rules": rules})


def _rule(when: dict, **kw) -> dict:
    base = {"id": "r1", "name": "테스트", "entity": "keyword", "when": when,
            "action": {"field": "bid", "op": "increase_pct", "value": 10}}
    base.update(kw)
    return base


@pytest.mark.parametrize("platform", list(Platform))
def test_default_rules_load(platform):
    rs = default_rules(platform)
    assert rs.platform == platform
    assert rs.rules and all(r.reason for r in rs.rules)


@pytest.mark.parametrize("name", ["rules.searchad.yaml", "rules.meta.yaml"])
def test_example_rules_load(name):
    rs = load_rules(ROOT / "examples" / name)
    assert rs.rules


def test_unknown_metric_is_reported_with_choices(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("platform: searchad_like\nrules:\n  - id: x\n    name: x\n    entity: keyword\n"
                 "    when: {all: [{metric: roas7d, op: '>=', value: 1}]}\n"
                 "    action: {field: bid, op: increase_pct, value: 10}\n", encoding="utf-8")
    with pytest.raises(RuleError) as exc:
        load_rules(f)
    assert "알 수 없는 지표 'roas7d'" in str(exc.value)
    assert "roas_7d" in str(exc.value)


def test_metric_must_fit_entity():
    with pytest.raises(ValueError, match="쓸 수 없는 지표"):
        _ruleset([_rule({"all": [{"metric": "frequency", "op": ">", "value": 1}]})])


def test_yaml_syntax_error(tmp_path):
    f = tmp_path / "broken.yaml"
    f.write_text("rules: [\n", encoding="utf-8")
    with pytest.raises(RuleError, match="YAML 문법 오류"):
        load_rules(f)


@pytest.mark.parametrize("action", [
    {"field": "bid", "op": "pause"},
    {"field": "status", "op": "increase_pct", "value": 10},
    {"field": "bid", "op": "increase_pct", "value": 150},
    {"field": "bid", "op": "set"},
])
def test_invalid_actions_rejected(action):
    with pytest.raises(ValueError):
        _ruleset([_rule({"all": [{"metric": "roas_7d", "op": ">", "value": 1}]}, action=action)])


def test_group_needs_exactly_one_of_all_any():
    with pytest.raises(ValueError, match="all 또는 any"):
        _ruleset([_rule({"all": [{"metric": "roas_7d", "op": ">", "value": 1}],
                         "any": [{"metric": "roas_7d", "op": ">", "value": 1}]})])


def test_duplicate_rule_ids():
    when = {"all": [{"metric": "roas_7d", "op": ">", "value": 1}]}
    with pytest.raises(ValueError, match="중복"):
        _ruleset([_rule(when), _rule(when)])


@pytest.mark.parametrize("op,value,expected", [
    (">", 400, True), (">=", 450, True), ("<", 450, False), ("<=", 450, True), ("==", 450, True), ("!=", 450, False),
])
def test_operators(op, value, expected):
    rs = _ruleset([_rule({"all": [{"metric": "roas_7d", "op": op, "value": value}]})])
    matches = evaluate(rs, {"k": _entity("k", bid=500)}, {"k": {"roas_7d": 450.0}})
    assert bool(matches) is expected


def test_nested_all_any():
    when = {"all": [
        {"metric": "conv_7d", "op": ">=", "value": 5},
        {"any": [{"metric": "avg_rank_7d", "op": ">=", "value": 4}, {"metric": "roas_7d", "op": ">=", "value": 800}]},
    ]}
    rs = _ruleset([_rule(when)])
    entities = {k: _entity(k, bid=500) for k in "abc"}
    metrics = {
        "a": {"conv_7d": 6, "avg_rank_7d": 4.5, "roas_7d": 300},  # any 첫 조건
        "b": {"conv_7d": 6, "avg_rank_7d": 2.0, "roas_7d": 900},  # any 둘째 조건
        "c": {"conv_7d": 2, "avg_rank_7d": 5.0, "roas_7d": 900},  # all 실패
    }
    assert sorted(m.entity.id for m in evaluate(rs, entities, metrics)) == ["a", "b"]


def test_missing_metric_value_does_not_match():
    rs = _ruleset([_rule({"all": [{"metric": "avg_rank_7d", "op": ">=", "value": 1}]})])
    assert evaluate(rs, {"k": _entity("k", bid=500)}, {"k": {"avg_rank_7d": None}}) == []


def test_paused_and_disabled_are_skipped():
    when = {"all": [{"metric": "roas_7d", "op": ">", "value": 1}]}
    rs = _ruleset([_rule(when), _rule(when, id="r2", enabled=False)])
    entities = {"on": _entity("on", bid=1), "off": _entity("off", status="PAUSED", bid=1)}
    matches = evaluate(rs, entities, {"on": {"roas_7d": 500}, "off": {"roas_7d": 500}})
    assert [(m.rule.id, m.entity.id) for m in matches] == [("r1", "on")]


def test_reason_template_and_auto_evidence():
    when = {"all": [{"metric": "roas_7d", "op": ">=", "value": 300}, {"metric": "spend_7d", "op": ">", "value": 0}]}
    templated = _ruleset([_rule(when, reason="ROAS {roas_7d}, 비용 {spend_7d}, 없음 {nope}")])
    m = evaluate(templated, {"k": _entity("k", bid=1)}, {"k": {"roas_7d": 512.3, "spend_7d": 12345}})[0]
    assert m.reason_text() == "ROAS 512%, 비용 12,345원, 없음 ?"
    auto = _ruleset([_rule(when)])
    m = evaluate(auto, {"k": _entity("k", bid=1)}, {"k": {"roas_7d": 512.3, "spend_7d": 12345}})[0]
    assert "최근 7일 ROAS 512% (>= 300%)" in m.reason_text()
