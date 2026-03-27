"""Pick one normal / recovery / multi_step row from per_sample.jsonl for report markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Write 3-way case study markdown from eval per_sample JSONL.")
    parser.add_argument("--per-sample", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows: list[dict] = []
    with args.per_sample.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    picked: dict[str, dict | None] = {"normal": None, "recovery": None, "multi_step": None}
    for r in rows:
        tt = r.get("trajectory_type")
        if tt in picked and picked[tt] is None:
            picked[tt] = r

    lines = [
        "# Base vs tuned — case studies",
        "",
        "从 `per_sample.jsonl` 自动抽取各 trajectory_type 的首条样本（若 eval 子集中缺失某类则对应节为空）。",
        "",
    ]
    for label, title in (
        ("normal", "Normal trajectory"),
        ("recovery", "Recovery trajectory"),
        ("multi_step", "Multi-step trajectory"),
    ):
        lines.append(f"## {title}")
        lines.append("")
        pr = picked.get(label)
        if pr is None:
            lines.append("_（本 eval 子集中未找到该类型。）_")
            lines.append("")
            continue
        lines.append(f"- sample_id: `{pr.get('sample_id')}`")
        lines.append("")
        lines.append("### Reference")
        lines.append("")
        lines.append("```")
        lines.append(str(pr.get("reference_head", "")))
        lines.append("```")
        lines.append("")
        lines.append("### Base output")
        lines.append("")
        lines.append("```")
        lines.append(str(pr.get("base_output_head", "")))
        lines.append("```")
        lines.append("")
        lines.append("### Tuned output")
        lines.append("")
        lines.append("```")
        lines.append(str(pr.get("tuned_output_head", "")))
        lines.append("```")
        lines.append("")
        lines.append("### Scores")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps({"base": pr.get("base_scores"), "tuned": pr.get("tuned_scores")}, indent=2))
        lines.append("```")
        lines.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[write_case_studies] wrote {args.out}")


if __name__ == "__main__":
    main()
