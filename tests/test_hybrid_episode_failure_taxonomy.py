from __future__ import annotations

import json

from embodied_scene_agent.reporting.make_project_report import _hybrid_eval_latest_where
from embodied_scene_agent.verifier.taxonomy import classify_hybrid_episode_failure


def test_classify_semantically_bad_valid_replan_from_missing_target() -> None:
    step = {
        "timestep": 0,
        "scene_memory_after_first": {"objects": {"drawer": {}, "table": {}}},
        "replan": {
            "task": "place",
            "subgoal": "in the workspace",
            "target_object": "workspace",
            "skill": "move_to",
            "success_check": "noop",
        },
        "replan_audit": {
            "revised_plan_validated": True,
        },
        "verification_replan": {
            "success": False,
            "failure_type": "target_not_found",
            "details": "target workspace missing in after memory",
        },
    }

    out = classify_hybrid_episode_failure([step], final_message="horizon_or_verify_failure")

    assert out["episode_failure_label"] == "schema_valid_but_semantically_bad_replan"
    assert out["terminal_failure_label"] == "schema_valid_but_semantically_bad_replan"
    assert "target_missing_after_valid_replan" in out["label_reasons"]
    assert "target_absent_from_scene_memory" in out["label_reasons"]


def test_classify_terminal_state_unchanged_after_valid_replan() -> None:
    step = {
        "timestep": 9,
        "replan": {
            "task": "open_drawer_retry",
            "subgoal": "Retry opening the drawer.",
            "target_object": "drawer",
            "skill": "open",
            "success_check": "drawer has state tag 'open'",
        },
        "replan_audit": {
            "revised_plan_validated": True,
        },
        "skill_result_replan": {
            "success": True,
            "message": "open",
        },
        "verification_replan": {
            "success": False,
            "failure_type": "state_unchanged",
            "details": "open had no effect",
        },
    }

    out = classify_hybrid_episode_failure([step], final_message="horizon_or_verify_failure")

    assert out["episode_failure_label"] == "no_state_change_after_valid_replan"
    assert out["terminal_failure_label"] == "no_state_change_after_valid_replan"
    assert out["terminal_failure_type"] == "state_unchanged"


def test_classify_repeated_no_effect_guard_exhaustion() -> None:
    step = {
        "timestep": 2,
        "replan_audit": {
            "revised_plan_validated": True,
            "repeated_no_effect_detected": True,
            "repeated_no_effect_signature": "open::drawer",
            "repeated_no_effect_consecutive": 2,
            "repeated_no_effect_stop": True,
        },
        "repeated_no_effect_guard": {
            "triggered": True,
            "signature": {"skill": "open", "target_object": "drawer"},
            "consecutive_no_effect_count": 2,
            "threshold": 2,
            "source": "verification_replan",
        },
        "verification_replan": {
            "success": False,
            "failure_type": "state_unchanged",
            "details": "open had no effect",
        },
    }

    out = classify_hybrid_episode_failure(
        [step], final_message="repeated_no_effect_fallback_exhausted"
    )

    assert out["episode_failure_label"] == "repeated_no_effect_fallback_exhausted"
    assert out["terminal_failure_label"] == "repeated_no_effect_fallback_exhausted"
    assert out["terminal_failure_type"] == "state_unchanged"


def test_classify_horizon_without_stronger_signal() -> None:
    step = {
        "timestep": 4,
        "verification": {
            "success": False,
            "failure_type": "unknown_failure",
            "details": "ambiguous diff",
        },
    }

    out = classify_hybrid_episode_failure([step], final_message="horizon_or_verify_failure")

    assert out["episode_failure_label"] == "environment_or_horizon_limit"
    assert out["terminal_failure_label"] == "environment_or_horizon_limit"


def test_hybrid_eval_snapshot_reads_refined_failure_counts(tmp_path) -> None:
    run = tmp_path / "results" / "experiments" / "hybrid_replanner_eval" / "hybrid_test_001"
    run.mkdir(parents=True)
    (run / "metrics.json").write_text(
        json.dumps(
            {
                "backend": "calvin_debug_real",
                "replan_parse_success_rate": 1.0,
                "validated_revision_rate": 1.0,
                "fallback_rate": 0.0,
                "repair_success_rate": 0.0,
                "unknown_failure_rate": 0.1,
                "unknown_skill_rate": 0.0,
                "alias_normalization_count": 0,
                "invalid_skill_count": 0,
                "acceptance_rejection_reason_counts": {
                    "target_absent_from_scene_memory": 2,
                },
                "episode_failure_label_counts": {
                    "schema_valid_but_semantically_bad_replan": 2,
                    "no_state_change_after_valid_replan": 1,
                },
                "terminal_failure_label_counts": {
                    "no_state_change_after_valid_replan": 3,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (run / "fallback_stats.json").write_text(json.dumps({}), encoding="utf-8")

    snap = _hybrid_eval_latest_where(tmp_path, lambda m: m.get("backend") == "calvin_debug_real")

    assert snap is not None
    assert snap["acceptance_rejection_reason_counts"]["target_absent_from_scene_memory"] == 2
    assert snap["episode_failure_label_counts"]["schema_valid_but_semantically_bad_replan"] == 2
    assert snap["terminal_failure_label_counts"]["no_state_change_after_valid_replan"] == 3
