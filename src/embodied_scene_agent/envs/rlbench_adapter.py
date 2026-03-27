"""
RLBench → SceneMemory bridge (blueprint: same cognition layer, swap adapter).

**Honest status**
- **Mapping + fixture path**: always available (``observation_like`` dict / JSON → ``SceneMemoryBuilder``).
- **Full sim**: requires CoppeliaSim + PyRep + ``rlbench`` (see ``docs/rlbench_install_log.md``).
"""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.memory.cognitive_snapshot import CognitiveEpisodeFrame, MemorySource
from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.planner.schema import PlannerOutput

RLBenchPhase = Literal["skeleton", "fixture_bridge", "sim_connected", "not_installed"]


@dataclass
class RLBenchAdapterConfig:
    """Documentary task subset (see ``docs/rlbench_task_subset.md``)."""

    task_names: list[str] = field(
        default_factory=lambda: [
            "ReachTarget",
            "OpenDrawer",
            "CloseDrawer",
            "PickUpCup",
        ]
    )
    phase: RLBenchPhase = "skeleton"


def rlbench_import_probe() -> tuple[bool, str]:
    try:
        import rlbench  # noqa: F401

        return True, "rlbench import ok"
    except Exception as e:  # noqa: BLE001
        return False, f"rlbench not available: {e!s}"


def pyrep_import_probe() -> tuple[bool, str]:
    try:
        import pyrep  # noqa: F401

        return True, "pyrep import ok"
    except Exception as e:  # noqa: BLE001
        return False, f"pyrep not available: {e!s}"


def _package_probe(name: str) -> dict[str, Any]:
    """importlib.metadata when installed; does not import the package."""
    try:
        ver = importlib.metadata.version(name)
        return {"present": True, "version": ver}
    except importlib.metadata.PackageNotFoundError:
        return {"present": False, "version": None}
    except Exception as e:  # noqa: BLE001
        return {"present": False, "version": None, "probe_error": str(e)[:200]}


def diagnose_rlbench_stack() -> dict[str, Any]:
    """
    Layered diagnostics (import → simulator paths → no side effects on sim).
    Used by smoke / ``docs/rlbench_install_log.md`` automation.
    """
    layers: dict[str, Any] = {}
    ok_rl, msg_rl = rlbench_import_probe()
    layers["1_import_rlbench"] = {"ok": bool(ok_rl), "message": msg_rl}
    ok_pr, msg_pr = pyrep_import_probe()
    layers["1b_import_pyrep"] = {"ok": bool(ok_pr), "message": msg_pr}

    croot = os.environ.get("COPPELIASIM_ROOT", "").strip()
    ld = os.environ.get("LD_LIBRARY_PATH", "")
    sim_path = Path(croot) if croot else None
    coppelia_hint = ""
    if sim_path and sim_path.is_dir():
        exe_guess = list(sim_path.glob("coppeliaSim*"))[:3]
        coppelia_hint = f"dir_ok;exe_candidates={[p.name for p in exe_guess]}"
    elif croot:
        coppelia_hint = "COPPELIASIM_ROOT set but path not a directory"
    else:
        coppelia_hint = "COPPELIASIM_ROOT unset"

    layers["2_simulator_locate"] = {
        "ok": bool(sim_path and sim_path.is_dir()),
        "COPPELIASIM_ROOT": croot[:500] if croot else "",
        "LD_LIBRARY_PATH_set": bool(ld),
        "LD_LIBRARY_PATH_head": ld[:240] if ld else "",
        "notes": coppelia_hint,
    }
    layers["3_env_construct"] = {"attempted": False, "ok": None, "message": "see sim_env_create smoke"}
    layers["4_task_reset"] = {"attempted": False, "ok": None, "message": "see sim_reset smoke"}
    layers["5_observation_capture"] = {"attempted": False, "ok": None, "message": "see sim_reset smoke"}
    layers["6_scene_memory_mapping"] = {
        "ok": True,
        "message": "observation_like_dict_to_scene_memory always available (fixture or live dict)",
    }
    return layers


