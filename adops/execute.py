"""실행 파이프라인: preview → approve → apply → verify → rollback.

상태 전이: planned → previewed → approved → applied → verified | failed → rolled_back
(옆길: previewed → blocked/rejected, approved → skipped)

- 승인(approved) 상태가 아닌 변경은 어떤 경로로도 반영하지 않는다.
- 반영 직후 플랫폼에서 다시 조회해 값이 맞는지 검증한다. 하나라도 실패하면 남은 변경은 건너뛰고 실행을 멈춘다.
- 되돌리기는 실행 ID 단위로, 반영된 변경을 역순으로 이전 값으로 되돌리고 다시 검증한다.
- 모든 단계는 감사 로그(events)에 남는다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adops.adapters.base import AdPlatformAdapter
from adops.adapters.fake_platform import ApiError
from adops.audit import AuditStore
from adops.metrics import field_value
from adops.models import Change, ChangeStatus, Run, RunStatus
from adops.rules.engine import Guardrails
from adops.safety import check_change, daily_cap_violation

SYSTEM = "system:executor"


class ApprovalRequiredError(RuntimeError):
    """승인되지 않은 변경을 반영하려 할 때."""


class RunStateError(RuntimeError):
    """실행 상태가 요청한 단계와 맞지 않을 때."""


@dataclass
class StepResult:
    change: Change
    ok: bool
    message: str = ""
    attempts: int = 0
    current: Any = None


@dataclass
class ApplyReport:
    run_id: str
    results: list[StepResult] = field(default_factory=list)
    halted: bool = False
    halt_reason: str = ""

    @property
    def verified(self) -> int:
        return sum(1 for r in self.results if r.change.status == ChangeStatus.VERIFIED)


class Executor:
    def __init__(self, adapter: AdPlatformAdapter, store: AuditStore, guardrails: Guardrails,
                 actor: str = "operator"):
        self.adapter = adapter
        self.store = store
        self.guardrails = guardrails
        self.actor = actor

    def _run(self, run_id: str) -> Run:
        run = self.store.get_run(run_id)
        if run.account_id != self.adapter.account_id:
            raise RunStateError(f"{run_id}는 {run.account_id} 계정 실행입니다")
        return run

    # ------------------------------------------------------------ preview
    def preview(self, run_id: str) -> list[StepResult]:
        """현재 값을 다시 조회해 변경 전/후를 확정하고 안전장치를 검사한다."""
        run = self._run(run_id)
        planned = [c for c in run.changes if c.status == ChangeStatus.PLANNED]
        if not planned:
            raise RunStateError(f"{run_id}: 미리보기할 계획 상태 변경이 없습니다")
        applied_today = self.store.count_applied(run.account_id, run.ops_date)
        queued = 0
        results = []
        for c in planned:
            current = self.adapter.get_state(c.entity_id)
            violations = check_change(c, current, self.guardrails, run.ops_date)
            cap = daily_cap_violation(applied_today, queued, self.guardrails)
            if cap and not violations:
                violations.append(cap)
            if violations:
                msg = "; ".join(v.message for v in violations)
                self.store.transition(c, ChangeStatus.BLOCKED, SYSTEM, note=msg)
                results.append(StepResult(c, False, msg, current=current.fields.get(c.field)))
            else:
                queued += 1
                self.store.transition(c, ChangeStatus.PREVIEWED, SYSTEM, detail="안전장치 통과")
                results.append(StepResult(c, True, "안전장치 통과", current=current.fields.get(c.field)))
        self.store.set_run_status(run_id, RunStatus.PREVIEWED, SYSTEM,
                                  f"통과 {queued}건, 차단 {len(planned) - queued}건")
        return results

    # ------------------------------------------------------------ approve
    def approve(self, run_id: str, seqs: list[int] | None = None, reject: list[int] | None = None,
                note: str = "") -> tuple[list[Change], list[Change]]:
        """seqs=None이면 미리보기를 통과한 변경을 모두 승인한다. reject에 든 번호는 거절한다."""
        run = self._run(run_id)
        reject = reject or []
        candidates = [c for c in run.changes if c.status == ChangeStatus.PREVIEWED]
        if not candidates:
            raise RunStateError(f"{run_id}: 승인할 변경이 없습니다(먼저 preview)")
        approved, rejected = [], []
        for c in candidates:
            if c.seq in reject:
                self.store.transition(c, ChangeStatus.REJECTED, self.actor, note=note or "승인 거절")
                rejected.append(c)
            elif seqs is None or c.seq in seqs:
                self.store.transition(c, ChangeStatus.APPROVED, self.actor, detail=note or "승인")
                approved.append(c)
        if approved:
            self.store.set_run_status(run_id, RunStatus.APPROVED, self.actor, f"승인 {len(approved)}건")
        return approved, rejected

    # ------------------------------------------------------------ apply + verify
    def apply(self, run_id: str) -> ApplyReport:
        run = self._run(run_id)
        approved = [c for c in run.changes if c.status == ChangeStatus.APPROVED]
        if not approved:
            raise ApprovalRequiredError(f"{run_id}: 승인된 변경이 없습니다. 승인 없이 반영하지 않습니다")
        report = ApplyReport(run_id)
        for i, c in enumerate(approved):
            if report.halted:
                self.store.transition(c, ChangeStatus.SKIPPED, SYSTEM, note=f"실행 중단: {report.halt_reason}")
                report.results.append(StepResult(c, False, "건너뜀(실행 중단)"))
                continue
            cap = daily_cap_violation(self.store.count_applied(run.account_id, run.ops_date), 0, self.guardrails)
            if cap:
                for rest in approved[i:]:
                    self.store.transition(rest, ChangeStatus.SKIPPED, SYSTEM, note=cap.message)
                    report.results.append(StepResult(rest, False, cap.message))
                break
            result = self.apply_one(c)
            report.results.append(result)
            if not result.ok:
                report.halted, report.halt_reason = True, f"{c.change_id} {result.message}"
                self.store.log(run_id, c.change_id, SYSTEM, "halted", "검증 실패로 남은 변경을 실행하지 않음")
        status = RunStatus.HALTED if report.halted else RunStatus.COMPLETED
        self.store.set_run_status(run_id, status, SYSTEM, f"검증 완료 {report.verified}건")
        return report

    def apply_one(self, c: Change) -> StepResult:
        """변경 1건 반영 → 재조회 검증. 승인 상태가 아니면 예외."""
        if c.status != ChangeStatus.APPROVED:
            raise ApprovalRequiredError(f"{c.change_id}: 상태가 '{c.status}'라 반영할 수 없습니다(승인 필요)")
        ok, attempts, err = self._call_with_retry(c, c.after)
        if not ok:
            self.store.transition(c, ChangeStatus.FAILED, SYSTEM, note=f"API 오류: {err}")
            return StepResult(c, False, f"API 오류: {err}", attempts)
        self.store.transition(c, ChangeStatus.APPLIED, SYSTEM,
                              detail=f"{field_value(c.field, c.before)} → {field_value(c.field, c.after)} "
                                     f"(시도 {attempts}회)")
        current = self.adapter.get_state(c.entity_id).fields.get(c.field)
        if current == c.after:
            self.store.transition(c, ChangeStatus.VERIFIED, SYSTEM,
                                  detail=f"재조회 값 {field_value(c.field, current)}")
            return StepResult(c, True, "재조회 값 일치", attempts, current)
        msg = f"검증 불일치: 기대 {field_value(c.field, c.after)}, 실제 {field_value(c.field, current)}"
        self.store.transition(c, ChangeStatus.FAILED, SYSTEM, note=msg)
        return StepResult(c, False, msg, attempts, current)

    def _call_with_retry(self, c: Change, value: Any) -> tuple[bool, int, str]:
        attempts, last = 0, ""
        for attempt in range(1, self.guardrails.max_retries + 2):
            attempts = attempt
            try:
                self.adapter.apply_change(c.entity_id, c.field, value)
                return True, attempts, ""
            except ApiError as exc:
                last = str(exc)
                self.store.log(c.run_id, c.change_id, SYSTEM, "api_error", f"시도 {attempt}: {exc}")
                if not exc.transient:
                    break
        return False, attempts, last

    # ------------------------------------------------------------ verify(재점검)
    def verify(self, run_id: str) -> list[StepResult]:
        """검증 완료된 변경이 지금도 그 값인지 다시 본다(사람이 콘솔에서 바꿨는지 확인)."""
        run = self._run(run_id)
        out = []
        for c in run.changes:
            if c.status != ChangeStatus.VERIFIED:
                continue
            current = self.adapter.get_state(c.entity_id).fields.get(c.field)
            ok = current == c.after
            if not ok:
                self.store.log(run_id, c.change_id, SYSTEM, "drift_detected", f"기대 {c.after}, 현재 {current}")
            msg = "일치" if ok else f"값이 바뀜(현재 {field_value(c.field, current)})"
            out.append(StepResult(c, ok, msg, current=current))
        return out

    # ------------------------------------------------------------ rollback
    def rollback(self, run_id: str) -> list[StepResult]:
        run = self._run(run_id)
        targets = [c for c in reversed(run.changes)
                   if c.status in (ChangeStatus.APPLIED, ChangeStatus.VERIFIED, ChangeStatus.FAILED)]
        if not targets:
            raise RunStateError(f"{run_id}: 되돌릴 변경이 없습니다")
        self.store.log(run_id, None, self.actor, "rollback_started", f"대상 {len(targets)}건")
        results, all_ok = [], True
        for c in targets:
            current = self.adapter.get_state(c.entity_id).fields.get(c.field)
            if current == c.before:
                before_text = field_value(c.field, c.before)
                self.store.transition(c, ChangeStatus.ROLLED_BACK, self.actor,
                                      detail=f"현재 값이 이미 이전 값({before_text})")
                results.append(StepResult(c, True, f"반영되지 않아 이미 이전 값({before_text})", 0, current))
                continue
            ok, attempts, err = self._call_with_retry(c, c.before)
            restored = self.adapter.get_state(c.entity_id).fields.get(c.field) if ok else current
            restore_text = f"{field_value(c.field, current)} → {field_value(c.field, c.before)}"
            if ok and restored == c.before:
                self.store.transition(c, ChangeStatus.ROLLED_BACK, self.actor,
                                      detail=f"{restore_text} 복원, 재조회 일치")
                results.append(StepResult(c, True, f"{restore_text} 복원 · 재조회 일치", attempts, restored))
            else:
                all_ok = False
                msg = err or (f"복원 검증 불일치: 기대 {field_value(c.field, c.before)}, "
                              f"실제 {field_value(c.field, restored)}")
                self.store.log(run_id, c.change_id, SYSTEM, "rollback_failed", msg)
                results.append(StepResult(c, False, msg, attempts, restored))
        self.store.set_run_status(run_id, RunStatus.ROLLED_BACK if all_ok else RunStatus.ROLLBACK_PARTIAL,
                                  self.actor, f"되돌림 {sum(r.ok for r in results)}/{len(results)}건")
        return results
