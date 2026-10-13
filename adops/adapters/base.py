"""광고 플랫폼 어댑터 인터페이스.

엔진(진단·규칙·실행)은 이 인터페이스만 안다. 플랫폼을 늘릴 때는 어댑터 하나만 새로 쓰면 된다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, ClassVar

from adops.models import DailyStat, Entity, EntityType, Platform


class AdPlatformAdapter(ABC):
    platform: Platform
    # 개체 종류별로 바꿀 수 있는 필드. 여기에 없는 필드 변경은 어댑터가 거부한다.
    editable_fields: ClassVar[dict[EntityType, set[str]]] = {}

    def __init__(self, account_id: str):
        self.account_id = account_id

    @property
    @abstractmethod
    def account_name(self) -> str: ...

    @property
    @abstractmethod
    def as_of(self) -> date:
        """실적이 마감된 마지막 날짜."""

    @property
    @abstractmethod
    def ops_date(self) -> date:
        """운영일(조정안을 만들고 반영하는 날)."""

    @abstractmethod
    def get_entities(self, entity_type: EntityType | None = None) -> list[Entity]:
        """계정의 광고 개체 목록."""

    @abstractmethod
    def get_stats(self, start: date, end: date, level: EntityType) -> list[DailyStat]:
        """기간(양 끝 포함)의 일별 실적."""

    @abstractmethod
    def get_state(self, entity_id: str) -> Entity:
        """개체 하나를 플랫폼에서 다시 조회한다(검증용, 캐시를 쓰지 않는다)."""

    @abstractmethod
    def apply_change(self, entity_id: str, field: str, value: Any) -> None:
        """필드 하나를 바꾼다. 실패하면 ApiError를 던진다."""

    def check_editable(self, entity: Entity, field: str) -> None:
        allowed = self.editable_fields.get(entity.type, set())
        if field not in allowed:
            raise ValueError(f"{entity.type}의 '{field}' 필드는 이 어댑터에서 바꿀 수 없습니다 "
                             f"(허용: {sorted(allowed)})")
