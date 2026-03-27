"""VLABench evaluation adapter (skeleton, planner/reasoning stress)."""

from __future__ import annotations

from typing import Any

from embodied_scene_agent.envs.base import BaseEmbodiedEnv


class VLABenchEvalAdapter(BaseEmbodiedEnv):
    """TODO: planner-only or partial control rollouts per blueprint."""

    def __init__(self, **_kwargs: Any) -> None:
        self._kwargs = _kwargs

    def reset(self, instruction: str) -> dict[str, Any]:
        raise NotImplementedError("VLABenchEvalAdapter.reset not wired in v0.")

    def get_teacher_state(self) -> dict[str, Any]:
        raise NotImplementedError("VLABenchEvalAdapter.get_teacher_state not wired in v0.")
