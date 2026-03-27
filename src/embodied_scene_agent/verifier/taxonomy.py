"""Canonical failure taxonomy metadata (single source for docs + reporting)."""

from __future__ import annotations

from embodied_scene_agent.verifier.schema import FailureType

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


def list_taxonomy_for_report() -> list[dict[str, str]]:
    rows = []
    for ft, meta in FAILURE_TAXONOMY_REGISTRY.items():
        rows.append({"failure_type": ft, **meta})
    return rows
