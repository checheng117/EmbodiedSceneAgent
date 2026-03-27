"""Rule-based recovery with explicit failure handling (not only delegation)."""

from __future__ import annotations

from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.planner.rule_based import RuleBasedPlanner
from embodied_scene_agent.planner.schema import PlannerInput, PlannerOutput
from embodied_scene_agent.replanner.audit import ReplannerAuditLog
from embodied_scene_agent.replanner.base import BaseReplanner
from embodied_scene_agent.verifier.schema import FailureType, VerificationResult, is_state_unchanged_failure


def _has_tag(mem: SceneMemory, oid: str, tag: str) -> bool:
    if oid not in mem.objects:
        return False
    return tag in mem.objects[oid].state_tags


class RuleBasedReplanner(BaseReplanner):
    """
    Failure-aware recovery for the mock env (blueprint: rule-first local revision).

    Priority:
    1. **precondition_unsatisfied** on **place** → insert open-drawer or grasp prerequisite.
    2. **state_unchanged** → retry grasp/open with alternate fallback wording.
    3. Fallback: ``RuleBasedPlanner`` with enriched ``failure_log`` (LLM hook reserved in
       :mod:`embodied_scene_agent.replanner.hybrid`).
    """

    def __init__(self) -> None:
        self._planner = RuleBasedPlanner()

    def replan(
        self,
        instruction: str,
        history: list[str],
        scene_memory: SceneMemory,
        failure: VerificationResult,
        previous: PlannerOutput,
    ) -> PlannerOutput:
        plan, _audit = self.replan_with_audit(
            instruction, history, scene_memory, failure, previous
        )
        return plan

    def replan_with_audit(
        self,
        instruction: str,
        history: list[str],
        scene_memory: SceneMemory,
        failure: VerificationResult,
        previous: PlannerOutput,
    ) -> tuple[PlannerOutput, ReplannerAuditLog]:
        flog = [f"failed:{failure.failure_type}:{failure.details}"]
        drawer_open = _has_tag(scene_memory, "drawer", "open")
        block_held = _has_tag(scene_memory, "red_block", "held")
        ft = failure.failure_type

        if ft == FailureType.PRECONDITION_UNSATISFIED and previous.skill == "place":
            if not drawer_open:
                flog.append("hint:open_drawer_before_place")
                plan = PlannerOutput(
                    task="open_drawer_recovery",
                    subgoal="Open the drawer before placing.",
                    target_object="drawer",
                    skill="open",
                    success_check="drawer has state tag 'open'",
                    fallback="re-approach handle",
                    reasoning="Replanner: drawer closed when place was attempted.",
                    confidence=0.9,
                )
                audit = ReplannerAuditLog(
                    original_subgoal=previous.subgoal,
                    failure_type=ft.value if ft else None,
                    repair_strategy="insert_precondition_subtask_open_drawer",
                    revised_subgoal=plan.subgoal,
                    whether_rule_based=True,
                    notes=";".join(flog),
                )
                return plan, audit
            if not block_held:
                flog.append("hint:need_grasp_before_place")
                plan = PlannerOutput(
                    task="grasp_block_recovery",
                    subgoal="Grasp the red block before placing.",
                    target_object="red_block",
                    skill="grasp",
                    success_check="red_block has state tag 'held'",
                    fallback="realign gripper",
                    reasoning="Replanner: block not held when place was attempted.",
                    confidence=0.9,
                )
                audit = ReplannerAuditLog(
                    original_subgoal=previous.subgoal,
                    failure_type=ft.value if ft else None,
                    repair_strategy="insert_precondition_subtask_grasp",
                    revised_subgoal=plan.subgoal,
                    whether_rule_based=True,
                    notes=";".join(flog),
                )
                return plan, audit

        if is_state_unchanged_failure(ft):
            if previous.skill == "grasp":
                flog.append("hint:retry_grasp")
                plan = PlannerOutput(
                    task="grasp_block_retry",
                    subgoal="Retry grasp on the red block.",
                    target_object="red_block",
                    skill="grasp",
                    success_check="red_block has state tag 'held'",
                    fallback="wiggle gripper",
                    reasoning="Replanner: grasp had no effect; retry once.",
                    confidence=0.6,
                )
                audit = ReplannerAuditLog(
                    original_subgoal=previous.subgoal,
                    failure_type=ft.value if ft else None,
                    repair_strategy="retry_same_skill_alternate_fallback",
                    revised_subgoal=plan.subgoal,
                    whether_rule_based=True,
                    notes=";".join(flog),
                )
                return plan, audit
            if previous.skill == "open":
                flog.append("hint:retry_open")
                plan = PlannerOutput(
                    task="open_drawer_retry",
                    subgoal="Retry opening the drawer.",
                    target_object="drawer",
                    skill="open",
                    success_check="drawer has state tag 'open'",
                    fallback="try alternate approach vector",
                    reasoning="Replanner: open had no effect; retry once.",
                    confidence=0.6,
                )
                audit = ReplannerAuditLog(
                    original_subgoal=previous.subgoal,
                    failure_type=ft.value if ft else None,
                    repair_strategy="retry_same_skill_alternate_fallback",
                    revised_subgoal=plan.subgoal,
                    whether_rule_based=True,
                    notes=";".join(flog),
                )
                return plan, audit

        if ft == FailureType.WRONG_OBJECT_GROUNDED:
            plan = PlannerOutput(
                task="reselect_target_recovery",
                subgoal="Re-ground on the instructed target object from scene memory.",
                target_object=previous.target_object,
                skill="reach",
                success_check="end_effector aligned with target_object bbox",
                fallback="request new observation",
                reasoning="Replanner: wrong object grounded — reposition / reselect.",
                confidence=0.5,
            )
            audit = ReplannerAuditLog(
                original_subgoal=previous.subgoal,
                failure_type=ft.value if ft else None,
                repair_strategy="reselect_target_reach",
                revised_subgoal=plan.subgoal,
                whether_rule_based=True,
                notes=";".join(flog),
            )
            return plan, audit

        if ft == FailureType.OCCLUSION_OR_LOW_CONFIDENCE:
            plan = PlannerOutput(
                task="observe_reposition",
                subgoal="Improve visibility or reposition sensor before acting.",
                target_object=previous.target_object,
                skill="reach",
                success_check="target visibility above threshold in memory",
                fallback="re-scan scene",
                reasoning="Replanner: occlusion / uncertainty — observe first.",
                confidence=0.55,
            )
            audit = ReplannerAuditLog(
                original_subgoal=previous.subgoal,
                failure_type=ft.value if ft else None,
                repair_strategy="observe_or_reposition",
                revised_subgoal=plan.subgoal,
                whether_rule_based=True,
                notes=";".join(flog),
            )
            return plan, audit

        inp = PlannerInput(
            instruction=instruction,
            scene_memory=scene_memory,
            history=history + [f"replan_after:{previous.subgoal}"],
            failure_log=flog,
        )
        plan = self._planner.plan(inp)
        if plan.skill == previous.skill and plan.target_object == previous.target_object:
            plan = PlannerOutput(
                task=plan.task + "_retry",
                subgoal=plan.subgoal + " (retry variant)",
                target_object=plan.target_object,
                skill=plan.skill,
                success_check=plan.success_check,
                fallback="try alternate approach",
                reasoning="shallow de-dup",
                confidence=0.3,
            )
        audit = ReplannerAuditLog(
            original_subgoal=previous.subgoal,
            failure_type=ft.value if ft else None,
            repair_strategy="delegate_rule_planner_with_failure_context",
            revised_subgoal=plan.subgoal,
            whether_rule_based=True,
            notes="rule_planner_fallback;" + ";".join(flog),
        )
        return plan, audit
