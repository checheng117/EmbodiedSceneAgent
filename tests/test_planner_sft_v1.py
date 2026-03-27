"""Planner SFT v1 prompt / export smoke tests."""

from __future__ import annotations

from embodied_scene_agent.training.agent_prompt import build_user_prompt, format_plan_block, parse_planner_completion
from embodied_scene_agent.training.mock_rollout_export import iter_rows_from_v0_trace, run_export_episode
from embodied_scene_agent.evaluation.planner_eval_utils import format_compliance_ok, last_skill_from_plans


def test_parse_planner_completion_roundtrip() -> None:
    plan = {
        "task": "open_drawer",
        "subgoal": "Open the drawer.",
        "target_object": "drawer",
        "skill": "open",
        "success_check": "drawer has state tag 'open'",
        "fallback": "retry",
    }
    text = format_plan_block(plan)
    parsed = parse_planner_completion(text)
    assert parsed is not None
    assert parsed["skill"] == "open"
    assert parsed["target_object"] == "drawer"


def test_build_user_prompt_contains_tools() -> None:
    u = build_user_prompt(
        instruction="Put the block in the drawer.",
        scene_memory={"objects": {}, "schema_version": "esa_sm/v1"},
        history=[],
        failure_log=[],
    )
    assert "grasp" in u
    assert "Scene memory" in u


def test_mock_rollout_export_has_v1_fields() -> None:
    trace, rows = run_export_episode(
        "Put the red block in the drawer.",
        episode_id="test::ep",
        split="train",
        forced_grasp_failures=0,
        max_steps=8,
    )
    assert trace.success
    assert rows
    assert rows[0]["schema_version"] == "planner_sft/v1"
    assert "user_prompt" in rows[0]
    assert "target_text" in rows[0]
    types = {r["trajectory_type"] for r in rows}
    assert "normal" in types or "multi_step" in types


def test_iter_rows_trajectory_recovery_when_replan() -> None:
    trace, rows = run_export_episode(
        "Put the red block in the drawer.",
        episode_id="test::re",
        split="train",
        forced_grasp_failures=1,
        max_steps=12,
    )
    assert any(r["trajectory_type"] == "recovery" for r in rows)


def test_format_compliance_on_target() -> None:
    _, rows = run_export_episode(
        "Open the drawer.",
        episode_id="x",
        split="train",
        forced_grasp_failures=0,
        max_steps=4,
    )
    assert format_compliance_ok(rows[0]["target_text"])
    assert last_skill_from_plans(rows[0]["target_text"])
