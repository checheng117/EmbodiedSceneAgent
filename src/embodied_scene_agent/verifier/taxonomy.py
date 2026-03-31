"""Canonical failure taxonomy metadata (single source for docs + reporting)."""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.verifier.schema import FailureType, is_state_unchanged_failure

# Keys are :class:`FailureType` values; used by ``docs/failure_taxonomy.md`` and report generator.
FAILURE_TAXONOMY_REGISTRY: dict[str, dict[str, str]] = {
    FailureType.TARGET_NOT_FOUND.value: {
        "condition": "Planned target object id absent from post-action scene memory.",
        "example": "Verifier expects ``red_block`` in ``after.objects`` but it is missing.",
        "replan": "Re-ground from instruction + memory; optional LLM planner (hybrid path).",
    },
    FailureType.WRONG_OBJECT_GROUNDED.value: {
        "condition": "Action applied to an object inconsistent with instruction or planner target.",
        "example": "Skill addresses ``blue_block`` when task names ``red_block``.",
        "replan": "Rule: ``reselect_target_reach`` — reposition / reselect correct instance.",
    },
    FailureType.PRECONDITION_UNSATISFIED.value: {
        "condition": "Necessary state tags or spatial preconditions not met before skill.",
        "example": "``place`` while drawer still ``closed`` or block not ``held``.",
        "replan": "Insert prerequisite subtask (open drawer, grasp) via rule replanner.",
    },
    FailureType.STATE_UNCHANGED.value: {
        "condition": "Skill ran but relevant object tags unchanged (same as legacy ``action_no_effect``).",
        "example": "``grasp`` on block; before/after tags identical.",
        "replan": "Retry with alternate fallback wording or approach vector.",
    },
    FailureType.ACTION_NO_EFFECT.value: {
        "condition": "Legacy wire value; treat as :attr:`FailureType.STATE_UNCHANGED` in new code.",
        "example": "Serialized logs from older rollouts.",
        "replan": "Same as ``state_unchanged``.",
    },
    FailureType.BLOCKED_OR_COLLISION.value: {
        "condition": "Physical blocking or collision prevents progress (reserved for sim hooks).",
        "example": "Gripper stuck; kinematic limit hit.",
        "replan": "Retreat / clear path / alternate skill ordering.",
    },
    FailureType.OCCLUSION_OR_LOW_CONFIDENCE.value: {
        "condition": "Target has low visibility or confidence in memory.",
        "example": "``visibility < threshold`` on manipulated object.",
        "replan": "Observe or reposition sensor before acting.",
    },
    FailureType.UNKNOWN_FAILURE.value: {
        "condition": "Verifier cannot classify; unhandled skill or ambiguous diff.",
        "example": "New skill string without verifier branch.",
        "replan": "Hybrid LLM replanner if configured; else delegate to planner with failure_log.",
    },
}

# Episode-level refinement used by hybrid batch reporting. This does not replace the step-level
# verifier taxonomy above; it summarizes why an episode still failed after a schema-valid replan.
HYBRID_EPISODE_FAILURE_REGISTRY: dict[str, dict[str, str]] = {
    "schema_valid_but_semantically_bad_replan": {
        "condition": "Hybrid replanner emitted a schema-valid plan, but scene grounding or task semantics were inconsistent.",
        "example": "Validated replan targets `workspace` even though no such object exists in scene memory.",
        "replan": "Tighten target grounding / semantic checks before accepting the revised plan.",
    },
    "precondition_not_satisfied_after_replan": {
        "condition": "Replanned skill still failed due to unmet prerequisites after the recovery step.",
        "example": "Replan returns `place`, but the drawer is still closed or the block is not held.",
        "replan": "Insert prerequisite recovery subtasks before re-attempting the skill.",
    },
    "no_state_change_after_valid_replan": {
        "condition": "Replan ran, but the relevant scene state did not change.",
        "example": "Repeated `open` retries leave the drawer tags unchanged across the remaining horizon.",
        "replan": "Treat as an ineffective execution path, not a generic horizon bucket.",
    },
    "repeated_no_effect_fallback_exhausted": {
        "condition": "Rule fallback repeated the same action/target with consecutive no-effect verifier outcomes until guarded stop.",
        "example": "Repeated `open` on `drawer` keeps returning `state_unchanged`, then loop stops early by guard.",
        "replan": "Stop early with explicit exhaustion evidence instead of spending horizon on identical retries.",
    },
    "execution_not_effective": {
        "condition": "Executor reports failure or no useful effect even when the taxonomy cannot pin it to a cleaner tag.",
        "example": "Skill execution returns an explicit failure before state diffing yields a stronger class.",
        "replan": "Capture executor-side evidence and avoid collapsing directly to `unknown_failure`.",
    },
    "environment_or_horizon_limit": {
        "condition": "Episode reaches the horizon without a stronger semantic or execution-side explanation.",
        "example": "No decisive verifier evidence beyond repeated timeout-style failure at the episode boundary.",
        "replan": "Treat as residual environment/horizon pressure, not a semantic planner failure.",
    },
    "residual_unknown_failure": {
        "condition": "Remaining ambiguous failure after applying the refinement rules.",
        "example": "Verifier and executor evidence stay inconclusive even after a hybrid replan.",
        "replan": "Keep for audit follow-up; avoid overclaiming a more specific class.",
    },
}


def list_taxonomy_for_report() -> list[dict[str, str]]:
    rows = []
    for ft, meta in FAILURE_TAXONOMY_REGISTRY.items():
        rows.append({"failure_type": ft, **meta})
    return rows


