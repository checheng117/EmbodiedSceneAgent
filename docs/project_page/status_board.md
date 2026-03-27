# Status board (auto)

_`2026-03-27T14:22:26.826195+00:00`_

| Area | State |
|------|-------|
| Cognition loop (mock/CALVIN) | implemented |
| RLBench import | False |
| RLBench simulator_locate | False |
| RLBench env_create | False |
| RLBench reset | False |
| RLBench deepest_reached_stage | `import_fail` |
| RLBench memory_bridge | True |
| RLBench planner_smoke | True |
| RLBench bridge_mode | `fixture_file` |
| E2 on mock | `available` |
| E2 on CALVIN fixture | `available` |
| E2 on CALVIN debug real-data | `available` |
| Hybrid replanner | `available` (strongest: `eval_batch`) |
| Hybrid batch (CALVIN debug real) headline | `{'replan_parse_success_rate': 0.5, 'validated_revision_rate': 0.5, 'fallback_rate': 0.5, 'repair_success_rate': 0.0, 'unknown_failure_rate': 0.1, 'unknown_skill_rate': 0.0, 'alias_normalization_count': 0, 'invalid_skill_count': 0}` |

## RLBench blocker_summary

rlbench import blocked: rlbench not available: No module named 'rlbench'

## E2 best case paths (demos dir)

```json
{
  "case1_none.json": "results/demos/e2_ablation_cases/case1_none.json",
  "case2_verifier_only.json": "results/demos/e2_ablation_cases/case2_verifier_only.json",
  "case3_plus_replan.json": "results/demos/e2_ablation_cases/case3_plus_replan.json",
  "mock_selection_meta.json": "results/demos/e2_ablation_cases/mock_selection_meta.json",
  "calvin_case_replan_fixes_stuck_verifier_only.json": "results/demos/e2_ablation_cases/calvin_case_replan_fixes_stuck_verifier_only.json",
  "calvin_case_repair_failed_after_failure_detected.json": "results/demos/e2_ablation_cases/calvin_case_repair_failed_after_failure_detected.json",
  "calvin_selection_meta.json": "results/demos/e2_ablation_cases/calvin_selection_meta.json",
  "calvin_debug_real_selection_meta.json": "results/demos/e2_ablation_cases/calvin_debug_real_selection_meta.json",
  "calvin_debug_real_case_verifier_only.json": "results/demos/e2_ablation_cases/calvin_debug_real_case_verifier_only.json",
  "calvin_debug_real_case_verifier_plus_replan.json": "results/demos/e2_ablation_cases/calvin_debug_real_case_verifier_plus_replan.json",
  "calvin_debug_real_aligned_selection_meta.json": "results/demos/e2_ablation_cases/calvin_debug_real_aligned_selection_meta.json",
  "calvin_debug_real_aligned_case_verifier_only.json": "results/demos/e2_ablation_cases/calvin_debug_real_aligned_case_verifier_only.json",
  "calvin_debug_real_aligned_case_verifier_plus_replan.json": "results/demos/e2_ablation_cases/calvin_debug_real_aligned_case_verifier_plus_replan.json",
  "calvin_debug_same_task_selection_meta.json": "results/demos/e2_ablation_cases/calvin_debug_same_task_selection_meta.json",
  "calvin_debug_same_task_case_verifier_only.json": "results/demos/e2_ablation_cases/calvin_debug_same_task_case_verifier_only.json",
  "calvin_debug_same_task_case_verifier_plus_replan.json": "results/demos/e2_ablation_cases/calvin_debug_same_task_case_verifier_plus_replan.json"
}
```

## mock_vs_calvin_short_note

Mock symbolic isolates verifier/replan mechanism; CALVIN fixture exercises adapter-shaped teacher state. Expect wiring consistency, not numeric parity with official benchmarks.

## Hybrid strongest case path

`results/demos/hybrid_replanner_cases/case_llm_repair_success.json`

## Hybrid parse error breakdown (eval batch)

```json
{}
```

## RLBench stages present (last smoke JSON)

`['diagnostics', 'fixture_file', 'memory_planner', 'sim_env_create', 'sim_import_only', 'sim_reset']`

## Hybrid headline (eval batch if present)

```json
{
  "replan_parse_success_rate": 1.0,
  "validated_revision_rate": 1.0,
  "fallback_rate": 0.0,
  "repair_success_rate": 1.0,
  "unknown_failure_rate": 0.6153846153846154,
  "unknown_skill_rate": null,
  "alias_normalization_count": null,
  "invalid_skill_count": null
}
```

## Strongest real artifacts

- `results/eval/planner_base_vs_tuned/metrics.json`
- `results/experiments/e2_ablation/e2_mock_20260325T090753Z`
- `results/experiments/e2_ablation/e2_calvin_fixture_20260325T090754Z`
- `results/experiments/e2_ablation/e2_doc_refresh_same_task`

## Smoke vs future

| Item | |
|------|--|
| RLBench fixture→memory→planner | **smoke** |
| RLBench sim_reset | only if CoppeliaSim+rlbench OK |
| Official benchmarks | **future_only** |
| A100 7B | **future_only** (template exists) |

## Limitations

- Official CALVIN / RLBench leaderboard numbers: not claimed.
- RLBench full sim: blocked without CoppeliaSim + PyRep (see docs/rlbench_install_log.md) unless bridge_mode=sim_reset.
- A100 7B production training: template only.
- VLABench: planning doc only.
- RLBench Python import: false on this machine — using fixture bridge for cognition smoke.