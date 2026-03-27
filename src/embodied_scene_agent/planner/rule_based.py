"""Deterministic planner for v0 smoke and regression tests."""

from __future__ import annotations

from embodied_scene_agent.planner.base import BasePlanner
from embodied_scene_agent.planner.schema import PlannerInput, PlannerOutput


def _has_tag(mem_objects: dict, oid: str, tag: str) -> bool:
    if oid not in mem_objects:
        return False
    return tag in mem_objects[oid].state_tags


class RuleBasedPlanner(BasePlanner):
    """
    Minimal rules for mock long-horizon demo: open drawer -> grasp block -> place in drawer.

    TODO: replace with data-driven rules or LLM once CALVIN adapter is connected.
    """

    def plan(self, inp: PlannerInput) -> PlannerOutput:
        inst = inp.instruction.lower()
        mem = inp.scene_memory.objects
        flog = inp.failure_log

        drawer_open = _has_tag(mem, "drawer", "open")
        block_held = _has_tag(mem, "red_block", "held")

        # Failure hints from replanner / previous steps (stable substring contracts).
        if any("hint:open_drawer_before_place" in x for x in flog) and not drawer_open:
            return PlannerOutput(
                task="open_drawer",
                subgoal="Open the drawer (recovery).",
                target_object="drawer",
                skill="open",
                success_check="drawer has state tag 'open'",
                fallback="re-approach handle",
                reasoning="failure_log requested opening before place",
                confidence=0.85,
            )
        if any("hint:need_grasp_before_place" in x for x in flog) and not block_held:
            return PlannerOutput(
                task="grasp_block",
                subgoal="Grasp the red block (recovery).",
                target_object="red_block",
                skill="grasp",
                success_check="red_block has state tag 'held'",
                fallback="realign gripper",
                reasoning="failure_log requested grasp before place",
                confidence=0.85,
            )
        if any("hint:retry_grasp" in x for x in flog) and not block_held:
            return PlannerOutput(
                task="grasp_block",
                subgoal="Retry grasp on the red block.",
                target_object="red_block",
                skill="grasp",
                success_check="red_block has state tag 'held'",
                fallback="wiggle gripper",
                reasoning="failure_log requested grasp retry",
                confidence=0.7,
            )
        if any("hint:retry_open" in x for x in flog) and not drawer_open:
            return PlannerOutput(
                task="open_drawer",
                subgoal="Retry opening the drawer.",
                target_object="drawer",
                skill="open",
                success_check="drawer has state tag 'open'",
                fallback="try alternate approach vector",
                reasoning="failure_log requested open retry",
                confidence=0.7,
            )

        # Prefer opening first when the task mentions the drawer and it is still closed.
        if not drawer_open and ("drawer" in inst or "open" in inst):
            return PlannerOutput(
                task="open_drawer",
                subgoal="Open the drawer fully.",
                target_object="drawer",
                skill="open",
                success_check="drawer has state tag 'open'",
                fallback="reach handle from the right",
                reasoning="Drawer must be open before placing inside.",
                confidence=1.0,
            )

        if not block_held and (
            "pick" in inst or "grasp" in inst or "take" in inst or "block" in inst
        ):
            return PlannerOutput(
                task="grasp_block",
                subgoal="Grasp the red block.",
                target_object="red_block",
                skill="grasp",
                success_check="red_block has state tag 'held'",
                fallback="realign gripper above block",
                reasoning="Need the object before placing.",
                confidence=1.0,
            )

        if drawer_open and block_held and ("place" in inst or "put" in inst or "in" in inst):
            return PlannerOutput(
                task="place_in_drawer",
                subgoal="Place the red block into the drawer.",
                target_object="drawer",
                skill="place",
                success_check="red_block has state tag 'in_drawer'",
                fallback="retract and re-approach",
                reasoning="Final placement subgoal.",
                confidence=1.0,
            )

        # Default: nudge environment toward opening if still closed
        if not drawer_open:
            return PlannerOutput(
                task="open_drawer",
                subgoal="Open the drawer.",
                target_object="drawer",
                skill="open",
                success_check="drawer has state tag 'open'",
                fallback="try alternate approach vector",
                reasoning="Heuristic default when instruction is underspecified.",
                confidence=0.5,
            )

        wants_manip = any(
            k in inst for k in ("block", "red", "pick", "put", "place", "take", "grasp")
        )
        if not block_held and wants_manip:
            return PlannerOutput(
                task="grasp_block",
                subgoal="Pick up the red block.",
                target_object="red_block",
                skill="grasp",
                success_check="red_block has state tag 'held'",
                fallback="regrasp",
                reasoning="Heuristic default when manipulation is implied.",
                confidence=0.5,
            )

        # Instruction-only tasks such as "open the drawer" with no object references.
        if drawer_open and not block_held and not wants_manip:
            return PlannerOutput(
                task="noop",
                subgoal="No further object-centric steps.",
                target_object="table",
                skill="reach",
                success_check="idle",
                fallback="",
                reasoning="Instruction does not require block manipulation.",
                confidence=0.5,
            )

        return PlannerOutput(
            task="place_in_drawer",
            subgoal="Place object into drawer.",
            target_object="drawer",
            skill="place",
            success_check="red_block has state tag 'in_drawer'",
            fallback="replan",
            reasoning="Final placement assumed.",
            confidence=0.5,
        )
