"""LLM-backed planner skeleton (Qwen2.5-VL via HF/TRL — not wired in v0)."""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.planner.base import BasePlanner
from embodied_scene_agent.planner.schema import PlannerInput, PlannerOutput
from embodied_scene_agent.planner.serialization import parse_planner_output_json


class LLMPlanner(BasePlanner):
    """
    Placeholder for Qwen2.5-VL 3B/7B structured generation.

    TODO:
    - Load processor/model from config
    - Build multimodal prompt (image optional + memory JSON + instruction)
    - Constrained JSON decoding or repair loop
    """

    def __init__(self, model_config: dict[str, Any] | None = None) -> None:
        self.model_config = model_config or {}

    def plan(self, inp: PlannerInput) -> PlannerOutput:
        raise NotImplementedError(
            "LLMPlanner.plan is not implemented in v0; use RuleBasedPlanner or implement training."
        )

    @staticmethod
    def from_model_json(text: str) -> PlannerOutput:
        """Helper for future JSON-only model outputs."""
        return parse_planner_output_json(text)
