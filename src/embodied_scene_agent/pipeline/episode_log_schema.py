"""Unified episode step log schema (consumable by viz + reporting)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

ESA_EPISODE_LOG_SCHEMA_VERSION = "esa_episode_log/v1"


class EpisodeStepLog(BaseModel):
    """
    One control-cycle record: observe → plan → execute → verify → (replan).

    Field names follow ``docs/episode_log_schema.md``.
    """

    schema_version: str = Field(default=ESA_EPISODE_LOG_SCHEMA_VERSION)
    observation_id: str = ""
    timestep: int = 0
    scene_memory_before: dict[str, Any] = Field(default_factory=dict)
    planner_output: dict[str, Any] | None = None
    executor_receipt: dict[str, Any] = Field(default_factory=dict)
    scene_memory_after: dict[str, Any] = Field(default_factory=dict)
    verifier_decision: dict[str, Any] = Field(default_factory=dict)
    failure_type: str | None = None
    replanner_output: dict[str, Any] | None = None
    replanner_audit: dict[str, Any] | None = None
    scene_memory_after_replan: dict[str, Any] | None = None
    executor_receipt_replan: dict[str, Any] | None = None
    verifier_decision_replan: dict[str, Any] | None = None
    final_step_outcome: str = "in_progress"

    def to_json_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


def step_dict_to_episode_step_log(raw: dict[str, Any], *, timestep: int, observation_id: str) -> EpisodeStepLog:
    """Best-effort map from legacy v0_loop step dict to :class:`EpisodeStepLog`."""
    ver = raw.get("verification") or {}
    ft = ver.get("failure_type")
    replan = raw.get("replan")
    ver2 = raw.get("verification_replan")
    outcome = "success_primary" if ver.get("success") else "failure_or_replan"
    if ver2:
        if ver2.get("success"):
            outcome = "success_after_replan"
        elif not ver.get("success"):
            outcome = "failure_after_replan"
    return EpisodeStepLog(
        observation_id=observation_id,
        timestep=timestep,
        scene_memory_before=raw.get("scene_memory_before") or {},
        planner_output=raw.get("plan"),
        executor_receipt=raw.get("skill_result") or {},
        scene_memory_after=raw.get("scene_memory_after_first") or {},
        verifier_decision=ver,
        failure_type=str(ft) if ft is not None else None,
        replanner_output=replan,
        replanner_audit=raw.get("replan_audit"),
        scene_memory_after_replan=raw.get("scene_memory_after_replan"),
        executor_receipt_replan=raw.get("skill_result_replan"),
        verifier_decision_replan=ver2,
        final_step_outcome=outcome,
    )
