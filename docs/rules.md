# 규칙 파일 작성법

규칙 파일 하나 = 플랫폼 하나의 **안전장치(guardrails) + 규칙 목록**입니다. 기본 규칙은
[`adops/rules/defaults/`](../adops/rules/defaults/)에 있고, 내 규칙은 `adops plan --rules 내파일.yaml`로 씁니다
(예시: [`examples/`](../examples/)).

## 모양

```yaml
version: 1
platform: meta_like            # searchad_like | meta_like

guardrails:
  max_change_pct: 20           # 변경 1건의 변경 폭 상한(%)
  max_changes_per_day: 6       # 계정당 하루 반영 건수 상한
  cooldown_days: 3             # 같은 개체를 다시 바꾸기 전에 기다릴 날 수(학습 기간 보호)
  max_retries: 2               # 일시 오류 재시도 횟수(0~5)
  bounds:                      # 필드별 절대 하한·상한(원)
    daily_budget: {min: 10000, max: 1000000}

rules:                         # 위에 있을수록 우선순위가 높다
  - id: mt-winning-scale-up    # 파일 안에서 겹치면 안 됨
    name: 위닝 광고 세트 예산 증액
    entity: adset              # campaign | keyword | adset | ad
    when:                      # all(모두) 또는 any(하나라도) — 서로 중첩 가능
      all:
        - {metric: roas_7d, op: ">=", value: 350}
        - {metric: conv_7d, op: ">=", value: 20}
        - any:
            - {metric: roas_rank_pct, op: "<=", value: 50}
            - {metric: cpa_7d, op: "<", value: 15000}
    action: {field: daily_budget, op: increase_pct, value: 20, round_to: 1000, max: 500000}
    risk: medium               # low | medium | high (브리핑·승인 화면에 표시)
    enabled: true              # false면 평가하지 않음
    reason: "최근 7일 ROAS {roas_7d}, 전환 {conv_7d}건으로 일예산을 늘립니다."
```

- `op`: `>` `>=` `<` `<=` `==` `!=`
- 값이 없는 지표(예: 전환이 0이라 계산할 수 없는 CPA)는 조건 불충족으로 봅니다.
- 중지된 개체는 평가하지 않습니다.

## 액션

| `op` | 의미 | 필요한 값 |
|---|---|---|
| `increase_pct` | 현재 값에서 N% 올림 | `value`(0 초과 100 이하) |
| `decrease_pct` | 현재 값에서 N% 내림 | `value` |
| `set` | 지정한 값으로 | `value` |
| `pause` | 중지(`field: status`와 함께) | — |

- `round_to`: 반올림 단위(입찰가 10원, 예산 1,000원 등). 반올림은 사사오입.
- `min`·`max`: 규칙 안의 하한·상한. 넘으면 그 값으로 맞추고 근거에 "규칙 상한으로 맞춤"을 남깁니다.
- 안전장치의 `max_change_pct`·`bounds`는 **규칙과 별개로** 미리보기에서 다시 검사합니다. 규칙이 실수로 크게 바꾸려 해도 여기서 차단됩니다.

## 근거 문장(`reason`)

`{지표 이름}` 자리에 실제 값이 단위와 함께 들어갑니다(ROAS → `477%`, 비용 → `132,165원`, 순위 → `4.7위`).
`reason`이 없으면 걸린 조건을 이어 붙여 만듭니다. 예) `최근 7일 ROAS 512% (>= 300%) · 최근 7일 비용 12,345원 (> 0원)`

## 지표 목록

비율 지표는 모두 % 값입니다(ROAS 300% → `300`).

| 지표 | 이름 | 단위 | 대상 | 설명 |
|---|---|---|---|---|
| `daily_budget` | 일예산 | 원 | 캠페인, 광고 세트 |  |
| `bid` | 입찰가 | 원 | 키워드 |  |
| `spend_7d` | 최근 7일 비용 | 원 | 캠페인, 키워드, 광고 세트, 소재 |  |
| `revenue_7d` | 최근 7일 전환 매출 | 원 | 캠페인, 키워드, 광고 세트, 소재 |  |
| `roas_7d` | 최근 7일 ROAS | % | 캠페인, 키워드, 광고 세트, 소재 | 전환 매출 ÷ 비용 × 100 |
| `conv_7d` | 최근 7일 전환 | 건 | 캠페인, 키워드, 광고 세트, 소재 |  |
| `impressions_7d` | 최근 7일 노출 | 회 | 캠페인, 키워드, 광고 세트, 소재 |  |
| `clicks_7d` | 최근 7일 클릭 | 회 | 캠페인, 키워드, 광고 세트, 소재 |  |
| `ctr_7d` | 최근 7일 CTR | % | 캠페인, 키워드, 광고 세트, 소재 |  |
| `cvr_7d` | 최근 7일 전환율 | % | 캠페인, 키워드, 광고 세트, 소재 | 전환 ÷ 클릭 × 100 |
| `cpc_7d` | 최근 7일 클릭당 비용 | 원 | 캠페인, 키워드, 광고 세트, 소재 |  |
| `cpa_7d` | 최근 7일 전환당 비용 | 원 | 캠페인, 키워드, 광고 세트, 소재 |  |
| `avg_rank_7d` | 최근 7일 평균 노출 순위 | 위 | 캠페인, 키워드 | 노출 수 가중 평균 |
| `exhausted_days_7d` | 최근 7일 예산 소진일 | 일 | 캠페인 | 하루가 끝나기 전에 노출이 멈춘 날 수(시간대별 노출 기준) |
| `avg_exhaust_hour_7d` | 평균 예산 소진 시각 | 시 | 캠페인 | 소진된 날의 마지막 노출 시간대 평균 |
| `lost_impr_est_7d` | 추정 노출 손실(7일) | 회 | 캠페인 | 소진 시각 이후를 평소 시간대 비중으로 추정 |
| `budget_util_7d` | 최근 7일 예산 사용률 | % | 캠페인, 광고 세트 |  |
| `campaign_exhausted_days_7d` | 소속 캠페인 예산 소진일 | 일 | 키워드 | "순위보다 예산이 먼저" 판단용 |
| `roas_rank_pct` | 계정 내 ROAS 순위 백분위 | % | 광고 세트, 소재 | 0 = 1등, 100 = 꼴찌(운영 중인 것끼리) |
| `days_since_change` | 마지막 변경 후 지난 날 | 일 | 캠페인, 키워드, 광고 세트, 소재 |  |
| `frequency` | 빈도(최근 7일) | 회 | 소재 | 플랫폼 보고값 |
| `ctr_change_pct` | CTR 변화율(직전 7일 대비) | % | 소재 | 소재 피로 판단용 |

- 캠페인 실적 지표는 검색광고형 캠페인에서 계산합니다. 메타형은 광고 세트·소재 단위로 씁니다.
- 지표 이름이 틀리거나 대상 개체에 없는 지표를 쓰면, 규칙 파일을 불러올 때 사용 가능한 이름과 함께 오류가 납니다.
