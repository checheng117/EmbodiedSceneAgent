"""Skill protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from embodied_scene_agent.planner.schema import PlannerOutput


class SkillContext(BaseModel):
    """Execution-time context for a skill."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    env: Any = Field(..., description="Opaque env handle (e.g. MockEmbodiedEnv).")
    target_object_id: str
    planner_output: PlannerOutput
    params: dict[str, Any] = Field(default_factory=dict)


class SkillResult(BaseModel):
    """Result of applying one skill."""

    success: bool
    message: str = ""
    delta: dict[str, Any] = Field(default_factory=dict)


class BaseSkill(ABC):
    """One named, parameterized manipulation primitive."""

    name: str = "base"

    @abstractmethod
    def execute(self, ctx: SkillContext) -> SkillResult:
        """Apply skill to environment."""
