"""HTML 일일 브리핑: 어제 성과, 진단 경보, 예산 소진 시간대, 조정 후보와 실행 결과, 최근 실행 이력.

외부 파일 없이 HTML 한 장(인라인 CSS·SVG)으로 만든다. 메일 본문이나 메신저 첨부로 그대로 보낼 수 있다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from adops import __version__
from adops.audit import AuditStore
from adops.diagnose import AccountDiagnosis
from adops.metrics import field_value
from adops.models import ENTITY_LABELS, FIELD_LABELS, STATUS_LABELS, Change, ChangeStatus, Run

WEEKDAYS = "월화수목금토일"

# 디자인 토큰(포트폴리오 공통 tokens.json과 같은 값)
THEME = {
    "primary": {"stroke": "#3730a3", "fill": "#e0e7ff", "solid": "#4f46e5"},
    "secondary": {"stroke": "#0f766e", "fill": "#ccfbf1", "solid": "#14b8a6"},
    "info": {"stroke": "#0369a1", "fill": "#e0f2fe", "solid": "#0ea5e9"},
    "success": {"stroke": "#15803d", "fill": "#dcfce7", "solid": "#22c55e"},
    "warning": {"stroke": "#b45309", "fill": "#fef3c7", "solid": "#f59e0b"},
    "danger": {"stroke": "#b91c1c", "fill": "#fee2e2", "solid": "#ef4444"},
    "neutral": {"stroke": "#334155", "fill": "#f1f5f9", "solid": "#64748b"},
    "accent": {"stroke": "#6d28d9", "fill": "#ede9fe", "solid": "#8b5cf6"},
}

STATUS_ROLE = {
    ChangeStatus.PLANNED: "neutral",
    ChangeStatus.PREVIEWED: "info",
    ChangeStatus.APPROVED: "primary",
    ChangeStatus.APPLIED: "primary",
    ChangeStatus.VERIFIED: "success",
    ChangeStatus.FAILED: "danger",
    ChangeStatus.ROLLED_BACK: "accent",
    ChangeStatus.BLOCKED: "warning",
    ChangeStatus.REJECTED: "neutral",
    ChangeStatus.SKIPPED: "neutral",
}

ACTION_LABELS = {
    "run_created": "조정안 생성",
    "run_status": "실행 상태",
    "api_error": "API 오류",
    "halted": "실행 중단",
    "rollback_started": "되돌리기 시작",
    "rollback_failed": "되돌리기 실패",
    "drift_detected": "값 변경 감지",
    "rule_conflict": "규칙 충돌",
}


def day_label(d: date) -> str:
    return f"{d.month}/{d.day}({WEEKDAYS[d.weekday()]})"


def sparkline(values: list[float], width: int = 260, height: int = 56, pad: int = 4) -> dict[str, Any]:
    if not values:
        return {"points": "", "area": "", "last": (0, 0)}
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    step = (width - 2 * pad) / max(len(values) - 1, 1)
    pts = [(pad + i * step, height - pad - (v - lo) / span * (height - 2 * pad)) for i, v in enumerate(values)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{pts[0][0]:.1f},{height} {line} {pts[-1][0]:.1f},{height}"
    return {"points": line, "area": area, "last": pts[-1], "width": width, "height": height}


def _delta(now: float, base: float) -> dict[str, Any]:
    if not base:
        return {"text": "-", "cls": "flat"}
    pct = (now - base) / base * 100
    return {"text": f"{pct:+.0f}%", "cls": "up" if pct > 2 else ("down" if pct < -2 else "flat")}


@dataclass
class AccountBrief:
    diag: AccountDiagnosis
    run: Run | None


def _account_view(ab: AccountBrief) -> dict[str, Any]:
    d = ab.diag
    y, a = d.kpi_yesterday, d.kpi_avg7
    kpis = [
        {"label": "비용", "value": f"{y['spend']:,.0f}원", "delta": _delta(y["spend"], a["spend"])},
        {"label": "전환 매출", "value": f"{y['revenue']:,.0f}원", "delta": _delta(y["revenue"], a["revenue"])},
        {"label": "ROAS", "value": f"{y['roas']:,.0f}%", "delta": _delta(y["roas"], a["roas"])},
        {"label": "전환", "value": f"{y['conversions']:,.0f}건", "delta": _delta(y["conversions"], a["conversions"])},
    ]
    spend = [r["cost"] for r in d.daily]
    revenue = [r["revenue"] for r in d.daily]
    heat = []
    for camp in d.exhaustion:
        if not any(day["exhaust_hour"] is not None for day in camp["days"]):
            continue
        peak = max((max(day["hourly"]) for day in camp["days"]), default=1) or 1
        rows = []
        for day in camp["days"]:
            eh = day["exhaust_hour"]
            cells = []
            for h, v in enumerate(day["hourly"]):
                off = eh is not None and h > eh
                cells.append({"alpha": round(0.08 + 0.92 * v / peak, 2) if v else 0, "off": off,
                              "title": f"{day_label(day['date'])} {h}시 노출 {v:,}"})
            rows.append({"label": day_label(day["date"]), "cells": cells,
                         "exhaust": f"{eh}시 소진" if eh is not None else ""})
        heat.append({"name": camp["name"], "budget": camp["daily_budget"], "rows": rows,
                     "exhausted": sum(1 for r in rows if r["exhaust"])})
    return {
        "id": d.account_id,
        "name": d.account_name,
        "platform": "검색광고형" if d.platform.value == "searchad_like" else "메타형",
        "kpis": kpis,
        "spark_spend": sparkline(spend),
        "spark_revenue": sparkline(revenue),
        "spark_range": f"{day_label(d.daily[0]['date'])} ~ {day_label(d.daily[-1]['date'])}" if d.daily else "",
        "findings": d.findings,
        "heat": heat,
        "ranking": d.ranking,
        "ranking_kind": "키워드" if d.platform.value == "searchad_like" else "소재",
        "run": _run_view(ab.run) if ab.run else None,
    }


def _change_view(c: Change) -> dict[str, Any]:
    pct = c.change_pct
    return {
        "seq": c.seq,
        "target": c.entity_name,
        "kind": ENTITY_LABELS.get(c.entity_type, c.entity_type),
        "field": FIELD_LABELS.get(c.field, c.field),
        "before": field_value(c.field, c.before),
        "after": field_value(c.field, c.after),
        "pct": f"{pct:+.0f}%" if pct is not None else "",
        "reason": c.reason,
        "impact": c.impact,
        "status": STATUS_LABELS[c.status],
        "role": STATUS_ROLE[c.status],
        "note": c.note,
        "rule": c.rule_id,
    }


def _run_view(run: Run) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for c in run.changes:
        counts[STATUS_LABELS[c.status]] = counts.get(STATUS_LABELS[c.status], 0) + 1
    return {"id": run.run_id, "status": run.status.value, "changes": [_change_view(c) for c in run.changes],
            "counts": counts}


def _event_view(e: dict[str, Any]) -> dict[str, Any]:
    ts = datetime.fromisoformat(e["ts"])
    if e["action"] == "transition":
        to = ChangeStatus(e["to_status"])
        label = STATUS_LABELS[to]
        role = STATUS_ROLE[to]
    else:
        label = ACTION_LABELS.get(e["action"], e["action"])
        role = "danger" if e["action"] in ("api_error", "halted", "rollback_failed") else "neutral"
    target = (e["change_id"] or "").replace(e["run_id"] + "-", "")
    return {"time": ts.strftime("%H:%M:%S"), "run": e["run_id"], "target": target, "label": label,
            "role": role, "actor": e["actor"], "detail": e["detail"]}


def render_brief(accounts: list[AccountBrief], store: AuditStore, generated_at: datetime | None = None) -> str:
    env = Environment(loader=PackageLoader("adops", "templates"), autoescape=select_autoescape(["html", "j2"]))
    tpl = env.get_template("brief.html.j2")
    first = accounts[0].diag
    events = [_event_view(e) for e in store.events(limit=18)]
    alert_counts = {"danger": 0, "warning": 0, "info": 0, "success": 0}
    for ab in accounts:
        for f in ab.diag.findings:
            alert_counts[f.level] = alert_counts.get(f.level, 0) + 1
    return tpl.render(
        theme=THEME,
        ops_date=f"{first.ops_date:%Y-%m-%d} ({WEEKDAYS[first.ops_date.weekday()]})",
        as_of=f"{first.as_of:%Y-%m-%d}",
        generated=(generated_at or datetime.now()).strftime("%Y-%m-%d %H:%M"),
        accounts=[_account_view(ab) for ab in accounts],
        events=events,
        alert_counts=alert_counts,
        version=__version__,
        hours=list(range(24)),
    )


def write_brief(accounts: list[AccountBrief], store: AuditStore, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_brief(accounts, store), encoding="utf-8")
    return out
