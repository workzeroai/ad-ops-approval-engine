"""규칙에서 쓸 수 있는 지표 목록(이름·한국어 이름·단위·대상 개체).

규칙 YAML의 `metric`은 여기 있는 이름만 쓸 수 있다. 이름이 틀리면 규칙을 불러올 때 바로 알려 준다.
비율 지표(ROAS·CTR·CVR·변화율)는 모두 % 값이다. 예) ROAS 300% → 300
"""
from __future__ import annotations

from dataclasses import dataclass

from adops.models import EntityType

C, K, S, A = EntityType.CAMPAIGN, EntityType.KEYWORD, EntityType.ADSET, EntityType.AD


@dataclass(frozen=True)
class MetricDef:
    name: str
    label: str
    unit: str  # won | count | pct | rank | day | hour | freq
    entities: frozenset[EntityType]
    help: str = ""


_DEFS = [
    MetricDef("daily_budget", "일예산", "won", frozenset({C, S})),
    MetricDef("bid", "입찰가", "won", frozenset({K})),
    MetricDef("spend_7d", "최근 7일 비용", "won", frozenset({C, K, S, A})),
    MetricDef("revenue_7d", "최근 7일 전환 매출", "won", frozenset({C, K, S, A})),
    MetricDef("roas_7d", "최근 7일 ROAS", "pct", frozenset({C, K, S, A}), "전환 매출 ÷ 비용 × 100"),
    MetricDef("conv_7d", "최근 7일 전환", "count", frozenset({C, K, S, A})),
    MetricDef("impressions_7d", "최근 7일 노출", "count", frozenset({C, K, S, A})),
    MetricDef("clicks_7d", "최근 7일 클릭", "count", frozenset({C, K, S, A})),
    MetricDef("ctr_7d", "최근 7일 CTR", "pct", frozenset({C, K, S, A})),
    MetricDef("cvr_7d", "최근 7일 전환율", "pct", frozenset({C, K, S, A}), "전환 ÷ 클릭 × 100"),
    MetricDef("cpc_7d", "최근 7일 클릭당 비용", "won", frozenset({C, K, S, A})),
    MetricDef("cpa_7d", "최근 7일 전환당 비용", "won", frozenset({C, K, S, A})),
    MetricDef("avg_rank_7d", "최근 7일 평균 노출 순위", "rank", frozenset({C, K})),
    MetricDef("exhausted_days_7d", "최근 7일 예산 소진일", "day", frozenset({C}),
              "하루가 끝나기 전에 노출이 멈춘 날 수(시간대별 노출 기준)"),
    MetricDef("avg_exhaust_hour_7d", "평균 예산 소진 시각", "hour", frozenset({C}),
              "소진된 날의 마지막 노출 시간대 평균"),
    MetricDef("lost_impr_est_7d", "추정 노출 손실(7일)", "count", frozenset({C}),
              "소진 시각 이후 평소 시간대 비중으로 추정한 노출 수"),
    MetricDef("budget_util_7d", "최근 7일 예산 사용률", "pct", frozenset({C, S})),
    MetricDef("campaign_exhausted_days_7d", "소속 캠페인 예산 소진일", "day", frozenset({K})),
    MetricDef("roas_rank_pct", "계정 내 ROAS 순위 백분위", "pct", frozenset({S, A}), "0 = 1등, 100 = 꼴찌"),
    MetricDef("days_since_change", "마지막 변경 후 지난 날", "day", frozenset({C, K, S, A})),
    MetricDef("frequency", "빈도(최근 7일)", "freq", frozenset({A})),
    MetricDef("ctr_change_pct", "CTR 변화율(직전 7일 대비)", "pct", frozenset({A})),
]

METRICS: dict[str, MetricDef] = {m.name: m for m in _DEFS}


def metrics_for(entity_type: EntityType) -> list[str]:
    return [m.name for m in _DEFS if entity_type in m.entities]


def format_value(unit: str, value: float | int | None) -> str:
    if value is None:
        return "-"
    if unit == "won":
        return f"{value:,.0f}원"
    if unit == "count":
        return f"{value:,.0f}"
    if unit == "pct":
        return f"{value:,.0f}%" if abs(value) >= 10 else f"{value:,.1f}%"
    if unit == "rank":
        return f"{value:.1f}위"
    if unit == "day":
        return f"{value:,.0f}일"
    if unit == "hour":
        return f"{value:.0f}시"
    if unit == "freq":
        return f"{value:.1f}회"
    return f"{value}"


def format_metric(name: str, value: float | int | None) -> str:
    unit = METRICS[name].unit if name in METRICS else ""
    return format_value(unit, value)


def field_value(field: str, value: object) -> str:
    """변경 대상 필드 값 표시: 금액은 '1,000원', 상태는 '운영/중지'."""
    if field == "status":
        return {"PAUSED": "중지", "ACTIVE": "운영"}.get(str(value), str(value))
    return f"{value:,.0f}원" if isinstance(value, int | float) else str(value)


def won(value: float | int) -> str:
    return f"{value:,.0f}원"


def signed_won(value: float | int) -> str:
    return f"{value:+,.0f}원"
