from __future__ import annotations

import json
from pathlib import Path

from embodied_scene_agent.envs.rlbench_adapter import (
    load_observation_like_fixture,
    observation_like_dict_to_scene_memory,
)
from embodied_scene_agent.utils.paths import repo_root


def test_observation_like_to_scene_memory() -> None:
    p = repo_root() / "tests" / "fixtures" / "rlbench_observation_like.json"
    d = load_observation_like_fixture(p)
    mem = observation_like_dict_to_scene_memory(d, task_name="ReachTarget", instruction="reach")
    assert "gripper" in mem.objects
    assert "rlbench_target" in mem.objects
    assert mem.relations


def test_numpy_observation_to_dict_roundtrip() -> None:
    from embodied_scene_agent.envs.rlbench_adapter import numpy_observation_to_dict

    class O:
        gripper_open = 0.5
        gripper_pose = __import__("numpy").zeros(7)
        task_low_dim_state = __import__("numpy").ones(4)
        misc = {}

    d = numpy_observation_to_dict(O())
    assert "gripper_open" in json.dumps(d)
