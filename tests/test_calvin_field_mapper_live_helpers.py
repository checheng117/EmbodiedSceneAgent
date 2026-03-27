"""Field mapper live helper entry points."""

from __future__ import annotations

from embodied_scene_agent.perception.calvin_field_mapper import (
    extract_robot_state_from_live_obs,
    extract_scene_objects_from_live_obs,
    map_live_calvin_to_teacher_bundle,
)


def test_map_live_calvin_tags_mapping_meta():
    obs = {
        "rgb_obs": {},
        "depth_obs": {},
        "robot_obs": [0.0] * 3,
        "scene_obs": [0.0] * 2,
    }
    info = {
        "robot_info": {"gripper_opening_width": 0.05, "tcp_pos": [1, 2, 3]},
        "scene_info": {"doors": {}, "movable_objects": {}},
    }
    b = map_live_calvin_to_teacher_bundle(obs, info, "do something")
    assert b["calvin_teacher_v0"]["mapping_meta"].get("live_path") is True


def test_extract_robot_and_scene_helpers():
    obs = {"robot_obs": [0.0] * 8, "scene_obs": [], "rgb_obs": {}, "depth_obs": {}}
    info = {"robot_info": {"tcp_pos": [0.1, 0.2, 0.3]}}
    rs = extract_robot_state_from_live_obs(obs, info)
    assert "robot_info" in rs
    so = extract_scene_objects_from_live_obs(obs, {"scene_info": {"doors": {}, "movable_objects": {}}})
    assert so == []
