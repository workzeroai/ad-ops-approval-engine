"""진단: 일별 실적에서 개체별 지표를 계산하고, 사람이 봐야 할 신호(경보)를 찾는다.

- 검색광고형: 예산 조기 소진일·소진 시각·노출 손실 추정, 순위 문제처럼 보이지만 예산이 원인인 키워드,
  전환 없는 비용
- 메타형: 위닝 소재, 소재 피로(CTR 하락 + 빈도 상승), ROAS 1 미만 광고 세트, 학습 기간 중인 세트

여기서 계산한 지표(metrics)를 규칙 엔진이 그대로 읽는다.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from statistics import mean

from adops.adapters.base import AdPlatformAdapter
from adops.metrics import format_metric, won
from adops.models import DailyStat, Entity, EntityType, Platform

WINDOW = 7
HISTORY = 28

# 진단 경보 기준(보고용). 실제 조정 기준은 규칙 YAML에서 따로 정한다.
EXHAUSTED_ALERT_DAYS = 3
WASTE_SPEND = 50_000
LOW_RANK = 4.0
FATIGUE_CTR_DROP = -30.0
FATIGUE_FREQUENCY = 3.5
WINNING_MIN_CONV = 20
LEARNING_DAYS = 3


@dataclass
class Finding:
    level: str  # danger | warning | info | success
    kind: str
    entity_id: str
    entity_name: str
    title: str
    detail: str


@dataclass
class AccountDiagnosis:
    account_id: str
    account_name: str
    platform: Platform
    as_of: date
    ops_date: date
    entities: dict[str, Entity]
    metrics: dict[str, dict[str, float | None]]
    findings: list[Finding] = field(default_factory=list)
    kpi_yesterday: dict[str, float] = field(default_factory=dict)
    kpi_avg7: dict[str, float] = field(default_factory=dict)
    daily: list[dict] = field(default_factory=list)  # 28일 계정 합계(브리핑 추세선)
    exhaustion: list[dict] = field(default_factory=list)  # 캠페인별 최근 7일 시간대 노출(브리핑 열지도)
    ranking: list[dict] = field(default_factory=list)  # 키워드·소재 성과 순위

    @property
    def window(self) -> tuple[date, date]:
        return self.as_of - timedelta(days=WINDOW - 1), self.as_of


# ------------------------------------------------------------------ 계산 도우미

def _ratio(a: float, b: float, scale: float = 100.0) -> float | None:
    return a / b * scale if b else None


def _sum_stats(stats: list[DailyStat]) -> dict[str, float]:
    keys = ("impressions", "clicks", "cost", "conversions", "revenue")
    return {k: float(sum(getattr(s, k) for s in stats)) for k in keys}


def _base_metrics(stats: list[DailyStat]) -> dict[str, float | None]:
    t = _sum_stats(stats)
    return {
        "spend_7d": t["cost"],
        "revenue_7d": t["revenue"],
        "roas_7d": _ratio(t["revenue"], t["cost"]),
        "conv_7d": t["conversions"],
        "impressions_7d": t["impressions"],
        "clicks_7d": t["clicks"],
        "ctr_7d": _ratio(t["clicks"], t["impressions"]),
        "cvr_7d": _ratio(t["conversions"], t["clicks"]),
        "cpc_7d": _ratio(t["cost"], t["clicks"], 1.0),
        "cpa_7d": _ratio(t["cost"], t["conversions"], 1.0),
    }


def _exhaust_hour(hourly: list[int] | None) -> int | None:
    """하루가 끝나기 전에 노출이 멈췄으면 마지막 노출 시간대, 아니면 None."""
    if not hourly or hourly[-1] > 0:
        return None
    for h in range(len(hourly) - 1, -1, -1):
        if hourly[h] > 0:
            return h
    return 0


def _hour_profile(stats: list[DailyStat]) -> list[float]:
    """예산이 소진되지 않은 날들로 평소 시간대별 노출 비중을 추정한다."""
    totals = [0.0] * 24
    for s in stats:
        if s.hourly_impressions and _exhaust_hour(s.hourly_impressions) is None:
            for h, v in enumerate(s.hourly_impressions):
                totals[h] += v
    total = sum(totals)
    return [v / total for v in totals] if total else [1 / 24] * 24


def _rank_pct(values: dict[str, float | None]) -> dict[str, float]:
    """값이 큰 순서로 0(1등)~100(꼴찌) 백분위."""
    ordered = sorted((v, k) for k, v in values.items() if v is not None)
    ordered.reverse()
    n = len(ordered)
    return {k: (i / (n - 1) * 100 if n > 1 else 0.0) for i, (_, k) in enumerate(ordered)}


def _by_entity(stats: list[DailyStat]) -> dict[str, list[DailyStat]]:
    out: dict[str, list[DailyStat]] = defaultdict(list)
    for s in stats:
        out[s.entity_id].append(s)
    return out


def _daily_totals(stats: list[DailyStat]) -> list[dict]:
    per_day: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for s in stats:
        d = per_day[s.date]
        for k in ("impressions", "clicks", "cost", "conversions", "revenue"):
            d[k] += getattr(s, k)
    return [{"date": d, **v} for d, v in sorted(per_day.items())]


def _kpis(day_rows: list[dict]) -> dict[str, float]:
    t = {k: sum(r[k] for r in day_rows) for k in ("impressions", "clicks", "cost", "conversions", "revenue")}
    n = max(len(day_rows), 1)
    return {
        "spend": t["cost"] / n,
        "revenue": t["revenue"] / n,
        "conversions": t["conversions"] / n,
        "clicks": t["clicks"] / n,
        "roas": (t["revenue"] / t["cost"] * 100) if t["cost"] else 0.0,
    }


# ------------------------------------------------------------------ 진단

def diagnose(adapter: AdPlatformAdapter) -> AccountDiagnosis:
    as_of = adapter.as_of
    start7 = as_of - timedelta(days=WINDOW - 1)
    hist_start = as_of - timedelta(days=HISTORY - 1)
    entities = {e.id: e for e in adapter.get_entities()}
    diag = AccountDiagnosis(
        account_id=adapter.account_id,
        account_name=adapter.account_name,
        platform=adapter.platform,
        as_of=as_of,
        ops_date=adapter.ops_date,
        entities=entities,
        metrics={},
    )
    top_level = EntityType.CAMPAIGN
    account_daily = _daily_totals(adapter.get_stats(hist_start, as_of, top_level))
    diag.daily = account_daily
    diag.kpi_yesterday = _kpis([r for r in account_daily if r["date"] == as_of])
    diag.kpi_avg7 = _kpis([r for r in account_daily if r["date"] >= start7])

    if adapter.platform == Platform.SEARCHAD_LIKE:
        _diagnose_searchad(adapter, diag, hist_start, start7)
    else:
        _diagnose_meta(adapter, diag, start7)

    for eid, e in entities.items():
        m = diag.metrics.setdefault(eid, {})
        m["days_since_change"] = float((diag.ops_date - e.updated_at).days) if e.updated_at else None
        for f in ("daily_budget", "bid"):
            if f in e.fields:
                m[f] = float(e.fields[f])
    return diag


def _diagnose_searchad(adapter: AdPlatformAdapter, diag: AccountDiagnosis, hist_start: date, start7: date) -> None:
    ents = diag.entities
    camp_hist = _by_entity(adapter.get_stats(hist_start, diag.as_of, EntityType.CAMPAIGN))
    kw_stats = _by_entity(adapter.get_stats(start7, diag.as_of, EntityType.KEYWORD))
    all_camp_stats = [s for rows in camp_hist.values() for s in rows]
    account_profile = _hour_profile(all_camp_stats)

    # 캠페인: 예산 소진
    for cid, rows in camp_hist.items():
        recent = [s for s in rows if s.date >= start7]
        m = _base_metrics(recent)
        profile = _hour_profile(rows)
        if profile == [1 / 24] * 24:
            profile = account_profile
        exhaust_hours, lost = [], 0.0
        for s in recent:
            h = _exhaust_hour(s.hourly_impressions)
            if h is None:
                continue
            exhaust_hours.append(h)
            served_share = sum(profile[: h + 1])
            if served_share > 0:
                lost += sum(s.hourly_impressions or []) / served_share * (1 - served_share)
        budget = ents[cid].fields.get("daily_budget", 0)
        m.update({
            "exhausted_days_7d": float(len(exhaust_hours)),
            "avg_exhaust_hour_7d": mean(exhaust_hours) if exhaust_hours else None,
            "lost_impr_est_7d": round(lost),
            "budget_util_7d": _ratio(m["spend_7d"] or 0, budget * WINDOW) if budget else None,
            "avg_rank_7d": _weighted_rank(recent),
        })
        diag.metrics[cid] = m
        diag.exhaustion.append({
            "entity_id": cid,
            "name": ents[cid].name,
            "daily_budget": budget,
            "days": [{"date": s.date, "hourly": s.hourly_impressions or [0] * 24,
                      "exhaust_hour": _exhaust_hour(s.hourly_impressions)}
                     for s in sorted(recent, key=lambda s: s.date)],
        })

    # 키워드
    group_campaign = {e.id: e.parent_id for e in ents.values() if e.type == EntityType.ADGROUP}
    for kid, rows in kw_stats.items():
        m = _base_metrics(rows)
        m["avg_rank_7d"] = _weighted_rank(rows)
        cid = group_campaign.get(ents[kid].parent_id or "")
        m["campaign_exhausted_days_7d"] = diag.metrics.get(cid or "", {}).get("exhausted_days_7d", 0.0)
        diag.metrics[kid] = m

    # 경보
    for cid in camp_hist:
        m, name = diag.metrics[cid], ents[cid].name
        days = m["exhausted_days_7d"] or 0
        if days >= EXHAUSTED_ALERT_DAYS:
            diag.findings.append(Finding(
                "warning", "budget_exhausted", cid, name, f"예산 조기 소진 · {name}",
                f"최근 7일 중 {days:.0f}일 일예산이 소진돼 평균 "
                f"{format_metric('avg_exhaust_hour_7d', m['avg_exhaust_hour_7d'])} 이후 노출이 멈췄습니다. "
                f"노출 손실 하루 평균 {m['lost_impr_est_7d'] / WINDOW:,.0f}회"
                "(추정: 소진되지 않은 날의 시간대 비중 기준).",
            ))
            for kid, km in diag.metrics.items():
                ke = ents[kid]
                if ke.type != EntityType.KEYWORD or group_campaign.get(ke.parent_id or "") != cid:
                    continue
                if (km.get("avg_rank_7d") or 0) >= LOW_RANK:
                    diag.findings.append(Finding(
                        "info", "rank_is_budget", kid, ke.name, f"순위보다 예산이 먼저 · {ke.name}",
                        f"평균 {format_metric('avg_rank_7d', km['avg_rank_7d'])}로 낮지만, 소속 캠페인이 "
                        f"{format_metric('avg_exhaust_hour_7d', m['avg_exhaust_hour_7d'])}쯤 예산을 다 써서 "
                        f"입찰가를 올리면 소진만 빨라집니다. 일예산 조정을 먼저 봅니다.",
                    ))
        elif days > 0:
            diag.findings.append(Finding(
                "info", "budget_watch", cid, name, f"예산 소진 관찰 · {name}",
                f"최근 7일 중 {days:.0f}일 마감 직전에 예산이 소진됐습니다. "
                f"기준({EXHAUSTED_ALERT_DAYS}일) 미만이라 조정하지 않고 지켜봅니다.",
            ))
    waste = sorted(
        (kid for kid, m in diag.metrics.items()
         if ents[kid].type == EntityType.KEYWORD and (m["spend_7d"] or 0) >= WASTE_SPEND and not m["conv_7d"]),
        key=lambda k: diag.metrics[k]["spend_7d"] or 0, reverse=True,
    )
    if waste:
        total = sum(diag.metrics[k]["spend_7d"] or 0 for k in waste)
        parts = ", ".join(f"'{ents[k].name}' {won(diag.metrics[k]['spend_7d'] or 0)}" for k in waste)
        diag.findings.append(Finding(
            "danger", "no_conversion", waste[0], ents[waste[0]].name, f"전환 없는 비용 · 키워드 {len(waste)}개",
            f"최근 7일 {won(total)}을 쓰고 전환 0건: {parts}.",
        ))

    diag.ranking = _ranking(diag, EntityType.KEYWORD)


def _ago(days: int) -> str:
    return "오늘" if days == 0 else f"{days}일 전에"


def _weighted_rank(rows: list[DailyStat]) -> float | None:
    pairs = [(s.avg_rank, s.impressions) for s in rows if s.avg_rank is not None and s.impressions]
    total = sum(w for _, w in pairs)
    return sum(r * w for r, w in pairs) / total if total else None


def _diagnose_meta(adapter: AdPlatformAdapter, diag: AccountDiagnosis, start7: date) -> None:
    ents = diag.entities
    prev_start, prev_end = start7 - timedelta(days=WINDOW), start7 - timedelta(days=1)
    ad_recent = _by_entity(adapter.get_stats(start7, diag.as_of, EntityType.AD))
    ad_prev = _by_entity(adapter.get_stats(prev_start, prev_end, EntityType.AD))
    adset_recent = _by_entity(adapter.get_stats(start7, diag.as_of, EntityType.ADSET))

    for sid, rows in adset_recent.items():
        m = _base_metrics(rows)
        budget = ents[sid].fields.get("daily_budget", 0)
        m["budget_util_7d"] = _ratio(m["spend_7d"] or 0, budget * WINDOW) if budget else None
        diag.metrics[sid] = m
    for aid, rows in ad_recent.items():
        m = _base_metrics(rows)
        latest = max(rows, key=lambda s: s.date)
        m["frequency"] = latest.frequency
        prev = _base_metrics(ad_prev.get(aid, []))
        m["ctr_change_pct"] = (
            (m["ctr_7d"] - prev["ctr_7d"]) / prev["ctr_7d"] * 100 if m["ctr_7d"] and prev["ctr_7d"] else None
        )
        diag.metrics[aid] = m

    active_sets = {k: diag.metrics[k]["roas_7d"] for k in adset_recent if ents[k].active}
    active_ads = {k: diag.metrics[k]["roas_7d"] for k in ad_recent if ents[k].active}
    for k, v in _rank_pct(active_sets).items():
        diag.metrics[k]["roas_rank_pct"] = v
    for k, v in _rank_pct(active_ads).items():
        diag.metrics[k]["roas_rank_pct"] = v

    # 경보
    ads_sorted = sorted(ad_recent, key=lambda k: diag.metrics[k]["roas_7d"] or 0, reverse=True)
    for aid in ads_sorted[:1]:
        m = diag.metrics[aid]
        if (m["conv_7d"] or 0) >= WINNING_MIN_CONV:
            parent = ents[ents[aid].parent_id or ""].name
            diag.findings.append(Finding(
                "success", "winning_creative", aid, ents[aid].name, f"위닝 소재 · {ents[aid].name}",
                f"ROAS {format_metric('roas_7d', m['roas_7d'])}, 전환 {m['conv_7d']:.0f}건(최근 7일) — 계정 1위. "
                f"소속 세트 '{parent}' 예산 증액 후보입니다.",
            ))
    for aid in ad_recent:
        m = diag.metrics[aid]
        if (m["ctr_change_pct"] or 0) <= FATIGUE_CTR_DROP and (m["frequency"] or 0) >= FATIGUE_FREQUENCY:
            diag.findings.append(Finding(
                "warning", "creative_fatigue", aid, ents[aid].name, f"소재 피로 · {ents[aid].name}",
                f"CTR이 직전 7일보다 {abs(m['ctr_change_pct']):.0f}% 떨어졌고 빈도가 {m['frequency']:.1f}회입니다. "
                f"같은 사람에게 반복 노출되고 있습니다.",
            ))
    for sid in adset_recent:
        m = diag.metrics[sid]
        if (m["roas_7d"] or 0) < 100 and (m["spend_7d"] or 0) >= 300_000:
            diag.findings.append(Finding(
                "danger", "low_roas", sid, ents[sid].name, f"ROAS 100% 미만 · {ents[sid].name}",
                f"최근 7일 비용 {won(m['spend_7d'] or 0)}, ROAS {format_metric('roas_7d', m['roas_7d'])}.",
            ))
        e = ents[sid]
        if e.updated_at and (diag.ops_date - e.updated_at).days < LEARNING_DAYS:
            diag.findings.append(Finding(
                "info", "learning", sid, e.name, f"학습 기간 · {e.name}",
                f"{_ago((diag.ops_date - e.updated_at).days)} 예산을 바꿨습니다. 성과가 좋아도 "
                f"{LEARNING_DAYS}일이 지나기 전에는 다시 바꾸지 않습니다.",
            ))

    diag.ranking = _ranking(diag, EntityType.AD)


def _ranking(diag: AccountDiagnosis, etype: EntityType) -> list[dict]:
    rows = []
    for eid, m in diag.metrics.items():
        e = diag.entities[eid]
        if e.type != etype:
            continue
        parent = diag.entities.get(e.parent_id or "")
        rows.append({
            "entity_id": eid, "name": e.name, "parent": parent.name if parent else "",
            "status": e.fields.get("status", "ACTIVE"),
            "spend": m["spend_7d"], "ctr": m["ctr_7d"], "cvr": m["cvr_7d"], "roas": m["roas_7d"],
            "conv": m["conv_7d"], "rank": m.get("avg_rank_7d"), "frequency": m.get("frequency"),
        })
    rows.sort(key=lambda r: r["roas"] or 0, reverse=True)
    return rows
