from __future__ import annotations

import json

from embodied_scene_agent.evaluation.run_ablation_e2 import pick_calvin_cases


def test_pick_calvin_cases_handles_reduced_episode_sets(tmp_path) -> None:
    payload = {
        "experiment_id": "unit_test_fixture_small_batch",
        "per_episode_by_mode": {
            "verifier_only": [
                {"episode_index": i, "success": True, "replan_count": 0} for i in range(6)
            ],
            "verifier_plus_replan": [
                {"episode_index": i, "success": True, "replan_count": 0} for i in range(6)
            ],
        },
    }
    pick_calvin_cases(tmp_path, payload)

    meta_path = tmp_path / "results" / "demos" / "e2_ablation_cases" / "calvin_selection_meta.json"
    assert meta_path.is_file()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["contrast_episode_index"] in range(6)
    assert meta["repair_fail_episode_index"] in range(6)
