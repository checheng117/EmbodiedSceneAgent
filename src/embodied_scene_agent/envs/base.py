"""Abstract embodied environment."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseEmbodiedEnv(ABC):
    """Minimal interface for adapters (CALVIN, RLBench, mock)."""

    @abstractmethod
    def reset(self, instruction: str, **kwargs: Any) -> dict[str, Any]:
        """Return initial observation bundle / teacher-state."""

    @abstractmethod
    def get_teacher_state(self) -> dict[str, Any]:
        """Expose simulator state for memory builder."""
