"""README용 데모 이미지 만들기(개발용, 포트폴리오 디자인 키트 필요).

    python scripts/make_demo_assets.py --kit ../_design

1. 임시 폴더에서 `adops demo`를 돌려 단계별 터미널 출력(ANSI)을 저장
2. 키트의 터미널 창 모양으로 PNG 렌더 → docs/shots/NN-*.png
3. PNG를 묶어 docs/demo.gif
4. 브리핑 HTML을 구역별로 캡처 → docs/shots/brief-*.png

키트 터미널 렌더러에 한 가지를 더한다: 한글 같은 전각 문자는 고정폭 글꼴에서 정확히 2칸이 아니라
rich 표의 세로선이 어긋나므로, 전각 문자는 2ch, 그 밖의 비ASCII 문자는 1ch 폭으로 고정한다.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path

from rich.console import Console

ROOT = Path(__file__).resolve().parents[1]
GIF_STEPS = ["02-diagnose", "03-plan", "04-preview", "06-apply", "07-rollback", "08-brief"]
BRIEF_SECTIONS = {"brief-overview": "#overview", "brief-runs": "#runs-section", "brief-heat": "#heat-section"}

_TAG = re.compile(r"(<[^>]+>)")
_BOX = range(0x2500, 0x2580)


def _fix_char(ch: str) -> str:
    if ord(ch) < 128 or ord(ch) in _BOX:
        return ch
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return f'<span class="w2">{ch}</span>'
    return f'<span class="w1">{ch}</span>'


_CORNERS = str.maketrans("╭╮╰╯", "┌┐└┘")  # 둥근 모서리 → 각진 모서리(글꼴에 있음)


def fix_wide(html: str) -> str:
    html = html.translate(_CORNERS)
    head, sep, rest = html.partition("<pre>")
    body, sep2, tail = rest.partition("</pre>")
    parts = _TAG.split(body)
    fixed = "".join(p if p.startswith("<") else "".join(_fix_char(c) for c in p) for p in parts)
    css = (".w2{display:inline-block;width:2ch;text-align:center}"
           ".w1{display:inline-block;width:1ch;text-align:center;overflow:visible}"
           # 줄바꿈 없이 창 폭을 내용(100칸)에 맞춘다
           "pre{white-space:pre !important;word-break:normal !important}.win{width:auto !important}")
    head = head.replace("</style>", css + "</style>", 1)
    return head + sep + fixed + sep2 + tail


def render_term(shots, launch_browser, text: str, out: Path, title: str, command: str | None) -> None:
    from playwright.sync_api import sync_playwright

    html = fix_wide(shots.terminal_html(text, title, command, width=900, font_size=15))
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_page(viewport={"width": 1400, "height": 400}, device_scale_factor=2)
        page.set_content(html, wait_until="load")
        page.evaluate("async () => { await document.fonts.load('15px Pretendard'); await document.fonts.ready; }")
        page.locator("body").screenshot(path=str(out), omit_background=True)
        browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kit", type=Path, default=ROOT.parent / "_design", help="포트폴리오 디자인 키트 폴더")
    ap.add_argument("--out", type=Path, default=ROOT / "docs")
    args = ap.parse_args()
    sys.path.insert(0, str(args.kit.resolve()))
    import shots  # type: ignore[import-not-found]
    from kit_common import launch_browser  # type: ignore[import-not-found]

    from adops.demo import run_demo

    shot_dir = args.out / "shots"
    shot_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="adops-assets-"))
    try:
        cap = tmp / "capture"
        console = Console(record=True, width=100, force_terminal=True, color_system="standard",
                          highlight=False, file=open(tmp / "stdout.txt", "w", encoding="utf-8"))  # noqa: SIM115
        result = run_demo(tmp / ".adops", console, cap)
        for ansi in sorted(cap.glob("*.ansi")):
            text = ansi.read_text(encoding="utf-8").strip("\n")
            command = "adops demo" if ansi.stem.startswith("01") else None
            out = shot_dir / f"{ansi.stem}.png"
            render_term(shots, launch_browser, text, out, f"adops demo · {ansi.stem[3:]}", command)
            print("생성:", out)
        frames = [shot_dir / f"{s}.png" for s in GIF_STEPS]
        gif = shots.make_gif(frames, args.out / "demo.gif", duration=2200, width=900)
        print("생성:", gif, f"{gif.stat().st_size / 1e6:.1f}MB")
        for name, selector in BRIEF_SECTIONS.items():
            out = shot_dir / f"{name}.png"
            shots.capture_html(str(result.brief_path), out, width=1280, height=900, scale=2, selector=selector)
            print("생성:", out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
