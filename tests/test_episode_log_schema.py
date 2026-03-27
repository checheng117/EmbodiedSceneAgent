from __future__ import annotations

from embodied_scene_agent.pipeline.episode_log_schema import step_dict_to_episode_step_log


def test_step_dict_mapping() -> None:
    raw = {
        "scene_memory_before": {"objects": {}},
        "plan": {"skill": "grasp"},
        "skill_result": {"success": True},
        "scene_memory_after_first": {"objects": {}},
        "verification": {"success": False, "failure_type": "state_unchanged"},
        "replan": {"skill": "open"},
        "verification_replan": {"success": True},
    }
    log = step_dict_to_episode_step_log(raw, timestep=0, observation_id="t0")
    assert log.timestep == 0
    assert log.failure_type == "state_unchanged"
    assert log.final_step_outcome == "success_after_replan"
