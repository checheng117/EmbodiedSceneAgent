"""
Optional live CALVIN probe: import / factory / reset / optional step smoke — never a benchmark run.

See ``docs/calvin_live_validation_plan.md`` and ``docs/calvin_env_factory_usage.md``.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from embodied_scene_agent.envs.calvin_live_summary import (
    format_live_summary_markdown,
    summarize_live_calvin_obs_info,
)


def attempt_play_table_reset(
    env_factory: Callable[[], Any] | None = None,
    *,
    try_step_smoke: bool = False,
) -> dict[str, Any]:
    """
    Try import + optional ``env_factory()`` + ``reset`` + ``get_info`` + optional zero-action ``step`` smoke.

    **Output**: JSON-serializable status dict; errors truncated — **no** HF tokens.
    """
    result: dict[str, Any] = {
        "import_play_table": False,
        "instantiated": False,
        "reset_ok": False,
        "teacher_mapping_eligible": False,
        "instruction_in_observation": False,
        "instruction_external_expected": True,
    }

    try:
        from calvin_env.envs.play_table_env import PlayTableSimEnv  # type: ignore import-not-found
    except ImportError as e:
        result["import_error"] = f"{type(e).__name__}: {e}"
        result["hint"] = "Install calvin_env per CALVIN / mees documentation; set PYTHONPATH if needed."
        return result

    result["import_play_table"] = True
    result["PlayTableSimEnv_module"] = getattr(PlayTableSimEnv, "__module__", "")
    _ = PlayTableSimEnv  # noqa: F841 — reference for static checkers

    if env_factory is None:
        result["hint"] = (
            "Import OK. Set ESA_CALVIN_ENV_FACTORY='module:callable' and implement factory per "
            "docs/calvin_env_factory_usage.md."
        )
        return result

    env: Any
    try:
        env = env_factory()
    except Exception as e:  # noqa: BLE001 — probe surfaces user env errors
        result["instantiate_error"] = f"{type(e).__name__}: {e}"[:800]
        return result

    result["instantiated"] = True

    try:
        obs = env.reset()
    except TypeError:
        try:
            obs = env.reset(robot_obs=None, scene_obs=None)
        except Exception as e2:  # noqa: BLE001
            result["reset_error"] = f"{type(e2).__name__}: {e2}"[:800]
            return result
    except Exception as e:  # noqa: BLE001
        result["reset_error"] = f"{type(e).__name__}: {e}"[:800]
        return result

    result["reset_ok"] = True
    get_info = getattr(env, "get_info", None)
    info: dict[str, Any] = {}
    if callable(get_info):
        try:
            raw = get_info()
            info = raw if isinstance(raw, dict) else {"non_dict_info": type(raw).__name__}
        except Exception as e:  # noqa: BLE001
            result["get_info_error"] = f"{type(e).__name__}: {e}"[:800]
            info = {}

    if isinstance(obs, dict):
        result["observation_summary"] = summarize_live_calvin_obs_info(obs, info)
    else:
        result["observation_summary"] = {"obs_type": type(obs).__name__, "note": "reset did not return dict"}

    result["info_summary_keys_only"] = sorted(info.keys()) if isinstance(info, dict) else []
    result["teacher_mapping_eligible"] = bool(
        isinstance(info, dict)
        and isinstance(info.get("scene_info"), dict)
        and isinstance(info.get("robot_info"), dict)
    )

    if try_step_smoke and result["reset_ok"]:
        from embodied_scene_agent.envs.calvin_action import normalize_calvin_live_action

        step_fn = getattr(env, "step", None)
        if not callable(step_fn):
            result["step_smoke"] = {"step_called": False, "error": "env.step is not callable"}
        else:
            try:
                # PlayTableSimEnv.step → robot.apply_action: relative mode expects a length-7 ndarray
                # (3 pos + 3 orn + gripper); a dict would have len 2 and hit AssertionError in relative_to_absolute.
                if result.get("import_play_table"):
                    import numpy as np

                    action = np.array((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0), dtype=np.float64)
                else:
                    action = normalize_calvin_live_action(None)
                raw_step = step_fn(action)
                result["step_smoke"] = {
                    "step_called": True,
                    "action_was_zero_smoke": True,
                    "return_python_type": type(raw_step).__name__,
                    "tuple_length": len(raw_step) if isinstance(raw_step, tuple) else None,
                    "note": "Interface smoke only — not a successful manipulation claim.",
                }
                get_obs = getattr(env, "get_obs", None)
                obs2: Any = {}
                if callable(get_obs):
                    o2 = get_obs()
                    if isinstance(o2, dict):
                        obs2 = o2
                info2: dict[str, Any] = {}
                if callable(get_info):
                    i2 = get_info()
                    if isinstance(i2, dict):
                        info2 = i2
                result["after_step_observation_summary"] = summarize_live_calvin_obs_info(obs2, info2)
                result["teacher_refresh_after_step_ok"] = bool(obs2) and isinstance(obs2, dict)
            except Exception as e:  # noqa: BLE001
                result["step_smoke"] = {
                    "step_called": True,
                    "error": f"{type(e).__name__}: {e}"[:800],
                    "note": "step failed during smoke — see error",
                }

    return result


def build_calvin_live_probe_report(
    *,
    dotenv_file_loaded: bool,
    hf_token_status: str,
    factory_resolve_meta: dict[str, Any],
    env_factory: Callable[[], Any] | None,
    try_step_smoke: bool = False,
) -> dict[str, Any]:
    """
    Full probe report for CLI / JSON / markdown export (not a benchmark).
    """
    calvin = attempt_play_table_reset(env_factory, try_step_smoke=try_step_smoke)
    return {
        "disclaimer": "NOT_A_BENCHMARK_RUN",
        "dotenv_file_loaded": dotenv_file_loaded,
        "hf_token_status": hf_token_status,
        "factory_resolve": factory_resolve_meta,
        "calvin": calvin,
    }


def probe_report_to_markdown(report: dict[str, Any]) -> str:
    """Human-readable summary; excludes any secrets."""
    lines = [
        "# CALVIN live probe (non-benchmark)",
        "",
        f"- **disclaimer**: `{report.get('disclaimer', '')}`",
        f"- **dotenv_file_loaded**: `{report.get('dotenv_file_loaded')}`",
        f"- **hf_token_status**: {report.get('hf_token_status')}",
        "",
        "## Factory resolve",
        "",
        "```json",
        json.dumps(report.get("factory_resolve", {}), indent=2, ensure_ascii=False),
        "```",
        "",
        "## CALVIN",
        "",
    ]
    calvin = report.get("calvin") or {}
    obs_sum = calvin.get("observation_summary")
    if isinstance(obs_sum, dict):
        lines.append("### Observation summary")
        lines.append(format_live_summary_markdown(obs_sum))
        lines.append("")
    lines.append("### Raw calvin dict keys")
    lines.append(f"- keys: `{sorted(calvin.keys())}`")
    return "\n".join(lines)
