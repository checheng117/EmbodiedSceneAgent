"""Verifier outputs."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FailureType(str, Enum):
    """High-level failure taxonomy for replanning and logging."""

    TARGET_NOT_FOUND = "target_not_found"
    WRONG_OBJECT_GROUNDED = "wrong_object_grounded"
    PRECONDITION_UNSATISFIED = "precondition_unsatisfied"
    STATE_UNCHANGED = "state_unchanged"
    """Skill executed but relevant object state did not change (blueprint category)."""
    ACTION_NO_EFFECT = "action_no_effect"
    """Legacy alias for logs / JSONL; prefer :attr:`STATE_UNCHANGED` in new verifier code."""
    BLOCKED_OR_COLLISION = "blocked_or_collision"
    OCCLUSION_OR_LOW_CONFIDENCE = "occlusion_or_low_confidence"
    """Low visibility / high uncertainty; blueprint synonym ``occlusion_or_uncertainty`` in docs."""
    UNKNOWN_FAILURE = "unknown_failure"


def is_state_unchanged_failure(ft: FailureType | None) -> bool:
    return ft in (FailureType.STATE_UNCHANGED, FailureType.ACTION_NO_EFFECT)


class VerificationResult(BaseModel):
    success: bool
    failure_type: FailureType | None = None
    should_replan: bool = False
    details: str = ""
    extras: dict[str, str] = Field(default_factory=dict)
