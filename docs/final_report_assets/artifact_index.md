# Artifact index (read order)

_Repo: this git clone (the directory that contains `pyproject.toml`)._

| Priority | Path | Why |
|----------|------|-----|
| 1 | `docs/final_report_assets/one_page_project_brief.md` | Fastest narrative for visitors / mentors. |
| 2 | `docs/final_report_assets/report_outline_final.md` | Full section-by-section evidence vs gaps. |
| 3 | `results/reports/latest_project_report.json` | Machine-readable single source for dashboards. |
| 4 | `docs/final_report_assets/tables/current_main_results_table.md` | Main quantitative pointers. |
| 5 | `docs/final_report_assets/case_studies/` | Report-ready case templates. |
| 6 | `docs/final_report_assets/limitations.md` | Non-negotiable honest boundaries. |
| 7 | `docs/narrative_consistency_audit.md` | Checklist: cognition layer vs policy vs benchmarks. |
| 8 | `docs/evidence_consistency_audit.md` | Paths + consistency checks. |
| 9 | `docs/figures/architecture_v2.svg` | Primary architecture figure. |
| 10 | `results/demos/e2_ablation_cases/` | Stable E2 demo JSON + selection meta. |
| 11 | `docs/calvin_debug_dataset_audit.md` | Official debug npz layout + honest gaps. |
| 12 | `docs/calvin_debug_real_data_stats.md` | Planner export from debug vectors (counts + lineage). |
| 13 | `docs/tables/e2_ablation_mock_vs_calvin_fixture_vs_calvin_debug_real.md` | Three-way E2 comparison table. |

## Auto bundle

- Run `bash scripts/build_final_report_assets.sh` after new experiments.
