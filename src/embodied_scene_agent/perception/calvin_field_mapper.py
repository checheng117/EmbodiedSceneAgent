"""
CALVIN raw ``observation`` / ``info`` → ``calvin_teacher_v0`` canonical teacher payload.

All mapping is **centralised** here (do not scatter field logic across adapters).

Verified field names refer to ``mees/calvin_env`` as documented in ``docs/calvin_real_fields_audit.md``.
"""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.planner.schema import PlannerOutput


def _as_float3(seq: Any) -> list[float]:
    if seq is None:
        return [0.0, 0.0, 0.0]
    t = list(seq)[:3]
    return [float(t[0]), float(t[1]), float(t[2])]

# --- Speculative constants (not from CALVIN; tune with real env) ---
GRIPPER_OPEN_WIDTH_THRESHOLD = 0.04
"""If ``gripper_opening_width`` > this, set ``gripper_open`` True (heuristic)."""
DOOR_OPEN_JOINT_EPS = 1e-3
"""If abs(door joint current_state) > this, treat drawer/slider as open (heuristic)."""


# Object naming: CALVIN scene object name substring → canonical uid + category for teacher layer
_NAME_HINTS: list[tuple[tuple[str, ...], str, str]] = [
    (("block", "cube", "red"), "red_block", "block"),
    (("drawer", "slider"), "drawer", "slider"),
]


def canonical_uid_and_category_from_calvin_name(name: str) -> tuple[str, str]:
    """
    Map CALVIN scene object **name** (movable / door key) to (teacher_uid, category).

    Output feeds ``calvin_teacher_v0.scene_objects[].uid`` and ``category``.
    """
    lower = name.lower()
    for substrings, uid, cat in _NAME_HINTS:
        if any(s in lower for s in substrings):
            return uid, cat
    return name, "unknown"


def map_robot_info_to_teacher_robot(robot_info: dict[str, Any]) -> dict[str, Any]:
    """
    **Input**: ``info["robot_info"]`` from ``PlayTableSimEnv.get_info()`` (see ``Robot.get_observation``).

    **Output** → ``calvin_teacher_v0.robot``:
    - ``gripper_open``: bool (from ``gripper_opening_width`` vs :data:`GRIPPER_OPEN_WIDTH_THRESHOLD`, **heuristic**)
    - ``gripper_opening_width``: float passthrough
    - ``held_object_uid``: always ``None`` until contact-based grounding is implemented
    - ``tcp_pos``: list[float] if present
    """
    gow = float(robot_info.get("gripper_opening_width", 0.0))
    tcp = robot_info.get("tcp_pos")
    tcp_list: list[float] | None = _as_float3(tcp) if tcp is not None else None
    return {
        "gripper_open": gow > GRIPPER_OPEN_WIDTH_THRESHOLD,
        "gripper_opening_width": gow,
        "held_object_uid": None,
        "tcp_pos": tcp_list,
        "gripper_action": robot_info.get("gripper_action"),
    }


def map_door_entry_to_scene_object(door_name: str, door_info: dict[str, Any]) -> dict[str, Any]:
    """
    **Input**: ``scene_info["doors"][door_name]`` — verified to contain ``current_state`` (float).

    **Output**: one ``scene_objects`` element with ``drawer_open`` from joint displacement heuristic
    (:data:`DOOR_OPEN_JOINT_EPS`).
    """
    joint_val = float(door_info.get("current_state", 0.0))
    uid, category = canonical_uid_and_category_from_calvin_name(door_name)
    return {
        "uid": door_name,
        "category": category,
        "instance_name": door_name,
        "position": [0.0, 0.0, 0.0],
        "drawer_open": abs(joint_val) > DOOR_OPEN_JOINT_EPS,
        "drawer_joint_value": joint_val,
        "metadata": {"calvin_door": True, "heuristic_drawer_open": True},
    }


def map_movable_entry_to_scene_object(obj_name: str, obj_info: dict[str, Any]) -> dict[str, Any]:
    """
    **Input**: ``scene_info["movable_objects"][obj_name]`` — verified keys include ``current_pos``, ``current_orn``.

    **Output**: ``scene_objects`` element with ``position`` from ``current_pos``.
    ``in_drawer`` / ``held`` are **not** set here (unstable without extra reasoning).
    """
    pos = obj_info.get("current_pos")
    if pos is None:
        raise ValueError(f"movable_objects[{obj_name}] missing current_pos")
    position = _as_float3(pos)
    uid, category = canonical_uid_and_category_from_calvin_name(obj_name)
    return {
        "uid": obj_name,
        "category": category,
        "instance_name": obj_name,
        "position": position,
        "in_drawer": False,
        "held": False,
        "metadata": {"calvin_movable": True},
    }


