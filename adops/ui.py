"""터미널 출력(rich). CLI와 데모가 같은 화면 함수를 쓴다.

색은 16색 기본 팔레트 이름만 쓴다(터미널·스크린샷 도구 어디서나 같은 색이 나오게).
글자가 긴 열은 overflow="fold"로 두어 한글 단어가 말줄임으로 사라지지 않게 한다.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from adops.diagnose import AccountDiagnosis
from adops.execute import ApplyReport, StepResult
from adops.metrics import field_value
from adops.models import ENTITY_LABELS, FIELD_LABELS, STATUS_LABELS, Change, ChangeStatus, Run

STATUS_STYLE = {
    ChangeStatus.PLANNED: "white",
    ChangeStatus.PREVIEWED: "blue",
    ChangeStatus.APPROVED: "cyan",
    ChangeStatus.APPLIED: "cyan",
    ChangeStatus.VERIFIED: "bold green",
    ChangeStatus.FAILED: "bold red",
    ChangeStatus.ROLLED_BACK: "bold magenta",
    ChangeStatus.BLOCKED: "bold yellow",
    ChangeStatus.REJECTED: "yellow",
    ChangeStatus.SKIPPED: "bright_black",
}
LEVEL_STYLE = {"danger": ("위험", "bold red"), "warning": ("주의", "bold yellow"),
               "info": ("참고", "cyan"), "success": ("기회", "bold green")}

# 열 너비(터미널 칸). 한글 1자 = 2칸
W_SEQ, W_TARGET, W_CHANGE, W_STATUS = 2, 20, 27, 9


def _table(**kw: Any) -> Table:
    return Table(box=box.ROUNDED, header_style="bold", expand=True, title_justify="left", title_style="bold", **kw)


def _base_columns(table: Table, change_header: str = "변경") -> None:
    table.add_column("#", width=W_SEQ, justify="right", style="bright_black")
    table.add_column("대상", width=W_TARGET, overflow="fold")
    table.add_column(change_header, width=W_CHANGE, no_wrap=True)


def status_text(status: ChangeStatus) -> Text:
    return Text(STATUS_LABELS[status], style=STATUS_STYLE[status])


def change_text(c: Change) -> Text:
    t = Text()
    t.append(field_value(c.field, c.before), style="bright_black")
    t.append(" → ")
    t.append(field_value(c.field, c.after), style="bold")
    pct = c.change_pct
    if pct is not None:
        t.append(f" {pct:+.0f}%", style="green" if pct > 0 else "red")
    return t


def target_text(c: Change) -> Text:
    t = Text(c.entity_name, style="bold")
    t.append(f"\n{ENTITY_LABELS.get(c.entity_type, c.entity_type)} · {FIELD_LABELS.get(c.field, c.field)}",
             style="bright_black")
    return t


def step(console: Console, n: int, total: int, title: str, sub: str = "") -> None:
    head = Text()
    head.append(f" {n}/{total} ", style="bold white on blue")
    head.append(f" {title}", style="bold")
    if sub:
        head.append(f"  {sub}", style="bright_black")
    console.print()
    console.print(head)


def panel(console: Console, body: str | Text, title: str, style: str = "blue") -> None:
    console.print(Panel(body, title=title, title_align="left", border_style=style, box=box.ROUNDED, padding=(0, 1)))


# ------------------------------------------------------------------ 진단

def show_diagnosis(console: Console, diag: AccountDiagnosis) -> None:
    y, a = diag.kpi_yesterday, diag.kpi_avg7
    kpi = Text()
    kpi.append(f"{diag.account_name} ", style="bold")
    kpi.append(f"어제({diag.as_of:%m/%d}) ", style="bright_black")
    kpi.append(f"비용 {y['spend']:,.0f}원 · 매출 {y['revenue']:,.0f}원 · ROAS {y['roas']:,.0f}%")
    kpi.append(f"  (7일 평균 ROAS {a['roas']:,.0f}%)", style="bright_black")
    console.print(kpi)
    table = Table(box=box.SIMPLE, show_header=False, pad_edge=False, padding=(0, 1), expand=True)
    table.add_column(width=4, no_wrap=True)
    table.add_column(ratio=1, overflow="fold")
    for f in diag.findings:
        label, style = LEVEL_STYLE[f.level]
        body = Text(f.title, style="bold")
        body.append("\n" + f.detail)
        table.add_row(Text(label, style=style), body)
    console.print(table)


# ------------------------------------------------------------------ 조정안·미리보기·반영·되돌리기

def show_plan(console: Console, run: Run, conflicts: Iterable[str] = (), title: str = "") -> None:
    table = _table(title=title or None)
    _base_columns(table)
    table.add_column("근거 (규칙 문장 틀 + 실제 지표로 자동 생성)", ratio=1, overflow="fold")
    for c in run.changes:
        table.add_row(str(c.seq), target_text(c), change_text(c), Text(c.reason))
    if not run.changes:
        table.add_row("", "조정안 없음", "", "")
    console.print(table)
    for text in conflicts:
        console.print(Text(f"  · 규칙 충돌: {text}", style="bright_black"))


def show_preview(console: Console, run_id: str, results: list[StepResult]) -> None:
    table = _table(title=run_id)
    _base_columns(table, "현재 → 반영 예정")
    table.add_column("예상 영향 · 안전장치", ratio=1, overflow="fold")
    table.add_column("결과", width=4, no_wrap=True)
    for r in results:
        c = r.change
        detail = Text(c.impact, style="default")
        if not r.ok:
            detail.append(f"\n✖ {r.message}", style="bold yellow")
        result = Text("통과", style="green") if r.ok else Text("차단", style="bold yellow")
        table.add_row(str(c.seq), target_text(c), change_text(c), detail, result)
    console.print(table)
    passed = sum(1 for r in results if r.ok)
    console.print(Text(f"  안전장치 통과 {passed}건 · 차단 {len(results) - passed}건 "
                       "(변경 폭·하한/상한·학습 기간·일일 건수·계획 이후 값 변경)", style="bright_black"))


def show_apply(console: Console, report: ApplyReport) -> None:
    table = _table(title=report.run_id)
    _base_columns(table)
    table.add_column("반영 → 재조회 검증", ratio=1, overflow="fold")
    table.add_column("상태", width=W_STATUS, no_wrap=True)
    for r in report.results:
        c = r.change
        flow = Text()
        if c.status == ChangeStatus.SKIPPED:
            flow.append("실행하지 않음", style="bright_black")
        else:
            if r.attempts > 1:
                flow.append(f"반영(일시 오류 → 재시도 {r.attempts - 1}회)", style="yellow")
            elif r.attempts == 1:
                flow.append("반영", style="green")
            flow.append(" → ")
            flow.append(r.message, style="green" if r.ok else "bold red")
        table.add_row(str(c.seq), target_text(c), change_text(c), flow, status_text(c.status))
    console.print(table)
    if report.halted:
        console.print(Text(f"  ■ 실행 중단: {report.halt_reason}\n    남은 변경은 반영하지 않았습니다.",
                           style="bold red"))
    else:
        console.print(Text(f"  ✔ 승인된 {len(report.results)}건 모두 반영 후 재조회 값 일치", style="green"))


def show_rollback(console: Console, run_id: str, results: list[StepResult]) -> None:
    table = _table(title=f"{run_id} 되돌리기 (역순)")
    table.add_column("#", width=W_SEQ, justify="right", style="bright_black")
    table.add_column("대상", width=W_TARGET, overflow="fold")
    table.add_column("되돌린 내용", ratio=1, overflow="fold")
    table.add_column("상태", width=W_STATUS, no_wrap=True)
    for r in results:
        c = r.change
        table.add_row(str(c.seq), target_text(c), Text(r.message, style="default" if r.ok else "red"),
                      status_text(c.status))
    console.print(table)
    ok = sum(r.ok for r in results)
    style = "bold magenta" if ok == len(results) else "bold red"
    console.print(Text(f"  ↺ 실행 ID 하나로 {ok}/{len(results)}건 되돌림 · 재조회로 이전 값 확인", style=style))


def show_runs(console: Console, runs: list[Run]) -> None:
    table = Table(box=box.ROUNDED, header_style="bold")
    table.add_column("실행 ID", no_wrap=True)
    table.add_column("계정", no_wrap=True)
    table.add_column("운영일", no_wrap=True)
    table.add_column("상태", no_wrap=True)
    table.add_column("변경 상태", overflow="fold")
    for run in runs:
        counts: dict[ChangeStatus, int] = {}
        for c in run.changes:
            counts[c.status] = counts.get(c.status, 0) + 1
        summary = Text()
        for st, n in counts.items():
            summary.append(f"{STATUS_LABELS[st]} {n}  ", style=STATUS_STYLE[st])
        table.add_row(run.run_id, run.account_id, f"{run.ops_date}", run.status.value, summary)
    console.print(table)


def show_history(console: Console, events: list[dict[str, Any]]) -> None:
    table = Table(box=box.SIMPLE_HEAD, header_style="bold", expand=True)
    table.add_column("시각", no_wrap=True, style="bright_black", width=8)
    table.add_column("실행 · 변경", no_wrap=True, width=19)
    table.add_column("단계", no_wrap=True, width=19)
    table.add_column("내용", ratio=1, overflow="fold")
    table.add_column("주체", no_wrap=True, style="bright_black", width=17)
    for e in events:
        if e["action"] == "transition":
            to = ChangeStatus(e["to_status"])
            stage = Text()
            if e["from_status"]:
                stage.append(f"{STATUS_LABELS[ChangeStatus(e['from_status'])]} → ", style="bright_black")
            stage.append(STATUS_LABELS[to], style=STATUS_STYLE[to])
        else:
            danger = e["action"] in ("api_error", "halted", "rollback_failed")
            stage = Text(e["action"], style="red" if danger else "white")
        target = e["run_id"] + (" " + e["change_id"].rsplit("-", 1)[-1] if e["change_id"] else "")
        table.add_row(e["ts"][11:19], target, stage, e["detail"], e["actor"])
    console.print(table)
