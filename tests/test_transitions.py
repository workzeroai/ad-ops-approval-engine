"""상태 전이: 허용 표, 감사 로그 저장소의 전이 검사와 이벤트 기록."""
from __future__ import annotations

import itertools

import pytest

from adops.models import ALLOWED_TRANSITIONS, ChangeStatus, InvalidTransitionError, check_transition

S = ChangeStatus

HAPPY_PATH = [S.PLANNED, S.PREVIEWED, S.APPROVED, S.APPLIED, S.VERIFIED, S.ROLLED_BACK]


def test_happy_path_is_allowed():
    for a, b in itertools.pairwise(HAPPY_PATH):
        check_transition(a, b)


@pytest.mark.parametrize("a,b", [
    (S.PLANNED, S.APPROVED),  # 미리보기 없이 승인 금지
    (S.PLANNED, S.APPLIED),  # 승인 없이 반영 금지
    (S.PREVIEWED, S.APPLIED),  # 승인 없이 반영 금지
    (S.BLOCKED, S.APPROVED),  # 차단된 변경은 승인 불가
    (S.REJECTED, S.APPROVED),
    (S.SKIPPED, S.APPLIED),
    (S.ROLLED_BACK, S.APPLIED),  # 되돌린 변경을 다시 반영하려면 새 조정안
    (S.VERIFIED, S.APPLIED),
])
def test_forbidden_transitions(a, b):
    with pytest.raises(InvalidTransitionError):
        check_transition(a, b)


def test_terminal_states_have_no_exit():
    for st in (S.ROLLED_BACK, S.BLOCKED, S.REJECTED, S.SKIPPED):
        assert ALLOWED_TRANSITIONS[st] == set()


def test_only_approved_can_reach_applied():
    sources = {a for a, targets in ALLOWED_TRANSITIONS.items() if S.APPLIED in targets}
    assert sources == {S.APPROVED}


def test_store_rejects_invalid_transition_and_keeps_state(store, sa_run):
    run, _ = sa_run
    change = run.changes[0]
    with pytest.raises(InvalidTransitionError):
        store.transition(change, S.APPLIED, "tester")
    assert store.get_run(run.run_id).changes[0].status == S.PLANNED


def test_store_records_every_transition(store, sa_run):
    run, _ = sa_run
    change = run.changes[0]
    store.transition(change, S.PREVIEWED, "tester", detail="ok")
    store.transition(change, S.REJECTED, "boss", note="이번 주는 보류")
    events = [e for e in store.events(run.run_id) if e["change_id"] == change.change_id]
    assert [(e["from_status"], e["to_status"]) for e in events] == [
        (None, "planned"), ("planned", "previewed"), ("previewed", "rejected")]
    assert events[-1]["actor"] == "boss"
    saved = store.get_run(run.run_id).changes[0]
    assert saved.status == S.REJECTED and saved.note == "이번 주는 보류"
