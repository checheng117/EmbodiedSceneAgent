"""Scene memory schema tests."""

from __future__ import annotations

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.memory.schema import RelationType


def test_builder_roundtrip() -> None:
    payload = {
        "frame_id": "0",
        "objects": [
            {
                "id": "a",
                "name": "block",
                "position": [0.0, 0.0, 0.0],
                "bbox": [0, 0, 0, 1, 1, 1],
                "state_tags": ["on_table"],
            }
        ],
        "relations": [
            {"subject_id": "a", "object_id": "b", "relation": "near"},
        ],
    }
    mem = SceneMemoryBuilder.from_teacher_payload(payload)
    assert "a" in mem.objects
    assert mem.relations[0].relation == RelationType.NEAR
    js = mem.to_json_dict()
    assert js["objects"]["a"]["object_id"] == "a"


def test_position_3d_and_display_name() -> None:
    mem = SceneMemoryBuilder.from_teacher_payload(
        {
            "objects": [
                {
                    "id": "a",
                    "name": "block",
                    "position_3d": [1.0, 2.0, 3.0],
                    "bbox_3d": [0, 0, 0, 1, 1, 1],
                    "display_name": "Red block",
                    "last_seen_step": 2,
                    "state_tags": [],
                }
            ],
        }
    )
    o = mem.objects["a"]
    assert o.position == (1.0, 2.0, 3.0)
    assert o.display_name == "Red block"
    assert o.last_seen_step == 2


def test_pretty_print() -> None:
    mem = SceneMemoryBuilder.from_teacher_payload(
        {
            "objects": [
                {
                    "id": "x",
                    "name": "x",
                    "position": [0, 0, 0],
                    "state_tags": [],
                }
            ],
            "relations": [],
        }
    )
    s = mem.pretty_print()
    assert "x" in s
