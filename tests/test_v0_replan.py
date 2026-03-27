"""Replan path: forced grasp failure then recovery."""

from __future__ import annotations

from embodied_scene_agent.pipeline.v0_loop import run_v0_episode


def test_forced_grasp_failure_triggers_replan_then_success() -> None:
    trace = run_v0_episode(
        "Put the red block in the drawer.",
        max_steps=16,
        forced_grasp_failures=1,
    )
    assert trace.success
    assert trace.replan_count >= 1
