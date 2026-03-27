"""CALVIN-grounded minimal closed loop: optional local factory → live or fixture → planner → action → verifier."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Callable, Literal

from embodied_scene_agent.envs.calvin import CalvinEnvAdapter
from embodied_scene_agent.envs.calvin_factory_load import resolve_calvin_env_factory_from_env
from embodied_scene_agent.planner.base import BasePlanner
from embodied_scene_agent.planner.schema import PlannerInput
from embodied_scene_agent.planner.rule_based import RuleBasedPlanner
from embodied_scene_agent.pipeline.v0_loop import EpisodeTrace, ReplannerMode, VerifierMode
from embodied_scene_agent.skills.base import SkillContext, SkillResult
from embodied_scene_agent.skills.executor import SkillExecutor
from embodied_scene_agent.utils.paths import repo_root
from embodied_scene_agent.replanner.hybrid import HybridReplanner
from embodied_scene_agent.replanner.rule_based import RuleBasedReplanner
from embodied_scene_agent.verifier.schema import VerificationResult, is_state_unchanged_failure
from embodied_scene_agent.verifier.state_diff import StateDiffVerifier

LiveActionStrategy = Literal["symbolic_fallback", "live_zero_action_smoke"]


def _default_fixture() -> Path:
    return repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json"


def run_calvin_minimal_episode(
    instruction: str,
    *,
    fixture_path: Path | None = None,
    initial_observation: dict[str, Any] | None = None,
    calvin_env: Any | None = None,
    try_local_factory: bool = False,
    live_action_strategy: LiveActionStrategy = "symbolic_fallback",
    max_steps: int = 12,
    robot_obs: Any | None = None,
    scene_obs: Any | None = None,
    live_action: Any | None = None,
    live_action_fn: Callable[[Any, Any], Any] | None = None,
    experiment_id: str = "",
    verifier_mode: VerifierMode = "verifier_plus_replan",
    replanner_mode: ReplannerMode = "rule",
    planner: BasePlanner | None = None,
) -> EpisodeTrace:
    """
    Minimal episode with explicit **env / teacher / action** lineage (never silent symbolic/live mix-up).

    **Resolution order**: explicit ``calvin_env`` → else if ``try_local_factory`` then ``ESA_CALVIN_ENV_FACTORY``
    → else fixture. On live failure, falls back to fixture and sets ``loop_fallback_reason``.

    **live_action_strategy**:
    - ``symbolic_fallback``: planner uses **live** SceneMemory when reset succeeded, but skills are **symbolic**
      (no ``env.step`` in the loop).
    - ``live_zero_action_smoke``: each iteration calls ``CalvinEnvAdapter.step`` with zeros (or ``live_action_fn``);
      **interface smoke only**, not a manipulation success claim.

    **Not** official CALVIN benchmark. **No** scores.
    """
    prefer_live_step = live_action_strategy == "live_zero_action_smoke"

    trace = EpisodeTrace(
        instruction=instruction,
        success=False,
        final_message="horizon_or_verify_failure",
        trace_id=str(uuid.uuid4()),
        experiment_id=experiment_id,
        live_probe_status={},
        verifier_mode=verifier_mode,
        replanner_mode=replanner_mode,
    )

    loop_fallback_reason = ""
    live_probe: dict[str, Any] = {}
    resolved_env = calvin_env

    if resolved_env is None and try_local_factory:
        fn, fac_meta = resolve_calvin_env_factory_from_env()
        live_probe["factory_resolve"] = fac_meta
        if fn is None:
            loop_fallback_reason = f"factory_unavailable:{fac_meta.get('status', 'unknown')}"
        else:
            try:
                resolved_env = fn()
                live_probe["factory_instantiate"] = "returned_env"
            except Exception as e:  # noqa: BLE001
                loop_fallback_reason = f"factory_exception:{type(e).__name__}"
                live_probe["factory_instantiate_error"] = str(e)[:800]
                resolved_env = None
    elif resolved_env is not None:
        live_probe["factory_resolve"] = {"status": "explicit_calvin_env_argument"}

    env: CalvinEnvAdapter
    if resolved_env is not None:
        try:
            env = CalvinEnvAdapter(calvin_env=resolved_env)
            env.reset(instruction, robot_obs=robot_obs, scene_obs=scene_obs)
            trace.env_mode = "live_env"
            trace.teacher_source = "live_mapper"
            trace.live_reset_succeeded = True
            trace.action_mode = (
                "live_zero_action_smoke" if prefer_live_step else "live_observation_symbolic_fallback"
            )
        except Exception as e:  # noqa: BLE001
            loop_fallback_reason = f"live_adapter_reset_failed:{type(e).__name__}:{e}"[:800]
            live_probe["adapter_reset_error"] = loop_fallback_reason
            resolved_env = None

    if resolved_env is None:
        if initial_observation is not None:
            env = CalvinEnvAdapter(initial_observation=initial_observation)
            env.reset(instruction)
        else:
            path = fixture_path or _default_fixture()
            env = CalvinEnvAdapter(fixture_path=path)
            env.reset(instruction)
        trace.env_mode = "fixture"
        trace.teacher_source = "fixture_json"
        trace.action_mode = "fixture_symbolic"
        if loop_fallback_reason:
            trace.loop_fallback_reason = loop_fallback_reason
        if try_local_factory or calvin_env is not None:
            trace.final_message = "fixture_fallback"

    trace.live_probe_status = live_probe

    planner_impl: BasePlanner = planner if planner is not None else RuleBasedPlanner()
    executor = SkillExecutor()
    verifier = StateDiffVerifier()
    if replanner_mode == "hybrid":
        replanner: HybridReplanner | RuleBasedReplanner = HybridReplanner(enable_llm=True)
    else:
        replanner = RuleBasedReplanner()

    history: list[str] = []
    failure_log: list[str] = []

    for step_idx in range(max_steps):
        if env.task_success_symbolic():
            trace.success = True
            trace.final_message = "task_success"
            break

        mem_before = env.build_scene_memory()
        plan = planner_impl.plan(
            PlannerInput(
                instruction=instruction,
                scene_memory=mem_before,
                history=history,
                failure_log=list(failure_log),
            )
        )

        live_step_executed = False
        step_return_note = ""
        if prefer_live_step and trace.env_mode == "live_env":
            action = live_action
            if live_action_fn is not None:
                action = live_action_fn(plan, mem_before)
            obs_b, reward, done, sinfo = env.step(action)
            live_step_executed = True
            trace.live_step_attempted = True
            trace.whether_live_step_executed = True
            step_return_note = f"reward={reward!r},done={done!r},step_info_keys={sorted(sinfo.keys()) if isinstance(sinfo, dict) else type(sinfo).__name__}"
            skill_result = SkillResult(
                success=True,
                message="live_env.step invoked (smoke); not a task success claim",
                delta={
                    "live_step": True,
                    "step_return_note": step_return_note[:500],
                    "teacher_refreshed_after_step": True,
                },
            )
            executor_mode = "live_calvin_env_step"
        else:
            ctx = SkillContext(env=env, target_object_id=plan.target_object, planner_output=plan)
            sr = executor.run(ctx)
            if trace.env_mode == "live_env":
                executor_mode = "symbolic_calvin_teacher_on_live_reset"
                skill_result = SkillResult(
                    success=sr.success,
                    message=sr.message
                    + " | planner_grounded_on_live_observation_action_executed_symbolically",
                    delta={**sr.delta, "symbolic_fallback_while_live_reset": True},
                )
            else:
                executor_mode = "symbolic_calvin_teacher_via_CalvinEnvAdapter.apply_skill"
                skill_result = sr

        mem_after = env.build_scene_memory()
        ver = verifier.verify(mem_before, mem_after, plan)
        if verifier_mode == "none":
            ver = VerificationResult(success=True, details="verifier_disabled_e2_mode")

        step_log: dict[str, Any] = {
            "observation_id": f"calvin_min::{trace.trace_id or 'na'}::{step_idx}",
            "timestep": step_idx,
            "schema_version": "esa_episode_log/v1",
            "verifier_mode": verifier_mode,
            "replanner_mode": replanner_mode,
            "scene_memory_before": mem_before.to_json_dict(),
            "history": list(history),
            "failure_log": list(failure_log),
            "planner_input_summary": {
                "instruction": instruction,
                "history_len": len(history),
                "failure_log_len": len(failure_log),
            },
            "plan": plan.model_dump(mode="json"),
            "skill_result": skill_result.model_dump(mode="json"),
            "scene_memory_after_first": mem_after.to_json_dict(),
            "verification": ver.model_dump(mode="json"),
            "replan": None,
            "replan_audit": None,
            "executor_mode": executor_mode,
            "env_mode": trace.env_mode,
            "teacher_source": trace.teacher_source,
            "action_mode": trace.action_mode,
            "live_step_executed": live_step_executed,
            "loop_fallback_reason": trace.loop_fallback_reason or None,
        }
        trace.steps.append(step_log)

        if ver.success:
            history.append(plan.subgoal)
            failure_log.clear()
        else:
            failure_log.append(f"failed:{ver.failure_type}:{ver.details}")
            if is_state_unchanged_failure(ver.failure_type):
                if plan.skill == "grasp":
                    failure_log.append("hint:retry_grasp")
                if plan.skill == "open":
                    failure_log.append("hint:retry_open")

        if not ver.success and verifier_mode == "verifier_only":
            if env.task_success_symbolic():
                trace.success = True
                trace.final_message = "task_success_after_step"
                break
            continue

        if not ver.success and verifier_mode == "verifier_plus_replan":
            trace.replan_count += 1
            new_plan, r_audit = replanner.replan_with_audit(
                instruction, history, mem_after, ver, plan
            )
            step_log["replan"] = new_plan.model_dump(mode="json")
            step_log["replan_audit"] = r_audit.to_json_dict()
            ctx2 = SkillContext(env=env, target_object_id=new_plan.target_object, planner_output=new_plan)
            sr2 = executor.run(ctx2)
            if trace.env_mode == "live_env":
                skill_result2 = SkillResult(
                    success=sr2.success,
                    message=sr2.message + " | replan_symbolic",
                    delta={**sr2.delta, "replan": True},
                )
            else:
                skill_result2 = sr2
            mem_after2 = env.build_scene_memory()
            ver2 = verifier.verify(mem_after, mem_after2, new_plan)
            step_log["scene_memory_after_replan"] = mem_after2.to_json_dict()
            step_log["skill_result_replan"] = skill_result2.model_dump(mode="json")
            step_log["verification_replan"] = ver2.model_dump(mode="json")
            if ver2.success:
                history.append(new_plan.subgoal)
                failure_log.clear()
            else:
                failure_log.append(f"replan_failed:{ver2.failure_type}:{ver2.details}")

        if env.task_success_symbolic():
            trace.success = True
            trace.final_message = "task_success_after_step"
            break

    return trace
