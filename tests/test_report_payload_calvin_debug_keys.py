"""Smoke: report payload includes CALVIN debug real slots (structure only)."""

from __future__ import annotations

from embodied_scene_agent.reporting.make_project_report import build_report_payload
from embodied_scene_agent.utils.paths import repo_root


def test_e2_snapshot_has_calvin_debug_real_key() -> None:
    p = build_report_payload(repo_root())
    e2 = p.get("e2_ablation_snapshot") or {}
    assert "e2_on_calvin_debug_real" in e2
    assert "status" in (e2["e2_on_calvin_debug_real"] or {})
    assert "e2_on_calvin_debug_real_aligned" in e2
    assert "e2_on_calvin_debug_same_task" in e2


def test_hybrid_status_has_eval_batch_calvin_debug_slot() -> None:
    p = build_report_payload(repo_root())
    hy = p.get("hybrid_replanner_status") or {}
    assert "eval_batch_calvin_debug_real" in hy
    assert "eval_batch_calvin_debug_real_aligned" in hy
    assert "eval_batch_calvin_debug_same_task" in hy
