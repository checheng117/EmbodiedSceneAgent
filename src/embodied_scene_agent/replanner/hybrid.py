"""Hybrid replanner: specialized rules first; LLM for delegate / high-uncertainty failures."""

from __future__ import annotations

from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.replanner.audit import ReplannerAuditLog
from embodied_scene_agent.replanner.base import BaseReplanner
from embodied_scene_agent.replanner.llm_replan import try_llm_replan_planner_output
from embodied_scene_agent.replanner.rule_based import RuleBasedReplanner
from embodied_scene_agent.verifier.schema import FailureType, VerificationResult

_RULE_FIRST_STRATEGIES = (
    "insert_precondition_subtask_open_drawer",
    "insert_precondition_subtask_grasp",
    "retry_same_skill_alternate_fallback",
    "reselect_target_reach",
    "observe_or_reposition",
)


class HybridReplanner(BaseReplanner):
    """
    1) Run :class:`RuleBasedReplanner` (local revisions).
    2) If strategy is **not** a specialized rule prefix, attempt LLM JSON replan
       (validated by ``planner_output_contract``); on failure keep rule output.
    """

    def __init__(self, *, enable_llm: bool = True) -> None:
        self._rules = RuleBasedReplanner()
        self._enable_llm = enable_llm

    def replan(
        self,
        instruction: str,
        history: list[str],
        scene_memory: SceneMemory,
        failure: VerificationResult,
        previous: PlannerOutput,
    ) -> PlannerOutput:
        p, _ = self.replan_with_audit(
            instruction, history, scene_memory, failure, previous
        )
        return p

    def replan_with_audit(
        self,
        instruction: str,
        history: list[str],
        scene_memory: SceneMemory,
        failure: VerificationResult,
        previous: PlannerOutput,
    ) -> tuple[PlannerOutput, ReplannerAuditLog]:
        r_plan, r_audit = self._rules.replan_with_audit(
            instruction, history, scene_memory, failure, previous
        )
        if not self._enable_llm:
            return r_plan, r_audit

        if r_audit.repair_strategy.startswith(_RULE_FIRST_STRATEGIES):
            return r_plan, r_audit

        if failure.failure_type not in (
            FailureType.UNKNOWN_FAILURE,
            FailureType.TARGET_NOT_FOUND,
            FailureType.WRONG_OBJECT_GROUNDED,
            FailureType.OCCLUSION_OR_LOW_CONFIDENCE,
        ) and not r_audit.repair_strategy.startswith("delegate_rule_planner"):
            return r_plan, r_audit

        loose, lm = try_llm_replan_planner_output(
            instruction=instruction,
            history=history,
            scene_memory=scene_memory,
            failure=failure,
            previous=previous,
        )
        if loose is not None:
            audit = ReplannerAuditLog.for_llm_fallback(
                original_subgoal=previous.subgoal,
                failure_type=failure.failure_type,
                revised=loose,
                notes="hybrid_after_rules;" + r_audit.repair_strategy,
                skill_alias_normalized_from=lm.get("skill_alias_normalized_from"),
            )
            return loose, audit

        merged = r_audit.model_copy(
            update={
                "llm_replanner_called": True,
                "replanner_parse_ok": lm.get("replanner_parse_ok"),
                "revised_plan_validated": False,
                "fallback_reason": lm.get("fallback_reason"),
                "fallback_stage": lm.get("fallback_stage"),
                "replanner_parse_error_kind": lm.get("replanner_parse_error_kind"),
                "notes": r_audit.notes + ";llm_failed_fallback_to_rules",
            }
        )
        return r_plan, merged
