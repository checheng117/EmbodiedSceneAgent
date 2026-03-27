"""Minimal closed-loop rollout for v0 (mock env)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from embodied_scene_agent.envs.mock import MockEmbodiedEnv
from embodied_scene_agent.perception.mock import MockTeacherStateAdapter
from embodied_scene_agent.planner.base import BasePlanner
from embodied_scene_agent.planner.schema import PlannerInput
from embodied_scene_agent.planner.rule_based import RuleBasedPlanner
from embodied_scene_agent.replanner.hybrid import HybridReplanner
from embodied_scene_agent.replanner.rule_based import RuleBasedReplanner
from embodied_scene_agent.skills.base import SkillContext
from embodied_scene_agent.skills.executor import SkillExecutor
from embodied_scene_agent.verifier.schema import VerificationResult, is_state_unchanged_failure
from embodied_scene_agent.verifier.state_diff import StateDiffVerifier

VerifierMode = Literal["none", "verifier_only", "verifier_plus_replan"]
ReplannerMode = Literal["rule", "hybrid"]


@dataclass
class EpisodeTrace:
    """Structured episode log for evaluation / visualization."""

    instruction: str
    success: bool
    steps: list[dict[str, Any]] = field(default_factory=list)
    replan_count: int = 0
    final_message: str = ""
    env_mode: str = ""
    teacher_source: str = ""
    action_mode: str = ""
    whether_live_step_executed: bool = False
    trace_id: str = ""
    experiment_id: str = ""
    live_probe_status: dict[str, Any] = field(default_factory=dict)
    live_reset_succeeded: bool = False
    live_step_attempted: bool = False
    loop_fallback_reason: str = ""
    verifier_mode: str = ""
    replanner_mode: str = ""


def run_v0_episode(
    instruction: str,
    *,
    max_steps: int = 12,
    env: MockEmbodiedEnv | None = None,
    forced_grasp_failures: int = 0,
    verifier_mode: VerifierMode = "verifier_plus_replan",
    replanner_mode: ReplannerMode = "rule",
    experiment_id: str = "",
    planner: BasePlanner | None = None,
) -> EpisodeTrace:
    """
    Run observation → memory → plan → execute → verify → (replan) loop until success or horizon.

    **verifier_mode**:
    - ``none``: verification always passes (ablation: no failure detection).
    - ``verifier_only``: on failure, **no** replan / second skill.
    - ``verifier_plus_replan``: full loop.

    **replanner_mode**: ``rule`` | ``hybrid`` (LLM JSON replan when rules delegate / uncertain).
    """
    if env is None:
        env = MockEmbodiedEnv(default_forced_grasp_failures=forced_grasp_failures)
    adapter = MockTeacherStateAdapter()
    planner_impl: BasePlanner = planner if planner is not None else RuleBasedPlanner()
    executor = SkillExecutor()
    verifier = StateDiffVerifier()
    if replanner_mode == "hybrid":
        replanner: HybridReplanner | RuleBasedReplanner = HybridReplanner(enable_llm=True)
    else:
        replanner = RuleBasedReplanner()

    env.reset(instruction)
    history: list[str] = []
    failure_log: list[str] = []
    trace = EpisodeTrace(
        instruction=instruction,
        success=False,
        verifier_mode=verifier_mode,
        replanner_mode=replanner_mode,
        experiment_id=experiment_id,
    )

    for step_idx in range(max_steps):
        if env.task_success():
            trace.success = True
            trace.final_message = "task_success"
            break

        mem_before = adapter.to_scene_memory(instruction, env.get_teacher_state())
        plan = planner_impl.plan(
            PlannerInput(
                instruction=instruction,
                scene_memory=mem_before,
                history=history,
                failure_log=list(failure_log),
            )
        )

        step_log: dict[str, Any] = {
            "observation_id": f"v0::{step_idx}",
            "timestep": step_idx,
            "schema_version": "esa_episode_log/v1",
            "verifier_mode": verifier_mode,
            "replanner_mode": replanner_mode,
            "scene_memory_before": mem_before.to_json_dict(),
            "plan": plan.model_dump(mode="json"),
            "replan": None,
            "replan_audit": None,
        }

        ctx = SkillContext(env=env, target_object_id=plan.target_object, planner_output=plan)
        skill_result = executor.run(ctx)
        mem_after = adapter.to_scene_memory(instruction, env.get_teacher_state())
        ver = verifier.verify(mem_before, mem_after, plan)
        if verifier_mode == "none":
            ver = VerificationResult(success=True, details="verifier_disabled_e2_mode")

        step_log["scene_memory_after_first"] = mem_after.to_json_dict()
        step_log["skill_result"] = skill_result.model_dump(mode="json")
        step_log["verification"] = ver.model_dump(mode="json")

        if ver.success:
            history.append(plan.subgoal)
            failure_log.clear()
            trace.steps.append(step_log)
            continue

        failure_log.append(f"failed:{ver.failure_type}:{ver.details}")
        if is_state_unchanged_failure(ver.failure_type):
            if plan.skill == "grasp":
                failure_log.append("hint:retry_grasp")
            if plan.skill == "open":
                failure_log.append("hint:retry_open")

        if verifier_mode == "verifier_only":
            trace.steps.append(step_log)
            continue

        trace.replan_count += 1
        new_plan, r_audit = replanner.replan_with_audit(
            instruction, history, mem_after, ver, plan
        )
        step_log["replan"] = new_plan.model_dump(mode="json")
        step_log["replan_audit"] = r_audit.to_json_dict()

        ctx2 = SkillContext(env=env, target_object_id=new_plan.target_object, planner_output=new_plan)
        skill_result2 = executor.run(ctx2)
        mem_after2 = adapter.to_scene_memory(instruction, env.get_teacher_state())
        ver2 = verifier.verify(mem_after, mem_after2, new_plan)

        step_log["scene_memory_after_replan"] = mem_after2.to_json_dict()
        step_log["skill_result_replan"] = skill_result2.model_dump(mode="json")
        step_log["verification_replan"] = ver2.model_dump(mode="json")

        if ver2.success:
            history.append(new_plan.subgoal)
            failure_log.clear()
        else:
            failure_log.append(f"replan_failed:{ver2.failure_type}:{ver2.details}")
            if is_state_unchanged_failure(ver2.failure_type):
                if new_plan.skill == "grasp":
                    failure_log.append("hint:retry_grasp")
                if new_plan.skill == "open":
                    failure_log.append("hint:retry_open")

        trace.steps.append(step_log)

        if env.task_success():
            trace.success = True
            trace.final_message = "task_success_after_replan_or_steps"
            break

    return trace
