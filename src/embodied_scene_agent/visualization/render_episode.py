"""Episode trace rendering."""

from __future__ import annotations

import json
from pathlib import Path

from embodied_scene_agent.pipeline.v0_loop import EpisodeTrace


def render_episode_text(trace: EpisodeTrace) -> str:
    """Plain-text timeline for logs or README snippets."""
    lines = [
        f"Instruction: {trace.instruction}",
        f"Success: {trace.success} ({trace.final_message})",
        f"Replans: {trace.replan_count}",
        "",
    ]
    for i, step in enumerate(trace.steps):
        lines.append(f"--- step {i} ---")
        lines.append(json.dumps(step, indent=2, ensure_ascii=False))
    return "\n".join(lines)


def write_episode(path: Path, trace: EpisodeTrace) -> None:
    """Write JSON + text sidecar."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "instruction": trace.instruction,
        "success": trace.success,
        "replan_count": trace.replan_count,
        "final_message": trace.final_message,
        "steps": trace.steps,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    path.with_suffix(".txt").write_text(render_episode_text(trace), encoding="utf-8")
