"""CALVIN-grounded minimal loop + adapter smoke tests (no benchmark scores)."""

from __future__ import annotations

import pytest

from embodied_scene_agent.envs.calvin import CalvinEnvAdapter
from embodied_scene_agent.pipeline.run_calvin_minimal_loop import run_calvin_minimal_episode
from embodied_scene_agent.training.build_planner_data import export_trace_to_jsonl, iter_planner_rows_from_calvin_trace
from embodied_scene_agent.utils.paths import repo_root


def test_run_calvin_minimal_episode_fixture_success():
    trace = run_calvin_minimal_episode(
        "Put the red block in the drawer.",
        fixture_path=repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json",
        max_steps=12,
    )
    assert trace.success is True
    assert trace.final_message.startswith("task_success")
    assert len(trace.steps) >= 1
    assert all("scene_memory_before" in s for s in trace.steps)
    assert all(s.get("executor_mode", "").startswith("symbolic") for s in trace.steps)
    assert trace.env_mode == "fixture"
    assert trace.teacher_source == "fixture_json"
    assert trace.action_mode == "fixture_symbolic"
    assert trace.trace_id
    assert not trace.whether_live_step_executed
    assert not trace.loop_fallback_reason


def test_build_planner_data_rows_roundtrip(tmp_path):
    trace = run_calvin_minimal_episode(
        "Put the red block in the drawer.",
        fixture_path=repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json",
        max_steps=8,
    )
    rows = list(iter_planner_rows_from_calvin_trace(trace))
    assert len(rows) == len(trace.steps)
    assert rows[0]["metadata"]["source"] == "calvin"
    out = tmp_path / "rows.jsonl"
    n = export_trace_to_jsonl(trace, out)
    assert n == len(rows)
    assert out.read_text(encoding="utf-8").count("\n") == n
    meta = rows[0]["metadata"]
    assert "trace_id" in meta
    assert meta.get("env_mode") == "fixture"
    assert meta.get("data_lineage") == "fixture"


class _FakePlayTableEnv:
    """Duck-typed stub: only for adapter reset + mapper wiring tests (not real CALVIN)."""

    def get_obs(self):
        return {
            "rgb_obs": {"rgb_static": None},
            "depth_obs": {},
            "robot_obs": [0.0] * 8,
            "scene_obs": [0.0] * 8,
        }

    def reset(self, robot_obs=None, scene_obs=None):
        return self.get_obs()

    def get_info(self):
        return {
            "robot_info": {
                "gripper_opening_width": 0.08,
                "tcp_pos": [0.4, 0.0, 0.3],
            },
            "scene_info": {
                "doors": {"left_slider": {"current_state": 0.02}},
                "movable_objects": {
                    "red_cube_0": {
                        "current_pos": [0.45, 0.0, 0.12],
                        "current_orn": [0.0, 0.0, 0.0, 1.0],
                        "uid": "red_cube_0",
                    }
                },
            },
        }

    def step(self, action):
        return (self.get_obs(), 0.0, False, {})


def test_run_calvin_minimal_episode_live_step_sets_flags():
    trace = run_calvin_minimal_episode(
        "Put the red block in the drawer.",
        calvin_env=_FakePlayTableEnv(),
        max_steps=2,
        live_action_strategy="live_zero_action_smoke",
    )
    assert trace.env_mode == "live_env"
    assert trace.action_mode == "live_zero_action_smoke"
    assert trace.whether_live_step_executed
    assert trace.live_step_attempted
    assert trace.steps and all(s.get("live_step_executed") for s in trace.steps)


def test_try_local_factory_fallback_without_env_var(monkeypatch):
    monkeypatch.delenv("ESA_CALVIN_ENV_FACTORY", raising=False)
    trace = run_calvin_minimal_episode(
        "Put the red block in the drawer.",
        try_local_factory=True,
        max_steps=2,
    )
    assert trace.env_mode == "fixture"
    assert "factory_unavailable" in trace.loop_fallback_reason


def test_live_symbolic_fallback_marks_trace():
    trace = run_calvin_minimal_episode(
        "Put the red block in the drawer.",
        calvin_env=_FakePlayTableEnv(),
        max_steps=1,
        live_action_strategy="symbolic_fallback",
    )
    assert trace.action_mode == "live_observation_symbolic_fallback"
    assert trace.steps
    assert "symbolic_fallback_while_live_reset" in trace.steps[0]["skill_result"]["delta"]


def test_calvin_adapter_live_reset_maps_teacher():
    env = CalvinEnvAdapter(calvin_env=_FakePlayTableEnv())
    bundle = env.reset("open the drawer")
    assert "calvin_teacher_v0" in bundle["observation"]
    teacher = bundle["observation"]["calvin_teacher_v0"]
    assert teacher["language"]["instruction"] == "open the drawer"
    mem = env.build_scene_memory()
    assert "drawer" in mem.objects
    assert "red_block" in mem.objects


def test_calvin_adapter_step_not_implemented():
    adapter = CalvinEnvAdapter(fixture_path=repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json")
    adapter.reset("x")
    with pytest.raises(NotImplementedError):
        adapter.step([0.0])


def test_calvin_adapter_live_step_refreshes_teacher():
    adapter = CalvinEnvAdapter(calvin_env=_FakePlayTableEnv())
    adapter.reset("probe")
    adapter.step(None)
    assert adapter.get_raw_observation().get("robot_obs") is not None


def test_calvin_adapter_symbolic_apply_skill_with_live_env_mutates_teacher():
    """Live reset + symbolic skill: teacher updates without env.step (documented dev semantics)."""
    from embodied_scene_agent.planner.schema import PlannerOutput
    from embodied_scene_agent.skills.base import SkillContext
    from embodied_scene_agent.skills.executor import SkillExecutor

    adapter = CalvinEnvAdapter(calvin_env=_FakePlayTableEnv())
    adapter.reset("Put the red block in the drawer.")
    plan = PlannerOutput(
        task="open_drawer",
        subgoal="Open the drawer fully.",
        target_object="drawer",
        skill="open",
        success_check="drawer has state tag 'open'",
    )
    SkillExecutor().run(SkillContext(env=adapter, target_object_id="drawer", planner_output=plan))
    mem = adapter.build_scene_memory()
    assert "open" in mem.objects["drawer"].state_tags
