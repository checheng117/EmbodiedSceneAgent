from __future__ import annotations

from embodied_scene_agent.evaluation.run_ablation_e2 import (
    calvin_fixture_scenario_grid,
    summarize_episodes,
)
from embodied_scene_agent.pipeline.run_calvin_minimal_loop import run_calvin_minimal_episode


def test_calvin_fixture_scenario_grid_len() -> None:
    g = list(calvin_fixture_scenario_grid())
    assert len(g) == 16
    assert "initial_observation" in g[0]


def test_summarize_single_calvin_fixture_episode() -> None:
    s = next(iter(calvin_fixture_scenario_grid()))
    tr = run_calvin_minimal_episode(
        s["instruction"],
        max_steps=8,
        initial_observation=s["initial_observation"],
        verifier_mode="verifier_plus_replan",
        replanner_mode="rule",
        experiment_id="unit_test_calvin_e2",
    )
    out = summarize_episodes(
        "verifier_plus_replan",
        [tr],
        setting_note="unit test CALVIN fixture — not benchmark",
    )
    for k in (
        "task_completion_rate",
        "failure_detected_rate",
        "replan_trigger_rate",
        "recovery_success_rate",
        "average_steps",
        "failure_taxonomy_counts",
    ):
        assert k in out
