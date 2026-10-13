"""안전장치: 변경 폭 상한, 하한·상한, 학습 기간, 계획 이후 값 변경, 일일 건수 상한."""
from __future__ import annotations

from datetime import date

import pytest

from adops.models import Change, ChangeStatus, Entity, EntityType, Platform
from adops.rules.engine import Bound, Guardrails
from adops.safety import check_change, daily_cap_violation
from tests.conftest import SA_ACCOUNT, executor

OPS = date(2026, 10, 13)


def _change(before=100_000, after=120_000, field="daily_budget") -> Change:
    return Change(change_id="R-C01", run_id="R", seq=1, account_id="a", platform=Platform.META_LIKE,
                  entity_id="e", entity_type=EntityType.ADSET, entity_name="세트", field=field, before=before,
                  after=after, rule_id="r", rule_name="규칙", reason="근거")


def _entity(value=100_000, updated=date(2026, 9, 1)) -> Entity:
    return Entity(id="e", account_id="a", platform=Platform.META_LIKE, type=EntityType.ADSET, name="세트",
                  fields={"daily_budget": value, "status": "ACTIVE"}, updated_at=updated)


def codes(violations):
    return [v.code for v in violations]


def test_passes_within_limits():
    assert check_change(_change(), _entity(), Guardrails(max_change_pct=20), OPS) == []


@pytest.mark.parametrize("after,blocked", [(120_000, False), (120_001, True), (79_000, True), (80_000, False)])
def test_max_change_pct(after, blocked):
    v = check_change(_change(after=after), _entity(), Guardrails(max_change_pct=20), OPS)
    assert ("max_change_pct" in codes(v)) is blocked


def test_bounds():
    g = Guardrails(max_change_pct=100, bounds={"daily_budget": Bound(min=90_000, max=110_000)})
    assert codes(check_change(_change(after=120_000), _entity(), g, OPS)) == ["bounds"]
    assert codes(check_change(_change(after=85_000), _entity(), g, OPS)) == ["bounds"]


def test_cooldown_protects_learning_period():
    g = Guardrails(cooldown_days=3)
    assert codes(check_change(_change(), _entity(updated=date(2026, 10, 12)), g, OPS)) == ["cooldown"]
    assert check_change(_change(), _entity(updated=date(2026, 10, 10)), g, OPS) == []


def test_drift_when_value_changed_after_plan():
    v = check_change(_change(), _entity(value=110_000), Guardrails(), OPS)
    assert codes(v) == ["drift"]
    assert "110,000원" in v[0].message


def test_daily_cap_helper():
    g = Guardrails(max_changes_per_day=3)
    assert daily_cap_violation(1, 1, g) is None
    assert daily_cap_violation(2, 1, g).code == "daily_cap"


def test_preview_blocks_over_daily_cap(ws, store, sa_run):
    run, ruleset = sa_run
    ruleset.guardrails.max_changes_per_day = 2
    results = executor(ws, store, SA_ACCOUNT, ruleset).preview(run.run_id)
    assert [r.change.status for r in results] == [
        ChangeStatus.PREVIEWED, ChangeStatus.PREVIEWED, ChangeStatus.BLOCKED, ChangeStatus.BLOCKED]
    assert "일일 변경 건수 상한" in results[-1].message


def test_preview_blocks_change_over_pct_cap(ws, store, sa_run):
    run, ruleset = sa_run
    ruleset.guardrails.max_change_pct = 12  # 기본 규칙의 +20%·-15%는 막히고 +11%만 통과
    results = executor(ws, store, SA_ACCOUNT, ruleset).preview(run.run_id)
    passed = [r.change.entity_name for r in results if r.ok]
    assert passed == ["폼롤러"]
    assert all("변경 폭" in r.message for r in results if not r.ok)
