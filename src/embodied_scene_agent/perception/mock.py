"""Pass-through builder for mock env teacher-state (strict schema)."""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.perception.base import BaseTeacherStateAdapter


class MockTeacherStateAdapter(BaseTeacherStateAdapter):
    """
    Expects ``state`` to already contain normalized ``objects`` / ``relations`` / ``frame_id``.

    TODO: add small helpers to convert flat legacy dicts if needed.
    """

    def to_scene_memory(self, instruction: str, state: dict[str, Any]) -> SceneMemory:
        _ = instruction
        if "objects" not in state:
            raise ValueError("MockTeacherStateAdapter: state must include 'objects' list")
        return SceneMemoryBuilder.from_teacher_payload(state, source="mock_teacher")
