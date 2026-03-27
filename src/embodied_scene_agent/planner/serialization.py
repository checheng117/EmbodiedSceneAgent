"""JSON helpers for planner outputs."""

from __future__ import annotations

import json
from typing import Any

from embodied_scene_agent.planner.schema import PlannerOutput


def planner_output_to_json(plan: PlannerOutput) -> str:
    """Serialize planner output to a stable JSON string."""
    return plan.model_dump_json(indent=2)


def parse_planner_output_json(text: str) -> PlannerOutput:
    """
    Parse and validate model JSON into `PlannerOutput`.

    Raises:
        ValueError: invalid JSON or schema mismatch.
    """
    data: Any = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("planner JSON must be an object")
    return PlannerOutput.model_validate(data)
