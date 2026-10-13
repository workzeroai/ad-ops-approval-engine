"""adops CLI.

  adops demo                      한 번에: 데이터 → 진단 → 조정안 → 미리보기 → 승인 → 반영·검증 → 실패·롤백 → 브리핑
  adops seed                      가상 데이터 새로 만들기
  adops diagnose                  진단 경보 보기
  adops plan                      규칙으로 조정안 만들기(실행 ID 발급)
  adops preview <실행 ID>          현재 값 재조회 + 안전장치 검사
  adops approve <실행 ID>          건별 승인(대화형) 또는 --yes 일괄 승인
  adops apply <실행 ID>            승인된 변경만 반영 → 재조회 검증
  adops verify <실행 ID>           검증 완료 값이 지금도 같은지 재점검
  adops rollback <실행 ID>         실행 단위로 이전 값 복원
  adops runs / history / brief    실행 목록, 감사 로그, HTML 브리핑
"""
from __future__ import annotations

import contextlib
import os
import sys
import webbrowser
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.text import Text

from adops import __version__, ui
from adops.adapters import FailureMode
from adops.brief import AccountBrief, write_brief
from adops.diagnose import diagnose
from adops.execute import ApprovalRequiredError, Executor, RunStateError
from adops.fakedata import DEFAULT_SEED, DEMO_AS_OF
from adops.models import ChangeStatus
from adops.plan import build_plan
from adops.rules.engine import RuleError
from adops.workspace import Workspace, load_ruleset, resolve_home

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="승인형 광고 운영 엔진 — 조정안은 규칙으로 자동 제안하고, 반영은 사람 승인 뒤에만 합니다. (가짜 광고 API)",
)
console = Console(highlight=False)


def _ws(ctx: typer.Context) -> Workspace:
    ws: Workspace = ctx.obj
    if not ws.platform_path.exists():
        console.print(Text(f"가상 데이터가 없습니다: {ws.platform_path}\n"
                           "먼저 `adops seed` 또는 `adops demo`를 실행하세요.", style="red"))
        raise typer.Exit(1)
    return ws


def _fail(msg: str) -> None:
    console.print(Text(msg, style="bold red"))
    raise typer.Exit(1)


def _executor(ws: Workspace, run_id: str, actor: str = "operator", failure: FailureMode | None = None,
              rules: Path | None = None) -> Executor:
    store = ws.store()
    try:
        run = store.get_run(run_id)
    except KeyError as exc:
        _fail(str(exc.args[0]))
    ruleset, _ = load_ruleset(run.platform, rules or (run.rules_file if Path(run.rules_file).is_file() else None))
    return Executor(ws.adapter(run.account_id, failure), store, ruleset.guardrails, actor=actor)


def _accounts(ws: Workspace, account: str) -> list[str]:
    ids = ws.account_ids()
    if account == "all":
        return ids
    if account not in ids:
        _fail(f"알 수 없는 계정: {account} (사용 가능: {', '.join(ids)}, all)")
    return [account]


def _version(value: bool) -> None:
    if value:
        console.print(f"adops {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    ctx: typer.Context,
    home: Annotated[Path | None, typer.Option("--home", help="작업 폴더(기본 .adops, 환경 변수 ADOPS_HOME)")] = None,
    version: Annotated[bool, typer.Option("--version", callback=_version, is_eager=True, help="버전")] = False,
) -> None:
    ctx.obj = Workspace(resolve_home(home))


@app.command()
def demo(
    ctx: typer.Context,
    open_brief: Annotated[bool, typer.Option("--open", help="끝나면 브리핑을 브라우저로 연다")] = False,
    capture: Annotated[Path | None, typer.Option(hidden=True, help="단계별 출력을 ANSI 파일로 저장")] = None,
    width: Annotated[int | None, typer.Option(hidden=True)] = None,
) -> None:
    """[bold]한 번에 시연[/bold]: 데이터 → 진단 → 조정안 → 미리보기 → 승인(데모 자동) → 반영·검증 → 롤백 → 브리핑."""
    from adops.demo import run_demo

    ws: Workspace = ctx.obj
    out = console
    if capture or width:
        out = Console(record=bool(capture), width=width or 100, force_terminal=True,
                      color_system="standard", highlight=False)
    out.print(Text(f"adops demo — 작업 폴더 {ws.home} 를 새로 만듭니다 (모든 데이터는 가상 데이터)", style="bold"))
    result = run_demo(ws.home, out, capture)
    if open_brief:
        webbrowser.open(result.brief_path.resolve().as_uri())


