"""가상 데이터·어댑터·진단·조정안."""
from __future__ import annotations

import pytest

from adops import fakedata
from adops.adapters import FailureMode, FakeAdServer, PermanentApiError, TransientApiError
from adops.diagnose import diagnose
from adops.models import EntityType, RunStatus
from adops.plan import build_plan, compute_after
from adops.rules.engine import Action, RuleSet
from tests.conftest import MT_ACCOUNT, SA_ACCOUNT


def test_fake_data_is_deterministic():
    assert fakedata.generate() == fakedata.generate()
    assert fakedata.generate(seed=1) != fakedata.generate(seed=2)


def test_searchad_adapter_normalizes(ws):
    a = ws.adapter(SA_ACCOUNT)
    kws = a.get_entities(EntityType.KEYWORD)
    assert kws and all("bid" in k.fields and k.fields["status"] == "ACTIVE" for k in kws)
    stats = a.get_stats(a.as_of, a.as_of, EntityType.CAMPAIGN)
    assert all(len(s.hourly_impressions) == 24 for s in stats)


def test_meta_adapter_aggregates_adsets_from_ads(ws):
    a = ws.adapter(MT_ACCOUNT)
    ads = a.get_stats(a.as_of, a.as_of, EntityType.AD)
    sets = a.get_stats(a.as_of, a.as_of, EntityType.ADSET)
    assert sum(s.cost for s in ads) == sum(s.cost for s in sets)
    assert isinstance(a.get_state("as-broad").fields["daily_budget"], int)  # 원본 문자열 → 정수


def test_adapter_refuses_non_editable_field(ws):
    with pytest.raises(ValueError, match="바꿀 수 없습니다"):
        ws.adapter(MT_ACCOUNT).apply_change("ad-a01", "daily_budget", 1000)


def test_fake_server_errors(ws):
    server = ws.server()
    with pytest.raises(PermanentApiError, match="404"):
        server.update_object(MT_ACCOUNT, "ads", "nope", "id", {"status": "PAUSED"})
    with pytest.raises(PermanentApiError, match="400"):
        server.update_object(MT_ACCOUNT, "ads", "ad-a01", "id", {"color": "red"})
    with pytest.raises(FileNotFoundError):
        FakeAdServer(ws.home / "missing.json")


def test_failure_mode_is_reproducible(ws):
    def outcomes(seed):
        server = ws.server(FailureMode(rate=0.5, seed=seed))
        out = []
        for _ in range(12):
            try:
                server.update_object(MT_ACCOUNT, "ads", "ad-a01", "id", {"status": "ACTIVE"})
                out.append(server.request_log[-1]["result"])
            except TransientApiError:
                out.append("503")
        return out

    first = outcomes(3)
    assert first == outcomes(3)
    assert {"200", "503", "200 (값 미반영)"} <= set(first)


def test_diagnosis_finds_planted_patterns(ws):
    sa = diagnose(ws.adapter(SA_ACCOUNT))
    kinds = {f.kind for f in sa.findings}
    assert {"budget_exhausted", "rank_is_budget", "budget_watch", "no_conversion"} <= kinds
    homegym = sa.metrics["cmp-homegym"]
    assert homegym["exhausted_days_7d"] >= 3 and 14 <= homegym["avg_exhaust_hour_7d"] <= 19
    assert homegym["lost_impr_est_7d"] > 0
    assert sa.metrics["cmp-brand"]["exhausted_days_7d"] == 0

    mt = diagnose(ws.adapter(MT_ACCOUNT))
    by_kind = {f.kind: f for f in mt.findings}
    assert by_kind["winning_creative"].entity_id == "ad-b01"
    assert by_kind["creative_fatigue"].entity_id == "ad-a02"
    assert by_kind["low_roas"].entity_id == "as-broad"
    assert by_kind["learning"].entity_id == "as-retarget"
    assert mt.metrics["ad-b01"]["roas_rank_pct"] == 0


def test_plan_matches_expected_changes(ws, sa_run, mt_run):
    sa, _ = sa_run
    assert [(c.entity_id, c.field, c.before, c.after) for c in sa.changes] == [
        ("cmp-homegym", "daily_budget", 130_000, 156_000),
        ("kw-foldbike", "bid", 1100, 940),
        ("kw-pilatesring", "bid", 520, 440),
        ("kw-foamroller", "bid", 350, 390),
    ]
    # 예산이 먼저 소진되는 캠페인의 키워드는 순위가 낮아도 입찰가를 올리지 않는다
    assert "kw-kettlebell" not in {c.entity_id for c in sa.changes}
    assert all(c.reason and "{" not in c.reason and c.impact for c in sa.changes)

    mt, _ = mt_run
    assert [(c.entity_id, c.after) for c in mt.changes] == [
        ("as-retarget", 72_000), ("as-lookalike", 144_000), ("as-broad", 64_000),
        ("ad-a02", "PAUSED"), ("ad-d02", "PAUSED")]


@pytest.mark.parametrize("action,before,expected", [
    (Action(field="bid", op="increase_pct", value=10, round_to=10), 350, 390),  # 385 → 반올림 390
    (Action(field="bid", op="decrease_pct", value=50, round_to=10, min=300), 520, 300),
    (Action(field="daily_budget", op="increase_pct", value=50, max=100_000), 80_000, 100_000),
    (Action(field="daily_budget", op="set", value=55_555, round_to=1000), 80_000, 56_000),
    (Action(field="status", op="pause"), "ACTIVE", "PAUSED"),
])
def test_compute_after(action, before, expected):
    assert compute_after(action, before)[0] == expected


def test_conflicting_rules_first_wins_and_noops_dropped(ws, store):
    diag = diagnose(ws.adapter(SA_ACCOUNT))
    when = {"all": [{"metric": "spend_7d", "op": ">=", "value": 0}]}
    rs = RuleSet.model_validate({"platform": "searchad_like", "rules": [
        {"id": "a", "name": "먼저", "entity": "campaign", "when": when,
         "action": {"field": "daily_budget", "op": "increase_pct", "value": 10, "round_to": 1000}},
        {"id": "b", "name": "나중", "entity": "campaign", "when": when,
         "action": {"field": "daily_budget", "op": "decrease_pct", "value": 10}},
        {"id": "c", "name": "그대로", "entity": "keyword", "when": when,
         "action": {"field": "bid", "op": "increase_pct", "value": 0.1, "round_to": 10}},
    ]})
    result = build_plan(diag, rs, store)
    assert {c.rule_id for c in result.run.changes} == {"a"}
    assert len(result.conflicts) == 3 and all("'먼저'" in t for t in result.conflicts)
    assert result.noops


def test_empty_plan(ws, store):
    diag = diagnose(ws.adapter(SA_ACCOUNT))
    rs = RuleSet.model_validate({"platform": "searchad_like", "rules": [
        {"id": "none", "name": "없음", "entity": "campaign",
         "when": {"all": [{"metric": "spend_7d", "op": "<", "value": 0}]},
         "action": {"field": "daily_budget", "op": "increase_pct", "value": 10}}]})
    result = build_plan(diag, rs, store)
    assert result.run.changes == [] and store.get_run(result.run.run_id).status == RunStatus.EMPTY
