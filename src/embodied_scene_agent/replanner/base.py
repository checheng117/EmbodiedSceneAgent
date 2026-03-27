"""Replanner protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.verifier.schema import VerificationResult


class BaseReplanner(ABC):
    """Revises the next plan given failure context."""

    @abstractmethod
    def replan(
        self,
        instruction: str,
        history: list[str],
        scene_memory: SceneMemory,
        failure: VerificationResult,
        previous: PlannerOutput,
    ) -> PlannerOutput:
        """Return a new structured plan."""
