from __future__ import annotations

from pathlib import Path

from embodied_scene_agent.reporting.make_project_report import build_report_payload, render_markdown
from embodied_scene_agent.utils.paths import repo_root


def test_build_report_payload_keys() -> None:
    root = repo_root()
    p = build_report_payload(root)
    assert "generated_utc" in p
    assert "failure_taxonomy" in p
    assert isinstance(p["failure_taxonomy"], list)
    md = render_markdown(p)
    assert "Failure taxonomy" in md


def test_export_demo_smoke(tmp_path: Path, monkeypatch) -> None:
    import embodied_scene_agent.reporting.export_demo_assets as ed

    monkeypatch.setattr(ed, "repo_root", lambda: tmp_path)
    ed.main()
    assert (tmp_path / "results" / "demos" / "success_put_block" / "case_summary.md").is_file()