def map_scene_info_to_scene_objects(scene_info: dict[str, Any]) -> list[dict[str, Any]]:
    """
    **Input**: ``scene_info`` from ``PlayTableScene.get_info()`` (nested dicts).

    **Output**: list for ``calvin_teacher_v0.scene_objects`` (doors + movables; other categories TODO).
    """
    out: list[dict[str, Any]] = []
    for door_name, door_info in scene_info.get("doors", {}).items():
        out.append(map_door_entry_to_scene_object(door_name, door_info))
    for obj_name, obj_info in scene_info.get("movable_objects", {}).items():
        out.append(map_movable_entry_to_scene_object(obj_name, obj_info))
    return out


def map_calvin_obs_and_info_to_teacher_bundle(
    obs: dict[str, Any],
    info: dict[str, Any],
    instruction: str,
    *,
    frame_id: str = "0",
) -> dict[str, Any]:
    """
    **Input**:
    - ``obs``: return value of ``PlayTableSimEnv.get_obs()``
    - ``info``: return value of ``PlayTableSimEnv.get_info()``
    - ``instruction``: language string from **dataset/eval layer** (not inside ``obs``)

    **Output**: dict suitable for merging into adapter state, containing ``calvin_teacher_v0`` and
    diagnostic ``calvin_raw`` keys.

    Raises:
        ValueError: if ``scene_info`` missing (object-level mapping requires ``use_scene_info=True``).
    """
    for k in ("rgb_obs", "robot_obs", "scene_obs"):
        if k not in obs:
            raise ValueError(f"observation missing required key {k!r} for CALVIN raw mapping")
    scene_info = info.get("scene_info")
    if scene_info is None:
        raise ValueError(
            "info['scene_info'] is None — enable use_scene_info=True when constructing PlayTableSimEnv, "
            "or use fixture-only mode."
        )
    robot_info = info.get("robot_info")
    if not isinstance(robot_info, dict):
        raise ValueError("info['robot_info'] must be a dict")

    robot_obs = obs["robot_obs"]
    scene_obs = obs["scene_obs"]
    teacher_v0: dict[str, Any] = {
        "frame_id": frame_id,
        "language": {"instruction": instruction},
        "robot": map_robot_info_to_teacher_robot(robot_info),
        "scene_objects": map_scene_info_to_scene_objects(scene_info),
        "mapping_meta": {
            "source": "calvin_field_mapper",
            "robot_obs_shape": getattr(robot_obs, "shape", None),
            "scene_obs_shape": getattr(scene_obs, "shape", None),
            "held_object_uid_note": "not inferred; TODO contacts+semantics",
        },
    }
    return {
        "calvin_teacher_v0": teacher_v0,
        "calvin_raw": {
            "observation_keys": sorted(obs.keys()),
            "info_keys": sorted(info.keys()),
        },
    }


def map_live_calvin_to_teacher_bundle(
    obs: dict[str, Any],
    info: dict[str, Any],
    instruction: str,
    *,
    frame_id: str = "0",
) -> dict[str, Any]:
    """
    **Live path** wrapper: raw ``obs`` + ``info`` → bundle with ``calvin_teacher_v0``.

    **Input**: same as :func:`map_calvin_obs_and_info_to_teacher_bundle` (``PlayTableSimEnv``-shaped).

    **Output**: canonical teacher payload + ``calvin_raw``; ``mapping_meta`` tagged with ``live_path=True``.

    **Status**: 映射逻辑与 :func:`map_calvin_obs_and_info_to_teacher_bundle` 相同；**运行级验证**见项目 probe。
    """
    bundle = map_calvin_obs_and_info_to_teacher_bundle(obs, info, instruction, frame_id=frame_id)
    teacher = bundle["calvin_teacher_v0"]
    meta = teacher.setdefault("mapping_meta", {})
    if isinstance(meta, dict):
        meta["live_path"] = True
    return bundle


