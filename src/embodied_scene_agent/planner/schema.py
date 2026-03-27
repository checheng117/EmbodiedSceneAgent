"""Structured planner I/O (JSON-friendly)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from embodied_scene_agent.memory.schema import SceneMemory


class PlannerInput(BaseModel):
    """Inputs required to propose the next subgoal."""

    instruction: str
    scene_memory: SceneMemory
    history: list[str] = Field(default_factory=list)
    failure_log: list[str] = Field(default_factory=list)


class PlannerOutput(BaseModel):
    """Fixed schema for downstream logging, verifier, and executor routing."""

    task: str = "unknown_task"
    subgoal: str
    target_object: str
    skill: str
    success_check: str
    fallback: str = ""
    reasoning: str | None = None
    confidence: float | None = None
