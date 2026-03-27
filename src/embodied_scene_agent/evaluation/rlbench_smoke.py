"""RLBench bridge smoke: layered sim probes + fixture → SceneMemory → planner."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from embodied_scene_agent.envs.rlbench_adapter import (
    RLBenchAdapterConfig,
    build_cognitive_frame_from_observation_like,
    build_rlbench_stack_diagnosis,
    diagnose_rlbench_stack,
    load_observation_like_fixture,
    list_rlbench_task_class_names,
    observation_like_dict_to_scene_memory,
    rlbench_import_probe,
    summarize_rlbench_blocker,
    try_rlbench_env_launch_only,
    try_rlbench_reset_observation,
)
from embodied_scene_agent.pipeline.v0_loop import EpisodeTrace
from embodied_scene_agent.planner.rule_based import RuleBasedPlanner
from embodied_scene_agent.planner.schema import PlannerInput
from embodied_scene_agent.utils.paths import rel_repo_path, repo_root
from embodied_scene_agent.visualization.render_episode import write_episode

SmokeMode = Literal[
    "fixture_file",
    "sim_import_only",
    "sim_env_create",
    "sim_reset",
    "all",
]


def _write_demo(out: Path, payload: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "rlbench_smoke_summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _stage_result(
    *,
    mode: str,
    ok: bool,
    message: str,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "ok": ok,
        "message": (message or "")[:2000],
        "meta": meta or {},
    }


def run_layered_stages(
    *,
    root: Path,
    task: str,
    mode: SmokeMode,
    headless: bool = True,
) -> dict[str, Any]:
    """Run one or more smoke stages; never raises — failures are structured."""
    cfg = RLBenchAdapterConfig()
    stages: dict[str, Any] = {}
    diag = diagnose_rlbench_stack()
    stages["diagnostics"] = diag

    import_ok, import_msg = rlbench_import_probe()
    tasks_live, list_msg = list_rlbench_task_class_names()

    def run_import_stage() -> None:
        stages["sim_import_only"] = _stage_result(
            mode="sim_import_only",
            ok=import_ok,
            message=import_msg,
            meta={"task_listing_message": list_msg[:500], "task_class_names_sample": tasks_live[:12]},
        )

    env_ok: bool | None = None
    env_msg = ""
    env_probed = False
    reset_ok: bool | None = None
    reset_msg = ""
    reset_probed = False
    obs_dict: dict[str, Any] | None = None
    reset_meta: dict[str, Any] = {}

    if mode in ("sim_import_only", "sim_env_create", "sim_reset", "all"):
        run_import_stage()
    if mode in ("sim_env_create", "all"):
        if not import_ok:
            stages["sim_env_create"] = _stage_result(
                mode="sim_env_create",
                ok=False,
                message="skipped: rlbench import failed",
                meta={},
            )
            env_ok = False
        else:
            env_probed = True
            env_ok, env_msg, env_meta = try_rlbench_env_launch_only(headless=headless)
            stages["sim_env_create"] = _stage_result(
                mode="sim_env_create",
                ok=env_ok,
                message=env_msg,
                meta=env_meta,
            )
    if mode in ("sim_reset", "all"):
        if not import_ok:
            stages["sim_reset"] = _stage_result(
                mode="sim_reset",
                ok=False,
                message="skipped: rlbench import failed",
                meta={},
            )
            reset_ok = False
        else:
            reset_probed = True
            obs_dict, reset_msg, reset_meta = try_rlbench_reset_observation(task, headless=headless)
            reset_ok = obs_dict is not None
            stages["sim_reset"] = _stage_result(
                mode="sim_reset",
                ok=reset_ok,
                message=reset_msg,
                meta=reset_meta,
            )

    bridge_mode = "fixture_file"
    sim_msg = ""
    if obs_dict is not None:
        bridge_mode = "sim_reset"
        sim_msg = "live_observation"
    elif mode in ("sim_reset",) and import_ok:
        sim_msg = (stages.get("sim_reset") or {}).get("message", "") or "sim_reset_failed"

    if mode in ("fixture_file", "all"):
        fix = root / "tests" / "fixtures" / "rlbench_observation_like.json"
        fix_disp = rel_repo_path(root, fix)
        try:
            fobs = load_observation_like_fixture(fix)
            use_fixture_obs = mode == "fixture_file" or obs_dict is None
            if use_fixture_obs:
                obs_dict = fobs
                bridge_mode = "fixture_file"
                sim_msg = (
                    f"using_fixture:{fix_disp}; prior_sim_note={sim_msg!s}"[:1200]
                    if mode == "all"
                    else f"fixture_only:{fix_disp}"
                )
            stages["fixture_file"] = _stage_result(
                mode="fixture_file",
                ok=True,
                message=f"loaded {fix_disp}" + ("" if use_fixture_obs else " (sim obs kept)"),
                meta={"path": fix_disp, "used_for_memory": use_fixture_obs},
            )
        except Exception as e:  # noqa: BLE001
            stages["fixture_file"] = _stage_result(
                mode="fixture_file",
                ok=False,
                message=str(e),
                meta={},
            )
            if mode == "fixture_file":
                obs_dict = None

    memory_bridge_ok = False
    planner_smoke_ok = False
    task_name = task
    instruction = f"complete {task}"
    plan_dict: dict[str, Any] | None = None
    mem_ids: list[str] = []
    relations: list[tuple[str, str, str]] = []

    if obs_dict is not None:
        task_name = str(obs_dict.get("task_name", task))
        instruction = str(obs_dict.get("instruction", f"complete {task_name}"))
        try:
            mem = observation_like_dict_to_scene_memory(
                obs_dict, task_name=task_name, instruction=instruction
            )
            memory_bridge_ok = True
            mem_ids = list(mem.objects.keys())
            planner = RuleBasedPlanner()
            plan = planner.plan(
                PlannerInput(instruction=instruction, scene_memory=mem, history=[], failure_log=[])
            )
            plan_dict = plan.model_dump(mode="json")
            frame = build_cognitive_frame_from_observation_like(
                obs_dict,
                task_name=task_name,
                instruction=instruction,
                planner_output=plan,
                observation_id=f"rlbench::{bridge_mode}",
                timestep=0,
            )
            relations = list(frame.relations_tuple_view)
            planner_smoke_ok = True
        except Exception as e:  # noqa: BLE001
            stages["memory_planner"] = _stage_result(
                mode="memory_planner",
                ok=False,
                message=f"{type(e).__name__}: {e}",
                meta={},
            )

    if obs_dict is not None and "memory_planner" not in stages:
        stages["memory_planner"] = _stage_result(
            mode="memory_planner",
            ok=memory_bridge_ok and planner_smoke_ok,
            message="observation → SceneMemory → RuleBasedPlanner",
            meta={
                "memory_bridge_ok": memory_bridge_ok,
                "planner_smoke_ok": planner_smoke_ok,
                "memory_object_ids": mem_ids,
            },
        )

    episode_step: dict[str, Any] | None = None
    if obs_dict is not None and plan_dict is not None:
        mem = observation_like_dict_to_scene_memory(
            obs_dict, task_name=task_name, instruction=instruction
        )
        planner = RuleBasedPlanner()
        plan = planner.plan(
            PlannerInput(instruction=instruction, scene_memory=mem, history=[], failure_log=[])
        )
        episode_step = {
            "observation_id": f"rlbench::{bridge_mode}",
            "timestep": 0,
            "schema_version": "esa_episode_log/v1",
            "scene_memory_before": mem.to_json_dict(),
            "plan": plan.model_dump(mode="json"),
            "bridge_mode": bridge_mode,
            "skill_result": None,
            "verification": None,
            "replan": None,
            "replan_audit": None,
            "notes": "qualitative smoke: planner on RLBench-mapped memory; no low-level RLBench action loop in fixture mode",
        }

    sim_loc_ok = bool((diag.get("2_simulator_locate") or {}).get("ok"))
    pyrep_ok = bool((diag.get("1b_import_pyrep") or {}).get("ok"))
    deepest, blocker = summarize_rlbench_blocker(
        import_rlbench_ok=import_ok,
        import_pyrep_ok=pyrep_ok,
        sim_locate_ok=sim_loc_ok,
        env_attempted=env_probed,
        env_create_ok=env_ok,
        reset_attempted=reset_probed,
        reset_ok=reset_ok,
        import_rlbench_message=import_msg,
        import_pyrep_message=str((diag.get("1b_import_pyrep") or {}).get("message") or ""),
        env_message=env_msg,
        reset_message=reset_msg,
    )

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "smoke_mode_requested": mode,
        "task": task,
        "subset_tasks_documented": cfg.task_names,
        "import_ok": import_ok,
        "import_message": import_msg,
        "task_listing_message": list_msg,
        "task_class_names_sample": tasks_live[:24],
        "bridge_mode": bridge_mode,
        "sim_message": (sim_msg or "")[:1200],
        "deepest_reached_stage": deepest,
        "blocker_summary": blocker,
        "layer_status": {
            "import": import_ok,
            "simulator_locate": sim_loc_ok,
            "env_create": env_ok,
            "reset": reset_ok,
            "observation": bool(reset_ok) if reset_ok is not None else None,
            "memory_bridge": memory_bridge_ok,
            "planner_smoke": planner_smoke_ok,
        },
        "stages": stages,
        "task_name": task_name,
        "instruction": instruction,
        "planner_output": plan_dict,
        "memory_object_ids": mem_ids,
        "relations": relations,
        "honest_scope": (
            "Not an RLBench benchmark score; cognition-layer bridge + planner only unless sim_reset succeeded."
        ),
    }
    return payload, episode_step, bridge_mode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--task", type=str, default="ReachTarget")
    parser.add_argument(
        "--mode",
        type=str,
        default="all",
        choices=["fixture_file", "sim_import_only", "sim_env_create", "sim_reset", "all"],
    )
    parser.add_argument("--headless", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Write results/rlbench_stack_diagnosis.json and exit (no dev_smoke.json).",
    )
    parser.add_argument(
        "--diagnose-no-sim",
        action="store_true",
        help="With --diagnose: skip env_create/reset probes (import + paths only).",
    )
    args, _ = parser.parse_known_args()
    root = args.root or repo_root()

    if args.diagnose:
        out = root / "results" / "rlbench_stack_diagnosis.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        diag = build_rlbench_stack_diagnosis(
            headless=args.headless,
            probe_sim=not args.diagnose_no_sim,
            task_for_reset=args.task,
        )
        out.write_text(json.dumps(diag, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"wrote": str(out), "deepest_reached_stage": diag.get("deepest_reached_stage")}, indent=2))
        return

    payload, episode_step, bridge_mode = run_layered_stages(
        root=root,
        task=args.task,
        mode=args.mode,  # type: ignore[arg-type]
        headless=args.headless,
    )

    out_json = root / "results" / "rlbench_dev_smoke.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    log_path = root / "results" / "episode_logs" / "rlbench_layered_smoke.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if episode_step is not None:
        log_path.write_text(
            json.dumps({"steps": [episode_step], "success": False, "bridge_mode": bridge_mode}, indent=2),
            encoding="utf-8",
        )
    else:
        log_path.write_text(
            json.dumps(
                {
                    "steps": [],
                    "success": False,
                    "bridge_mode": bridge_mode,
                    "note": "no episode_step (fixture/sim observation unavailable)",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    demo_dir = root / "results" / "demos" / f"rlbench_{bridge_mode.replace('.', '_')}"
    demo_payload = {
        "planner": payload.get("planner_output"),
        "memory_object_ids": payload.get("memory_object_ids"),
        "layer_status": payload.get("layer_status"),
    }
    _write_demo(demo_dir, demo_payload)

    if episode_step is not None:
        instruction = str(payload.get("instruction", ""))
        trace = EpisodeTrace(
            instruction=instruction,
            success=False,
            final_message=f"rlbench_smoke_{bridge_mode}",
            env_mode="rlbench_bridge",
            teacher_source=bridge_mode,
        )
        trace.steps.append(episode_step)
        write_episode(demo_dir / "trace.json", trace)

    print(json.dumps({"wrote": str(out_json), "bridge_mode": bridge_mode, "layer_status": payload["layer_status"]}, indent=2))


if __name__ == "__main__":
    main()
