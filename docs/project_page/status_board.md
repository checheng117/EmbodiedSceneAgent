# Status board (auto)

_`2026-03-31T11:48:17.904870+00:00`_

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
| Hybrid batch (CALVIN debug real) headline | `{'replan_parse_success_rate': 1.0, 'validated_revision_rate': 1.0, 'fallback_rate': 0.0, 'repair_success_rate': 0.0, 'unknown_failure_rate': 0.375, 'unknown_skill_rate': 0.0, 'alias_normalization_count': 0, 'invalid_skill_count': 0}` |

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
{
  "missing_required_keys": 3
}
```

## Hybrid refined failure labels (CALVIN debug real)

```json
{
  "episode_failure_label_counts": {
    "repeated_no_effect_fallback_exhausted": 3
  },
  "terminal_failure_label_counts": {
    "repeated_no_effect_fallback_exhausted": 3
  },
  "acceptance_rejection_reason_counts": {
    "target_absent_from_scene_memory": 1
  }
}
```

## RLBench stages present (last smoke JSON)

`['diagnostics', 'fixture_file', 'memory_planner', 'sim_env_create', 'sim_import_only', 'sim_reset']`

## Hybrid headline (eval batch if present)

```json
{
  "replan_parse_success_rate": 0.0,
  "validated_revision_rate": 0.0,
  "fallback_rate": 1.0,
  "repair_success_rate": 1.0,
  "unknown_failure_rate": 0.6,
  "unknown_skill_rate": 0.0,
  "alias_normalization_count": 0,
  "invalid_skill_count": 0
}
```

## Strongest real artifacts

- `results/eval/planner_base_vs_tuned/metrics.json`
- `results/experiments/e2_ablation/e2_mock_20260331T083930Z`
- `results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z`
- `results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z`

## Reproducibility contract

```json
{
  "planner_train_run": {
    "status": "ready",
    "latest_dir": "results/checkpoints/planner_sft_3b_minimal/run_latest",
    "run_meta_path": "results/checkpoints/planner_sft_3b_minimal/run_latest/run_meta.json",
    "config_snapshot_path": "results/checkpoints/planner_sft_3b_minimal/run_latest/config.snapshot.yaml",
    "experiment_id": null
  },
  "latest_e2_mock": {
    "status": "ready",
    "latest_dir": "results/experiments/e2_ablation/e2_mock_20260331T083930Z",
    "config_snapshot_path": "results/experiments/e2_ablation/e2_mock_20260331T083930Z/config.snapshot.json",
    "run_manifest_path": "results/experiments/e2_ablation/e2_mock_20260331T083930Z/run_manifest.json",
    "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
    "config_snapshot_sha256": "8b5387ca8061dba706bab0812243e41019405d38c1f46f1f8388691c8c1c6f38"
  },
  "latest_e2_calvin_fixture": {
    "status": "ready",
    "latest_dir": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z",
    "config_snapshot_path": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z/config.snapshot.json",
    "run_manifest_path": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z/run_manifest.json",
    "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
    "config_snapshot_sha256": "b70f223d9ca4b1788281d5b4f14c65989eaa314dd88abda51d9e5ec7e1872999"
  },
  "latest_e2_calvin_debug_real": {
    "status": "ready",
    "latest_dir": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z",
    "config_snapshot_path": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z/config.snapshot.json",
    "run_manifest_path": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z/run_manifest.json",
    "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
    "config_snapshot_sha256": "d111060a8b95beae18916149fea11e01a2d72c432d6b831c9cb7384e12a0407d"
  },
  "latest_hybrid_eval": {
    "status": "ready",
    "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z",
    "config_snapshot_path": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z/config.snapshot.json",
    "run_manifest_path": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z/run_manifest.json",
    "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
    "config_snapshot_sha256": "462c5a759642e0c4281e491b7427ad76ca55cfc3a41a1fe6f5a6feb590336562"
  },
  "latest_hybrid_eval_calvin_debug_real": {
    "status": "ready",
    "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun",
    "config_snapshot_path": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun/config.snapshot.json",
    "run_manifest_path": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun/run_manifest.json",
    "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
    "config_snapshot_sha256": "9ea7d8b1a42968af68676d90c44731d4877f911fa40d46e67fb135f9ae96917d"
  },
  "latest_hybrid_smoke": {
    "status": "ready",
    "latest_dir": "results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260331T084216Z",
    "config_snapshot_path": "results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260331T084216Z/config.snapshot.json",
    "run_manifest_path": "results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260331T084216Z/run_manifest.json",
    "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
    "config_snapshot_sha256": "88cb81e2b8d67dfa42a239d79dbd026c40654ad9ca257632e955cb89d2ed6c04"
  }
}
```

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