from __future__ import annotations

from unittest.mock import patch

from embodied_scene_agent.envs.mock import MockEmbodiedEnv
from embodied_scene_agent.pipeline.v0_loop import run_v0_episode
from embodied_scene_agent.planner.base import BasePlanner
from embodied_scene_agent.planner.schema import PlannerInput
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
        return good, {
            "llm_replanner_called": True,
            "replanner_parse_ok": True,
            "raw_generation_head": '{"task":"fix"...}',
            "repair_actions": ["success_check:inferred_from_skill_target"],
        }

    with patch(
        "embodied_scene_agent.replanner.hybrid.try_llm_replan_planner_output",
        fake_try,
    ):
        h = HybridReplanner(enable_llm=True)
        plan, audit = h.replan_with_audit("instr", [], mem, fail, prev)
    assert plan.skill == "open"
    assert audit.whether_rule_based is False
    assert audit.revised_plan_accepted is True
    assert audit.raw_generation_head == '{"task":"fix"...}'
    assert audit.parser_repair_actions == ["success_check:inferred_from_skill_target"]


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


def test_hybrid_rejects_absent_target_before_execution() -> None:
    mem = SceneMemoryBuilder.from_teacher_payload(
        {
            "objects": [
                {"id": "drawer", "name": "drawer", "position": [0, 0, 0], "state_tags": ["closed"]},
                {"id": "red_block", "name": "block", "position": [0, 0, 0], "state_tags": ["on_table"]},
                {"id": "table", "name": "table", "position": [0, 0, 0], "state_tags": ["static"]},
            ]
        }
    )
    prev = PlannerOutput(
        task="t",
        subgoal="g",
        target_object="drawer",
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
    bad = PlannerOutput(
        task="place",
        subgoal="in the workspace",
        target_object="workspace",
        skill="move_to",
        success_check="noop",
        fallback="none",
    )

    def fake_try(**_kwargs):
        return bad, {
            "llm_replanner_called": True,
            "replanner_parse_ok": True,
            "raw_generation_head": '{"target_object":"workspace"}',
            "repair_actions": [],
        }

    with patch(
        "embodied_scene_agent.replanner.hybrid.try_llm_replan_planner_output",
        fake_try,
    ):
        h = HybridReplanner(enable_llm=True)
        plan, audit = h.replan_with_audit("put the red block in the drawer", [], mem, fail, prev)

    assert plan.target_object != "workspace"
    assert audit.llm_replanner_called is True
    assert audit.replanner_parse_ok is True
    assert audit.revised_plan_validated is True
    assert audit.revised_plan_accepted is False
    assert audit.acceptance_rejection_reason == "target_absent_from_scene_memory"
    assert audit.fallback_stage == "semantic_acceptance"


def test_hybrid_rejects_drawer_goal_target_mismatch() -> None:
    mem = SceneMemoryBuilder.from_teacher_payload(
        {
            "objects": [
                {"id": "drawer", "name": "drawer", "position": [0, 0, 0], "state_tags": ["closed"]},
                {"id": "red_block", "name": "block", "position": [0, 0, 0], "state_tags": ["on_table"]},
                {"id": "table", "name": "table", "position": [0, 0, 0], "state_tags": ["static"]},
            ]
        }
    )
    prev = PlannerOutput(
        task="t",
        subgoal="g",
        target_object="drawer",
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
    bad = PlannerOutput(
        task="move_to",
        subgoal="place_blue_block_in_drawer",
        target_object="table",
        skill="place",
        success_check="placement completed for table",
        fallback="none",
    )

    def fake_try(**_kwargs):
        return bad, {
            "llm_replanner_called": True,
            "replanner_parse_ok": True,
            "raw_generation_head": '{"target_object":"table"}',
            "repair_actions": [],
        }

    with patch(
        "embodied_scene_agent.replanner.hybrid.try_llm_replan_planner_output",
        fake_try,
    ):
        h = HybridReplanner(enable_llm=True)
        plan, audit = h.replan_with_audit("put the red block in the drawer", [], mem, fail, prev)

    assert plan.target_object != "table" or plan.skill != "place"
    assert audit.revised_plan_validated is True
    assert audit.revised_plan_accepted is False
    assert audit.acceptance_rejection_reason == "drawer_goal_target_mismatch"
    assert audit.fallback_reason == "drawer_goal_target_mismatch"


class _AlwaysUnknownPlanner(BasePlanner):
    def plan(self, inp: PlannerInput) -> PlannerOutput:
        return PlannerOutput(
            task="unknown",
            subgoal="force unknown for fallback",
            target_object="drawer",
            skill="diagnostic_verifier_unknown",
            success_check="noop",
            fallback="none",
            reasoning=f"history={len(inp.history)}",
            confidence=0.1,
        )


class _StuckDrawerEnv(MockEmbodiedEnv):
    def apply_skill(self, skill: str, target_object_id: str) -> bool:
        if skill == "open" and target_object_id == "drawer":
            self._step += 1
            # Keep drawer closed to emulate repeated no-effect open retries.
            return True
        return super().apply_skill(skill, target_object_id)


def test_hybrid_stops_repeated_no_effect_fallback_early() -> None:
    env = _StuckDrawerEnv()

    bad = PlannerOutput(
        task="place",
        subgoal="in workspace",
        target_object="workspace",
        skill="move_to",
        success_check="noop",
        fallback="none",
    )

    def fake_try(**_kwargs):
        return bad, {
            "llm_replanner_called": True,
            "replanner_parse_ok": True,
            "raw_generation_head": '{"target_object":"workspace"}',
            "repair_actions": [],
        }

    with patch(
        "embodied_scene_agent.replanner.hybrid.try_llm_replan_planner_output",
        fake_try,
    ):
        trace = run_v0_episode(
            "put the red block in the drawer",
            max_steps=10,
            env=env,
            verifier_mode="verifier_plus_replan",
            replanner_mode="hybrid",
            planner=_AlwaysUnknownPlanner(),
        )

    assert trace.success is False
    assert trace.final_message == "repeated_no_effect_fallback_exhausted"
    assert trace.replan_count <= 2
    last = trace.steps[-1]
    guard = last.get("repeated_no_effect_guard") or {}
    assert guard.get("triggered") is True
    assert guard.get("consecutive_no_effect_count") == 2
    audit = last.get("replan_audit") or {}
    assert audit.get("repeated_no_effect_detected") is True
    assert audit.get("repeated_no_effect_stop") is True
