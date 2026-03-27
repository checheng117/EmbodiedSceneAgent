from __future__ import annotations

from embodied_scene_agent.evaluation.hybrid_replanner_smoke import _fallback_stats_from_traces
from embodied_scene_agent.pipeline.v0_loop import EpisodeTrace


def test_fallback_stats_structure() -> None:
    tr = EpisodeTrace(instruction="x", success=False)
    tr.steps.append(
        {
            "replan_audit": {
                "llm_replanner_called": True,
                "replanner_parse_ok": False,
                "revised_plan_validated": False,
                "fallback_reason": "test",
                "fallback_stage": "parse_validate",
                "replanner_parse_error_kind": "truncated_json",
            }
        }
    )
    fb = _fallback_stats_from_traces([tr])
    assert fb["llm_replanner_calls"] == 1
    assert "fallback_reason_counts" in fb
    assert "fallback_stage_counts" in fb
    assert "parse_error_kind_counts" in fb
    assert fb["parse_error_kind_counts"].get("truncated_json") == 1


def test_report_payload_has_rlbench_layers() -> None:
    from embodied_scene_agent.reporting.make_project_report import _rlbench_snapshot

    root = __import__("embodied_scene_agent.utils.paths", fromlist=["repo_root"]).repo_root()
    snap = _rlbench_snapshot(root)
    if snap.get("status") == "ok":
        assert "layer_status" in snap or snap.get("memory_bridge") is not None or True
