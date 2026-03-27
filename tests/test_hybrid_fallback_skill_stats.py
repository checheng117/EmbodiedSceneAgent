"""Hybrid fallback_stats includes skill normalization counters."""

from __future__ import annotations

from types import SimpleNamespace

from embodied_scene_agent.evaluation.hybrid_replanner_smoke import _fallback_stats_from_traces


def test_fallback_stats_skill_fields() -> None:
    trace = SimpleNamespace(
        steps=[
            {
                "replan_audit": {
                    "llm_replanner_called": True,
                    "replanner_parse_ok": True,
                    "revised_plan_validated": True,
                    "skill_alias_normalized_from": "pick",
                    "replanner_parse_error_kind": None,
                }
            },
            {
                "replan_audit": {
                    "llm_replanner_called": True,
                    "replanner_parse_ok": False,
                    "revised_plan_validated": False,
                    "replanner_parse_error_kind": "invalid_skill",
                }
            },
        ]
    )
    fb = _fallback_stats_from_traces([trace])
    assert fb["llm_replanner_calls"] == 2
    assert fb["alias_normalization_count"] == 1
    assert fb["invalid_skill_count"] == 1
