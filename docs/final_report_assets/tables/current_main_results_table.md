# Current main results (auto)

_All numbers trace to `results/` or `docs/` paths — not official leaderboards._

| Category | Metric | Value | Artifact |
|----------|--------|-------|----------|
| Planner SFT (3B minimal) | checkpoint + run_meta | see run_meta.json | `results/checkpoints/planner_sft_3b_minimal/run_latest` |
| Planner SFT | notes |  | `` |
| Base vs tuned (JSONL proxy) | primary metric (file) | ['n', 'format_compliance_rate_base', 'format_compliance_rate_tuned'] | `results/eval/planner_base_vs_tuned/metrics.json` |
| E2 mock symbolic | task_completion (verifier_plus_replan) | 1 | `results/experiments/e2_ablation/e2_mock_20260325T090753Z/metrics.json` |
| E2 CALVIN fixture | task_completion (verifier_plus_replan) | 1 | `results/experiments/e2_ablation/e2_calvin_fixture_20260325T090754Z/metrics.json` |
| E2 CALVIN debug real-data (latest any batch) | task_completion (verifier_plus_replan) | 0 | `results/experiments/e2_ablation/e2_doc_refresh_same_task/metrics.json` |
| E2 CALVIN debug grouped_sequence batch | task_completion (verifier_plus_replan) | 0 | `results/experiments/e2_ablation/e2_doc_refresh_aligned/metrics.json` |
| E2 CALVIN debug same_task_subset batch | task_completion (verifier_plus_replan) | 0 | `results/experiments/e2_ablation/e2_doc_refresh_same_task/metrics.json` |
| Hybrid replanner batch | parse / validated / repair rates | {'replan_parse_success_rate': 1.0, 'validated_revision_rate': 1.0, 'fallback_rate': 0.0, 'repair_success_rate': 1.0, 'unknown_failure_rate': 0.6153846153846154, 'unknown_skill_rate': None, 'alias_normalization_count': None, 'invalid_skill_count': None} | `results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260325T090504Z/metrics.json` |
| Hybrid replanner (CALVIN debug real) | parse / validated / repair rates | {'replan_parse_success_rate': 0.5, 'validated_revision_rate': 0.5, 'fallback_rate': 0.5, 'repair_success_rate': 0.0, 'unknown_failure_rate': 0.1, 'unknown_skill_rate': 0.0, 'alias_normalization_count': 0, 'invalid_skill_count': 0} | `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_same_task_20260326T095232Z/metrics.json` |
| CALVIN debug planner SFT export | row counts + lineage | see stats md | `docs/calvin_debug_real_data_stats.md` |
| RLBench bridge | deepest_reached_stage | import_fail | `results/rlbench_dev_smoke.json; results/rlbench_stack_diagnosis.json` |
