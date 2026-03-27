"""Abstract adapter: benchmark state -> SceneMemory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from embodied_scene_agent.memory.schema import SceneMemory


class BaseTeacherStateAdapter(ABC):
    """
    Convert simulator / benchmark teacher-state to `SceneMemory`.

    Subclasses implement CALVIN, RLBench, etc. v0 uses `MockTeacherStateAdapter`.
    """

    @abstractmethod
    def to_scene_memory(self, instruction: str, state: dict[str, Any]) -> SceneMemory:
        """Map raw state dict to object-centric memory for the given instruction context."""
