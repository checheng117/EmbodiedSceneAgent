from __future__ import annotations

from unittest.mock import patch

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.replanner.hybrid import HybridReplanner
from embodied_scene_agent.verifier.schema import FailureType, VerificationResult


def test_hybrid_uses_llm_then_validates() -> None:
    mem = SceneMemoryBuilder.from_teacher_payload(
        {
            "objects": [
                {"id": "drawer", "name": "d", "position": [0, 0, 0], "state_tags": ["closed"]},
                {"id": "red_block", "name": "b", "position": [0, 0, 0], "state_tags": ["on_table"]},
            ]
        }
    )
    prev = PlannerOutput(
        task="t",
        subgoal="s",
        target_object="red_block",
        skill="bad_skill",
        success_check="x",
        fallback="",
    )
    fail = VerificationResult(
        success=False,
        failure_type=FailureType.UNKNOWN_FAILURE,
        should_replan=True,
        details="unhandled",
    )
    good = PlannerOutput(
        task="fix",
        subgoal="open",
        target_object="drawer",
        skill="open",
        success_check="open",
        fallback="retry",
    )

    def fake_try(**_kwargs):
        return good, {"llm_replanner_called": True, "replanner_parse_ok": True}

    with patch(
        "embodied_scene_agent.replanner.hybrid.try_llm_replan_planner_output",
        fake_try,
    ):
        h = HybridReplanner(enable_llm=True)
        plan, audit = h.replan_with_audit("instr", [], mem, fail, prev)
    assert plan.skill == "open"
    assert audit.whether_rule_based is False


def test_hybrid_llm_fallback_to_rules_on_bad_parse() -> None:
    mem = SceneMemoryBuilder.from_teacher_payload(
        {"objects": [{"id": "red_block", "name": "b", "position": [0, 0, 0], "state_tags": ["on_table"]}]}
    )
    prev = PlannerOutput(
        task="t",
        subgoal="g",
        target_object="red_block",
        skill="bad",
        success_check="x",
        fallback="",
    )
    fail = VerificationResult(
        success=False,
        failure_type=FailureType.UNKNOWN_FAILURE,
        should_replan=True,
        details="x",
    )

    def bad_try(**_kwargs):
        return None, {
            "llm_replanner_called": True,
            "replanner_parse_ok": False,
            "fallback_reason": "bad json",
            "fallback_stage": "parse_validate",
            "replanner_parse_error_kind": "truncated_json",
        }

    with patch(
        "embodied_scene_agent.replanner.hybrid.try_llm_replan_planner_output",
        bad_try,
    ):
        h = HybridReplanner(enable_llm=True)
        plan, audit = h.replan_with_audit("put the red block in the drawer", [], mem, fail, prev)
    assert plan.skill  # rule fallback still returns a plan
    assert audit.llm_replanner_called is True
    assert audit.fallback_reason or audit.notes