def build_rlbench_stack_diagnosis(
    *,
    headless: bool = True,
    probe_sim: bool = True,
    task_for_reset: str = "ReachTarget",
) -> dict[str, Any]:
    """
    Structured, machine-local facts for ``results/rlbench_stack_diagnosis.json``.

    When ``probe_sim`` is True and ``rlbench`` imports, runs env_create + reset probes
    (may launch CoppeliaSim — can be slow / noisy).
    """
    layers = diagnose_rlbench_stack()
    ok_rl, msg_rl = rlbench_import_probe()
    ok_pr, msg_pr = pyrep_import_probe()

    env_probe: dict[str, Any] = {
        "attempted": False,
        "ok": None,
        "message": "",
        "meta": {},
    }
    reset_probe: dict[str, Any] = {
        "attempted": False,
        "ok": None,
        "message": "",
        "meta": {},
    }

    if probe_sim and ok_rl:
        env_probe["attempted"] = True
        e_ok, e_msg, e_meta = try_rlbench_env_launch_only(headless=headless)
        env_probe["ok"] = e_ok
        env_probe["message"] = e_msg
        env_probe["meta"] = e_meta
        if e_ok:
            reset_probe["attempted"] = True
            obs, r_msg, r_meta = try_rlbench_reset_observation(task_for_reset, headless=headless)
            reset_probe["ok"] = obs is not None
            reset_probe["message"] = r_msg
            reset_probe["meta"] = r_meta
        else:
            reset_probe["attempted"] = False
            reset_probe["ok"] = None
            reset_probe["message"] = "skipped: env_create failed"
    elif probe_sim and not ok_rl:
        env_probe["message"] = "skipped: rlbench import failed"
        reset_probe["message"] = "skipped: rlbench import failed"

    deepest, blocker = summarize_rlbench_blocker(
        import_rlbench_ok=ok_rl,
        import_pyrep_ok=ok_pr,
        sim_locate_ok=bool((layers.get("2_simulator_locate") or {}).get("ok")),
        env_attempted=bool(env_probe.get("attempted")),
        env_create_ok=env_probe.get("ok"),
        reset_attempted=bool(reset_probe.get("attempted")),
        reset_ok=reset_probe.get("ok"),
        import_rlbench_message=msg_rl,
        import_pyrep_message=msg_pr,
        env_message=str(env_probe.get("message") or ""),
        reset_message=str(reset_probe.get("message") or ""),
    )

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "conda_default_env": os.environ.get("CONDA_DEFAULT_ENV", ""),
        "conda_prefix": os.environ.get("CONDA_PREFIX", ""),
        "virtual_env": os.environ.get("VIRTUAL_ENV", ""),
        "pip_distribution_probe": {
            "rlbench": _package_probe("rlbench"),
            "pyrep": _package_probe("pyrep"),
        },
        "environment": {
            "COPPELIASIM_ROOT": os.environ.get("COPPELIASIM_ROOT", ""),
            "LD_LIBRARY_PATH_set": bool(os.environ.get("LD_LIBRARY_PATH", "").strip()),
            "LD_LIBRARY_PATH_head": (os.environ.get("LD_LIBRARY_PATH", "") or "")[:400],
        },
        "import_status": {
            "rlbench": {"ok": ok_rl, "message": msg_rl},
            "pyrep": {"ok": ok_pr, "message": msg_pr},
        },
        "layers": layers,
        "env_create_probe": env_probe,
        "reset_probe": reset_probe,
        "deepest_reached_stage": deepest,
        "blocker_summary": blocker,
    }


def summarize_rlbench_blocker(
    *,
    import_rlbench_ok: bool,
    import_pyrep_ok: bool,
    sim_locate_ok: bool,
    env_attempted: bool,
    env_create_ok: bool | None,
    reset_attempted: bool,
    reset_ok: bool | None,
    import_rlbench_message: str,
    import_pyrep_message: str,
    env_message: str,
    reset_message: str,
) -> tuple[str, str]:
    """
    Return (deepest_reached_stage, blocker_summary) for dashboards.

    Stages are ordered: import → simulator_locate → env_create → sim_reset.
    """
    if not import_rlbench_ok:
        return "import_fail", f"rlbench import blocked: {import_rlbench_message[:280]}"
    if not import_pyrep_ok:
        return "import_fail", f"pyrep import blocked: {import_pyrep_message[:280]}"
    if not sim_locate_ok:
        return (
            "simulator_locate_fail",
            "COPPELIASIM_ROOT missing or not a directory — PyRep/launch typically needs a real install tree.",
        )
    if not env_attempted:
        return (
            "simulator_locate_ok",
            "Imports and COPPELIASIM_ROOT path OK in this snapshot; env_create/reset not probed (use full diagnose).",
        )
    if env_create_ok is False:
        return "env_create_fail", (env_message or "Environment.launch failed")[:400]
    if env_create_ok is True and not reset_attempted:
        return "env_create_ok", (env_message or "launch OK; reset skipped")[:400]
    if env_create_ok is True and reset_ok is False:
        return "sim_reset_fail", (reset_message or "task.reset failed")[:400]
    if env_create_ok is True and reset_ok is True:
        return "sim_reset_ok", "live sim stack reached reset+observation capture (see rlbench_dev_smoke for full bridge)."
    return "import_ok", "indeterminate sim state; re-run diagnosis with probe_sim=true."


