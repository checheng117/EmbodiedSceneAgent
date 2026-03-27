from __future__ import annotations

from embodied_scene_agent.reporting.make_project_report import build_report_payload
from embodied_scene_agent.utils.paths import repo_root


def test_build_report_payload_has_rlbench_hybrid_e2_fields() -> None:
    root = repo_root()
    p = build_report_payload(root)
    snap = p.get("project_status_snapshot") or {}
    assert "rlbench_deepest_reached_stage" in snap
    assert "rlbench_blocker_summary" in snap
    assert "hybrid_parse_error_breakdown" in snap
    assert "e2_best_case_paths" in snap
    assert "mock_vs_calvin_short_note" in snap
    uhf = p.get("unified_headline_facts") or {}
    assert isinstance(uhf, dict)
    assert "rlbench_deepest_stage" in uhf
    assert "open_gaps" in uhf
