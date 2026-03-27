"""Verifier protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.verifier.schema import VerificationResult


class BaseVerifier(ABC):
    """Compares before/after states against the current subgoal."""

    @abstractmethod
    def verify(
        self,
        before: SceneMemory,
        after: SceneMemory,
        plan: PlannerOutput,
    ) -> VerificationResult:
        """Return success/failure and whether to replan."""