def extract_robot_state_from_live_obs(
    obs: dict[str, Any],
    info: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract **canonical robot subset** for debugging / overlays.

    **Input**:
    - ``obs["robot_obs"]``: 向量 — **待确认**各维语义（需 ``get_observation_labels`` 或配置）；此处仅记录 ``shape``/``len``。
    - ``info["robot_info"]``: **已验证（源码级）** 含 ``tcp_pos``, ``gripper_opening_width`` 等（见审计文档）。

    **Output**: dict with ``robot_info`` passthrough (if dict), ``robot_obs_meta`` (shape/len only).

    **Status**: **不**替代 ``map_robot_info_to_teacher_robot``；供 live summary / 调试。
    """
    robot_obs = obs.get("robot_obs")
    meta: dict[str, Any] = {
        "robot_obs_shape": getattr(robot_obs, "shape", None),
        "robot_obs_len": len(robot_obs) if hasattr(robot_obs, "__len__") else None,
    }
    try:
        if meta["robot_obs_shape"] is not None:
            meta["robot_obs_shape"] = [int(x) for x in meta["robot_obs_shape"]]  # type: ignore[arg-type]
    except (TypeError, ValueError):
        pass
    ri = info.get("robot_info") if isinstance(info, dict) else None
    out: dict[str, Any] = {"robot_obs_meta": meta}
    if isinstance(ri, dict):
        out["robot_info"] = dict(ri)
    return out


def extract_scene_objects_from_live_obs(
    obs: dict[str, Any],
    info: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Build minimal **scene_objects** list for ``calvin_teacher_v0`` from **structured** scene info.

    **Input**:
    - ``info["scene_info"]``: **已验证（源码级）** 嵌套 dict（doors, movable_objects, …）。
    - ``obs["scene_obs"]``: **不用于**逐物体解析（**待确认**索引映射）；忽略向量内容。

    **Output**: list of scene object dicts (same schema as :func:`map_scene_info_to_scene_objects`).

    **Status**: 与 teacher 映射一致；物体级 pose 来自 ``scene_info``，非 ``scene_obs`` 切片。
    """
    _ = obs
    if not isinstance(info, dict):
        return []
    scene_info = info.get("scene_info")
    if not isinstance(scene_info, dict):
        return []
    return map_scene_info_to_scene_objects(scene_info)


def apply_symbolic_plan_to_calvin_teacher_v0(teacher: dict[str, Any], plan: PlannerOutput) -> None:
    """
    **Dev-only**: mutate ``calvin_teacher_v0`` dict in place to mimic one skill (fixture / smoke).

    Does **not** call PyBullet. Not used for real-env training claims.
    """
    robot = teacher.setdefault("robot", {})

    def _ensure_block() -> dict[str, Any]:
        for o in teacher.get("scene_objects", []):
            if o.get("uid") == "red_block" or canonical_uid_and_category_from_calvin_name(str(o.get("uid")))[0] == "red_block":
                return o
        o = {
            "uid": "red_block",
            "category": "block",
            "instance_name": "red block",
            "position": [0.45, 0.0, 0.12],
            "in_drawer": False,
            "held": False,
        }
        teacher.setdefault("scene_objects", []).append(o)
        return o

    def _ensure_drawer() -> dict[str, Any]:
        for o in teacher.get("scene_objects", []):
            if o.get("drawer_open") is not None or "drawer" in str(o.get("uid", "")).lower():
                return o
        for o in teacher.get("scene_objects", []):
            if o.get("category") == "slider":
                return o
        o = {
            "uid": "drawer",
            "category": "slider",
            "instance_name": "drawer",
            "position": [0.6, 0.0, 0.35],
            "drawer_open": False,
        }
        teacher.setdefault("scene_objects", []).append(o)
        return o

    skill = plan.skill
    tgt = plan.target_object

    if skill == "open" and tgt == "drawer":
        d = _ensure_drawer()
        d["drawer_open"] = True
        return
    if skill == "grasp" and tgt == "red_block":
        b = _ensure_block()
        b["held"] = True
        b["in_drawer"] = False
        robot["held_object_uid"] = "red_block"
        return
    if skill == "place" and tgt == "drawer":
        b = _ensure_block()
        b["held"] = False
        b["in_drawer"] = True
        robot["held_object_uid"] = None
        return
    if skill in {"reach", "move_to"}:
        return
    # Unknown: no-op for dev trace completeness
