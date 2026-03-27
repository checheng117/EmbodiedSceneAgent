"""CALVIN adapter: fixture / ingest dev path + optional live ``calvin_env`` handle (explicit TODOs)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from embodied_scene_agent.envs.base import BaseEmbodiedEnv
from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.perception.calvin_field_mapper import (
    apply_symbolic_plan_to_calvin_teacher_v0,
    map_live_calvin_to_teacher_bundle,
)
from embodied_scene_agent.perception.calvin_teacher import CalvinTeacherStateAdapter
from embodied_scene_agent.planner.schema import PlannerOutput


class CalvinEnvAdapter(BaseEmbodiedEnv):
    """
    Development wrapper for CALVIN-shaped observations.

    Modes (at most one primary source):

    - **Fixture / initial_observation**: JSON or dict with ``calvin_teacher_v0`` (existing dev path).
    - **Live ``calvin_env``**: duck-typed ``PlayTableSimEnv``-like object; only partially wired — see method docstrings.

    This does **not** implement the official CALVIN benchmark protocol or leaderboard integration.
    """

    def __init__(
        self,
        *,
        fixture_path: str | Path | None = None,
        initial_observation: dict[str, Any] | None = None,
        calvin_env: Any | None = None,
    ) -> None:
        sources = [fixture_path is not None, initial_observation is not None, calvin_env is not None]
        if sum(sources) > 1:
            raise ValueError("Provide at most one of fixture_path, initial_observation, calvin_env.")
        self._fixture_path = Path(fixture_path) if fixture_path is not None else None
        self._initial_observation = initial_observation
        self._calvin_env = calvin_env
        self._observation: dict[str, Any] = {}
        self._instruction: str = ""
        self._raw_observation: dict[str, Any] | None = None
        self._raw_info: dict[str, Any] | None = None
        self._step_index: int = 0

    def reset(self, instruction: str, **kwargs: Any) -> dict[str, Any]:
        self._instruction = instruction
        self._raw_observation = None
        self._raw_info = None
        self._step_index = 0

        if self._calvin_env is not None:
            self._observation = self._reset_live_calvin(instruction, **kwargs)
        elif self._fixture_path is not None:
            text = self._fixture_path.read_text(encoding="utf-8")
            self._observation = json.loads(text)
            self._inject_instruction(instruction)
        elif self._initial_observation is not None:
            self._observation = copy.deepcopy(self._initial_observation)
            self._inject_instruction(instruction)
        else:
            self._observation = {}
            self._inject_instruction(instruction)

        return {"instruction": instruction, "observation": self._observation}

    def _reset_live_calvin(self, instruction: str, **kwargs: Any) -> dict[str, Any]:
        env = self._calvin_env
        reset_fn = getattr(env, "reset", None)
        if reset_fn is None:
            raise NotImplementedError(
                "CalvinEnvAdapter: live env has no reset(); cannot obtain CALVIN observation."
            )
        robot_obs = kwargs.get("robot_obs")
        scene_obs = kwargs.get("scene_obs")
        try:
            if robot_obs is not None or scene_obs is not None:
                obs = reset_fn(robot_obs=robot_obs, scene_obs=scene_obs)
            else:
                obs = reset_fn()
        except TypeError as e:
            raise NotImplementedError(
                "CalvinEnvAdapter: calvin_env.reset() failed; pass robot_obs= / scene_obs= as required by "
                "PlayTableSimEnv.reset (see docs/calvin_real_fields_audit.md §1.5)."
            ) from e

        get_info = getattr(env, "get_info", None)
        if get_info is None:
            raise NotImplementedError("CalvinEnvAdapter: live env has no get_info() — cannot map to teacher bundle.")
        info = get_info()
        if not isinstance(obs, dict):
            raise NotImplementedError(
                "CalvinEnvAdapter: expected reset() to return an observation dict (get_obs shape); got "
                f"{type(obs).__name__}."
            )
        if not isinstance(info, dict):
            raise NotImplementedError(
                f"CalvinEnvAdapter: get_info() must return dict, got {type(info).__name__}."
            )

        self._raw_observation = obs
        self._raw_info = info

        try:
            bundle = map_live_calvin_to_teacher_bundle(obs, info, instruction, frame_id="0")
        except ValueError as e:
            raise NotImplementedError(
                "CalvinEnvAdapter: mapping obs/info to calvin_teacher_v0 failed — ensure use_scene_info=True "
                "on PlayTableSimEnv so info['scene_info'] is populated (see calvin_field_mapper docstring)."
            ) from e
        return bundle

    def refresh_teacher_from_live(self) -> dict[str, Any]:
        """
        Re-read ``get_obs()`` + ``get_info()`` and rebuild ``calvin_teacher_v0`` (live path only).

        Raises:
            NotImplementedError: if no live env or CALVIN APIs missing.
        """
        if self._calvin_env is None:
            raise NotImplementedError(
                "CalvinEnvAdapter.refresh_teacher_from_live: only valid with calvin_env handle."
            )
        get_obs = getattr(self._calvin_env, "get_obs", None)
        get_info = getattr(self._calvin_env, "get_info", None)
        if not callable(get_obs) or not callable(get_info):
            raise NotImplementedError("calvin_env must expose get_obs() and get_info() for refresh.")
        obs = get_obs()
        info = get_info()
        if not isinstance(obs, dict) or not isinstance(info, dict):
            raise NotImplementedError(
                f"refresh_teacher_from_live: expected dict obs/info, got {type(obs).__name__}/{type(info).__name__}."
            )
        self._raw_observation = obs
        self._raw_info = info
        self._step_index += 1
        bundle = map_live_calvin_to_teacher_bundle(
            obs, info, self._instruction, frame_id=str(self._step_index)
        )
        self._observation = bundle
        self._inject_instruction(self._instruction)
        return self._observation

    def _inject_instruction(self, instruction: str) -> None:
        teacher = self._observation.setdefault("calvin_teacher_v0", {})
        lang = teacher.setdefault("language", {})
        lang["instruction"] = instruction

    def get_raw_observation(self) -> dict[str, Any]:
        """
        Last low-level observation dict from ``calvin_env`` after :meth:`reset` / :meth:`step`, if any.

        Fixture-only mode returns an empty dict (no simulator observation).
        """
        if self._raw_observation is not None:
            return dict(self._raw_observation)
        return {}

    def get_raw_info(self) -> dict[str, Any] | None:
        """Last ``get_info()`` dict from live env, or ``None`` in fixture mode."""
        if self._raw_info is not None:
            return dict(self._raw_info)
        return None

    def get_teacher_state(self) -> dict[str, Any]:
        """Full observation bundle (includes ``calvin_teacher_v0`` when present)."""
        return self._observation

    def build_scene_memory(self, instruction: str | None = None) -> SceneMemory:
        inst = self._instruction if instruction is None else instruction
        adapter = CalvinTeacherStateAdapter()
        return adapter.to_scene_memory(inst, self.get_teacher_state())

    def step(self, action: Any) -> tuple[dict[str, Any], float, bool, dict[str, Any]]:
        """
        Live low-level step: ``normalize_calvin_live_action`` → ``calvin_env.step`` → refresh teacher from
        ``get_obs`` / ``get_info``.

        See ``docs/calvin_action_contract.md``. **Fixture path** raises — no silent symbolic fallback.
        """
        if self._calvin_env is None:
            raise NotImplementedError(
                "CalvinEnvAdapter.step: no live calvin_env — cannot step. Use symbolic executor "
                "(apply_symbolic_planner_output / apply_skill) or attach PlayTableSimEnv."
            )
        from embodied_scene_agent.envs.calvin_action import normalize_calvin_live_action

        step_fn = getattr(self._calvin_env, "step", None)
        if not callable(step_fn):
            raise NotImplementedError("CalvinEnvAdapter.step: calvin_env has no callable step().")

        normalized = normalize_calvin_live_action(action)
        raw_out = step_fn(normalized)

        reward = 0.0
        done = False
        step_info: dict[str, Any] = {}
        if isinstance(raw_out, tuple):
            if len(raw_out) >= 4:
                reward = float(raw_out[1])
                done = bool(raw_out[2])
                si = raw_out[3]
                if isinstance(si, dict):
                    step_info = si
            elif len(raw_out) == 3:
                reward = float(raw_out[1])
                done = bool(raw_out[2])

        self.refresh_teacher_from_live()
        return (self._observation, reward, done, step_info)

    def apply_symbolic_planner_output(self, plan: PlannerOutput) -> None:
        """
        **Dev-only executor**: mutate ``calvin_teacher_v0`` in place (no PyBullet).

        Used by the CALVIN-grounded minimal loop when real skill controllers are unavailable.
        """
        teacher = self._observation.setdefault("calvin_teacher_v0", {})
        apply_symbolic_plan_to_calvin_teacher_v0(teacher, plan)

    def apply_skill(self, skill: str, target_object_id: str) -> bool:
        """
        Routes to :meth:`apply_symbolic_planner_output` (teacher-state mutation only).

        **Important**: with a live ``calvin_env``, this still does **not** call ``env.step`` — the PyBullet state
        and ``calvin_teacher_v0`` may **diverge**. Use only for planner SFT / dev tracing until a real controller
        is wired.
        """
        plan = PlannerOutput(
            task="symbolic_adhoc",
            subgoal=f"{skill} {target_object_id}",
            target_object=target_object_id,
            skill=skill,
            success_check="symbolic",
            fallback="",
            reasoning="CalvinEnvAdapter.apply_skill symbolic bridge",
            confidence=None,
        )
        self.apply_symbolic_planner_output(plan)
        return True

    def task_success_symbolic(self) -> bool:
        """True if :class:`SceneMemory` shows ``red_block`` with ``in_drawer`` tag (fixture / symbolic semantics)."""
        mem = self.build_scene_memory()
        rb = mem.objects.get("red_block")
        return rb is not None and "in_drawer" in rb.state_tags

    def ingest_observation(self, observation: dict[str, Any]) -> None:
        """Replace internal bundle (e.g. after an external env step)."""
        self._observation = copy.deepcopy(observation)
        if self._instruction:
            self._inject_instruction(self._instruction)
