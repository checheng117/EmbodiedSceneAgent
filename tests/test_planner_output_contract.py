from __future__ import annotations

import pytest

from embodied_scene_agent.planner.planner_output_contract import (
    PlannerParseError,
    PlannerParseErrorCode,
    parse_planner_output_text,
    validate_planner_output_dict,
)


def test_validate_ok() -> None:
    p = validate_planner_output_dict(
        {
            "task": "t",
            "subgoal": "s",
            "target_object": "o",
            "skill": "grasp",
            "success_check": "held",
            "fallback": "",
        }
    )
    assert p.skill == "grasp"


def test_validate_skill_alias_normalizes() -> None:
    audit: dict = {}
    p = validate_planner_output_dict(
        {
            "task": "t",
            "subgoal": "s",
            "target_object": "o",
            "skill": "open_gripper",
            "success_check": "ok",
            "fallback": "",
        },
        parse_audit=audit,
    )
    assert p.skill == "open"
    assert audit.get("skill_alias_normalized_from") == "open_gripper"


def test_validate_missing() -> None:
    with pytest.raises(PlannerParseError) as e:
        validate_planner_output_dict({"task": "t"})
    assert e.value.code == PlannerParseErrorCode.MISSING_FIELD


def test_parse_text_block() -> None:
    text = """Plan:
Task: open_drawer
Subgoal: Open the drawer.
Target: drawer
Skill: open
Success_Check: drawer is open
Fallback: retry
Observation:
foo
"""
    p = parse_planner_output_text(text)
    assert p.task == "open_drawer"
    assert p.skill == "open"
