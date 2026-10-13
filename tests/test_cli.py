"""CLI 전체 흐름과 데모, 브리핑."""
from __future__ import annotations

import re

from typer.testing import CliRunner

from adops.cli import app

runner = CliRunner()


def run(home, *args, input=None):
    result = runner.invoke(app, ["--home", str(home), *args], input=input, catch_exceptions=False)
    return result


def run_id(text: str, kind: str) -> str:
    return re.search(rf"R\d{{8}}-{kind}-\d\d", text).group(0)


def test_demo_end_to_end(tmp_path):
    home = tmp_path / "demo"
    result = run(home, "demo")
    assert result.exit_code == 0, result.output
    out = result.output
    for word in ("1/8", "8/8", "차단", "검증 완료", "실행 중단", "되돌림", "가상 데이터 기준"):
        assert word in out
    html = (home / "briefs" / "brief-2026-10-13.html").read_text(encoding="utf-8")
    for word in ("아침 브리핑", "예산 소진 시간대", "조정안과 실행 결과", "최근 실행 이력", "가상 데이터"):
        assert word in html


def test_demo_capture_writes_step_files(tmp_path):
    cap = tmp_path / "cap"
    result = run(tmp_path / "home", "demo", "--capture", str(cap))
    assert result.exit_code == 0
    files = sorted(p.name for p in cap.glob("*.ansi"))
    assert len(files) == 8 and files[0].startswith("01-")
    assert "\x1b[" in (cap / files[5]).read_text(encoding="utf-8")


def test_step_by_step_commands(tmp_path):
    home = tmp_path / "h"
    assert run(home, "plan").exit_code == 1  # 데이터 없음
    assert run(home, "seed").exit_code == 0
    assert "예산 조기 소진" in run(home, "diagnose", "-a", "sa-fitroutine").output
    assert run(home, "diagnose", "-a", "nope").exit_code == 1

    out = run(home, "plan", "-a", "sa-fitroutine").output
    rid = run_id(out, "SA")
    assert run(home, "apply", rid).exit_code == 1  # 승인 없이 반영 불가
    assert "통과" in run(home, "preview", rid).output

    # 대화형 승인: 1 승인, 2 거절, 3 보류, 4 승인
    out = run(home, "approve", rid, input="y\nn\ns\ny\n").output
    assert "승인 #1" in out and "거절 #2" in out and "승인 #4" in out

    out = run(home, "apply", rid).output
    assert "재조회 값 일치" in out
    assert "일치" in run(home, "verify", rid).output
    assert rid in run(home, "runs").output
    assert "검증 완료" in run(home, "history", "--run", rid).output

    assert run(home, "rollback", rid, input="n\n").exit_code == 0  # 확인에서 취소
    out = run(home, "rollback", rid, "--yes").output
    assert "2/2건 되돌림" in out

    out = run(home, "brief", "--out", str(tmp_path / "b.html")).output
    assert "브리핑 생성" in out and (tmp_path / "b.html").exists()


def test_apply_with_failure_simulation_exits_2(tmp_path):
    home = tmp_path / "h"
    run(home, "seed")
    rid = run_id(run(home, "plan", "-a", "mt-fitroutine").output, "MT")
    run(home, "preview", rid)
    run(home, "approve", rid, "--yes")
    result = run(home, "apply", rid, "--fail-rate", "0.35", "--fail-seed", "7")
    assert result.exit_code == 2 and "실행 중단" in result.output


def test_custom_rules_and_errors(tmp_path):
    home = tmp_path / "h"
    run(home, "seed")
    out = run(home, "plan", "-a", "sa-fitroutine", "-r", "examples/rules.searchad.yaml").output
    assert "+10%" in out
    result = run(home, "plan", "-a", "sa-fitroutine", "-r", "examples/rules.meta.yaml")
    assert result.exit_code == 1 and "meta_like" in result.output
    assert run(home, "preview", "R00000000-SA-01").exit_code == 1
    assert run(home, "--version").exit_code == 0
