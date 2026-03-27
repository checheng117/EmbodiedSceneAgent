"""Build `SceneMemory` from structured payloads (e.g. teacher-state dicts)."""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.memory.schema import (
    ESA_SCENE_MEMORY_SCHEMA_VERSION,
    ObjectState,
    RelationEdge,
    RelationType,
    SceneMemory,
)


class SceneMemoryBuilder:
    """Constructs validated `SceneMemory` instances from loose dict inputs."""

    _RESERVED_TOP_LEVEL = frozenset(
        {"objects", "relations", "frame_id", "schema_version", "timestamp_s", "source"}
    )

    @staticmethod
    def from_teacher_payload(payload: dict[str, Any], *, source: str = "teacher_state") -> SceneMemory:
        """
        Parse a normalized teacher-state dictionary.

        Expected keys:
        - ``objects``: list[dict] with at least ``id``, optional ``name``, ``position``, ``bbox``,
          ``state_tags``, ``aliases``, ``category``, etc.
        - ``relations``: optional list of dicts with ``subject_id``, ``object_id``, ``relation``.
        - ``frame_id``: optional str
        - ``schema_version``: optional str (defaults to :data:`ESA_SCENE_MEMORY_SCHEMA_VERSION`)
        - ``timestamp_s``: optional float
        """
        frame_id = payload.get("frame_id")
        schema_version = str(payload.get("schema_version", ESA_SCENE_MEMORY_SCHEMA_VERSION))
        timestamp_s = payload.get("timestamp_s")
        if timestamp_s is not None:
            timestamp_s = float(timestamp_s)

        objects: dict[str, ObjectState] = {}
        for raw in payload.get("objects", []):
            oid = str(raw["id"])
            name = str(raw.get("name", oid))
            cat = raw.get("category")
            class_name = str(raw.get("class_name", ""))
            if not class_name:
                class_name = str(cat) if cat is not None else name
            pos3 = raw.get("position_3d")
            if pos3 is not None:
                if not isinstance(pos3, (list, tuple)) or len(pos3) != 3:
                    raise ValueError(f"object {oid}: position_3d must be length-3 list")
                pos = [float(pos3[0]), float(pos3[1]), float(pos3[2])]
            else:
                pos = raw.get("position", [0.0, 0.0, 0.0])
                if not isinstance(pos, (list, tuple)) or len(pos) != 3:
                    raise ValueError(f"object {oid}: position must be length-3 list")
            bbox_raw = raw.get("bbox_3d", raw.get("bbox"))
            if bbox_raw is not None:
                if not isinstance(bbox_raw, (list, tuple)) or len(bbox_raw) != 6:
                    raise ValueError(f"object {oid}: bbox_3d must be length-6 list")
                bbox_t = (
                    float(bbox_raw[0]),
                    float(bbox_raw[1]),
                    float(bbox_raw[2]),
                    float(bbox_raw[3]),
                    float(bbox_raw[4]),
                    float(bbox_raw[5]),
                )
            else:
                bbox_t = None
            ls = raw.get("last_seen_step")
            objects[oid] = ObjectState(
                object_id=oid,
                name=name,
                display_name=str(raw.get("display_name", "")),
                class_name=class_name,
                category=str(cat) if cat is not None else None,
                aliases=list(raw.get("aliases", [])),
                position=(float(pos[0]), float(pos[1]), float(pos[2])),
                bbox=bbox_t,
                oriented_bbox=raw.get("oriented_bbox"),
                state_tags=list(raw.get("state_tags", [])),
                visibility=float(raw.get("visibility", 1.0)),
                confidence=float(raw.get("confidence", 1.0)),
                last_seen_step=int(ls) if ls is not None else None,
                metadata=dict(raw.get("metadata", {})),
            )

        relations: list[RelationEdge] = []
        for raw in payload.get("relations", []):
            rel_s = str(raw["relation"])
            try:
                rtype = RelationType(rel_s)
            except ValueError as e:
                raise ValueError(f"unknown relation type: {rel_s}") from e
            relations.append(
                RelationEdge(
                    subject_id=str(raw["subject_id"]),
                    object_id=str(raw["object_id"]),
                    relation=rtype,
                    confidence=float(raw.get("confidence", 1.0)),
                )
            )

        extra = {k: v for k, v in payload.items() if k not in SceneMemoryBuilder._RESERVED_TOP_LEVEL}
        src = str(payload.get("source", source))
        return SceneMemory(
            objects=objects,
            relations=relations,
            frame_id=frame_id,
            schema_version=schema_version,
            timestamp_s=timestamp_s,
            source=src,
            extra=extra,
        )
