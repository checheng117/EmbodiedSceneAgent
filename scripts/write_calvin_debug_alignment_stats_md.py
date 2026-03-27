#!/usr/bin/env python3
"""Aggregate JSONL line counts for CALVIN debug planner exports → docs/calvin_debug_alignment_stats.md."""

from __future__ import annotations

import argparse
from pathlib import Path

from embodied_scene_agent.utils.paths import repo_root


def _count_jsonl_lines(p: Path) -> int | None:
    if not p.is_file():
        return None
    n = 0
    with p.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    root = args.root or repo_root()
    planner = root / "data" / "processed" / "planner_sft"
    modes: list[tuple[str, str, tuple[str, ...]]] = [
        (
            "pooled_manifest",
            "Loose random npz sample + round-robin instruction index (legacy-style).",
            ("calvin_debug_real_train.jsonl", "calvin_debug_real_val.jsonl", "calvin_debug_real_test.jsonl"),
        ),
        (
            "grouped_sequence",
            "Consecutive npz windows; one stable-hash instruction per window (recommended for interpretable E2/hybrid).",
            (
                "calvin_debug_real_aligned_train.jsonl",
                "calvin_debug_real_aligned_val.jsonl",
                "calvin_debug_real_aligned_test.jsonl",
            ),
        ),
        (
            "same_task_subset",
            "Smaller same-task-like subset; manifests under `data/processed/calvin_debug_same_task_subset/`.",
            (
                "calvin_debug_real_same_task_train.jsonl",
                "calvin_debug_real_same_task_val.jsonl",
                "calvin_debug_real_same_task_test.jsonl",
            ),
        ),
    ]
    lines_out = [
        "# CALVIN debug alignment — export statistics (auto)",
        "",
        "_Official debug vectors only; instructions from YAML manifest pool — **not** official CALVIN benchmark._",
        "",
        "## Samples per alignment_mode",
        "",
        "| alignment_mode | train rows | val rows | test rows | notes |",
        "|----------------|------------|----------|-----------|-------|",
    ]
    for mode, note, names in modes:
        c_train = _count_jsonl_lines(planner / names[0])
        c_val = _count_jsonl_lines(planner / names[1])
        c_test = _count_jsonl_lines(planner / names[2])
        lines_out.append(
            f"| `{mode}` | {c_train!s} | {c_val!s} | {c_test!s} | {note} |"
        )
    lines_out.extend(
        [
            "",
            "## Lineage fields (per-row `metadata`)",
            "",
            "- `alignment_mode`, `instruction_source`, `instruction_assignment_strategy`",
            "- `episode_key`, `clip_key`, `npz_group_key`, `temporal_group_id`",
            "- `whether_same_task_subset`, `lineage_note`",
            "",
            "## Recommendation",
            "",
            "- **E2 / hybrid small-batch explainability**: prefer **`grouped_sequence`** exports + matching `--calvin-debug-batch grouped_sequence`.",
            "- **Tightest batch coherence**: **`same_task_subset`** (smallest N; not official task labels).",
            "",
        ]
    )
    out = root / "docs" / "calvin_debug_alignment_stats.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
