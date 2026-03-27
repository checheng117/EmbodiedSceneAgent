"""Verifier tests."""

from __future__ import annotations

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.verifier.schema import FailureType
from embodied_scene_agent.verifier.state_diff import StateDiffVerifier


def _mem(payload: dict) -> object:
    return SceneMemoryBuilder.from_teacher_payload(payload)


def test_open_success() -> None:
    before = _mem(
        {
            "objects": [
                {
                    "id": "drawer",
                    "name": "d",
                    "position": [0, 0, 0],
                    "state_tags": ["closed"],
                }
            ],
            "relations": [],
        }
    )
    after = _mem(
        {
            "objects": [
                {
                    "id": "drawer",
                    "name": "d",
                    "position": [0, 0, 0],
                    "state_tags": ["open"],
                }
            ],
            "relations": [],
        }
    )
    plan = PlannerOutput(
        task="t",
        subgoal="s",
        target_object="drawer",
        skill="open",
        success_check="open",
    )
    v = StateDiffVerifier()
    r = v.verify(before, after, plan)  # type: ignore[arg-type]
    assert r.success


def test_place_precondition_not_held() -> None:
    before = _mem(
        {
            "objects": [
                {
                    "id": "drawer",
                    "name": "d",
                    "position": [0, 0, 0],
                    "state_tags": ["open"],
                },
                {
                    "id": "red_block",
                    "name": "b",
                    "position": [0, 0, 0],
                    "state_tags": ["on_table"],
                },
            ],
            "relations": [],
        }
    )
    after = before
    plan = PlannerOutput(
        task="t",
        subgoal="s",
        target_object="drawer",
        skill="place",
        success_check="in_drawer",
    )
    v = StateDiffVerifier()
    r = v.verify(before, after, plan)  # type: ignore[arg-type]
    assert not r.success
    assert r.failure_type == FailureType.PRECONDITION_UNSATISFIED


def test_grasp_no_effect() -> None:
    before = _mem(
        {
            "objects": [
                {
                    "id": "red_block",
                    "name": "b",
                    "position": [0, 0, 0],
                    "state_tags": ["on_table"],
                }
            ],
            "relations": [],
        }
    )
    after = before
    plan = PlannerOutput(
        task="t",
        subgoal="s",
        target_object="red_block",
        skill="grasp",
        success_check="held",
    )
    v = StateDiffVerifier()
    r = v.verify(before, after, plan)  # type: ignore[arg-type]
    assert not r.success
    assert r.failure_type == FailureType.STATE_UNCHANGED
