"""Aggregate metrics for v0 and future benchmarks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from embodied_scene_agent.pipeline.v0_loop import EpisodeTrace


@dataclass
class V0Metrics:
    """Episode-level metrics for mock v0."""

    success: bool
    num_steps: int
    replan_count: int
    failure_counts: dict[str, int] = field(default_factory=dict)


def summarize_v0_trace(trace: EpisodeTrace) -> V0Metrics:
    """Compute simple statistics from an episode trace."""
    fail_counts: dict[str, int] = {}
    for step in trace.steps:
        ver = step.get("verification") or {}
        if not ver.get("success"):
            ft = (ver.get("failure_type") or "unknown")
            fail_counts[ft] = fail_counts.get(ft, 0) + 1
        ver2 = (
            (step.get("verification_replan") or {}) if isinstance(step.get("verification_replan"), dict) else {}
        )
        if ver2 and not ver2.get("success"):
            ft = (ver2.get("failure_type") or "unknown")
            fail_counts[ft] = fail_counts.get(ft, 0) + 1
    return V0Metrics(
        success=trace.success,
        num_steps=len(trace.steps),
        replan_count=trace.replan_count,
        failure_counts=fail_counts,
    )


def metrics_to_dict(m: V0Metrics) -> dict[str, Any]:
    """JSON-serializable dict."""
    return {
        "success": m.success,
        "num_steps": m.num_steps,
        "replan_count": m.replan_count,
        "failure_counts": m.failure_counts,
    }
