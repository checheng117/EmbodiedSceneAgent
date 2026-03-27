"""Dispatch planner skill field to registered skills."""

from __future__ import annotations

from embodied_scene_agent.skills.base import SkillContext, SkillResult
from embodied_scene_agent.skills.registry import SkillRegistry
from embodied_scene_agent.skills.vocabulary import normalize_planner_skill


class SkillExecutor:
    """Runs one skill step given structured planner output."""

    def __init__(self, registry: SkillRegistry | None = None) -> None:
        self.registry = registry or SkillRegistry()

    def run(self, ctx: SkillContext) -> SkillResult:
        skill_name = ctx.planner_output.skill
        _canon, alias_from = normalize_planner_skill(skill_name)
        try:
            skill = self.registry.get(skill_name)
        except KeyError:
            return SkillResult(
                success=False,
                message=f"unknown_skill:{skill_name}",
                delta={"unknown_skill": skill_name},
            )
        result = skill.execute(ctx)
        if alias_from and isinstance(result.delta, dict):
            d = dict(result.delta)
            d["skill_alias_normalized_from"] = alias_from
            return result.model_copy(update={"delta": d})
        return result
