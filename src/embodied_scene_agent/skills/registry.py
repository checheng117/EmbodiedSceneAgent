"""Skill name -> implementation."""

from __future__ import annotations

from embodied_scene_agent.skills.base import BaseSkill
from embodied_scene_agent.skills.primitives import (
    CloseSkill,
    DiagnosticVerifierUnknownSkill,
    GraspSkill,
    MoveToSkill,
    OpenSkill,
    PlaceSkill,
    ReachSkill,
)
from embodied_scene_agent.skills.vocabulary import normalize_planner_skill


class SkillRegistry:
    """Registers built-in skills; swap/extend for benchmark-specific controllers."""

    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}
        self.register_defaults()

    def register_defaults(self) -> None:
        for s in (
            ReachSkill(),
            GraspSkill(),
            PlaceSkill(),
            OpenSkill(),
            CloseSkill(),
            MoveToSkill(),
            DiagnosticVerifierUnknownSkill(),
        ):
            self.register(s)

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill:
        resolved, _alias = normalize_planner_skill(name)
        if resolved not in self._skills:
            raise KeyError(f"unknown skill: {name}")
        return self._skills[resolved]
