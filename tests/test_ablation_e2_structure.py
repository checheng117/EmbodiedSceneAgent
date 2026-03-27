from __future__ import annotations

from embodied_scene_agent.evaluation.run_ablation_e2 import run_all_modes


def test_run_all_modes_structure(monkeypatch) -> None:
    import embodied_scene_agent.evaluation.run_ablation_e2 as m

    monkeypatch.setattr(
        m,
        "scenario_grid",
        lambda: iter(
            [
                {"episode_index": 0, "instruction": "put the red block in the drawer", "forced_grasp_failures": 1},
                {"episode_index": 1, "instruction": "put the red block in the drawer", "forced_grasp_failures": 0},
            ]
        ),
    )
    p = m.run_all_modes(experiment_id="unit_test_e2", replanner_mode="rule")
    assert set(p["modes"]) == {"none", "verifier_only", "verifier_plus_replan"}
    for mode, stats in p["modes"].items():
        assert "task_completion_rate" in stats
        assert stats["n_episodes"] == 2
