"""실행 파이프라인: 승인 없는 반영 금지, 반영→검증, 검증 실패 시 중단, 재시도, 롤백, 재점검."""
from __future__ import annotations

import pytest

from adops.adapters import FailureMode, PermanentApiError
from adops.execute import ApprovalRequiredError, RunStateError
from adops.models import ChangeStatus, RunStatus
from tests.conftest import MT_ACCOUNT, SA_ACCOUNT, executor

S = ChangeStatus


def _ready(ws, store, run, ruleset, account, failure=None):
    ex = executor(ws, store, account, ruleset, failure)
    ex.preview(run.run_id)
    ex.approve(run.run_id)
    return ex


def _value(ws, account, entity_id, field):
    return ws.adapter(account).get_state(entity_id).fields[field]


def test_apply_refuses_without_approval(ws, store, sa_run):
    run, ruleset = sa_run
    ex = executor(ws, store, SA_ACCOUNT, ruleset)
    ex.preview(run.run_id)
    with pytest.raises(ApprovalRequiredError, match="승인된 변경이 없습니다"):
        ex.apply(run.run_id)
    change = store.get_run(run.run_id).changes[0]
    with pytest.raises(ApprovalRequiredError, match="승인 필요"):
        ex.apply_one(change)
    # 플랫폼 값은 그대로
    assert _value(ws, SA_ACCOUNT, change.entity_id, change.field) == change.before


def test_preview_and_approve_require_right_state(ws, store, sa_run):
    run, ruleset = sa_run
    ex = executor(ws, store, SA_ACCOUNT, ruleset)
    with pytest.raises(RunStateError, match="먼저 preview"):
        ex.approve(run.run_id)
    ex.preview(run.run_id)
    with pytest.raises(RunStateError, match="미리보기할"):
        ex.preview(run.run_id)


def test_partial_approval_and_rejection(ws, store, sa_run):
    run, ruleset = sa_run
    ex = executor(ws, store, SA_ACCOUNT, ruleset)
    ex.preview(run.run_id)
    approved, rejected = ex.approve(run.run_id, seqs=[1, 2], reject=[3])
    assert [c.seq for c in approved] == [1, 2] and [c.seq for c in rejected] == [3]
    report = ex.apply(run.run_id)
    statuses = [c.status for c in store.get_run(run.run_id).changes]
    assert statuses == [S.VERIFIED, S.VERIFIED, S.REJECTED, S.PREVIEWED]
    assert report.verified == 2


def test_apply_then_verify_happy_path(ws, store, sa_run):
    run, ruleset = sa_run
    ex = _ready(ws, store, run, ruleset, SA_ACCOUNT)
    report = ex.apply(run.run_id)
    assert not report.halted and report.verified == len(run.changes)
    saved = store.get_run(run.run_id)
    assert saved.status == RunStatus.COMPLETED
    for c in saved.changes:
        assert _value(ws, SA_ACCOUNT, c.entity_id, c.field) == c.after
    assert all(r.ok for r in ex.verify(run.run_id))


def test_verify_detects_manual_change_after_apply(ws, store, sa_run):
    run, ruleset = sa_run
    ex = _ready(ws, store, run, ruleset, SA_ACCOUNT)
    ex.apply(run.run_id)
    first = run.changes[0]
    ws.adapter(SA_ACCOUNT).apply_change(first.entity_id, first.field, 99_000)  # 누군가 콘솔에서 바꿈
    results = ex.verify(run.run_id)
    assert next(r.ok for r in results) is False
    assert any(e["action"] == "drift_detected" for e in store.events(run.run_id))


def test_silent_failure_halts_remaining_changes(ws, store, mt_run, monkeypatch):
    run, ruleset = mt_run
    ex = _ready(ws, store, run, ruleset, MT_ACCOUNT)
    approved = [c for c in store.get_run(run.run_id).changes if c.status == S.APPROVED]
    target = approved[1]
    real = ex.adapter.apply_change

    def flaky(entity_id, field, value):  # 두 번째 변경만 '응답 성공·값 미반영'
        if entity_id != target.entity_id:
            real(entity_id, field, value)

    monkeypatch.setattr(ex.adapter, "apply_change", flaky)
    report = ex.apply(run.run_id)
    assert report.halted and target.change_id in report.halt_reason
    by_id = {c.change_id: c.status for c in store.get_run(run.run_id).changes}
    assert by_id[approved[0].change_id] == S.VERIFIED
    assert by_id[target.change_id] == S.FAILED
    assert all(by_id[c.change_id] == S.SKIPPED for c in approved[2:])
    assert store.get_run(run.run_id).status == RunStatus.HALTED
    # 건너뛴 변경은 플랫폼에 닿지 않았다
    for c in approved[2:]:
        assert _value(ws, MT_ACCOUNT, c.entity_id, c.field) == c.before


