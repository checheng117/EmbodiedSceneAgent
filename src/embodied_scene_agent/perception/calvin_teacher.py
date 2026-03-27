"""CALVIN-aligned teacher-state ingestion → :class:`SceneMemory` (no RGB-D, no open-vocabulary)."""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.perception.base import BaseTeacherStateAdapter

# Fixed uid → canonical object_id for RuleBasedPlanner / mock-aligned skills (extend as needed).
_UID_TO_CANONICAL: dict[str, str] = {
    "slider_left": "drawer",
    "block_red": "red_block",
    "drawer": "drawer",
    "red_block": "red_block",
    "table": "table",
    "gripper": "gripper",
}


def _canonical_id(uid: str, category: str | None) -> str:
    u = uid.strip().lower()
    if u in _UID_TO_CANONICAL:
        return _UID_TO_CANONICAL[u]
    if u in ("drawer", "red_block", "table", "gripper"):
        return u
    c = (category or "").lower()
    if c in ("slider", "drawer", "articulated_drawer"):
        return "drawer"
    if c in ("block", "cube"):
        return "red_block"
    return uid


class CalvinTeacherStateAdapter(BaseTeacherStateAdapter):
    """
    Map a **CALVIN-style teacher bundle** to canonical :class:`SceneMemory`.

    Supported input shapes:

    1. **Recommended (minimal dev)**: top-level or nested ``calvin_teacher_v0`` dict containing:
       - ``frame_id`` (optional), ``timestamp_s`` (optional)
       - ``robot``: ``held_object_uid`` (optional str | null), ``gripper_open`` (optional bool)
       - ``scene_objects``: list of dicts with ``uid``, ``category``, ``position`` [x,y,z],
         and flags: ``drawer_open``, ``in_drawer``, ``held`` (per-object), as available.

    2. **Not supported in v0**: raw pixel-only CALVIN ``rgb_obs`` without a teacher bundle — raise
       :class:`ValueError` with a clear message.

    TODO: Map from real CALVIN simulator ``info`` / scene graph when env is wired.
    TODO: Broader object vocabulary once canonical naming table exists.
    """

    def to_scene_memory(self, instruction: str, state: dict[str, Any]) -> SceneMemory:
        inner = self._extract_teacher_layer(state)
        payload = self._build_normalized_payload(instruction=instruction, teacher=inner)
        return SceneMemoryBuilder.from_teacher_payload(payload, source="calvin_teacher")

    @staticmethod
    def _extract_teacher_layer(state: dict[str, Any]) -> dict[str, Any]:
        if "calvin_teacher_v0" in state:
            return dict(state["calvin_teacher_v0"])
        if "scene_objects" in state and "robot" in state:
            return dict(state)
        if "rgb_obs" in state and "calvin_teacher_v0" not in state:
            raise ValueError(
                "CalvinTeacherStateAdapter: raw RGB-only observation has no teacher bundle; "
                "provide calvin_teacher_v0 (see docs/calvin_adapter_plan.md)."
            )
        raise ValueError(
            "CalvinTeacherStateAdapter: expected calvin_teacher_v0 or scene_objects+robot teacher fields."
        )

    def _build_normalized_payload(self, *, instruction: str, teacher: dict[str, Any]) -> dict[str, Any]:
        frame_id = str(teacher.get("frame_id", "0"))
        timestamp_s = teacher.get("timestamp_s")
        robot = dict(teacher.get("robot", {}))
        held_uid_raw = robot.get("held_object_uid")
        held_canonical: str | None = None
        if held_uid_raw:
            held_canonical = _canonical_id(str(held_uid_raw), None)

        objects_out: list[dict[str, Any]] = []
        relations_out: list[dict[str, Any]] = []

        # Static table (for relations)
        objects_out.append(
            {
                "id": "table",
                "name": "table",
                "class_name": "table",
                "category": "support_surface",
                "position": [0.5, 0.0, 0.0],
                "state_tags": ["static"],
                "aliases": ["table_top"],
            }
        )

        block_held = bool(held_canonical == "red_block")

        for obj in teacher.get("scene_objects", []):
            uid = str(obj["uid"])
            cat = obj.get("category")
            cid = _canonical_id(uid, str(cat) if cat is not None else None)
            pos = obj.get("position", [0.0, 0.0, 0.0])
            if not isinstance(pos, (list, tuple)) or len(pos) != 3:
                raise ValueError(f"scene_objects[{uid}]: position must be length-3")
            aliases = [uid] if uid != cid else []
            meta: dict[str, Any] = {"calvin_uid": uid}

            if cid == "drawer":
                drawer_open = bool(obj.get("drawer_open", False))
                tags = ["open"] if drawer_open else ["closed"]
                objects_out.append(
                    {
                        "id": "drawer",
                        "name": "drawer",
                        "class_name": str(cat or "slider"),
                        "category": str(cat) if cat is not None else "slider",
                        "aliases": aliases,
                        "position": [float(pos[0]), float(pos[1]), float(pos[2])],
                        "state_tags": tags,
                        "metadata": meta,
                    }
                )
            elif cid == "red_block":
                in_dr = bool(obj.get("in_drawer", False))
                held_o = bool(obj.get("held", False)) or block_held
                tags: list[str] = []
                if in_dr:
                    tags.append("in_drawer")
                if held_o:
                    tags.append("held")
                if not in_dr and not held_o:
                    tags.append("on_table")
                objects_out.append(
                    {
                        "id": "red_block",
                        "name": str(obj.get("instance_name", "red block")),
                        "class_name": str(cat or "block"),
                        "category": str(cat) if cat is not None else "block",
                        "aliases": aliases,
                        "position": [float(pos[0]), float(pos[1]), float(pos[2])],
                        "state_tags": tags,
                        "metadata": meta,
                    }
                )

        # Ensure minimal objects if scene_objects omitted partially
        ids_present = {o["id"] for o in objects_out}
        if "drawer" not in ids_present:
            objects_out.append(
                {
                    "id": "drawer",
                    "name": "drawer",
                    "class_name": "slider",
                    "category": "slider",
                    "position": [0.6, 0.0, 0.35],
                    "state_tags": ["closed"],
                    "metadata": {"placeholder": True},
                }
            )
        if "red_block" not in ids_present:
            objects_out.append(
                {
                    "id": "red_block",
                    "name": "red block",
                    "class_name": "block",
                    "category": "block",
                    "position": [0.45, 0.0, 0.12],
                    "state_tags": ["on_table"],
                    "metadata": {"placeholder": True},
                }
            )

        # Re-sync block / gripper from robot held (overrides partial flags)
        rb = next((o for o in objects_out if o["id"] == "red_block"), None)
        if rb is not None:
            if held_canonical == "red_block":
                rb["state_tags"] = [t for t in rb["state_tags"] if t not in ("on_table", "in_drawer")]
                if "held" not in rb["state_tags"]:
                    rb["state_tags"].append("held")
            st = set(rb["state_tags"])
            if "in_drawer" in st:
                st.discard("on_table")
                st.discard("held")
            elif "held" in st:
                st.discard("on_table")
                st.discard("in_drawer")
            rb["state_tags"] = list(st)

        if held_canonical == "red_block":
            objects_out.append(
                {
                    "id": "gripper",
                    "name": "gripper",
                    "class_name": "end_effector",
                    "category": "gripper",
                    "position": [0.5, 0.0, 0.2],
                    "state_tags": ["end_effector"],
                    "metadata": {},
                }
            )

        block_in_drawer_final = rb is not None and "in_drawer" in rb["state_tags"]
        if held_canonical == "red_block":
            relations_out.append(
                {"subject_id": "red_block", "object_id": "gripper", "relation": "on"}
            )
        elif block_in_drawer_final:
            relations_out.append({"subject_id": "red_block", "object_id": "drawer", "relation": "in"})
        else:
            relations_out.append({"subject_id": "red_block", "object_id": "table", "relation": "on"})

        out: dict[str, Any] = {
            "frame_id": frame_id,
            "timestamp_s": timestamp_s,
            "objects": objects_out,
            "relations": relations_out,
            "source": "calvin_teacher",
            "calvin_robot_meta": robot,
            "language_instruction": instruction,
            "gripper_open": robot.get("gripper_open"),
        }
        sv = teacher.get("schema_version")
        if sv is not None:
            out["schema_version"] = sv
        et = teacher.get("extra")
        if et:
            out["extra_teacher"] = et
        return out
