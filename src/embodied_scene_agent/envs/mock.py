"""Toy environment for v0 closed-loop testing."""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.envs.base import BaseEmbodiedEnv


class MockEmbodiedEnv(BaseEmbodiedEnv):
    """
    Deterministic table + drawer + block scene.

    Teacher-state format matches `SceneMemoryBuilder.from_teacher_payload`.
    """

    def __init__(self, *, default_forced_grasp_failures: int = 0) -> None:
        self._instruction: str = ""
        self._step: int = 0
        self._drawer_open: bool = False
        self._block_held: bool = False
        self._block_in_drawer: bool = False
        self._default_forced_grasp_failures = max(0, default_forced_grasp_failures)
        self._forced_grasp_failures: int = 0

    def reset(self, instruction: str, **kwargs: Any) -> dict[str, Any]:
        self._instruction = instruction
        self._step = 0
        self._drawer_open = False
        self._block_held = False
        self._block_in_drawer = False
        self._forced_grasp_failures = self._default_forced_grasp_failures
        return {"instruction": instruction, "teacher_state": self.get_teacher_state()}

    def set_default_forced_grasp_failures(self, n: int) -> None:
        """Configure how many grasp attempts return False without state change (for replan tests)."""
        self._default_forced_grasp_failures = max(0, n)

    def get_teacher_state(self) -> dict[str, Any]:
        """Serialize internal discrete state to teacher dict."""
        objects: list[dict[str, Any]] = [
            {
                "id": "table",
                "name": "table",
                "position": [0.5, 0.0, 0.0],
                "bbox": [0.0, 0.0, 0.0, 1.0, 0.1, 0.5],
                "state_tags": ["static"],
                "confidence": 1.0,
            },
            {
                "id": "drawer",
                "name": "drawer",
                "position": [0.6, 0.0, 0.35],
                "bbox": [0.55, -0.05, 0.25, 0.65, 0.05, 0.45],
                "state_tags": self._drawer_tags(),
                "confidence": 1.0,
            },
            {
                "id": "red_block",
                "name": "red block",
                "position": [0.45, 0.0, 0.12] if not self._block_held else [0.55, 0.0, 0.25],
                "bbox": [0.42, -0.02, 0.08, 0.48, 0.02, 0.16],
                "state_tags": self._block_tags(),
                "confidence": 1.0,
            },
        ]
        if self._block_held:
            objects.append(
                {
                    "id": "gripper",
                    "name": "gripper",
                    "position": [0.5, 0.0, 0.2],
                    "bbox": [0.48, -0.02, 0.15, 0.52, 0.02, 0.25],
                    "state_tags": ["end_effector"],
                    "confidence": 1.0,
                }
            )
        return {
            "frame_id": str(self._step),
            "objects": objects,
            "relations": self._relations(),
        }

    def _relations(self) -> list[dict[str, str]]:
        rels: list[dict[str, str]] = []
        if self._block_in_drawer:
            rels.append({"subject_id": "red_block", "object_id": "drawer", "relation": "in"})
        elif not self._block_held:
            rels.append({"subject_id": "red_block", "object_id": "table", "relation": "on"})
        else:
            rels.append({"subject_id": "red_block", "object_id": "gripper", "relation": "on"})
        return rels

    def _drawer_tags(self) -> list[str]:
        return ["open"] if self._drawer_open else ["closed"]

    def _block_tags(self) -> list[str]:
        tags: list[str] = []
        if self._block_in_drawer:
            tags.append("in_drawer")
        if self._block_held:
            tags.append("held")
        if not self._block_in_drawer and not self._block_held:
            tags.append("on_table")
        return tags

    def apply_skill(self, skill: str, target_object_id: str) -> bool:
        """
        Execute one high-level skill on the mock world.

        Returns:
            True if the skill application was physically valid in mock semantics.
        """
        self._step += 1
        if skill == "open" and target_object_id == "drawer":
            if not self._drawer_open:
                self._drawer_open = True
            return True

        if skill == "close" and target_object_id == "drawer":
            if self._drawer_open and not self._block_in_drawer:
                self._drawer_open = False
            return True

        if skill == "grasp" and target_object_id == "red_block":
            if self._block_in_drawer:
                return False
            if self._forced_grasp_failures > 0:
                self._forced_grasp_failures -= 1
                return False
            if not self._block_held:
                self._block_held = True
            return True

        if skill == "place" and target_object_id == "drawer":
            if not self._drawer_open:
                return False
            if not self._block_held:
                return False
            self._block_held = False
            self._block_in_drawer = True
            return True

        if skill in {"reach", "move_to"}:
            return True

        return False

    def task_success(self) -> bool:
        """Long-horizon success: block inside drawer."""
        return self._block_in_drawer
