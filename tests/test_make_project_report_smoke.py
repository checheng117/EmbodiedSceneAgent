from __future__ import annotations

from embodied_scene_agent.reporting.make_project_report import build_report_payload
from embodied_scene_agent.utils.paths import repo_root


def test_build_report_payload_structure() -> None:
    p = build_report_payload(repo_root())
    assert "project_status_snapshot" in p
    assert "e2_ablation_snapshot" in p
    assert "e2_on_mock" in p["e2_ablation_snapshot"]
    assert "rlbench_bridge_status" in p
    ls = (p.get("rlbench_bridge_status") or {}).get("layer_status")
    if ls is not None:
        assert "import" in ls or "memory_bridge" in ls