@app.command()
def seed(
    ctx: typer.Context,
    as_of: Annotated[str, typer.Option(help="실적 마감일(YYYY-MM-DD)")] = DEMO_AS_OF.isoformat(),
    seed_value: Annotated[int, typer.Option("--seed", help="난수 seed")] = DEFAULT_SEED,
) -> None:
    """가상 데이터를 새로 만든다(작업 폴더의 감사 로그·브리핑도 지운다)."""
    ws: Workspace = ctx.obj
    path = ws.seed(date.fromisoformat(as_of), seed_value)
    console.print(Text(f"가상 데이터 생성: {path} (실적 마감 {as_of}, seed {seed_value})", style="green"))


@app.command("diagnose")
def diagnose_cmd(
    ctx: typer.Context,
    account: Annotated[str, typer.Option("--account", "-a", help="계정 ID 또는 all")] = "all",
) -> None:
    """진단 경보: 예산 조기 소진, 순위보다 예산이 먼저인 키워드, 위닝·피로 소재 등."""
    ws = _ws(ctx)
    for acc in _accounts(ws, account):
        ui.show_diagnosis(console, diagnose(ws.adapter(acc)))


@app.command()
def plan(
    ctx: typer.Context,
    account: Annotated[str, typer.Option("--account", "-a", help="계정 ID 또는 all")] = "all",
    rules: Annotated[Path | None, typer.Option("--rules", "-r", help="규칙 YAML(없으면 플랫폼 기본 규칙)")] = None,
) -> None:
    """규칙으로 조정안을 만든다. 아무것도 반영하지 않고 실행 ID만 발급한다."""
    ws = _ws(ctx)
    store = ws.store()
    for acc in _accounts(ws, account):
        adapter = ws.adapter(acc)
        try:
            ruleset, label = load_ruleset(adapter.platform, rules)
        except (RuleError, ValueError) as exc:
            _fail(str(exc))
        result = build_plan(diagnose(adapter), ruleset, store, label)
        ui.show_plan(console, result.run, result.conflicts, title=f"{adapter.account_name} · {result.run.run_id}")
        if result.run.changes:
            console.print(Text(f"  다음: adops preview {result.run.run_id}", style="bright_black"))


@app.command()
def preview(ctx: typer.Context, run_id: str) -> None:
    """현재 값을 다시 조회해 변경 전/후를 확정하고 안전장치를 검사한다."""
    ex = _executor(_ws(ctx), run_id)
    try:
        ui.show_preview(console, run_id, ex.preview(run_id))
    except RunStateError as exc:
        _fail(str(exc))
    console.print(Text(f"  다음: adops approve {run_id}", style="bright_black"))


def _parse_seqs(value: str | None) -> list[int] | None:
    if not value:
        return None
    return [int(x) for x in value.replace(" ", "").split(",") if x]


@app.command()
def approve(
    ctx: typer.Context,
    run_id: str,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="미리보기를 통과한 변경을 모두 승인")] = False,
    only: Annotated[str | None, typer.Option(help="이 번호만 승인(예: 1,3)")] = None,
    reject: Annotated[str | None, typer.Option(help="이 번호는 거절(예: 2)")] = None,
    actor: Annotated[str, typer.Option(help="승인자 이름(감사 로그에 기록)")] = "operator",
) -> None:
    """건별 승인. 옵션이 없으면 한 건씩 물어본다(y 승인 · n 거절 · s 보류 · a 나머지 모두 승인)."""
    ws = _ws(ctx)
    ex = _executor(ws, run_id, actor=actor)
    run = ex.store.get_run(run_id)
    pending = [c for c in run.changes if c.status == ChangeStatus.PREVIEWED]
    if not pending:
        _fail(f"{run_id}: 승인할 변경이 없습니다(먼저 preview)")
    seqs, rej = _parse_seqs(only), _parse_seqs(reject) or []
    if not (yes or only or reject):
        seqs, approve_rest = [], False
        for c in pending:
            if approve_rest:
                seqs.append(c.seq)
                continue
            console.print(ui.target_text(c), ui.change_text(c))
            console.print(Text(f"   근거: {c.reason}\n   영향: {c.impact}", style="bright_black"))
            answer = typer.prompt("   승인? [y/n/s/a]", default="s").strip().lower()
            if answer == "y":
                seqs.append(c.seq)
            elif answer == "n":
                rej.append(c.seq)
            elif answer == "a":
                seqs.append(c.seq)
                approve_rest = True
        if not seqs and not rej:
            console.print("변경 없음(모두 보류).")
            return
    approved, rejected = ex.approve(run_id, seqs if not yes else None, rej)
    for c in approved:
        console.print(Text(f"  ✔ 승인 #{c.seq} {c.entity_name}", style="cyan"))
    for c in rejected:
        console.print(Text(f"  ✖ 거절 #{c.seq} {c.entity_name}", style="yellow"))
    if approved:
        console.print(Text(f"  다음: adops apply {run_id}", style="bright_black"))