def list_hybrid_episode_taxonomy_for_report() -> list[dict[str, str]]:
    rows = []
    for label, meta in HYBRID_EPISODE_FAILURE_REGISTRY.items():
        rows.append({"failure_label": label, **meta})
    return rows


def _scene_object_ids(step: dict[str, Any], key: str) -> set[str]:
    scene = step.get(key) or {}
    if not isinstance(scene, dict):
        return set()
    objects = scene.get("objects") or {}
    if isinstance(objects, dict):
        return set(objects.keys())
    return set()


def _normalized_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _semantic_replan_reasons(step: dict[str, Any]) -> list[str]:
    audit = step.get("replan_audit") or {}
    plan = step.get("replan") or {}
    if not isinstance(audit, dict) or not isinstance(plan, dict):
        return []
    if not audit.get("revised_plan_validated"):
        return []

    reasons: list[str] = []
    target = _normalized_str(plan.get("target_object"))
    task_text = " ".join(
        part for part in (_normalized_str(plan.get("task")), _normalized_str(plan.get("subgoal"))) if part
    ).lower()
    verification_replan = step.get("verification_replan") or {}
    failure_type = _normalized_str((verification_replan or {}).get("failure_type"))
    after_first_ids = _scene_object_ids(step, "scene_memory_after_first")

    if failure_type == FailureType.TARGET_NOT_FOUND.value:
        reasons.append("target_missing_after_valid_replan")
    if target and after_first_ids and target not in after_first_ids:
        reasons.append("target_absent_from_scene_memory")
    if any(tok in task_text for tok in ("drawer", "slider")) and target and target != "drawer":
        reasons.append("drawer_goal_target_mismatch")

    deduped: list[str] = []
    for reason in reasons:
        if reason not in deduped:
            deduped.append(reason)
    return deduped


def _terminal_failure_label(step: dict[str, Any] | None, final_message: str) -> str:
    if not isinstance(step, dict):
        if final_message == "repeated_no_effect_fallback_exhausted":
            return "repeated_no_effect_fallback_exhausted"
        return (
            "environment_or_horizon_limit"
            if final_message == "horizon_or_verify_failure"
            else "residual_unknown_failure"
        )
    guard = step.get("repeated_no_effect_guard") or {}
    if isinstance(guard, dict) and guard.get("triggered") is True:
        return "repeated_no_effect_fallback_exhausted"

    verification = step.get("verification_replan")
    source = "verification_replan"
    if not isinstance(verification, dict) or verification.get("success") is not False:
        verification = step.get("verification")
        source = "verification"
    if not isinstance(verification, dict):
        return (
            "environment_or_horizon_limit"
            if final_message == "horizon_or_verify_failure"
            else "residual_unknown_failure"
        )

    ft_raw = verification.get("failure_type")
    ft = FailureType(ft_raw) if ft_raw in FailureType._value2member_map_ else None
    if ft == FailureType.PRECONDITION_UNSATISFIED:
        return "precondition_not_satisfied_after_replan"
    if is_state_unchanged_failure(ft):
        return "no_state_change_after_valid_replan" if source == "verification_replan" else "execution_not_effective"
    if ft in (FailureType.TARGET_NOT_FOUND, FailureType.WRONG_OBJECT_GROUNDED):
        return "schema_valid_but_semantically_bad_replan"

    skill_result = step.get("skill_result_replan") or step.get("skill_result") or {}
    if isinstance(skill_result, dict) and skill_result.get("success") is False:
        return "execution_not_effective"
    if final_message == "repeated_no_effect_fallback_exhausted":
        return "repeated_no_effect_fallback_exhausted"
    if final_message == "horizon_or_verify_failure":
        return "environment_or_horizon_limit"
    return "residual_unknown_failure"


def classify_hybrid_episode_failure(steps: list[dict[str, Any]], *, final_message: str = "") -> dict[str, Any]:
    semantic_issue_step: dict[str, Any] | None = None
    semantic_reasons: list[str] = []
    terminal_step: dict[str, Any] | None = None

    for step in steps:
        reasons = _semantic_replan_reasons(step)
        if reasons and semantic_issue_step is None:
            semantic_issue_step = step
            semantic_reasons = reasons

        verification_replan = step.get("verification_replan")
        verification = step.get("verification")
        if isinstance(verification_replan, dict) and verification_replan.get("success") is False:
            terminal_step = step
        elif isinstance(verification, dict) and verification.get("success") is False:
            terminal_step = step

    terminal_label = _terminal_failure_label(terminal_step, final_message)
    primary_label = (
        "schema_valid_but_semantically_bad_replan" if semantic_issue_step is not None else terminal_label
    )
    terminal_ver = (terminal_step or {}).get("verification_replan") or (terminal_step or {}).get("verification") or {}

    return {
        "episode_failure_label": primary_label,
        "terminal_failure_label": terminal_label,
        "validated_replan_issue_label": (
            "schema_valid_but_semantically_bad_replan" if semantic_issue_step is not None else None
        ),
        "label_reasons": list(semantic_reasons),
        "semantic_issue_step_index": (semantic_issue_step or {}).get("timestep"),
        "terminal_step_index": (terminal_step or {}).get("timestep"),
        "terminal_failure_type": _normalized_str((terminal_ver or {}).get("failure_type")) or None,
        "terminal_failure_details": _normalized_str((terminal_ver or {}).get("details")) or None,
    }