def list_rlbench_task_class_names() -> tuple[list[str], str]:
    """Best-effort discover ``rlbench.tasks.*``; falls back to config subset on error."""
    ok, msg = rlbench_import_probe()
    if not ok:
        return list(RLBenchAdapterConfig().task_names), msg
    try:
        import pkgutil

        import rlbench.tasks as tasks_pkg

        names: list[str] = []
        for m in pkgutil.iter_modules(tasks_pkg.__path__):
            if m.ispkg or m.name.startswith("_"):
                continue
            try:
                mod = importlib.import_module(f"rlbench.tasks.{m.name}")
            except Exception:  # noqa: BLE001
                continue
            for attr in dir(mod):
                if not attr[0].isupper():
                    continue
                obj = getattr(mod, attr, None)
                if isinstance(obj, type) and attr not in names:
                    names.append(attr)
        return sorted(set(names))[:80] or list(RLBenchAdapterConfig().task_names), "discovered from rlbench.tasks"
    except Exception as e:  # noqa: BLE001
        return list(RLBenchAdapterConfig().task_names), f"task listing failed: {e!s}"


def resolve_task_class(task_name: str) -> tuple[Any | None, str]:
    """Import ``rlbench.tasks.<snake>.<TaskName>``."""
    ok, msg = rlbench_import_probe()
    if not ok:
        return None, msg
    try:
        snake = "".join(["_" + c.lower() if c.isupper() else c for c in task_name]).lstrip("_")
        mod = importlib.import_module(f"rlbench.tasks.{snake}")
        cls = getattr(mod, task_name)
        return cls, "ok"
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def try_rlbench_env_launch_only(
    *,
    headless: bool = True,
) -> tuple[bool, str, dict[str, Any]]:
    """
    Import + construct :class:`rlbench.environment.Environment` + ``launch()`` + ``shutdown()``.
    Does **not** load a task or call ``reset()`` — isolates CoppeliaSim / PyRep wiring.
    """
    meta: dict[str, Any] = {"headless": headless}
    ok, msg = rlbench_import_probe()
    if not ok:
        return False, msg, meta
    env = None
    try:
        from rlbench.action_modes.action_mode import MoveArmThenGripper
        from rlbench.environment import Environment
        from rlbench.observation_config import ObservationConfig

        obs_config = ObservationConfig()
        obs_config.set_all_high_dim(False)
        obs_config.set_all_low_dim(True)
        env = Environment(
            action_mode=MoveArmThenGripper(),
            obs_config=obs_config,
            headless=headless,
        )
        env.launch()
        meta["phase"] = "env_launched"
        return True, "ok", meta
    except Exception as e:  # noqa: BLE001
        meta["exception"] = f"{type(e).__name__}: {e}"[:500]
        return False, meta["exception"], meta
    finally:
        if env is not None:
            try:
                env.shutdown()
            except Exception:  # noqa: BLE001
                pass


def numpy_observation_to_dict(obs: Any) -> dict[str, Any]:
    """Serialize RLBench ``Observation`` to JSON-friendly dict (minimal fields for memory)."""
    return {
        "gripper_open": float(obs.gripper_open) if obs.gripper_open is not None else 0.0,
        "gripper_pose": np.asarray(obs.gripper_pose).reshape(-1).tolist(),
        "task_low_dim_state": np.asarray(obs.task_low_dim_state).reshape(-1).tolist(),
        "misc": {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in (obs.misc or {}).items()},
    }


