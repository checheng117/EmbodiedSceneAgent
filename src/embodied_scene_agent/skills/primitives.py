"""Built-in mock-friendly skills."""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.skills.base import BaseSkill, SkillContext, SkillResult


class ReachSkill(BaseSkill):
    name = "reach"

    def execute(self, ctx: SkillContext) -> SkillResult:
        env: Any = ctx.env
        ok = env.apply_skill(self.name, ctx.target_object_id)
        return SkillResult(success=ok, message="reach", delta={"skill": self.name})


class GraspSkill(BaseSkill):
    name = "grasp"

    def execute(self, ctx: SkillContext) -> SkillResult:
        env: Any = ctx.env
        ok = env.apply_skill(self.name, ctx.target_object_id)
        return SkillResult(success=ok, message="grasp", delta={"skill": self.name})


class PlaceSkill(BaseSkill):
    name = "place"

    def execute(self, ctx: SkillContext) -> SkillResult:
        env: Any = ctx.env
        ok = env.apply_skill(self.name, ctx.target_object_id)
        return SkillResult(success=ok, message="place", delta={"skill": self.name})


class OpenSkill(BaseSkill):
    name = "open"

    def execute(self, ctx: SkillContext) -> SkillResult:
        env: Any = ctx.env
        ok = env.apply_skill(self.name, ctx.target_object_id)
        return SkillResult(success=ok, message="open", delta={"skill": self.name})


class CloseSkill(BaseSkill):
    name = "close"

    def execute(self, ctx: SkillContext) -> SkillResult:
        env: Any = ctx.env
        ok = env.apply_skill(self.name, ctx.target_object_id)
        return SkillResult(success=ok, message="close", delta={"skill": self.name})


class MoveToSkill(BaseSkill):
    name = "move_to"

    def execute(self, ctx: SkillContext) -> SkillResult:
        env: Any = ctx.env
        ok = env.apply_skill(self.name, ctx.target_object_id)
        return SkillResult(success=ok, message="move_to", delta={"skill": self.name})


class DiagnosticVerifierUnknownSkill(BaseSkill):
    """Smoke / hybrid tests: registered skill that :class:`StateDiffVerifier` treats as unknown."""

    name = "diagnostic_verifier_unknown"

    def execute(self, ctx: SkillContext) -> SkillResult:
        return SkillResult(
            success=False,
            message="diagnostic no-op for verifier UNKNOWN path",
            delta={"skill": self.name},
        )