def test_transient_errors_are_retried(ws, store, sa_run, monkeypatch):
    run, ruleset = sa_run
    ex = _ready(ws, store, run, ruleset, SA_ACCOUNT)
    real, calls = ex.adapter.apply_change, {"n": 0}

    def flaky(entity_id, field, value):
        calls["n"] += 1
        if calls["n"] == 1:
            from adops.adapters import TransientApiError
            raise TransientApiError("HTTP 503")
        real(entity_id, field, value)

    monkeypatch.setattr(ex.adapter, "apply_change", flaky)
    report = ex.apply(run.run_id)
    assert not report.halted and report.results[0].attempts == 2
    assert any(e["action"] == "api_error" for e in store.events(run.run_id))


def test_permanent_error_fails_without_retry(ws, store, sa_run, monkeypatch):
    run, ruleset = sa_run
    ex = _ready(ws, store, run, ruleset, SA_ACCOUNT)
    calls = {"n": 0}

    def broken(*_):
        calls["n"] += 1
        raise PermanentApiError("HTTP 400")

    monkeypatch.setattr(ex.adapter, "apply_change", broken)
    report = ex.apply(run.run_id)
    assert report.halted and calls["n"] == 1
    statuses = [c.status for c in store.get_run(run.run_id).changes]
    assert statuses[0] == S.FAILED and set(statuses[1:]) == {S.SKIPPED}


def test_rollback_restores_previous_values(ws, store, mt_run):
    run, ruleset = mt_run
    ex = _ready(ws, store, run, ruleset, MT_ACCOUNT)
    ex.apply(run.run_id)
    applied = [c for c in store.get_run(run.run_id).changes if c.status == S.VERIFIED]
    assert applied
    results = executor(ws, store, MT_ACCOUNT, ruleset).rollback(run.run_id)
    assert all(r.ok for r in results)
    assert [r.change.seq for r in results] == sorted((c.seq for c in applied), reverse=True)  # 역순
    for c in applied:
        assert _value(ws, MT_ACCOUNT, c.entity_id, c.field) == c.before
    saved = store.get_run(run.run_id)
    assert saved.status == RunStatus.ROLLED_BACK
    assert {c.status for c in saved.changes if c.change_id in {a.change_id for a in applied}} == {S.ROLLED_BACK}
    with pytest.raises(RunStateError, match="되돌릴 변경이 없습니다"):
        executor(ws, store, MT_ACCOUNT, ruleset).rollback(run.run_id)


def test_rollback_after_failure_with_simulation(ws, store, mt_run):
    """데모와 같은 실패 시뮬레이션: 재시도 1회 후 성공 → 다음 건 검증 실패 → 롤백."""
    run, ruleset = mt_run
    ex = _ready(ws, store, run, ruleset, MT_ACCOUNT, FailureMode(rate=0.35, seed=7))
    report = ex.apply(run.run_id)
    assert report.halted
    assert [r.change.status for r in report.results] == [S.VERIFIED, S.FAILED, S.SKIPPED, S.SKIPPED]
    results = executor(ws, store, MT_ACCOUNT, ruleset).rollback(run.run_id)
    assert all(r.ok for r in results) and len(results) == 2
    assert "이미 이전 값" in results[0].message


def test_rollback_failure_is_reported(ws, store, sa_run, monkeypatch):
    run, ruleset = sa_run
    ex = _ready(ws, store, run, ruleset, SA_ACCOUNT)
    ex.apply(run.run_id)
    rb = executor(ws, store, SA_ACCOUNT, ruleset)
    monkeypatch.setattr(rb.adapter, "apply_change", lambda *a: None)  # 응답만 성공, 값은 그대로
    results = rb.rollback(run.run_id)
    assert not any(r.ok for r in results)
    assert store.get_run(run.run_id).status == RunStatus.ROLLBACK_PARTIAL
    assert any(e["action"] == "rollback_failed" for e in store.events(run.run_id))


def test_daily_cap_rechecked_at_apply(ws, store, sa_run):
    run, ruleset = sa_run
    ex = _ready(ws, store, run, ruleset, SA_ACCOUNT)
    ex.guardrails.max_changes_per_day = 2  # 승인 뒤 상한이 줄어든 상황
    report = ex.apply(run.run_id)
    statuses = [c.status for c in store.get_run(run.run_id).changes]
    assert statuses == [S.VERIFIED, S.VERIFIED, S.SKIPPED, S.SKIPPED]
    assert "일일 변경 건수 상한" in report.results[-1].message


def test_executor_rejects_other_account_run(ws, store, sa_run, mt_run):
    run, _ = sa_run
    _, mt_rules = mt_run
    with pytest.raises(RunStateError, match="계정 실행"):
        executor(ws, store, MT_ACCOUNT, mt_rules).preview(run.run_id)
