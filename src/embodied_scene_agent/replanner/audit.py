"""Structured audit trail for replanning (blueprint: fail-aware local revision)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.verifier.schema import FailureType


class ReplannerAuditLog(BaseModel):
    """One replanning decision (rule-based or LLM fallback)."""

    original_subgoal: str = ""
    failure_type: str | None = None
    repair_strategy: str = ""
    revised_subgoal: str = ""
    whether_rule_based: bool = True
    notes: str = ""
    llm_replanner_called: bool = False
    replanner_parse_ok: bool | None = None
    revised_plan_validated: bool | None = None
    revised_plan_accepted: bool | None = None
    fallback_reason: str | None = None
    fallback_stage: str | None = None
    replanner_parse_error_kind: str | None = None
    skill_alias_normalized_from: str | None = None
    raw_generation_head: str | None = None
    parser_repair_actions: list[str] = Field(default_factory=list)
    acceptance_rejection_reason: str | None = None
    acceptance_rejection_details: list[str] = Field(default_factory=list)
    repeated_no_effect_detected: bool = False
    repeated_no_effect_signature: str | None = None
    repeated_no_effect_consecutive: int | None = None
    repeated_no_effect_threshold: int | None = None
    repeated_no_effect_stop: bool = False

    def to_json_dict(self) -> dict:
        return self.model_dump(mode="json")

    @staticmethod
    def for_llm_fallback(
        *,
        original_subgoal: str,
        failure_type: FailureType | None,
        revised: PlannerOutput,
        notes: str = "",
        skill_alias_normalized_from: str | None = None,
        raw_generation_head: str | None = None,
        parser_repair_actions: list[str] | None = None,
    ) -> ReplannerAuditLog:
        return ReplannerAuditLog(
            original_subgoal=original_subgoal,
            failure_type=failure_type.value if failure_type else None,
            repair_strategy="llm_planner_fallback",
            revised_subgoal=revised.subgoal,
            whether_rule_based=False,
            notes=notes,
            llm_replanner_called=True,
            replanner_parse_ok=True,
            revised_plan_validated=True,
            revised_plan_accepted=True,
            fallback_stage="validated",
            skill_alias_normalized_from=skill_alias_normalized_from,
            raw_generation_head=raw_generation_head,
            parser_repair_actions=list(parser_repair_actions or []),
        )
