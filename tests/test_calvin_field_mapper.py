"""Unit tests for calvin_field_mapper (no calvin_env import)."""

from __future__ import annotations

import pytest

from embodied_scene_agent.perception.calvin_field_mapper import (
    map_calvin_obs_and_info_to_teacher_bundle,
    map_robot_info_to_teacher_robot,
    map_scene_info_to_scene_objects,
)


def test_map_robot_info_to_teacher_robot():
    r = map_robot_info_to_teacher_robot(
        {"gripper_opening_width": 0.1, "tcp_pos": [1.0, 2.0, 3.0], "gripper_action": 1.0}
    )
    assert r["gripper_open"] is True
    assert r["tcp_pos"] == [1.0, 2.0, 3.0]
    assert r["held_object_uid"] is None


def test_map_scene_info_doors_and_movables():
    scene = {
        "doors": {"my_slider": {"current_state": 0.1}},
        "movable_objects": {
            "obj_red": {"current_pos": [0.1, 0.2, 0.3], "current_orn": [0, 0, 0, 1]}
        },
    }
    objs = map_scene_info_to_scene_objects(scene)
    assert len(objs) == 2


def test_map_calvin_obs_and_info_requires_scene_info():
    obs = {"rgb_obs": {}, "depth_obs": {}, "robot_obs": [], "scene_obs": []}
    info = {"robot_info": {}}
    with pytest.raises(ValueError, match="scene_info"):
        map_calvin_obs_and_info_to_teacher_bundle(obs, info, "go")
