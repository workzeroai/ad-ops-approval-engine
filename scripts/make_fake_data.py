"""가상 데이터 파일을 만든다(data/seed/platform.json).

    python scripts/make_fake_data.py                     # 기본 seed, 실적 마감 2026-10-12
    python scripts/make_fake_data.py --seed 7 --as-of 2026-11-01 --out /tmp/p.json

저장소에 들어 있는 data/seed/platform.json은 이 스크립트의 기본값 산출물이다.
`adops seed`·`adops demo`는 같은 생성기(adops.fakedata)로 작업 폴더에 새로 만든다.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from adops import fakedata

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=fakedata.DEFAULT_SEED)
    ap.add_argument("--as-of", default=fakedata.DEMO_AS_OF.isoformat(), help="실적 마감일 YYYY-MM-DD")
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "seed" / "platform.json")
    args = ap.parse_args()
    state = fakedata.generate(date.fromisoformat(args.as_of), args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(state, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    rows = sum(len(v) for v in state["stats"].values())
    print(f"생성: {args.out} (계정 {len(state['accounts'])}개, 일별 실적 {rows}행, seed {args.seed})")


if __name__ == "__main__":
    main()
