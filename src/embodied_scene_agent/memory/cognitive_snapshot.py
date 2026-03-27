"""Unified cognitive frame: instruction + scene memory + planner context (blueprint v2).

Distinguishes **teacher_state**-derived memory vs **predicted** memory (placeholder until perception is learned).
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from embodied_scene_agent.memory.schema import RelationEdge, SceneMemory


class MemorySource(str, Enum):
    """Provenance of object-centric graph fed to the planner."""

    TEACHER_STATE = "teacher_state_memory"
    PREDICTED = "predicted_memory"
    HYBRID = "hybrid_teacher_plus_predicted"


class PredictedMemoryPlaceholder(BaseModel):
    """Explicit placeholder when predicted memory is not yet available."""

    status: str = "not_implemented"
    message: str = "GT teacher-state bootstrap only; predicted memory TBD per blueprint E3."

    def to_json_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class CognitiveEpisodeFrame(BaseModel):
    """
    Single timestep envelope aligned with ``docs/scene_memory_contract_v2.md``.

    - ``scene_memory`` holds the canonical :class:`SceneMemory` graph (objects + relations).
    - ``instruction`` duplicates task language at this frame (also on trace root).
    - ``history`` / ``failure_log`` are planner-facing strings (same as :class:`PlannerInput`).
    - ``planner_output`` is optional when recording observation-only frames.
    """

    observation_id: str = ""
    timestep: int = 0
    instruction: str = ""
    memory_source: MemorySource = MemorySource.TEACHER_STATE
    scene_memory: SceneMemory
    relations_tuple_view: list[tuple[str, str, str]] = Field(default_factory=list)
    history: list[str] = Field(default_factory=list)
    failure_log: list[str] = Field(default_factory=list)
    planner_output: Any | None = None
    predicted_memory_placeholder: PredictedMemoryPlaceholder | None = None

    @staticmethod
    def relations_as_tuples(relations: list[RelationEdge]) -> list[tuple[str, str, str]]:
        return [(e.subject_id, e.relation.value, e.object_id) for e in relations]

    @classmethod
    def from_scene_memory(
        cls,
        *,
        scene_memory: SceneMemory,
        instruction: str,
        observation_id: str = "",
        timestep: int = 0,
        history: list[str] | None = None,
        failure_log: list[str] | None = None,
        planner_output: Any | None = None,
        memory_source: MemorySource = MemorySource.TEACHER_STATE,
    ) -> CognitiveEpisodeFrame:
        return cls(
            observation_id=observation_id,
            timestep=timestep,
            instruction=instruction,
            memory_source=memory_source,
            scene_memory=scene_memory,
            relations_tuple_view=cls.relations_as_tuples(scene_memory.relations),
            history=list(history or []),
            failure_log=list(failure_log or []),
            planner_output=planner_output,
            predicted_memory_placeholder=PredictedMemoryPlaceholder()
            if memory_source == MemorySource.PREDICTED
            else None,
        )

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "timestep": self.timestep,
            "instruction": self.instruction,
            "memory_source": self.memory_source.value,
            "scene_memory": self.scene_memory.to_json_dict(),
            "relations": self.relations_tuple_view,
            "history": self.history,
            "failure_log": self.failure_log,
            "planner_output": self.planner_output.model_dump(mode="json") if self.planner_output else None,
            "predicted_memory": self.predicted_memory_placeholder.to_json_dict()
            if self.predicted_memory_placeholder
            else None,
        }
