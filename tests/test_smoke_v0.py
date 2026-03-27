"""End-to-end mock v0 smoke."""

from __future__ import annotations

from embodied_scene_agent.pipeline.v0_loop import run_v0_episode


def test_v0_episode_success() -> None:
    trace = run_v0_episode("Put the red block in the drawer.", max_steps=12)
    assert trace.success
    assert len(trace.steps) >= 1
