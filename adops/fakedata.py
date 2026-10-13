"""가상 데이터 생성기.

가상 브랜드 '핏루틴'(홈트레이닝 기구 온라인 쇼핑몰, 지어낸 이름)의 광고 계정 2개와 28일 일별 실적을 만든다.
모든 값은 seed로 고정된 난수에서 나오므로 같은 seed면 같은 파일이 나온다.

진단이 잡아내도록 일부러 심어 둔 패턴
- 검색광고형 '홈트 기구_일반' 캠페인: 최근 2주 수요가 늘어 평일 오후에 일예산이 소진된다(예산 조기 소진).
- 같은 캠페인의 '케틀벨 추천' 키워드: 노출 순위가 낮지만, 입찰가보다 예산이 먼저 문제다.
- '폼롤러' 키워드: 순위는 낮고 효율은 좋다(입찰가 인상 후보).
- '접이식 실내자전거', '필라테스 링' 키워드: 비용만 쓰고 전환이 없다(입찰가 인하 후보).
- 메타형 '유사타겟_구매자 1%' 광고 세트의 'B-01 고객 후기 릴스': 위닝 소재(ROAS 상위, 전환 다수).
- 메타형 '리타게팅_장바구니 7일': 성과는 좋지만 어제 예산을 바꿔 학습 기간 보호 대상이다.
- 'A-02 30일 홈트 챌린지 영상': 최근 7일 CTR 급락 + 빈도 상승(소재 피로).
- '광범위_25-44' 광고 세트와 'D-02 제품 나열 카탈로그': ROAS 1 미만(감액·중지 후보).
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

DEMO_AS_OF = date(2026, 10, 12)  # 실적 마감일(어제). 운영일은 다음 날.
DEFAULT_SEED = 20261013
DAYS = 28
BRAND = "핏루틴"

# 하루 노출의 시간대별 비중(검색 수요 곡선). 합이 1이 되도록 정규화한다.
_RAW_PROFILE = [1.2, 0.8, 0.5, 0.4, 0.4, 0.6, 1.2, 2.4, 3.8, 5.0, 5.8, 6.2,
                6.0, 5.6, 5.4, 5.2, 5.0, 4.8, 4.6, 5.0, 5.8, 6.2, 5.4, 3.6]
HOURLY_PROFILE = [v / sum(_RAW_PROFILE) for v in _RAW_PROFILE]


@dataclass(frozen=True)
class KeywordSpec:
    id: str
    adgroup: str
    text: str
    bid: int
    base_impr: int  # 예산 제한이 없을 때 하루 노출
    ctr: float
    cvr: float
    aov: int  # 객단가(원)
    rank: float
    cpc_ratio: float = 0.82  # 실제 클릭당 비용 / 입찰가


@dataclass(frozen=True)
class CampaignSpec:
    id: str
    name: str
    daily_budget: int
    demand: tuple[float, float]  # (첫 2주 수요 배수, 마지막 주 수요 배수) — 사이 구간은 선형 증가
    weekend: float


@dataclass(frozen=True)
class AdSpec:
    id: str
    adset: str
    name: str
    share: float  # 광고 세트 지출 중 이 소재 비중
    cpm: int
    ctr: float
    cvr: float
    aov: int
    freq: float
    fatigue: bool = False  # 최근 7일 CTR 급락·빈도 상승


SA_ACCOUNT = "sa-fitroutine"
MT_ACCOUNT = "mt-fitroutine"

SA_CAMPAIGNS = [
    CampaignSpec("cmp-brand", "브랜드 검색", 50_000, (1.0, 1.05), 0.9),
    CampaignSpec("cmp-homegym", "홈트 기구_일반", 130_000, (0.80, 1.45), 0.58),
    CampaignSpec("cmp-yoga", "요가·필라테스 소품", 56_000, (1.0, 1.06), 0.85),
]
SA_ADGROUPS = [
    ("grp-brand", "cmp-brand", "브랜드"),
    ("grp-dumbbell", "cmp-homegym", "덤벨·케틀벨"),
    ("grp-bike", "cmp-homegym", "실내 자전거"),
    ("grp-general", "cmp-homegym", "홈트 일반"),
    ("grp-yoga", "cmp-yoga", "요가 소품"),
    ("grp-pilates", "cmp-yoga", "필라테스"),
]
SA_KEYWORDS = [
    KeywordSpec("kw-brand", "grp-brand", BRAND, 300, 900, 0.090, 0.060, 85_000, 1.0, 0.60),
    KeywordSpec("kw-brand-dumbbell", "grp-brand", f"{BRAND} 덤벨", 250, 400, 0.070, 0.050, 60_000, 1.1, 0.64),
    KeywordSpec("kw-dumbbell", "grp-dumbbell", "가정용 덤벨", 620, 2600, 0.032, 0.040, 59_000, 2.1),
    KeywordSpec("kw-kettlebell", "grp-dumbbell", "케틀벨 추천", 480, 1500, 0.024, 0.042, 45_000, 4.1, 0.85),
    KeywordSpec("kw-bike", "grp-bike", "실내 자전거 추천", 900, 1800, 0.030, 0.022, 289_000, 2.4, 0.84),
    KeywordSpec("kw-foldbike", "grp-bike", "접이식 실내자전거", 1100, 900, 0.026, 0.0, 259_000, 2.9, 0.86),
    KeywordSpec("kw-homegym", "grp-general", "홈트 기구", 750, 2000, 0.022, 0.025, 120_000, 2.6, 0.85),
    KeywordSpec("kw-yogamat", "grp-yoga", "요가매트 두꺼운", 400, 2400, 0.030, 0.050, 32_000, 2.3),
    KeywordSpec("kw-foamroller", "grp-yoga", "폼롤러", 350, 1200, 0.025, 0.055, 28_000, 4.6, 0.86),
    KeywordSpec("kw-pilatesring", "grp-pilates", "필라테스 링", 520, 1300, 0.028, 0.0, 33_000, 3.0, 0.85),
    KeywordSpec("kw-pilatestools", "grp-pilates", "필라테스 소도구", 450, 900, 0.024, 0.030, 35_000, 3.3, 0.84),
]

MT_ADSETS = [
    # id, 이름, 일예산, 마지막 예산 변경일(운영일 기준 며칠 전)
    ("as-interest", "관심사_홈트 입문자", 100_000, 20),
    ("as-lookalike", "유사타겟_구매자 1%", 120_000, 12),
    ("as-retarget", "리타게팅_장바구니 7일", 60_000, 1),
    ("as-broad", "광범위_25-44", 80_000, 16),
]
MT_ADS = [
    AdSpec("ad-a01", "as-interest", "A-01 덤벨 세트 이미지", 0.55, 7000, 0.013, 0.018, 69_000, 1.9),
    AdSpec("ad-a02", "as-interest", "A-02 30일 홈트 챌린지 영상", 0.45, 7500, 0.016, 0.020, 69_000, 2.1, fatigue=True),
    AdSpec("ad-b01", "as-lookalike", "B-01 고객 후기 릴스", 0.60, 8000, 0.019, 0.036, 79_000, 1.7),
    AdSpec("ad-b02", "as-lookalike", "B-02 할인 배너", 0.40, 7000, 0.012, 0.022, 75_000, 1.8),
    AdSpec("ad-c01", "as-retarget", "C-01 장바구니 리마인드", 1.00, 12000, 0.024, 0.040, 72_000, 2.6),
    AdSpec("ad-d01", "as-broad", "D-01 브랜드 소개 영상", 0.55, 5000, 0.008, 0.010, 70_000, 1.5),
    AdSpec("ad-d02", "as-broad", "D-02 제품 나열 카탈로그", 0.45, 5000, 0.006, 0.004, 60_000, 1.6),
]


def _count(rng: random.Random, expected: float) -> int:
    """기댓값을 정수 건수로 바꾼다(소수 부분은 확률로)."""
    base = int(expected)
    return base + (1 if rng.random() < expected - base else 0)


def _demand(spec: CampaignSpec, i: int) -> float:
    """i: 0(28일 전) ~ 27(마감일). 첫 14일은 낮게, 이후 선형 증가, 마지막 7일은 최고치."""
    lo, hi = spec.demand
    if i < 14:
        return lo
    if i >= 21:
        return hi
    return lo + (hi - lo) * (i - 13) / 8


def _searchad(rng: random.Random, days: list[date], ops: date) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    objects = {
        "campaigns": [
            {"campaignId": c.id, "name": c.name, "dailyBudget": c.daily_budget, "userLock": False,
             "editTm": (ops - timedelta(days=30)).isoformat()}
            for c in SA_CAMPAIGNS
        ],
        "adgroups": [
            {"adgroupId": g, "campaignId": c, "name": n, "userLock": False} for g, c, n in SA_ADGROUPS
        ],
        "keywords": [
            {"keywordId": k.id, "adgroupId": k.adgroup, "keyword": k.text, "bidAmt": k.bid, "userLock": False,
             "editTm": (ops - timedelta(days=21)).isoformat()}
            for k in SA_KEYWORDS
        ],
    }
    group_campaign = {g: c for g, c, _ in SA_ADGROUPS}
    rows: list[dict[str, Any]] = []
    for i, day in enumerate(days):
        for camp in SA_CAMPAIGNS:
            kws = [k for k in SA_KEYWORDS if group_campaign[k.adgroup] == camp.id]
            factor = _demand(camp, i) * (camp.weekend if day.weekday() >= 5 else 1.0)
            raw = []
            for k in kws:
                imps = k.base_impr * factor * rng.uniform(0.92, 1.08)
                clicks = imps * k.ctr * rng.uniform(0.9, 1.1)
                cpc = k.bid * k.cpc_ratio * rng.uniform(0.95, 1.05)
                raw.append((k, imps, clicks, cpc))
            full_cost = sum(c * p for _, _, c, p in raw)
            # 시간대별로 비용을 쌓다가 일예산에 닿으면 그 뒤로는 노출하지 않는다.
            served = [1.0] * 24
            if full_cost > camp.daily_budget:
                cum = 0.0
                for h, share in enumerate(HOURLY_PROFILE):
                    hour_cost = full_cost * share
                    if cum + hour_cost <= camp.daily_budget:
                        cum += hour_cost
                        continue
                    served[h] = max(0.0, (camp.daily_budget - cum) / hour_cost)
                    for rest in range(h + 1, 24):
                        served[rest] = 0.0
                    break
            served_share = sum(s * p for s, p in zip(served, HOURLY_PROFILE, strict=True))
            total_imps = sum(imps for _, imps, _, _ in raw)
            hourly = [round(total_imps * p * s) for p, s in zip(HOURLY_PROFILE, served, strict=True)]
            camp_row = {"statDt": day.isoformat(), "level": "campaign", "id": camp.id,
                        "impCnt": 0, "clkCnt": 0, "spendAmt": 0, "convCnt": 0, "convAmt": 0,
                        "hourlyImpCnt": hourly}
            rank_weighted = 0.0
            for k, imps, clicks, cpc in raw:
                k_imps = round(imps * served_share)
                k_clicks = round(clicks * served_share)
                k_cost = round(k_clicks * cpc)
                conv = _count(rng, k_clicks * k.cvr)
                revenue = round(conv * k.aov * rng.uniform(0.9, 1.1))
                rank = round(max(1.0, k.rank + rng.uniform(-0.3, 0.3)), 1)
                rows.append({"statDt": day.isoformat(), "level": "keyword", "id": k.id, "impCnt": k_imps,
                             "clkCnt": k_clicks, "spendAmt": k_cost, "convCnt": conv, "convAmt": revenue,
                             "avgRank": rank})
                camp_row["impCnt"] += k_imps
                camp_row["clkCnt"] += k_clicks
                camp_row["spendAmt"] += k_cost
                camp_row["convCnt"] += conv
                camp_row["convAmt"] += revenue
                rank_weighted += rank * k_imps
            camp_row["avgRank"] = round(rank_weighted / camp_row["impCnt"], 1) if camp_row["impCnt"] else None
            rows.append(camp_row)
    return objects, rows


def _meta(rng: random.Random, days: list[date], ops: date) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    objects = {
        "campaigns": [{"id": "cmp-conv", "name": "전환_홈트 기구", "status": "ACTIVE"}],
        "adsets": [
            {"id": a, "campaign_id": "cmp-conv", "name": n, "daily_budget": str(b), "status": "ACTIVE",
             "updated_time": (ops - timedelta(days=ago)).isoformat()}
            for a, n, b, ago in MT_ADSETS
        ],
        "ads": [{"id": ad.id, "adset_id": ad.adset, "name": ad.name, "status": "ACTIVE"} for ad in MT_ADS],
    }
    budgets = {a: b for a, _, b, _ in MT_ADSETS}
    rows: list[dict[str, Any]] = []
    n = len(days)
    for i, day in enumerate(days):
        recent = i >= n - 7
        for ad in MT_ADS:
            budget = budgets[ad.adset]
            if ad.adset == "as-retarget" and i < n - 1:
                budget = 50_000  # 마감일에 60,000원으로 올렸다(학습 기간 보호 시연용)
            spend = budget * ad.share * rng.uniform(0.93, 1.0)
            ctr, freq = ad.ctr, ad.freq
            if ad.fatigue and recent:
                # 같은 사람에게 너무 자주 노출돼 클릭률이 떨어지는 패턴
                progress = (i - (n - 7) + 1) / 7
                ctr = ad.ctr * (1 - 0.48 * progress)
                freq = ad.freq + 2.6 * progress
            imps = spend / ad.cpm * 1000
            clicks = imps * ctr * rng.uniform(0.9, 1.1)
            conv = _count(rng, clicks * ad.cvr)
            revenue = conv * ad.aov * rng.uniform(0.9, 1.1)
            rows.append({
                "date_start": day.isoformat(), "date_stop": day.isoformat(),
                "ad_id": ad.id, "adset_id": ad.adset,
                "impressions": str(round(imps)), "clicks": str(round(clicks)),
                "spend": f"{spend:.0f}", "frequency": f"{freq * rng.uniform(0.97, 1.03):.2f}",
                "actions": [{"action_type": "purchase", "value": str(conv)}],
                "action_values": [{"action_type": "purchase", "value": f"{revenue:.0f}"}],
            })
    return objects, rows


def generate(as_of: date = DEMO_AS_OF, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    """가짜 플랫폼 상태(JSON으로 저장할 dict)를 만든다."""
    rng = random.Random(seed)
    days = [as_of - timedelta(days=DAYS - 1 - i) for i in range(DAYS)]
    ops = as_of + timedelta(days=1)
    sa_objects, sa_rows = _searchad(rng, days, ops)
    mt_objects, mt_rows = _meta(rng, days, ops)
    return {
        "meta": {
            "as_of": as_of.isoformat(),
            "seed": seed,
            "days": DAYS,
            "note": "가상 데이터: adops.fakedata.generate()가 만든 값이며 실제 광고 계정과 무관합니다.",
            "brand": f"{BRAND} (가상 홈트레이닝 기구 쇼핑몰)",
        },
        "accounts": {
            SA_ACCOUNT: {"platform": "searchad_like", "name": f"{BRAND} 검색광고", "currency": "KRW"},
            MT_ACCOUNT: {"platform": "meta_like", "name": f"{BRAND} 메타", "currency": "KRW"},
        },
        "objects": {SA_ACCOUNT: sa_objects, MT_ACCOUNT: mt_objects},
        "stats": {SA_ACCOUNT: sa_rows, MT_ACCOUNT: mt_rows},
    }
