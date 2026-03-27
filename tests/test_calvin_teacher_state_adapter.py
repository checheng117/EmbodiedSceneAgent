"""CalvinTeacherStateAdapter → SceneMemory."""

from __future__ import annotations

import json
from pathlib import Path

from embodied_scene_agent.memory.schema import ESA_SCENE_MEMORY_SCHEMA_VERSION
from embodied_scene_agent.perception.calvin_teacher import CalvinTeacherStateAdapter
from embodied_scene_agent.planner.rule_based import RuleBasedPlanner
from embodied_scene_agent.planner.schema import PlannerInput
from embodied_scene_agent.planner.serialization import planner_output_to_json
from embodied_scene_agent.utils.paths import repo_root


def _load_obs() -> dict:
    p = repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_mock_calvin_to_scene_memory_tags_and_relations() -> None:
    obs = _load_obs()
    ad = CalvinTeacherStateAdapter()
    mem = ad.to_scene_memory("Put the red block in the drawer.", obs)
    assert mem.schema_version == ESA_SCENE_MEMORY_SCHEMA_VERSION
    assert "drawer" in mem.objects
    assert "closed" in mem.objects["drawer"].state_tags or "open" in mem.objects["drawer"].state_tags
    assert "red_block" in mem.objects
    assert "on_table" in mem.objects["red_block"].state_tags
    assert any(r.subject_id == "red_block" for r in mem.relations)


def test_drawer_open_and_block_in_drawer() -> None:
    obs = _load_obs()
    ct = obs["calvin_teacher_v0"]
    ct["scene_objects"] = [
        {"uid": "drawer", "category": "slider", "position": [0.6, 0.0, 0.35], "drawer_open": True},
        {
            "uid": "red_block",
            "category": "block",
            "position": [0.5, 0.0, 0.3],
            "in_drawer": True,
            "held": False,
        },
    ]
    mem = CalvinTeacherStateAdapter().to_scene_memory("t", obs)
    assert "open" in mem.objects["drawer"].state_tags
    assert "in_drawer" in mem.objects["red_block"].state_tags


def test_planner_input_serialization_roundtrip() -> None:
    obs = _load_obs()
    mem = CalvinTeacherStateAdapter().to_scene_memory("Put the red block in the drawer.", obs)
    inp = PlannerInput(instruction="Put the red block in the drawer.", scene_memory=mem)
    raw = inp.model_dump(mode="json")
    assert raw["instruction"] == "Put the red block in the drawer."
    assert "drawer" in str(raw["scene_memory"])
    plan = RuleBasedPlanner().plan(inp)
    assert plan.skill in {"open", "grasp", "place", "reach", "move_to", "close"}
    assert len(planner_output_to_json(plan)) > 10


def test_rgb_only_obs_raises() -> None:
    ad = CalvinTeacherStateAdapter()
    try:
        ad.to_scene_memory("x", {"rgb_obs": {"static": []}})
    except ValueError as e:
        assert "teacher" in str(e).lower() or "RGB" in str(e)
    else:
        raise AssertionError("expected ValueError")
