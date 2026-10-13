"""메타형 어댑터: 캠페인 → 광고 세트(일예산) → 광고 소재(상태).

가짜 서버의 메타형 응답은 숫자를 문자열로 주고(예: "spend": "51234"),
전환은 actions 목록 안에 들어 있다. 어댑터가 이를 공통 모델로 바꾸고,
광고 세트 실적은 소재 실적을 합쳐 만든다.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, ClassVar

from adops.adapters.base import AdPlatformAdapter
from adops.adapters.fake_platform import FakeAdServer
from adops.models import DailyStat, Entity, EntityType, Platform

_COLLECTIONS: dict[EntityType, tuple[str, str | None]] = {
    EntityType.CAMPAIGN: ("campaigns", None),
    EntityType.ADSET: ("adsets", "campaign_id"),
    EntityType.AD: ("ads", "adset_id"),
}


def _action_value(items: list[dict[str, str]] | None, action_type: str) -> float:
    for item in items or []:
        if item.get("action_type") == action_type:
            return float(item["value"])
    return 0.0


class MetaLikeAdapter(AdPlatformAdapter):
    platform = Platform.META_LIKE
    editable_fields: ClassVar[dict[EntityType, set[str]]] = {
        EntityType.CAMPAIGN: {"status"},
        EntityType.ADSET: {"daily_budget", "status"},
        EntityType.AD: {"status"},
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

    def _to_entity(self, etype: EntityType, obj: dict[str, Any]) -> Entity:
        parent_key = _COLLECTIONS[etype][1]
        fields: dict[str, Any] = {"status": obj["status"]}
        if "daily_budget" in obj:
            fields["daily_budget"] = int(obj["daily_budget"])  # 원본은 문자열
        return Entity(
            id=obj["id"],
            account_id=self.account_id,
            platform=self.platform,
            type=etype,
            name=obj["name"],
            parent_id=obj.get(parent_key) if parent_key else None,
            fields=fields,
            updated_at=date.fromisoformat(obj["updated_time"]) if obj.get("updated_time") else None,
        )

    def get_entities(self, entity_type: EntityType | None = None) -> list[Entity]:
        types = [entity_type] if entity_type else list(_COLLECTIONS)
        out: list[Entity] = []
        for et in types:
            if et not in _COLLECTIONS:
                continue
            out += [self._to_entity(et, o) for o in self.server.list_objects(self.account_id, _COLLECTIONS[et][0])]
        return out

    def get_stats(self, start: date, end: date, level: EntityType) -> list[DailyStat]:
        rows = self.server.list_stats(self.account_id, start, end)
        ad_stats = [
            DailyStat(
                date=date.fromisoformat(r["date_start"]),
                entity_id=r["ad_id"],
                impressions=int(r["impressions"]),
                clicks=int(r["clicks"]),
                cost=round(float(r["spend"])),
                conversions=int(_action_value(r.get("actions"), "purchase")),
                revenue=round(_action_value(r.get("action_values"), "purchase")),
                frequency=float(r["frequency"]),
            )
            for r in rows
        ]
        if level == EntityType.AD:
            return ad_stats
        # 광고 세트·캠페인 실적은 소재 실적을 합쳐 만든다.
        ads = {e.id: e for e in self.get_entities(EntityType.AD)}
        adsets = {e.id: e for e in self.get_entities(EntityType.ADSET)}
        agg: dict[tuple[date, str], dict[str, int]] = defaultdict(
            lambda: {"impressions": 0, "clicks": 0, "cost": 0, "conversions": 0, "revenue": 0})
        for s in ad_stats:
            parent = ads[s.entity_id].parent_id
            if level == EntityType.CAMPAIGN:
                parent = adsets[parent].parent_id
            bucket = agg[(s.date, parent)]
            for k in bucket:
                bucket[k] += getattr(s, k)
        return [DailyStat(date=d, entity_id=eid, **v) for (d, eid), v in sorted(agg.items())]

    def _locate(self, entity_id: str) -> tuple[EntityType, dict[str, Any]]:
        for et, (collection, _) in _COLLECTIONS.items():
            for obj in self.server.list_objects(self.account_id, collection):
                if obj["id"] == entity_id:
                    return et, obj
        raise KeyError(f"개체를 찾을 수 없습니다: {entity_id}")

    def get_state(self, entity_id: str) -> Entity:
        et, _ = self._locate(entity_id)
        return self._to_entity(et, self.server.get_object(self.account_id, _COLLECTIONS[et][0], entity_id, "id"))

    def apply_change(self, entity_id: str, field: str, value: Any) -> None:
        et, obj = self._locate(entity_id)
        self.check_editable(self._to_entity(et, obj), field)
        native = str(int(value)) if field == "daily_budget" else value
        self.server.update_object(self.account_id, _COLLECTIONS[et][0], entity_id, "id", {field: native})


class MetaLiveAdapter(AdPlatformAdapter):  # pragma: no cover - 실연동 자리
    """실제 메타 마케팅 API 연동 자리. 이 저장소에서는 구현하지 않는다.

    실연동 시 할 일(Graph API 기준의 일반적인 방식):
    - 인증: 시스템 사용자 액세스 토큰 + appsecret_proof = HMAC-SHA256(app_secret, access_token)
    - 조회: GET /act_{ad_account_id}/insights?level=ad&time_increment=1&fields=spend,impressions,clicks,
      frequency,actions,action_values
    - 변경: POST /{adset_id} daily_budget=<통화 최소 단위 문자열>, POST /{ad_id} status=PAUSED
    - 예산을 크게 바꾸면 학습 단계가 다시 시작될 수 있어, 변경 폭 상한과 쿨다운(안전장치)을 함께 둔다.
    - 호출량 제한(Business Use Case 한도) 응답 헤더를 보고 요청 속도를 조절한다.
    """

    platform = Platform.META_LIKE

    def __init__(self, account_id: str, access_token: str, app_secret: str):
        raise NotImplementedError("실제 API 연동은 이 저장소 범위 밖입니다. README '다음 단계'를 참고하세요.")
