from __future__ import annotations

from embodied_scene_agent.reporting.make_project_report import build_report_payload
from embodied_scene_agent.utils.paths import repo_root


def test_build_report_has_dashboard_fields() -> None:
    p = build_report_payload(repo_root())
    assert "project_status_snapshot" in p
    assert "e2_ablation_snapshot" in p
    assert "rlbench_bridge_status" in p
    assert "hybrid_replanner_status" in p
    assert "reproducibility_snapshot" in p
    assert "open_gaps_limitations" in p
