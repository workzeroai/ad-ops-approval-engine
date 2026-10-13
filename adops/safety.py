"""안전장치 검사(순수 함수). 미리보기와 반영 직전에 같은 검사를 쓴다.

| 장치 | 위반 시 |
|---|---|
| 계획 이후 값이 바뀜(drift) | 차단 — 오래된 조정안으로 덮어쓰지 않는다 |
| 1회 변경 폭 상한 | 차단 |
| 필드별 절대 하한·상한 | 차단 |
| 학습 기간 보호(cooldown) | 차단 |
| 일일 변경 건수 상한 | 차단(미리보기) / 건너뜀(반영 직전) |
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from adops.metrics import field_value, won
from adops.models import Change, Entity
from adops.rules.engine import Guardrails


@dataclass(frozen=True)
class Violation:
    code: str  # drift | max_change_pct | bounds | cooldown | daily_cap
    message: str


def check_change(change: Change, current: Entity, guardrails: Guardrails, ops_date: date) -> list[Violation]:
    """변경 1건이 안전장치를 통과하는지 본다. 빈 목록이면 통과."""
    out: list[Violation] = []
    now_value = current.fields.get(change.field)
    if now_value != change.before:
        out.append(Violation("drift", f"계획 이후 값이 바뀜(계획 때 {field_value(change.field, change.before)}, "
                                      f"지금 {field_value(change.field, now_value)})"))

    pct = change.change_pct
    if pct is not None and abs(pct) > guardrails.max_change_pct + 1e-9:
        out.append(Violation("max_change_pct",
                             f"변경 폭 {pct:+.1f}%가 상한 ±{guardrails.max_change_pct:.0f}%를 넘음"))

    bound = guardrails.bounds.get(change.field)
    if bound and isinstance(change.after, int | float):
        if bound.min is not None and change.after < bound.min:
            out.append(Violation("bounds", f"새 값 {won(change.after)}이 하한 {won(bound.min)}보다 작음"))
        if bound.max is not None and change.after > bound.max:
            out.append(Violation("bounds", f"새 값 {won(change.after)}이 상한 {won(bound.max)}보다 큼"))

    if guardrails.cooldown_days and current.updated_at:
        days = (ops_date - current.updated_at).days
        if days < guardrails.cooldown_days:
            out.append(Violation("cooldown", f"학습 기간 보호: {days}일 전에 바뀜 "
                                             f"(쿨다운 {guardrails.cooldown_days}일)"))
    return out


def daily_cap_violation(already_applied: int, queued: int, guardrails: Guardrails) -> Violation | None:
    """이미 반영한 건수 + 이번에 앞에 줄 선 건수가 상한에 닿았으면 위반."""
    if already_applied + queued >= guardrails.max_changes_per_day:
        return Violation("daily_cap", f"일일 변경 건수 상한 {guardrails.max_changes_per_day}건 도달"
                                      f"(오늘 반영 {already_applied}건)")
    return None