@app.command()
def apply(
    ctx: typer.Context,
    run_id: str,
    fail_rate: Annotated[float, typer.Option(help="실패 시뮬레이션 확률(0~1)")] = 0.0,
    fail_seed: Annotated[int, typer.Option(help="실패 시뮬레이션 seed")] = 7,
) -> None:
    """승인된 변경만 반영하고, 한 건마다 다시 조회해 검증한다. 실패하면 남은 변경은 건너뛴다."""
    failure = FailureMode(rate=fail_rate, seed=fail_seed) if fail_rate else None
    ex = _executor(_ws(ctx), run_id, failure=failure)
    try:
        report = ex.apply(run_id)
    except (ApprovalRequiredError, RunStateError) as exc:
        _fail(str(exc))
    ui.show_apply(console, report)
    if report.halted:
        console.print(Text(f"  되돌리기: adops rollback {run_id}", style="bright_black"))
        raise typer.Exit(2)


@app.command()
def verify(ctx: typer.Context, run_id: str) -> None:
    """검증 완료된 변경이 지금도 같은 값인지 다시 본다."""
    ex = _executor(_ws(ctx), run_id)
    results = ex.verify(run_id)
    for r in results:
        style = "green" if r.ok else "red"
        console.print(Text(f"  #{r.change.seq} {r.change.entity_name}: {r.message}", style=style))
    if not results:
        console.print("검증 완료 상태인 변경이 없습니다.")
    if any(not r.ok for r in results):
        raise typer.Exit(2)


@app.command()
def rollback(
    ctx: typer.Context,
    run_id: str,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="확인 없이 되돌리기")] = False,
    actor: Annotated[str, typer.Option(help="실행자 이름(감사 로그에 기록)")] = "operator",
) -> None:
    """실행 ID 하나로 반영된 변경을 역순으로 이전 값으로 되돌리고 다시 검증한다."""
    ex = _executor(_ws(ctx), run_id, actor=actor)
    if not yes and not typer.confirm(f"{run_id}의 반영 내용을 모두 이전 값으로 되돌릴까요?"):
        raise typer.Exit()
    try:
        results = ex.rollback(run_id)
    except RunStateError as exc:
        _fail(str(exc))
    ui.show_rollback(console, run_id, results)
    if not all(r.ok for r in results):
        raise typer.Exit(2)


@app.command()
def runs(ctx: typer.Context, limit: Annotated[int, typer.Option(help="최근 N건")] = 20) -> None:
    """실행 목록."""
    ui.show_runs(console, _ws(ctx).store().list_runs(limit))


@app.command()
def history(
    ctx: typer.Context,
    run: Annotated[str | None, typer.Option("--run", help="이 실행 ID만")] = None,
    limit: Annotated[int, typer.Option(help="최근 N건")] = 40,
) -> None:
    """감사 로그: 누가 언제 어떤 단계로 무엇을 바꿨는지."""
    ui.show_history(console, _ws(ctx).store().events(run, limit))


@app.command()
def brief(
    ctx: typer.Context,
    out: Annotated[Path | None, typer.Option(help="저장 경로(기본 <작업 폴더>/briefs/brief-<운영일>.html)")] = None,
    open_brief: Annotated[bool, typer.Option("--open", help="브라우저로 연다")] = False,
) -> None:
    """HTML 일일 브리핑: 어제 성과, 진단 경보, 예산 소진 시간대, 조정안·실행 결과, 실행 이력."""
    ws = _ws(ctx)
    store = ws.store()
    latest = {}
    for run in store.list_runs(200):
        latest.setdefault(run.account_id, run)
    items = [AccountBrief(diagnose(ws.adapter(a)), latest.get(a)) for a in ws.account_ids()]
    path = out or ws.briefs_dir / f"brief-{ws.server().ops_date}.html"
    write_brief(items, store, path)
    console.print(Text(f"브리핑 생성: {path}", style="green"))
    if open_brief:
        webbrowser.open(path.resolve().as_uri())


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(Exception):
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    app()


if __name__ == "__main__":
    main()
