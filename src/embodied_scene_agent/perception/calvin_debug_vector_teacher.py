"""
Map official CALVIN **debug dataset** flat vectors (``robot_obs``, ``scene_obs``) → ``calvin_teacher_v0``.

Layout follows upstream ``dataset/README.md`` (mees/calvin). This is **not** a substitute for live
``get_obs`` / ``get_info`` — it reconstructs a minimal structured teacher so
:class:`~embodied_scene_agent.envs.calvin.CalvinEnvAdapter` + :class:`CalvinTeacherStateAdapter` can
build :class:`~embodied_scene_agent.memory.schema.SceneMemory` without PyBullet.

**Honest scope**: vector decoding uses fixed index layout; object naming uses CALVIN play-table
conventions (``block_red`` / ``base__drawer``). Instruction text is **not** inside ``*.npz`` for
the debug zip we ship — callers must pass language from a documented pool and record lineage in
metadata.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from embodied_scene_agent.perception.calvin_field_mapper import (
    map_robot_info_to_teacher_robot,
    map_scene_info_to_scene_objects,
)


def scene_obs_vector_to_scene_info(scene_obs: np.ndarray) -> dict[str, Any]:
    """
    Unpack ``scene_obs`` (24,) per official dataset README (debug / D split family).

    Indices:
    - 0: sliding door joint, 1: drawer, 2: button, 3: switch, 4: lightbulb, 5: green led
    - 6–11: red block (pos 3 + euler 3)
    - 12–17: blue block
    - 18–23: pink block
    """
    s = np.asarray(scene_obs, dtype=np.float64).reshape(-1)
    if s.size < 24:
        raise ValueError(f"scene_obs must have at least 24 elements, got {s.size}")

    scene_info: dict[str, Any] = {
        "doors": {
            "base__slide": {"current_state": float(s[0])},
            "base__drawer": {"current_state": float(s[1])},
        },
        "movable_objects": {
            "block_red": {
                "current_pos": s[6:9].copy(),
                "current_orn": s[9:12].copy(),
            },
            "block_blue": {
                "current_pos": s[12:15].copy(),
                "current_orn": s[15:18].copy(),
            },
            "block_pink": {
                "current_pos": s[18:21].copy(),
                "current_orn": s[21:24].copy(),
            },
        },
        "debug_vector_extras": {
            "button_joint": float(s[2]),
            "switch_joint": float(s[3]),
            "lightbulb": float(s[4]),
            "green_led": float(s[5]),
        },
    }
    return scene_info


def robot_obs_vector_to_robot_info(robot_obs: np.ndarray) -> dict[str, Any]:
    """
    Unpack ``robot_obs`` (15,): tcp pos 3, tcp euler 3, gripper width 1, arm joints 7, gripper_action 1.
    """
    r = np.asarray(robot_obs, dtype=np.float64).reshape(-1)
    if r.size < 15:
        raise ValueError(f"robot_obs must have at least 15 elements, got {r.size}")
    ga = float(r[14])
    return {
        "tcp_pos": r[0:3].copy(),
        "tcp_orn": r[3:6].copy(),
        "gripper_opening_width": float(r[6]),
        "arm_joint_states": r[7:14].tolist(),
        "gripper_action": int(np.sign(ga)) if abs(ga) > 0.5 else int(ga),
    }


def build_initial_observation_from_debug_vectors(
    robot_obs: np.ndarray,
    scene_obs: np.ndarray,
    instruction: str,
    *,
    frame_id: str = "0",
    npz_stem: str = "",
) -> dict[str, Any]:
    """
    Return a dict suitable for ``CalvinEnvAdapter(initial_observation=...)`` (fixture path).

    Contains ``calvin_teacher_v0`` built via the same field mappers as the live path (robot_info /
    scene_info shapes).
    """
    ri = robot_obs_vector_to_robot_info(robot_obs)
    si = scene_obs_vector_to_scene_info(scene_obs)
    teacher_v0: dict[str, Any] = {
        "frame_id": str(frame_id),
        "language": {"instruction": instruction},
        "robot": map_robot_info_to_teacher_robot(ri),
        "scene_objects": map_scene_info_to_scene_objects(si),
        "mapping_meta": {
            "source": "calvin_debug_vector_teacher",
            "npz_stem": npz_stem or None,
            "robot_obs_len": int(np.asarray(robot_obs).size),
            "scene_obs_len": int(np.asarray(scene_obs).size),
            "instruction_in_npz": False,
            "note": "Reconstructed from official debug dataset vectors; not live sim info dicts.",
        },
    }
    return {"calvin_teacher_v0": teacher_v0}
