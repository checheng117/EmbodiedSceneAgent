"""Safe summaries of live CALVIN obs/info for audits (no token, no full array dumps)."""

from __future__ import annotations

from typing import Any


def _shape(x: Any) -> list[int] | None:
    sh = getattr(x, "shape", None)
    if sh is None:
        return None
    try:
        return [int(s) for s in sh]
    except (TypeError, ValueError):
        return None


def _len_or_none(x: Any) -> int | None:
    if x is None:
        return None
    try:
        return len(x)
    except TypeError:
        return None


def summarize_live_calvin_obs_info(obs: Any, info: Any) -> dict[str, Any]:
    """
    Build a JSON-friendly summary for field audits.

    **Input**: raw ``obs`` from ``get_obs()`` / ``reset``, ``info`` from ``get_info()``.

    **Output**: nested dict with keys only, shapes, and short counts — **not** full ``robot_obs`` / ``scene_obs`` values.

    **Status**: 代码层安全摘要；具体键集合以运行级验证为准（见 ``docs/calvin_live_validation_plan.md``）。
    """
    out: dict[str, Any] = {"observation_type": type(obs).__name__, "info_type": type(info).__name__}

    if not isinstance(obs, dict):
        out["observation_note"] = "expected dict observation from CALVIN get_obs/reset"
        return out

    out["obs_top_level_keys"] = sorted(obs.keys())
    rgb = obs.get("rgb_obs")
    if isinstance(rgb, dict):
        out["rgb_obs_camera_keys"] = sorted(rgb.keys())
    depth = obs.get("depth_obs")
    if isinstance(depth, dict):
        out["depth_obs_keys"] = sorted(depth.keys())
    out["robot_obs_shape"] = _shape(obs.get("robot_obs"))
    out["robot_obs_len"] = _len_or_none(obs.get("robot_obs"))
    out["scene_obs_shape"] = _shape(obs.get("scene_obs"))
    out["scene_obs_len"] = _len_or_none(obs.get("scene_obs"))

    if not isinstance(info, dict):
        out["info_note"] = "expected dict from get_info()"
        return out

    out["info_top_level_keys"] = sorted(info.keys())
    ri = info.get("robot_info")
    if isinstance(ri, dict):
        out["robot_info_keys"] = sorted(ri.keys())
    si = info.get("scene_info")
    if isinstance(si, dict):
        out["scene_info_top_keys"] = sorted(si.keys())
        for cat in ("doors", "movable_objects", "fixed_objects", "buttons", "switches", "lights"):
            sub = si.get(cat)
            if isinstance(sub, dict):
                out[f"scene_info_{cat}_names"] = sorted(sub.keys())[:64]
                out[f"scene_info_{cat}_count"] = len(sub)

    return out


def format_live_summary_markdown(summary: dict[str, Any]) -> str:
    """Single-page markdown-ish text for logs (still no secrets)."""
    lines = ["## CALVIN live obs/info summary", ""]
    for k in sorted(summary.keys()):
        lines.append(f"- **{k}**: `{summary[k]!r}`")
    return "\n".join(lines)
