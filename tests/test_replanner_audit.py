from __future__ import annotations

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.replanner.rule_based import RuleBasedReplanner
from embodied_scene_agent.verifier.schema import FailureType, VerificationResult


def test_replan_emits_audit() -> None:
    mem = SceneMemoryBuilder.from_teacher_payload(
        {
            "objects": [
                {"id": "drawer", "name": "d", "position": [0, 0, 0], "state_tags": ["closed"]},
                {"id": "red_block", "name": "b", "position": [0, 0, 0], "state_tags": []},
            ]
        }
    )
    prev = PlannerOutput(
        subgoal="place block",
        target_object="red_block",
        skill="place",
        success_check="in drawer",
        task="t",
        fallback="",
    )
    fail = VerificationResult(
        success=False,
        failure_type=FailureType.PRECONDITION_UNSATISFIED,
        should_replan=True,
        details="drawer must be open",
    )
    r = RuleBasedReplanner()
    plan, audit = r.replan_with_audit("instr", [], mem, fail, prev)
    assert plan.skill == "open"
    assert audit.whether_rule_based is True
    assert "precondition" in audit.repair_strategy
