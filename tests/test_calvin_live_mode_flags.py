"""Episode trace mode flags for CALVIN minimal loop."""

from __future__ import annotations

from embodied_scene_agent.pipeline.run_calvin_minimal_loop import run_calvin_minimal_episode
from embodied_scene_agent.utils.paths import repo_root


def test_trace_experiment_id_passed_through():
    trace = run_calvin_minimal_episode(
        "Put the red block in the drawer.",
        fixture_path=repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json",
        max_steps=4,
        experiment_id="exp_smoke_001",
    )
    assert trace.experiment_id == "exp_smoke_001"
