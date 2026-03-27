"""Core scene memory schema: objects, relations, serialization."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# Bump when making incompatible changes to SceneMemory / ObjectState JSON shape.
ESA_SCENE_MEMORY_SCHEMA_VERSION = "esa_sm/v1"
"""Default serialized schema tag (v1 wire format preserved for CALVIN / JSONL)."""

ESA_SCENE_MEMORY_CONTRACT_V2 = "esa_sm_contract/v2"
"""Logical contract id documented in ``docs/scene_memory_contract_v2.md`` (superset of v1 fields)."""


class RelationType(str, Enum):
    """Spatial / affordance relations between objects (extensible)."""

    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"
    IN_FRONT_OF = "in_front_of"
    BEHIND = "behind"
    ABOVE = "above"
    BELOW = "below"
    ON = "on"
    IN = "in"
    NEAR = "near"
    REACHABLE = "reachable"
    BLOCKED = "blocked"


class ObjectState(BaseModel):
    """Single object hypothesis in the scene graph."""

    object_id: str
    """Canonical instance id in this frame (stable for planner / verifier)."""
    name: str = ""
    """Human-readable instance label (may match object_id)."""
    display_name: str = ""
    """UI / report label; defaults to ``name`` or ``object_id`` if empty (contract v2)."""
    class_name: str = ""
    """Semantic category or class (e.g. ``block``, ``slider`` / drawer mechanism)."""
    category: str | None = None
    """Optional high-level category; may duplicate ``class_name`` for adapters."""
    aliases: list[str] = Field(default_factory=list)
    """Alternate names from benchmarks (e.g. CALVIN uid) for debugging and future grounding."""
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    """3D position in world frame (alias name in contract: ``position_3d``)."""
    bbox: tuple[float, float, float, float, float, float] | None = None
    """Axis-aligned bbox (min_x, min_y, min_z, max_x, max_y, max_z); contract alias ``bbox_3d``."""
    oriented_bbox: dict[str, Any] | None = None
    """Optional OBB or 9D representation; v0 keeps dict for flexibility."""
    state_tags: list[str] = Field(default_factory=list)
    visibility: float = 1.0
    confidence: float = 1.0
    last_seen_step: int | None = None
    """Optional discrete timestep index for temporal tracking (contract v2)."""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _default_display_name(self) -> ObjectState:
        if not (self.display_name or "").strip():
            self.display_name = self.name or self.object_id
        return self

    @field_validator("visibility", "confidence")
    @classmethod
    def _clip_unit(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class RelationEdge(BaseModel):
    """Directed relation between two object ids."""

    subject_id: str
    object_id: str
    relation: RelationType
    confidence: float = 1.0


class SceneMemory(BaseModel):
    """Frame-level object-centric scene memory."""

    objects: dict[str, ObjectState] = Field(default_factory=dict)
    relations: list[RelationEdge] = Field(default_factory=list)
    frame_id: str | None = None
    schema_version: str = Field(default=ESA_SCENE_MEMORY_SCHEMA_VERSION)
    """Schema version string for serialized snapshots (``esa_sm/v1``)."""
    timestamp_s: float | None = None
    """Optional wall-clock or sim time in seconds."""
    source: str = "unknown"
    extra: dict[str, Any] = Field(default_factory=dict)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict (nested primitives only)."""
        return self.model_dump(mode="json")

    def pretty_print(self) -> str:
        """Human-readable summary for debugging."""
        lines = [
            f"SceneMemory(schema={self.schema_version}, frame={self.frame_id}, source={self.source})"
        ]
        for oid, obj in self.objects.items():
            lines.append(
                f"  - {oid}: {obj.name or obj.class_name} @ {obj.position} "
                f"tags={obj.state_tags} vis={obj.visibility:.2f} conf={obj.confidence:.2f}"
            )
        for rel in self.relations:
            lines.append(f"  - {rel.subject_id} --{rel.relation.value}--> {rel.object_id}")
        return "\n".join(lines)


def scene_memory_json_schema() -> dict[str, Any]:
    """Return JSON Schema for :class:`SceneMemory` (Pydantic ``model_json_schema``)."""
    return SceneMemory.model_json_schema()
