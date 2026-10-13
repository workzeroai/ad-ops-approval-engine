"""README용 데모 이미지 만들기(개발용, 포트폴리오 디자인 키트 필요).

    python scripts/make_demo_assets.py --kit ../_design

1. 임시 폴더에서 `adops demo`를 돌려 단계별 터미널 출력(ANSI)을 저장
2. 키트의 터미널 창 모양으로 PNG 렌더 → docs/shots/NN-*.png
3. PNG를 묶어 docs/demo.gif
4. 브리핑 HTML을 구역별로 캡처 → docs/shots/brief-*.png

터미널 PNG는 키트의 `shots.render_terminal`을 그대로 쓴다. 키트가 한글(2칸)과 표 세로선을
셀 격자에 맞추면서 한글은 자연 간격으로 렌더한다(저장소 쪽 후처리 없음).
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

from rich.console import Console

ROOT = Path(__file__).resolve().parents[1]
GIF_STEPS = ["02-diagnose", "03-plan", "04-preview", "06-apply", "07-rollback", "08-brief"]
BRIEF_SECTIONS = {"brief-overview": "#overview", "brief-runs": "#runs-section", "brief-heat": "#heat-section"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kit", type=Path, default=ROOT.parent / "_design", help="포트폴리오 디자인 키트 폴더")
    ap.add_argument("--out", type=Path, default=ROOT / "docs")
    args = ap.parse_args()
    sys.path.insert(0, str(args.kit.resolve()))
    import shots  # type: ignore[import-not-found]

    from adops.demo import run_demo

    shot_dir = args.out / "shots"
    shot_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="adops-assets-"))
    try:
        cap = tmp / "capture"
        console = Console(record=True, width=100, force_terminal=True, color_system="standard",
                          highlight=False, file=open(tmp / "stdout.txt", "w", encoding="utf-8"))  # noqa: SIM115
        # 화면에 로컬 임시 경로가 찍히지 않도록 임시 폴더로 이동해 상대 경로(.adops)로 실행한다
        prev = Path.cwd()
        os.chdir(tmp)
        try:
            result = run_demo(Path(".adops"), console, cap)
            brief_path = result.brief_path.resolve()
        finally:
            os.chdir(prev)
        for ansi in sorted(cap.glob("*.ansi")):
            text = ansi.read_text(encoding="utf-8").strip("\n")
            command = "adops demo" if ansi.stem.startswith("01") else None
            out = shot_dir / f"{ansi.stem}.png"
            shots.render_terminal(text, out, f"adops demo · {ansi.stem[3:]}", command, width=900, scale=2)
            print("생성:", out)
        frames = [shot_dir / f"{s}.png" for s in GIF_STEPS]
        gif = shots.make_gif(frames, args.out / "demo.gif", duration=2200, width=900)
        print("생성:", gif, f"{gif.stat().st_size / 1e6:.1f}MB")
        for name, selector in BRIEF_SECTIONS.items():
            out = shot_dir / f"{name}.png"
            shots.capture_html(str(brief_path), out, width=1280, height=900, scale=2, selector=selector)
            print("생성:", out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
