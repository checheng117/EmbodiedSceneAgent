from __future__ import annotations

from embodied_scene_agent.evaluation.run_ablation_e2 import select_stable_mock_case_rows


def test_select_stable_mock_prefers_verifier_contrast() -> None:
    per = {
        "none": [{"episode_index": 0, "success": True, "num_steps": 3, "replan_count": 0}],
        "verifier_only": [
            {"episode_index": 0, "success": False, "num_steps": 5, "forced_grasp_failures": 0},
            {"episode_index": 1, "success": False, "num_steps": 4, "forced_grasp_failures": 1},
        ],
        "verifier_plus_replan": [
            {"episode_index": 0, "success": False, "replan_count": 0},
            {"episode_index": 1, "success": True, "replan_count": 2},
        ],
    }
    none_row, vo_row, vpr_row, meta = select_stable_mock_case_rows(per)
    assert none_row["episode_index"] == 0
    assert meta["strategy"] == "verifier_only_fail_and_verifier_plus_success"
    assert meta["episode_index"] == 1
    assert vo_row["episode_index"] == 1
    assert vpr_row["episode_index"] == 1