def observation_like_dict_to_scene_memory(
    d: dict[str, Any],
    *,
    task_name: str,
    instruction: str,
    frame_id: str = "rlbench_frame",
) -> SceneMemory:
    """
    Map RLBench-like low-dim snapshot → teacher payload → :class:`SceneMemory`.

    Heuristic objects:
    - ``gripper`` from ``gripper_pose`` (first 3 = position)
    - ``rlbench_target`` from first 3 of ``task_low_dim_state`` (Reach-style tasks)
    - ``workspace`` table anchor
    """
    gp = d.get("gripper_pose") or [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    gp = [float(x) for x in gp]
    pos_g = gp[:3]
    tls = d.get("task_low_dim_state") or [0.0, 0.0, 0.0]
    tls = [float(x) for x in tls]
    tgt = tls[:3] if len(tls) >= 3 else [0.3, 0.0, 0.8]
    grip_open = float(d.get("gripper_open", 0.0))
    gtags = ["open"] if grip_open > 0.5 else ["closed"]

    objects: list[dict[str, Any]] = [
        {
            "id": "workspace",
            "name": "workspace",
            "class_name": "table",
            "position": [0.0, 0.0, 0.0],
            "bbox": [-0.6, -0.6, 0.0, 0.6, 0.6, 0.02],
            "state_tags": ["static"],
            "metadata": {"rlbench_task": task_name},
        },
        {
            "id": "gripper",
            "name": "gripper",
            "class_name": "gripper",
            "position": pos_g,
            "bbox": [pos_g[0] - 0.02, pos_g[1] - 0.02, pos_g[2] - 0.02, pos_g[0] + 0.02, pos_g[1] + 0.02, pos_g[2] + 0.02],
            "state_tags": gtags,
            "metadata": {"source": "gripper_pose"},
        },
        {
            "id": "rlbench_target",
            "name": "task_target",
            "class_name": "target",
            "position": tgt,
            "bbox": [tgt[0] - 0.03, tgt[1] - 0.03, tgt[2] - 0.03, tgt[0] + 0.03, tgt[1] + 0.03, tgt[2] + 0.03],
            "state_tags": ["goal_region"],
            "metadata": {"from": "task_low_dim_state[:3]"},
        },
    ]
    rels = [
        {"subject_id": "gripper", "object_id": "rlbench_target", "relation": "near"},
        {"subject_id": "rlbench_target", "object_id": "workspace", "relation": "on"},
    ]
    payload = {
        "frame_id": frame_id,
        "objects": objects,
        "relations": rels,
        "source": "rlbench_observation_bridge",
        "metadata": {"instruction": instruction, "fixture_or_live": True, "misc": d.get("misc")},
    }
    return SceneMemoryBuilder.from_teacher_payload(payload, source="rlbench_observation_bridge")


def build_cognitive_frame_from_observation_like(
    d: dict[str, Any],
    *,
    task_name: str,
    instruction: str,
    planner_output: PlannerOutput | None = None,
    observation_id: str = "",
    timestep: int = 0,
) -> CognitiveEpisodeFrame:
    mem = observation_like_dict_to_scene_memory(d, task_name=task_name, instruction=instruction)
    return CognitiveEpisodeFrame.from_scene_memory(
        scene_memory=mem,
        instruction=instruction,
        observation_id=observation_id,
        timestep=timestep,
        planner_output=planner_output,
        memory_source=MemorySource.TEACHER_STATE,
    )


def build_scene_memory_from_rlbench_stub(
    *,
    instruction: str,
    task_name: str,
    obs_summary: dict[str, Any] | None = None,
) -> SceneMemory:
    """Backward-compatible stub → use observation_like path with empty low-dim."""
    d = {"task_low_dim_state": [0.3, 0.0, 0.8], "gripper_pose": [0.2, 0.0, 0.9, 0, 0, 0, 1], "gripper_open": 0.8}
    if obs_summary:
        d.update(obs_summary)
    return observation_like_dict_to_scene_memory(d, task_name=task_name, instruction=instruction)


def try_rlbench_reset_observation(
    task_name: str,
    *,
    headless: bool = True,
) -> tuple[dict[str, Any] | None, str, dict[str, Any]]:
    """
    If sim available: ``task.reset()`` → observation dict.
    Else: (None, error, meta).
    """
    meta: dict[str, Any] = {"task_name": task_name, "headless": headless}
    cls, err = resolve_task_class(task_name)
    if cls is None:
        return None, err, meta
    env = None
    try:
        from rlbench.action_modes.action_mode import MoveArmThenGripper
        from rlbench.environment import Environment
        from rlbench.observation_config import ObservationConfig

        obs_config = ObservationConfig()
        obs_config.set_all_high_dim(False)
        obs_config.set_all_low_dim(True)
        env = Environment(
            action_mode=MoveArmThenGripper(),
            obs_config=obs_config,
            headless=headless,
        )
        env.launch()
        task = env.get_task(cls)
        _desc, obs = task.reset()
        d = numpy_observation_to_dict(obs)
        d["task_name"] = task_name
        meta["phase"] = "sim_connected"
        return d, "ok", meta
    except Exception as e:  # noqa: BLE001
        meta["exception"] = f"{type(e).__name__}: {e}"[:500]
        return None, meta["exception"], meta
    finally:
        if env is not None:
            try:
                env.shutdown()
            except Exception:  # noqa: BLE001
                pass


def load_observation_like_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def scene_memory_to_relations_tuples(mem: SceneMemory) -> list[tuple[str, str, str]]:
    return [(e.subject_id, e.relation.value, e.object_id) for e in mem.relations]
