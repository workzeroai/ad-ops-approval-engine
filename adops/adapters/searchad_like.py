"""검색광고형 어댑터: 캠페인(일예산) → 광고그룹 → 키워드(입찰가).

가짜 서버의 검색광고형 응답(camelCase 필드, ON/OFF 상태, 시간대별 노출)을 공통 모델로 바꾼다.
"""
from __future__ import annotations

from datetime import date
from typing import Any, ClassVar

from adops.adapters.base import AdPlatformAdapter
from adops.adapters.fake_platform import FakeAdServer
from adops.models import DailyStat, Entity, EntityType, Platform

# 공통 개체 종류 → (원본 컬렉션, id 키, 이름 키, 부모 id 키)
_COLLECTIONS: dict[EntityType, tuple[str, str, str, str | None]] = {
    EntityType.CAMPAIGN: ("campaigns", "campaignId", "name", None),
    EntityType.ADGROUP: ("adgroups", "adgroupId", "name", "campaignId"),
    EntityType.KEYWORD: ("keywords", "keywordId", "keyword", "adgroupId"),
}
# 공통 필드 → 원본 필드
_FIELD_TO_NATIVE = {"daily_budget": "dailyBudget", "bid": "bidAmt", "status": "userLock"}


def _status_from_native(obj: dict[str, Any]) -> str:
    return "PAUSED" if obj.get("userLock") else "ACTIVE"


class SearchAdLikeAdapter(AdPlatformAdapter):
    platform = Platform.SEARCHAD_LIKE
    editable_fields: ClassVar[dict[EntityType, set[str]]] = {
        EntityType.CAMPAIGN: {"daily_budget", "status"},
        EntityType.ADGROUP: {"status"},
        EntityType.KEYWORD: {"bid", "status"},
    }

    def __init__(self, server: FakeAdServer, account_id: str):
        super().__init__(account_id)
        self.server = server

    @property
    def account_name(self) -> str:
        return self.server.account(self.account_id)["name"]

    @property
    def as_of(self) -> date:
        return self.server.as_of

    @property
    def ops_date(self) -> date:
        return self.server.ops_date

    # ------------------------------------------------------------ 변환
    def _to_entity(self, etype: EntityType, obj: dict[str, Any]) -> Entity:
        _, id_key, name_key, parent_key = _COLLECTIONS[etype]
        fields: dict[str, Any] = {"status": _status_from_native(obj)}
        if "dailyBudget" in obj:
            fields["daily_budget"] = int(obj["dailyBudget"])
        if "bidAmt" in obj:
            fields["bid"] = int(obj["bidAmt"])
        return Entity(
            id=obj[id_key],
            account_id=self.account_id,
            platform=self.platform,
            type=etype,
            name=obj[name_key],
            parent_id=obj.get(parent_key) if parent_key else None,
            fields=fields,
            updated_at=date.fromisoformat(obj["editTm"]) if obj.get("editTm") else None,
        )

    # ------------------------------------------------------------ 인터페이스
    def get_entities(self, entity_type: EntityType | None = None) -> list[Entity]:
        types = [entity_type] if entity_type else list(_COLLECTIONS)
        out: list[Entity] = []
        for et in types:
            if et not in _COLLECTIONS:
                continue
            collection = _COLLECTIONS[et][0]
            out += [self._to_entity(et, o) for o in self.server.list_objects(self.account_id, collection)]
        return out

    def get_stats(self, start: date, end: date, level: EntityType) -> list[DailyStat]:
        rows = self.server.list_stats(self.account_id, start, end, level=level.value)
        return [
            DailyStat(
                date=date.fromisoformat(r["statDt"]),
                entity_id=r["id"],
                impressions=r["impCnt"],
                clicks=r["clkCnt"],
                cost=r["spendAmt"],
                conversions=r["convCnt"],
                revenue=r["convAmt"],
                avg_rank=r.get("avgRank"),
                hourly_impressions=r.get("hourlyImpCnt"),
            )
            for r in rows
        ]

    def _locate(self, entity_id: str) -> tuple[EntityType, dict[str, Any]]:
        for et, (collection, id_key, _, _) in _COLLECTIONS.items():
            for obj in self.server.list_objects(self.account_id, collection):
                if obj[id_key] == entity_id:
                    return et, obj
        raise KeyError(f"개체를 찾을 수 없습니다: {entity_id}")

    def get_state(self, entity_id: str) -> Entity:
        et, _ = self._locate(entity_id)
        collection, id_key, _, _ = _COLLECTIONS[et]
        return self._to_entity(et, self.server.get_object(self.account_id, collection, entity_id, id_key))

    def apply_change(self, entity_id: str, field: str, value: Any) -> None:
        et, obj = self._locate(entity_id)
        self.check_editable(self._to_entity(et, obj), field)
        collection, id_key, _, _ = _COLLECTIONS[et]
        native_value: Any = (value == "PAUSED") if field == "status" else int(value)
        self.server.update_object(self.account_id, collection, entity_id, id_key,
                                  {_FIELD_TO_NATIVE[field]: native_value})


class SearchAdLiveAdapter(AdPlatformAdapter):  # pragma: no cover - 실연동 자리
    """실제 검색광고 API 연동 자리. 이 저장소에서는 구현하지 않는다.

    실연동 시 할 일(네이버 검색광고 API 기준의 일반적인 방식):
    - 인증 헤더: X-Timestamp(ms), X-API-KEY(액세스 라이선스), X-Customer(광고주 계정 ID), X-Signature
    - 서명: Base64(HMAC-SHA256(secret_key, f"{timestamp}.{HTTP_METHOD}.{URI}"))
    - 키는 환경 변수(.env)로만 받고 저장소에 두지 않는다(.env.example 참고).
    - 입찰가 변경은 키워드 단위 PUT, 일예산은 캠페인 단위 PUT. 응답 직후 GET으로 재조회해 검증한다.
    - 호출량 제한(초당 요청 수)을 넘지 않도록 요청 간격과 재시도(지수 백오프)를 둔다.
    """

    platform = Platform.SEARCHAD_LIKE

    def __init__(self, account_id: str, api_key: str, secret_key: str, customer_id: str):
        raise NotImplementedError("실제 API 연동은 이 저장소 범위 밖입니다. README '다음 단계'를 참고하세요.")
