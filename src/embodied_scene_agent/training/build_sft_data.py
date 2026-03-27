"""Construct planner SFT JSONL from scene memory snapshots (stub pipeline)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description="Build planner SFT JSONL (v0 stub).")
    parser.add_argument("--in_dir", type=Path, required=True, help="Directory with memory JSON files.")
    parser.add_argument("--out", type=Path, required=True, help="Output JSONL path.")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for p in sorted(args.in_dir.glob("*.json")):
        rows.append(json.loads(p.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
