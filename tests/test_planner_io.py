"""Planner schema and JSON parsing."""

from __future__ import annotations

import json

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.planner.schema import PlannerInput, PlannerOutput
from embodied_scene_agent.planner.serialization import parse_planner_output_json, planner_output_to_json


def test_planner_output_json_roundtrip() -> None:
    mem = SceneMemoryBuilder.from_teacher_payload({"objects": [], "relations": []})
    out = PlannerOutput(
        task="t",
        subgoal="s",
        target_object="o",
        skill="open",
        success_check="c",
        fallback="f",
    )
    text = planner_output_to_json(out)
    out2 = parse_planner_output_json(text)
    assert out2.task == "t"
    inp = PlannerInput(instruction="i", scene_memory=mem)
    assert inp.instruction == "i"


def test_parse_planner_output_json_from_dict_string() -> None:
    raw = {
        "task": "t",
        "subgoal": "s",
        "target_object": "o",
        "skill": "grasp",
        "success_check": "x",
        "fallback": "",
    }
    out = parse_planner_output_json(json.dumps(raw))
    assert out.skill == "grasp"
