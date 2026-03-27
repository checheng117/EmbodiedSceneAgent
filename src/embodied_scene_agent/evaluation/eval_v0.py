"""Evaluate v0 mock episodes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from embodied_scene_agent.evaluation.metrics import metrics_to_dict, summarize_v0_trace
from embodied_scene_agent.pipeline.v0_loop import run_v0_episode


def run_eval_v0(
    instructions: list[str] | None = None,
    *,
    out_path: Path | None = None,
) -> dict[str, Any]:
    """Run one or more mock episodes and optionally write JSON summary."""
    instructions = instructions or []
    if not instructions:
        instructions = [
            "Put the red block in the drawer.",
        ]
    results: list[dict[str, Any]] = []
    for ins in instructions:
        trace = run_v0_episode(ins)
        m = summarize_v0_trace(trace)
        results.append(
            {
                "instruction": ins,
                "metrics": metrics_to_dict(m),
                "steps": len(trace.steps),
            }
        )
    summary = {"episodes": results}
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
