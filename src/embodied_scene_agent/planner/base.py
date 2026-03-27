"""Planner protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from embodied_scene_agent.planner.schema import PlannerInput, PlannerOutput


class BasePlanner(ABC):
    """Produces structured `PlannerOutput` from `PlannerInput`."""

    @abstractmethod
    def plan(self, inp: PlannerInput) -> PlannerOutput:
        """Return the next subgoal plan."""
