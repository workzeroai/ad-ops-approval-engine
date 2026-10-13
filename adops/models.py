"""공통 데이터 모델: 광고 개체, 일별 실적, 변경(Change), 실행(Run), 상태 전이."""
from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Platform(StrEnum):
    SEARCHAD_LIKE = "searchad_like"
    META_LIKE = "meta_like"


class EntityType(StrEnum):
    CAMPAIGN = "campaign"
    ADGROUP = "adgroup"
    KEYWORD = "keyword"
    ADSET = "adset"
    AD = "ad"


ENTITY_LABELS = {
    EntityType.CAMPAIGN: "캠페인",
    EntityType.ADGROUP: "광고그룹",
    EntityType.KEYWORD: "키워드",
    EntityType.ADSET: "광고 세트",
    EntityType.AD: "소재",
}

FIELD_LABELS = {"daily_budget": "일예산", "bid": "입찰가", "status": "상태"}


class Entity(BaseModel):
    """플랫폼마다 다른 원본 응답을 어댑터가 정규화한 광고 개체."""

    id: str
    account_id: str
    platform: Platform
    type: EntityType
    name: str
    parent_id: str | None = None
    fields: dict[str, Any] = Field(default_factory=dict)  # daily_budget, bid, status
    updated_at: date | None = None  # 마지막으로 값이 바뀐 날(학습 기간 보호에 사용)

    @property
    def active(self) -> bool:
        return self.fields.get("status", "ACTIVE") == "ACTIVE"


class DailyStat(BaseModel):
    date: date
    entity_id: str
    impressions: int = 0
    clicks: int = 0
    cost: int = 0
    conversions: int = 0
    revenue: int = 0
    avg_rank: float | None = None  # 검색광고형: 평균 노출 순위
    frequency: float | None = None  # 메타형: 최근 7일 빈도(플랫폼 보고값)
    hourly_impressions: list[int] | None = None  # 검색광고형 캠페인: 시간대별 노출


class ChangeStatus(StrEnum):
    PLANNED = "planned"
    PREVIEWED = "previewed"
    APPROVED = "approved"
    APPLIED = "applied"
    VERIFIED = "verified"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    BLOCKED = "blocked"  # 안전장치 위반으로 미리보기 단계에서 차단
    REJECTED = "rejected"  # 사람이 승인하지 않음
    SKIPPED = "skipped"  # 앞선 실패·상한 때문에 실행하지 않음


# 허용되는 상태 전이. 여기에 없는 전이는 모두 거부한다.
ALLOWED_TRANSITIONS: dict[ChangeStatus, set[ChangeStatus]] = {
    ChangeStatus.PLANNED: {ChangeStatus.PREVIEWED, ChangeStatus.BLOCKED},
    ChangeStatus.PREVIEWED: {ChangeStatus.APPROVED, ChangeStatus.REJECTED, ChangeStatus.BLOCKED},
    ChangeStatus.APPROVED: {ChangeStatus.APPLIED, ChangeStatus.FAILED, ChangeStatus.SKIPPED},
    ChangeStatus.APPLIED: {ChangeStatus.VERIFIED, ChangeStatus.FAILED, ChangeStatus.ROLLED_BACK},
    ChangeStatus.VERIFIED: {ChangeStatus.ROLLED_BACK},
    ChangeStatus.FAILED: {ChangeStatus.ROLLED_BACK},
    ChangeStatus.ROLLED_BACK: set(),
    ChangeStatus.BLOCKED: set(),
    ChangeStatus.REJECTED: set(),
    ChangeStatus.SKIPPED: set(),
}

STATUS_LABELS = {
    ChangeStatus.PLANNED: "계획",
    ChangeStatus.PREVIEWED: "미리보기",
    ChangeStatus.APPROVED: "승인",
    ChangeStatus.APPLIED: "반영",
    ChangeStatus.VERIFIED: "검증 완료",
    ChangeStatus.FAILED: "실패",
    ChangeStatus.ROLLED_BACK: "되돌림",
    ChangeStatus.BLOCKED: "차단",
    ChangeStatus.REJECTED: "거절",
    ChangeStatus.SKIPPED: "건너뜀",
}


class InvalidTransitionError(RuntimeError):
    pass


def check_transition(current: ChangeStatus, target: ChangeStatus) -> None:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransitionError(f"허용되지 않는 상태 전이: {current} → {target}")


class RunStatus(StrEnum):
    PLANNED = "planned"
    PREVIEWED = "previewed"
    APPROVED = "approved"
    COMPLETED = "completed"  # 승인된 변경이 모두 검증 완료
    HALTED = "halted"  # 검증 실패로 중단
    ROLLED_BACK = "rolled_back"
    ROLLBACK_PARTIAL = "rollback_partial"
    EMPTY = "empty"  # 조정안 없음


class Risk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Change(BaseModel):
    """변경 1건. 대상·필드·이전 값·새 값·근거 규칙·위험 등급을 함께 가진다."""

    change_id: str
    run_id: str
    seq: int
    account_id: str
    platform: Platform
    entity_id: str
    entity_type: EntityType
    entity_name: str
    field: str
    before: Any
    after: Any
    rule_id: str
    rule_name: str
    reason: str
    evidence: list[str] = Field(default_factory=list)
    risk: Risk = Risk.MEDIUM
    impact: str = ""
    status: ChangeStatus = ChangeStatus.PLANNED
    note: str = ""  # 차단·실패·건너뜀 사유

    @property
    def change_pct(self) -> float | None:
        if isinstance(self.before, int | float) and isinstance(self.after, int | float) and self.before:
            return (self.after - self.before) / self.before * 100
        return None


class Run(BaseModel):
    run_id: str
    account_id: str
    platform: Platform
    ops_date: date
    created_at: str
    status: RunStatus = RunStatus.PLANNED
    rules_file: str = ""
    changes: list[Change] = Field(default_factory=list)
