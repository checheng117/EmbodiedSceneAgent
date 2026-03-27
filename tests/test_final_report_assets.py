from __future__ import annotations

import json

from embodied_scene_agent.reporting.build_final_report_assets import run_build
from embodied_scene_agent.utils.paths import repo_root

REQUIRED_RELATIVE = [
    "docs/final_report_assets/report_outline_final.md",
    "docs/final_report_assets/executive_summary.md",
    "docs/final_report_assets/abstract_candidates.md",
    "docs/final_report_assets/appendix_notes.md",
    "docs/final_report_assets/limitations.md",
    "docs/final_report_assets/reproducibility.md",
    "docs/final_report_assets/artifact_index.md",
    "docs/final_report_assets/one_page_project_brief.md",
    "docs/final_report_assets/advisor_brief.md",
    "docs/final_report_assets/interview_brief.md",
    "docs/final_report_assets/tables/current_main_results_table.md",
    "docs/final_report_assets/tables/benchmark_coverage_table.md",
    "docs/final_report_assets/tables/system_status_table.md",
    "docs/final_report_assets/figures/architecture_final.svg",
    "docs/final_report_assets/case_studies/rlbench_bridge_case.md",
    "results/final_report_assets/unified_headlines.json",
    "results/final_report_assets/manifest.json",
    "docs/narrative_consistency_audit.md",
    "docs/evidence_consistency_audit.md",
]


def test_final_report_assets_bundle() -> None:
    """Regenerates assets (skip README patch to avoid mutating repo under parallel tests)."""
    root = repo_root()
    run_build(root=root, skip_readme_patch=True)
    missing = [r for r in REQUIRED_RELATIVE if not (root / r).is_file()]
    assert not missing, f"missing: {missing}"

    lim = (root / "docs/final_report_assets/limitations.md").read_text(encoding="utf-8")
    assert "RLBench" in lim and "future_only" in lim

    mt = (root / "docs/final_report_assets/tables/current_main_results_table.md").read_text(encoding="utf-8")
    assert "|" in mt and "Artifact" in mt

    uhf = json.loads((root / "results/final_report_assets/unified_headlines.json").read_text(encoding="utf-8"))
    assert "rlbench_deepest_stage" in uhf
    assert "open_gaps" in uhf

    ev = (root / "docs/evidence_consistency_audit.md").read_text(encoding="utf-8")
    assert "Evidence consistency audit" in ev
