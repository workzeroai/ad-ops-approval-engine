"""`adops demo`: 가상 데이터 생성부터 브리핑까지 한 번에 보여 준다.

데이터 생성 → 진단 → 조정안 → 미리보기(안전장치) → 승인(데모용 자동 승인) → 반영·검증
→ 실패 1건과 실행 중단·롤백 → HTML 브리핑
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.text import Text

from adops import fakedata, ui
from adops.adapters import FailureMode
from adops.brief import AccountBrief, write_brief
from adops.diagnose import diagnose
from adops.execute import Executor
from adops.models import ChangeStatus, Platform
from adops.plan import build_plan
from adops.workspace import Workspace, load_ruleset

TOTAL = 8
# 메타형 반영 때 켜는 실패 시뮬레이션. seed를 고정해 매번 같은 지점에서 실패한다.
DEMO_FAILURE = FailureMode(rate=0.35, seed=7, transient_share=0.5)
DEMO_ACTOR = "demo:auto-approve"


@dataclass
class DemoResult:
    brief_path: Path
    run_ids: dict[str, str] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    events: int = 0


class _Capture:
    """단계별 출력을 파일로 남긴다(README 스크린샷·GIF용)."""

    def __init__(self, console: Console, out_dir: Path | None):
        self.console, self.out_dir = console, out_dir
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)

    def cut(self, name: str) -> None:
        if not self.out_dir:
            return
        text = self.console.export_text(styles=True, clear=True)
        (self.out_dir / f"{name}.ansi").write_text(text, encoding="utf-8")


def run_demo(home: Path, console: Console, capture_dir: Path | None = None,
             failure: FailureMode = DEMO_FAILURE) -> DemoResult:
    ws = Workspace(home)
    cap = _Capture(console, capture_dir)

    # 1. 데이터 ------------------------------------------------------------
    ui.step(console, 1, TOTAL, "가상 데이터 생성", f"{ws.home}/platform.json")
    ws.seed()
    server = ws.server()
    accounts = server.accounts()
    body = Text()
    body.append(f"{fakedata.BRAND}", style="bold")
    body.append(" — 지어낸 홈트레이닝 기구 쇼핑몰 · 실제 계정과 무관\n", style="bright_black")
    for acc_id, acc in accounts.items():
        kind = "검색광고형" if acc["platform"] == Platform.SEARCHAD_LIKE else "메타형"
        sizes = ", ".join(f"{k} {n}" for k, n in server.object_counts(acc_id).items())
        body.append(f"• {acc['name']} ({kind}): {sizes}\n")
    body.append(f"• 일별 실적 {fakedata.DAYS}일 · 실적 마감 {server.as_of} · 운영일 {server.ops_date}\n")
    body.append("• 심어 둔 패턴: 예산 조기 소진, 위닝 소재, 소재 피로, 전환 없는 비용", style="cyan")
    ui.panel(console, body, "seed", "blue")
    cap.cut("01-seed")

    store = ws.store()
    diags = {}
    # 2. 진단 ------------------------------------------------------------
    ui.step(console, 2, TOTAL, "진단", "예산 소진 시각·노출 손실·소재 순위")
    for acc_id in accounts:
        diags[acc_id] = diagnose(ws.adapter(acc_id))
        ui.show_diagnosis(console, diags[acc_id])
    cap.cut("02-diagnose")

    # 3. 조정안 ------------------------------------------------------------
    ui.step(console, 3, TOTAL, "조정안", "YAML 규칙 → 변경 + 근거 문장")
    runs: dict[str, str] = {}
    guardrails = {}
    for acc_id, diag in diags.items():
        ruleset, label = load_ruleset(diag.platform)
        guardrails[acc_id] = ruleset.guardrails
        plan = build_plan(diag, ruleset, store, label)
        runs[acc_id] = plan.run.run_id
        ui.show_plan(console, plan.run, plan.conflicts, title=f"{diag.account_name} · {plan.run.run_id}")
    cap.cut("03-plan")

    # 4. 미리보기 ------------------------------------------------------------
    ui.step(console, 4, TOTAL, "미리보기", "현재 값 재조회 + 안전장치 검사")
    for acc_id, run_id in runs.items():
        ex = Executor(ws.adapter(acc_id), store, guardrails[acc_id], actor=DEMO_ACTOR)
        ui.show_preview(console, run_id, ex.preview(run_id))
    cap.cut("04-preview")

    # 5. 승인 ------------------------------------------------------------
    ui.step(console, 5, TOTAL, "승인", "데모용 자동 승인")
    console.print(Text("  실제 운영에서는 `adops approve <실행 ID>`로 사람이 건별로 승인합니다. "
                       "데모는 안전장치를 통과한 건을 자동 승인(demo:auto-approve)합니다.", style="yellow"))
    for acc_id, run_id in runs.items():
        ex = Executor(ws.adapter(acc_id), store, guardrails[acc_id], actor=DEMO_ACTOR)
        approved, _ = ex.approve(run_id, note="데모 자동 승인")
        names = ", ".join(c.entity_name for c in approved)
        console.print(Text(f"  ✔ {run_id} 승인 {len(approved)}건: {names}", style="cyan"))
    cap.cut("05-approve")

    # 6. 반영·검증(검색광고형) -------------------------------------------------
    sa = next(a for a, d in diags.items() if d.platform == Platform.SEARCHAD_LIKE)
    mt = next(a for a, d in diags.items() if d.platform == Platform.META_LIKE)
    ui.step(console, 6, TOTAL, "반영 → 재조회 검증", diags[sa].account_name)
    ex_sa = Executor(ws.adapter(sa), store, guardrails[sa], actor=DEMO_ACTOR)
    ui.show_apply(console, ex_sa.apply(runs[sa]))
    cap.cut("06-apply")

    # 7. 실패·롤백(메타형) ------------------------------------------------------
    ui.step(console, 7, TOTAL, "실패 → 중단 → 롤백",
            f"{diags[mt].account_name} · 실패 시뮬레이션 rate={failure.rate} seed={failure.seed}")
    ex_mt = Executor(ws.adapter(mt, failure), store, guardrails[mt], actor=DEMO_ACTOR)
    ui.show_apply(console, ex_mt.apply(runs[mt]))
    console.print(Text(f"  $ adops rollback {runs[mt]} --yes", style="bold"))
    ex_rb = Executor(ws.adapter(mt), store, guardrails[mt], actor=DEMO_ACTOR)
    ui.show_rollback(console, runs[mt], ex_rb.rollback(runs[mt]))
    cap.cut("07-rollback")

    # 8. 브리핑 ------------------------------------------------------------
    ui.step(console, 8, TOTAL, "아침 브리핑", "HTML 한 장")
    briefs = [AccountBrief(diagnose(ws.adapter(a)), store.get_run(runs[a])) for a in accounts]
    out = write_brief(briefs, store, ws.briefs_dir / f"brief-{server.ops_date}.html")
    events = store.events(limit=100_000)
    reached = Counter(e["to_status"] for e in events if e["action"] == "transition")
    counts = {st.value: reached.get(st.value, 0) for st in ChangeStatus}
    summary = Text()
    summary.append("가상 데이터 기준 결과\n", style="bold")
    summary.append(f"• 조정안 {counts['planned']}건 → 안전장치 통과 {counts['previewed']}건 · "
                   f"차단 {counts['blocked']}건\n")
    summary.append(f"• 승인 {counts['approved']}건 → 검증 완료 {counts['verified']}건 · "
                   f"검증 실패 {counts['failed']}건 · 실행 중단으로 건너뜀 {counts['skipped']}건\n")
    summary.append(f"• 실패한 실행은 실행 ID 하나로 {counts['rolled_back']}건 되돌림\n")
    summary.append(f"• 감사 로그 {len(events)}건 ({ws.audit_path})\n")
    summary.append(f"• 브리핑: {out}\n", style="cyan")
    summary.append(f"다음: adops runs · adops history --run {runs[mt]} · adops brief --open", style="bright_black")
    ui.panel(console, summary, "완료", "green")
    cap.cut("08-brief")
    store.close()
    return DemoResult(brief_path=out, run_ids=runs, counts=counts, events=len(events))
