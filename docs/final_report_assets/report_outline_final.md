# Final report outline (blueprint-aligned)

_Generated: `2026-03-27T14:22:34.108702+00:00`_ · Source sketch: `docs/report_outline.md`

Each section lists: **Evidence paths** · **Strongest defensible statement** · **Explicit boundary / gap**.

## 1. Title & Positioning

- **Evidence:** `README.md`, `docs/EmbodiedSceneAgent_Project_Blueprint_CheCheng.docx` (blueprint), `docs/final_report_assets/one_page_project_brief.md`.
- **Strongest claim (accurate):** Object-level 3D scene memory as the **cognition layer** for high-level planning with verifier + replanner — **not** an end-to-end low-level policy.
- **Boundary:** Do not sell as VLA replacement or official benchmark winner.

## 2. Motivation & Core Claim

- **Evidence:** README Motivation; `docs/scene_memory_contract_v2.md`; failure taxonomy.
- **Strongest:** Explicit memory improves checkability of subgoals and enables structured recovery.
- **Gap:** Large-scale human study / user trust metrics — not in repo.

## 3. System Architecture

- **Evidence:** `docs/figures/architecture_v2.svg` → copied as `docs/final_report_assets/figures/architecture_final.svg`; `docs/final_report_assets/figures/planner_verifier_replanner_loop.svg`.
- **Strongest:** Six-stage loop implemented in `src/embodied_scene_agent/pipeline/`.
- **Gap:** A100-scale deployment diagram — template only.

## 4. Scene Memory Design

- **Evidence:** `docs/scene_memory_contract_v2.md`; builder tests under `tests/`.
- **Strongest:** Teacher-state bootstrap is a **deliberate** engineering choice for reproducible cognition I/O.
- **Gap:** Predicted vs teacher-only memory ablation at scale — future.

## 5. Planner / Verifier / Replanner

- **Evidence:** `planner_output_contract.py`; `docs/failure_taxonomy.md`; `docs/replanner_design_v2.md`; `step_log['replan_audit']`.
- **Strongest:** Hybrid replanner batch shows JSON contract path + audit (`results/experiments/hybrid_replanner_eval/`).
- **Gap:** Not a massive LLM replan benchmark.

## 6. Training Data Construction

- **Evidence:** `docs/planner_data_stats.md`; `data/` layout; SFT checkpoint `results/checkpoints/planner_sft_3b_minimal/`.
- **Strongest:** Real 3B LoRA training artifact exists.
- **Gap:** Full rollout dataset at 7B scale — future_only.

## 7. Experimental Settings

- **Evidence:** `configs/`; experiment scripts in `scripts/`; `environment.yml`.
- **Strongest:** Repro commands documented in `docs/final_report_assets/reproducibility.md`.
- **Gap:** Container image — not shipped.

## 8. Main Results

- **Evidence:** `docs/final_report_assets/tables/current_main_results_table.md`; `results/reports/latest_project_report.json`.
- **Strongest:** JSONL proxy + E2 two-layer ablation + hybrid batch + RLBench diagnosis JSON.
- **Gap:** Official leaderboard rows — explicitly **not** claimed.

## 9. E2 Ablation

- **Evidence:** `results/experiments/e2_ablation/`; `docs/tables/e2_ablation_mock_vs_calvin_fixture.md`; `docs/failure_cases/e2_ablation_cases.md`.
- **Strongest:** E2 mock (symbolic): latest batch shows verifier_plus_replan task_completion=1.0, recovery_success_rate=0.75 — **fixture/smoke**, not official CALVIN.
- **Gap:** E2 is symbolic + fixture — not CALVIN challenge split.

## 10. Hybrid Replanner Analysis

- **Evidence:** `docs/replanner_hybrid_results.md`; latest eval dir under `results/experiments/hybrid_replanner_eval/`.
- **Strongest:** {"replan_parse_success_rate": 1.0, "validated_revision_rate": 1.0, "fallback_rate": 0.0, "repair_success_rate": 1.0, "unknown_failure_rate": 0.6153846153846154, "unknown_skill_rate": null, "alias_normalization_count": null, "invalid_skill_count": null}
- **Gap:** `parse_error_kind_counts` empty in latest batch = **high success**, not proof of zero failures forever.

## 11. RLBench Bridge Status

- **Evidence:** `results/rlbench_stack_diagnosis.json`; `results/rlbench_dev_smoke.json`; `docs/rlbench_install_log.md`.
- **Strongest stage reached:** `import_fail`; fixture memory bridge works.
- **Gap:** Real `sim_reset` — blocked at import / CoppeliaSim stack on current machine.

## 12. Failure Analysis & Limitations

- **Evidence:** `docs/failure_taxonomy.md`; `docs/final_report_assets/limitations.md`; case studies folder.
- **Strongest:** Taxonomy + logged verifier failures + curated cases.
- **Gap:** Real-robot failure videos — not in asset pack.

## 13. Reproducibility & Engineering Notes

- **Evidence:** `docs/final_report_assets/reproducibility.md`; `scripts/build_final_report_assets.sh`.
- **Strongest:** Single-command report regen + conda-resolved scripts.
- **Gap:** Full OS-level CoppeliaSim install — user-side.

## 14. Future Directions

- **Evidence:** `configs/experiment/a100_final.yaml`; `docs/vlabench_plan.md`.
- **Strongest:** Clear staged roadmap without pretending completion.
- **Gap:** A100 7B runs, VLABench harness, official benchmarks — **future_only**.
