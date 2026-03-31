"""Hybrid replanner: specialized rules first; LLM for delegate / high-uncertainty failures."""

from __future__ import annotations

from typing import Any

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
_DRAWER_LIKE_TOKENS = ("drawer", "slider")


def _string_list(*values: Any) -> list[str]:
    out: list[str] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            for item in value:
                s = str(item or "").strip()
                if s:
                    out.append(s)
            continue
        s = str(value).strip()
        if s:
            out.append(s)
    return out


def _is_drawer_like_object(scene_memory: SceneMemory, object_id: str) -> bool:
    obj = scene_memory.objects.get(object_id)
    if obj is None:
        return False
    hay = " ".join(
        x.lower()
        for x in _string_list(
            object_id,
            obj.name,
            obj.display_name,
            obj.class_name,
            obj.category,
            obj.aliases,
        )
    )
    return any(tok in hay for tok in _DRAWER_LIKE_TOKENS)


def _plan_implies_drawer_like_target(plan: PlannerOutput) -> bool:
    if plan.skill in {"open", "close"}:
        return True
    hay = " ".join(
        x.lower() for x in _string_list(plan.task, plan.subgoal, plan.reasoning)
    )
    return any(tok in hay for tok in _DRAWER_LIKE_TOKENS)


def _reject_semantically_bad_revised_plan(
    scene_memory: SceneMemory,
    plan: PlannerOutput,
) -> tuple[str | None, list[str]]:
    details: list[str] = []
    if not plan.target_object.strip():
        details.append("target_object empty after schema validation")
        return "empty_critical_field", details
    if not plan.subgoal.strip() or not plan.skill.strip() or not plan.success_check.strip():
        details.append("subgoal/skill/success_check empty after schema validation")
        return "empty_critical_field", details

    if plan.target_object not in scene_memory.objects:
        details.append(
            f"target_object `{plan.target_object}` absent from current scene memory objects="
            f"{sorted(scene_memory.objects.keys())}"
        )
        return "target_absent_from_scene_memory", details

    if _plan_implies_drawer_like_target(plan) and not _is_drawer_like_object(scene_memory, plan.target_object):
        obj = scene_memory.objects.get(plan.target_object)
        details.append(
            f"drawer/slider-like plan text grounded to non-drawer target `{plan.target_object}` "
            f"(class={getattr(obj, 'class_name', '')!r}, category={getattr(obj, 'category', '')!r})"
        )
        return "drawer_goal_target_mismatch", details

    return None, []


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
            rejection_reason, rejection_details = _reject_semantically_bad_revised_plan(
                scene_memory, loose
            )
            if rejection_reason is not None:
                merged = r_audit.model_copy(
                    update={
                        "llm_replanner_called": True,
                        "replanner_parse_ok": True,
                        "revised_plan_validated": True,
                        "revised_plan_accepted": False,
                        "fallback_reason": rejection_reason,
                        "fallback_stage": "semantic_acceptance",
                        "acceptance_rejection_reason": rejection_reason,
                        "acceptance_rejection_details": list(rejection_details),
                        "skill_alias_normalized_from": lm.get("skill_alias_normalized_from"),
                        "raw_generation_head": lm.get("raw_generation_head"),
                        "parser_repair_actions": list(lm.get("repair_actions") or []),
                        "notes": r_audit.notes + ";llm_rejected_before_execution",
                    }
                )
                return r_plan, merged
            audit = ReplannerAuditLog.for_llm_fallback(
                original_subgoal=previous.subgoal,
                failure_type=failure.failure_type,
                revised=loose,
                notes="hybrid_after_rules;" + r_audit.repair_strategy,
                skill_alias_normalized_from=lm.get("skill_alias_normalized_from"),
                raw_generation_head=lm.get("raw_generation_head"),
                parser_repair_actions=lm.get("repair_actions") or [],
            )
            return loose, audit

        merged = r_audit.model_copy(
            update={
                "llm_replanner_called": True,
                "replanner_parse_ok": lm.get("replanner_parse_ok"),
                "revised_plan_validated": False,
                "revised_plan_accepted": False,
                "fallback_reason": lm.get("fallback_reason"),
                "fallback_stage": lm.get("fallback_stage"),
                "replanner_parse_error_kind": lm.get("replanner_parse_error_kind"),
                "raw_generation_head": lm.get("raw_generation_head"),
                "parser_repair_actions": list(lm.get("repair_actions") or []),
                "notes": r_audit.notes + ";llm_failed_fallback_to_rules",
            }
        )
        return r_plan, merged
