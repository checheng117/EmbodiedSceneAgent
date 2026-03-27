"""Central planner output contract: schema, validation, text/JSON parsing (blueprint A2)."""

from __future__ import annotations

import json
import re
from enum import Enum
from typing import Any

from pydantic import ValidationError

from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.skills.vocabulary import (
    is_known_planner_skill,
    normalize_planner_output_skill_inplace,
)

REQUIRED_PLANNER_KEYS = (
    "task",
    "subgoal",
    "target_object",
    "skill",
    "success_check",
    "fallback",
)


class PlannerParseErrorCode(str, Enum):
    MISSING_FIELD = "missing_field"
    EMPTY_VALUE = "empty_value"
    JSON_DECODE = "json_decode"
    VALIDATION = "validation"
    INVALID_SKILL = "invalid_skill"
    UNKNOWN_LINE = "unknown_line"
    NO_PLAN_BLOCK = "no_plan_block"


class PlannerParseError(ValueError):
    def __init__(self, code: PlannerParseErrorCode, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


def planner_output_json_schema() -> dict[str, Any]:
    """JSON Schema for the fixed planner fields (subset of :class:`PlannerOutput`)."""
    return {
        "type": "object",
        "additionalProperties": True,
        "required": list(REQUIRED_PLANNER_KEYS),
        "properties": {
            "task": {"type": "string"},
            "subgoal": {"type": "string"},
            "target_object": {"type": "string"},
            "skill": {"type": "string"},
            "success_check": {"type": "string"},
            "fallback": {"type": "string"},
            "reasoning": {"type": "string"},
            "confidence": {"type": "number"},
        },
    }


def validate_planner_output_dict(
    data: dict[str, Any],
    *,
    parse_audit: dict[str, Any] | None = None,
) -> PlannerOutput:
    """Strict check on required keys + Pydantic coercion for optional fields."""
    missing = [k for k in REQUIRED_PLANNER_KEYS if k not in data]
    if missing:
        raise PlannerParseError(
            PlannerParseErrorCode.MISSING_FIELD,
            f"missing keys: {missing}",
            details={"missing": missing},
        )
    for k in REQUIRED_PLANNER_KEYS:
        v = data.get(k)
        if v is None:
            raise PlannerParseError(
                PlannerParseErrorCode.EMPTY_VALUE,
                f"null field: {k}",
                details={"field": k},
            )
        if k != "fallback" and isinstance(v, str) and not str(v).strip():
            raise PlannerParseError(
                PlannerParseErrorCode.EMPTY_VALUE,
                f"empty field: {k}",
                details={"field": k},
            )
    alias_from, invalid = normalize_planner_output_skill_inplace(data)
    if parse_audit is not None:
        if alias_from:
            parse_audit["skill_alias_normalized_from"] = alias_from
    if invalid is not None or not is_known_planner_skill(str(data.get("skill", ""))):
        sk = str(data.get("skill", ""))
        raise PlannerParseError(
            PlannerParseErrorCode.INVALID_SKILL,
            f"skill not in canonical vocabulary after alias normalize: {sk!r}",
            details={"invalid_skill": sk, "alias_attempted_from": alias_from},
        )
    try:
        return PlannerOutput.model_validate(data)
    except ValidationError as e:
        raise PlannerParseError(
            PlannerParseErrorCode.VALIDATION,
            str(e),
            details={"errors": e.errors()},
        ) from e


def parse_planner_output_json(text: str) -> PlannerOutput:
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as e:
        raise PlannerParseError(
            PlannerParseErrorCode.JSON_DECODE,
            str(e),
            details={},
        ) from e
    if not isinstance(raw, dict):
        raise PlannerParseError(
            PlannerParseErrorCode.VALIDATION,
            "JSON root must be an object",
            details={},
        )
    return validate_planner_output_dict(raw)


_LINE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("task", re.compile(r"^\s*Task:\s*(.+?)\s*$", re.I)),
    ("subgoal", re.compile(r"^\s*Subgoal:\s*(.+?)\s*$", re.I)),
    ("target_object", re.compile(r"^\s*Target:\s*(.+?)\s*$", re.I)),
    ("skill", re.compile(r"^\s*Skill:\s*(.+?)\s*$", re.I)),
    ("success_check", re.compile(r"^\s*Success_Check:\s*(.+?)\s*$", re.I)),
    ("fallback", re.compile(r"^\s*Fallback:\s*(.+?)\s*$", re.I)),
]


def parse_planner_output_text(plan_text: str) -> PlannerOutput:
    """
    Parse the training/eval ``Plan:`` block (line-oriented keys).

    Stops at ``Observation:`` if present (recovery samples).
    """
    lines = plan_text.strip().splitlines()
    data: dict[str, str] = {}
    for line in lines:
        if line.strip().lower().startswith("observation:"):
            break
        for key, pat in _LINE_PATTERNS:
            m = pat.match(line)
            if m:
                data[key] = m.group(1).strip()
                break
    if not data:
        raise PlannerParseError(
            PlannerParseErrorCode.NO_PLAN_BLOCK,
            "no Task:/Subgoal:/... lines found",
            details={"head": plan_text[:200]},
        )
    return validate_planner_output_dict(data)
