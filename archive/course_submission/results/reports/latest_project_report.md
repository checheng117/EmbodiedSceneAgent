# EmbodiedSceneAgent — project report (auto)

_Generated: `2026-03-31T11:48:17.904870+00:00`_

## Unified headline facts (machine-derived)

```json
{
  "generated_utc": "2026-03-31T11:48:17.904870+00:00",
  "strongest_real_result": {
    "name": "planner JSONL proxy (base vs tuned)",
    "path": "results/eval/planner_base_vs_tuned/metrics.json",
    "note": "Not official CALVIN benchmark."
  },
  "strongest_real_results_all": [
    {
      "name": "planner JSONL proxy (base vs tuned)",
      "path": "results/eval/planner_base_vs_tuned/metrics.json",
      "note": "Not official CALVIN benchmark."
    },
    {
      "name": "E2 ablation on mock (symbolic)",
      "path": "results/experiments/e2_ablation/e2_mock_20260331T083930Z",
      "note": "no_verifier vs verifier_only vs verifier_plus_replan \u2014 not official CALVIN."
    },
    {
      "name": "E2 ablation on CALVIN fixture batch",
      "path": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z",
      "note": "Fixture minimal loop \u2014 **not** official CALVIN ablation."
    },
    {
      "name": "E2 ablation on CALVIN official debug npz (vector teacher)",
      "path": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z",
      "note": "Official debug dataset vectors + symbolic minimal loop \u2014 **not** leaderboard."
    }
  ],
  "strongest_hybrid_result": {
    "kind": "eval_batch",
    "metrics_headline": {
      "replan_parse_success_rate": 0.0,
      "validated_revision_rate": 0.0,
      "fallback_rate": 1.0,
      "repair_success_rate": 1.0,
      "unknown_failure_rate": 0.6,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "case_path": "results/demos/hybrid_replanner_cases/case_llm_repair_success.json",
    "parse_error_kind_counts": {
      "missing_required_keys": 3
    },
    "parse_breakdown_empty_reason": null
  },
  "e2_best_story": {
    "mock_status": "available",
    "mock_latest_dir": "results/experiments/e2_ablation/e2_mock_20260331T083930Z",
    "calvin_fixture_status": "available",
    "calvin_latest_dir": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z",
    "calvin_debug_real_status": "available",
    "calvin_debug_real_latest_dir": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z",
    "mock_verifier_plus_replan_task_completion_rate": 1.0,
    "mock_verifier_plus_replan_recovery_success_rate": 0.6666666666666666,
    "one_line": "E2 mock (symbolic): latest batch shows verifier_plus_replan task_completion=1.0, recovery_success_rate=0.6666666666666666 \u2014 **fixture/smoke**, not official CALVIN.",
    "calvin_debug_real_note": "E2 on official CALVIN **debug** vectors: status `available` \u2014 **not** leaderboard."
  },
  "hybrid_calvin_debug_real_headline": {
    "replan_parse_success_rate": 1.0,
    "validated_revision_rate": 1.0,
    "fallback_rate": 0.0,
    "repair_success_rate": 0.0,
    "unknown_failure_rate": 0.375,
    "unknown_skill_rate": 0.0,
    "alias_normalization_count": 0,
    "invalid_skill_count": 0
  },
  "rlbench_deepest_stage": "import_fail",
  "rlbench_blocker_summary": "rlbench import blocked: rlbench not available: No module named 'rlbench'",
  "rlbench_bridge_mode": "fixture_file",
  "rlbench_memory_bridge": true,
  "open_gaps": [
    "Official CALVIN / RLBench leaderboard numbers: not claimed.",
    "RLBench full sim: blocked without CoppeliaSim + PyRep (see docs/rlbench_install_log.md) unless bridge_mode=sim_reset.",
    "A100 7B production training: template only.",
    "VLABench: planning doc only.",
    "RLBench Python import: false on this machine \u2014 using fixture bridge for cognition smoke."
  ],
  "smoke_vs_future_note": "RLBench: **real** = fixture\u2192memory\u2192planner smoke; **sim_reset** = only if CoppeliaSim stack OK. Official CALVIN/RLBench leaderboards: **future_only**. A100 7B / VLABench: **future_only**."
}
```

## Project Status Snapshot

```json
{
  "cognition_layer": "implemented (mock + CALVIN fixture + CALVIN debug vectors + RLBench observation bridge)",
  "rlbench_import": false,
  "rlbench_simulator_locate": false,
  "rlbench_env_create": false,
  "rlbench_reset": false,
  "rlbench_deepest_reached_stage": "import_fail",
  "rlbench_blocker_summary": "rlbench import blocked: rlbench not available: No module named 'rlbench'",
  "rlbench_memory_bridge": true,
  "rlbench_planner_smoke": true,
  "rlbench_bridge_mode": "fixture_file",
  "e2_on_mock": "available",
  "e2_on_calvin_fixture": "available",
  "e2_on_calvin_debug_real": "available",
  "e2_best_case_paths": {
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
  },
  "mock_vs_calvin_short_note": "Mock symbolic isolates verifier/replan mechanism; CALVIN fixture exercises adapter-shaped teacher state. Expect wiring consistency, not numeric parity with official benchmarks.",
  "hybrid_replanner": "available",
  "hybrid_strongest_kind": "eval_batch",
  "hybrid_replanner_batch_headline": {
    "replan_parse_success_rate": 0.0,
    "validated_revision_rate": 0.0,
    "fallback_rate": 1.0,
    "repair_success_rate": 1.0,
    "unknown_failure_rate": 0.6,
    "unknown_skill_rate": 0.0,
    "alias_normalization_count": 0,
    "invalid_skill_count": 0
  },
  "hybrid_parse_error_breakdown": {
    "missing_required_keys": 3
  },
  "strongest_hybrid_case_path": "results/demos/hybrid_replanner_cases/case_llm_repair_success.json",
  "hybrid_calvin_debug_real_batch_headline": {
    "replan_parse_success_rate": 1.0,
    "validated_revision_rate": 1.0,
    "fallback_rate": 0.0,
    "repair_success_rate": 0.0,
    "unknown_failure_rate": 0.375,
    "unknown_skill_rate": 0.0,
    "alias_normalization_count": 0,
    "invalid_skill_count": 0
  },
  "hybrid_calvin_debug_real_failure_labels": {
    "repeated_no_effect_fallback_exhausted": 3
  },
  "hybrid_calvin_debug_real_terminal_labels": {
    "repeated_no_effect_fallback_exhausted": 3
  },
  "hybrid_calvin_debug_real_acceptance_rejections": {
    "target_absent_from_scene_memory": 1
  },
  "hybrid_calvin_debug_real_aligned_batch_headline": {
    "replan_parse_success_rate": 1.0,
    "validated_revision_rate": 1.0,
    "fallback_rate": 0.0,
    "repair_success_rate": 0.0,
    "unknown_failure_rate": 0.375,
    "unknown_skill_rate": 0.0,
    "alias_normalization_count": 0,
    "invalid_skill_count": 0
  },
  "hybrid_calvin_debug_same_task_batch_headline": {
    "replan_parse_success_rate": 0.5,
    "validated_revision_rate": 0.5,
    "fallback_rate": 0.5,
    "repair_success_rate": 0.0,
    "unknown_failure_rate": 0.1,
    "unknown_skill_rate": 0.0,
    "alias_normalization_count": 0,
    "invalid_skill_count": 0
  },
  "calvin_debug_alignment_stats_present": true,
  "skill_schema_audit_present": true
}
```

## Current Strongest Results

- **planner JSONL proxy (base vs tuned)**: `results/eval/planner_base_vs_tuned/metrics.json` — _Not official CALVIN benchmark._
- **E2 ablation on mock (symbolic)**: `results/experiments/e2_ablation/e2_mock_20260331T083930Z` — _no_verifier vs verifier_only vs verifier_plus_replan — not official CALVIN._
- **E2 ablation on CALVIN fixture batch**: `results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z` — _Fixture minimal loop — **not** official CALVIN ablation._
- **E2 ablation on CALVIN official debug npz (vector teacher)**: `results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z` — _Official debug dataset vectors + symbolic minimal loop — **not** leaderboard._

## E2 Ablation (mock + CALVIN fixture)

```json
{
  "e2_on_mock": {
    "status": "available",
    "backend": "mock",
    "latest_dir": "results/experiments/e2_ablation/e2_mock_20260331T083930Z",
    "modes": {
      "none": {
        "verifier_mode": "none",
        "n_episodes": 6,
        "task_completion_rate": 1.0,
        "failure_detected_rate": 0.0,
        "failure_detected_steps": 0,
        "total_steps": 24,
        "state_unchanged_rate": 0.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 0,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 4.0,
        "failure_taxonomy_counts": {},
        "notes": {
          "setting": "MockEmbodiedEnv symbolic \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_only": {
        "verifier_mode": "verifier_only",
        "n_episodes": 6,
        "task_completion_rate": 1.0,
        "failure_detected_rate": 0.25,
        "failure_detected_steps": 6,
        "total_steps": 24,
        "state_unchanged_rate": 1.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 4,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 4.0,
        "failure_taxonomy_counts": {
          "state_unchanged": 6
        },
        "notes": {
          "setting": "MockEmbodiedEnv symbolic \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_plus_replan": {
        "verifier_mode": "verifier_plus_replan",
        "n_episodes": 6,
        "task_completion_rate": 1.0,
        "failure_detected_rate": 0.2,
        "failure_detected_steps": 4,
        "total_steps": 20,
        "state_unchanged_rate": 1.0,
        "replan_trigger_rate": 0.6666666666666666,
        "recovery_success_rate": 0.6666666666666666,
        "recovery_eligible_episodes": 4,
        "recovery_success_after_replan_episodes": 4,
        "average_steps": 3.3333333333333335,
        "failure_taxonomy_counts": {
          "state_unchanged": 4,
          "replan::state_unchanged": 2
        },
        "notes": {
          "setting": "MockEmbodiedEnv symbolic \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      }
    },
    "experiment_id": "e2_mock_20260331T083930Z",
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/e2_ablation/e2_mock_20260331T083930Z",
      "config_snapshot_path": "results/experiments/e2_ablation/e2_mock_20260331T083930Z/config.snapshot.json",
      "run_manifest_path": "results/experiments/e2_ablation/e2_mock_20260331T083930Z/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "8b5387ca8061dba706bab0812243e41019405d38c1f46f1f8388691c8c1c6f38"
    }
  },
  "e2_on_calvin_fixture": {
    "status": "available",
    "backend": "calvin_fixture",
    "latest_dir": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z",
    "modes": {
      "none": {
        "verifier_mode": "none",
        "n_episodes": 6,
        "task_completion_rate": 1.0,
        "failure_detected_rate": 0.0,
        "failure_detected_steps": 0,
        "total_steps": 14,
        "state_unchanged_rate": 0.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 0,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 2.3333333333333335,
        "failure_taxonomy_counts": {},
        "notes": {
          "setting": "CALVIN **fixture** minimal loop (``run_calvin_minimal_episode``) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_only": {
        "verifier_mode": "verifier_only",
        "n_episodes": 6,
        "task_completion_rate": 1.0,
        "failure_detected_rate": 0.0,
        "failure_detected_steps": 0,
        "total_steps": 14,
        "state_unchanged_rate": 0.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 0,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 2.3333333333333335,
        "failure_taxonomy_counts": {},
        "notes": {
          "setting": "CALVIN **fixture** minimal loop (``run_calvin_minimal_episode``) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_plus_replan": {
        "verifier_mode": "verifier_plus_replan",
        "n_episodes": 6,
        "task_completion_rate": 1.0,
        "failure_detected_rate": 0.0,
        "failure_detected_steps": 0,
        "total_steps": 14,
        "state_unchanged_rate": 0.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 0,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 2.3333333333333335,
        "failure_taxonomy_counts": {},
        "notes": {
          "setting": "CALVIN **fixture** minimal loop (``run_calvin_minimal_episode``) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      }
    },
    "experiment_id": "e2_calvin_fixture_20260331T084742Z",
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z",
      "config_snapshot_path": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z/config.snapshot.json",
      "run_manifest_path": "results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "b70f223d9ca4b1788281d5b4f14c65989eaa314dd88abda51d9e5ec7e1872999"
    }
  },
  "e2_on_calvin_debug_real": {
    "status": "available",
    "backend": "calvin_debug_real",
    "latest_dir": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z",
    "modes": {
      "none": {
        "verifier_mode": "none",
        "n_episodes": 4,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.0,
        "failure_detected_steps": 0,
        "total_steps": 48,
        "state_unchanged_rate": 0.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 0,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {},
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`grouped_sequence` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_only": {
        "verifier_mode": "verifier_only",
        "n_episodes": 4,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.9583333333333334,
        "failure_detected_steps": 46,
        "total_steps": 48,
        "state_unchanged_rate": 1.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 4,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {
          "state_unchanged": 46
        },
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`grouped_sequence` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_plus_replan": {
        "verifier_mode": "verifier_plus_replan",
        "n_episodes": 4,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.9583333333333334,
        "failure_detected_steps": 46,
        "total_steps": 48,
        "state_unchanged_rate": 1.0,
        "replan_trigger_rate": 11.5,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 4,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {
          "state_unchanged": 46,
          "replan::state_unchanged": 46
        },
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`grouped_sequence` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      }
    },
    "experiment_id": "e2_calvin_debug_real_aligned_20260331T084633Z",
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z",
      "config_snapshot_path": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z/config.snapshot.json",
      "run_manifest_path": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "d111060a8b95beae18916149fea11e01a2d72c432d6b831c9cb7384e12a0407d"
    }
  },
  "e2_on_calvin_debug_real_aligned": {
    "status": "available",
    "backend": "calvin_debug_real",
    "calvin_debug_batch": "grouped_sequence",
    "latest_dir": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z",
    "modes": {
      "none": {
        "verifier_mode": "none",
        "n_episodes": 4,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.0,
        "failure_detected_steps": 0,
        "total_steps": 48,
        "state_unchanged_rate": 0.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 0,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {},
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`grouped_sequence` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_only": {
        "verifier_mode": "verifier_only",
        "n_episodes": 4,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.9583333333333334,
        "failure_detected_steps": 46,
        "total_steps": 48,
        "state_unchanged_rate": 1.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 4,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {
          "state_unchanged": 46
        },
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`grouped_sequence` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_plus_replan": {
        "verifier_mode": "verifier_plus_replan",
        "n_episodes": 4,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.9583333333333334,
        "failure_detected_steps": 46,
        "total_steps": 48,
        "state_unchanged_rate": 1.0,
        "replan_trigger_rate": 11.5,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 4,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {
          "state_unchanged": 46,
          "replan::state_unchanged": 46
        },
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`grouped_sequence` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      }
    },
    "experiment_id": "e2_calvin_debug_real_aligned_20260331T084633Z",
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z",
      "config_snapshot_path": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z/config.snapshot.json",
      "run_manifest_path": "results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "d111060a8b95beae18916149fea11e01a2d72c432d6b831c9cb7384e12a0407d"
    }
  },
  "e2_on_calvin_debug_same_task": {
    "status": "available",
    "backend": "calvin_debug_real",
    "calvin_debug_batch": "same_task_subset",
    "latest_dir": "results/experiments/e2_ablation/e2_doc_refresh_same_task",
    "modes": {
      "none": {
        "verifier_mode": "none",
        "n_episodes": 8,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.0,
        "failure_detected_steps": 0,
        "total_steps": 96,
        "state_unchanged_rate": 0.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 0,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {},
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`same_task_subset` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_only": {
        "verifier_mode": "verifier_only",
        "n_episodes": 8,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.9583333333333334,
        "failure_detected_steps": 92,
        "total_steps": 96,
        "state_unchanged_rate": 1.0,
        "replan_trigger_rate": 0.0,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 8,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {
          "state_unchanged": 92
        },
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`same_task_subset` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      },
      "verifier_plus_replan": {
        "verifier_mode": "verifier_plus_replan",
        "n_episodes": 8,
        "task_completion_rate": 0.0,
        "failure_detected_rate": 0.9583333333333334,
        "failure_detected_steps": 92,
        "total_steps": 96,
        "state_unchanged_rate": 1.0,
        "replan_trigger_rate": 11.5,
        "recovery_success_rate": 0.0,
        "recovery_eligible_episodes": 8,
        "recovery_success_after_replan_episodes": 0,
        "average_steps": 12.0,
        "failure_taxonomy_counts": {
          "state_unchanged": 92,
          "replan::state_unchanged": 92
        },
        "notes": {
          "setting": "CALVIN **official debug** ``*.npz`` vectors \u2192 vector teacher \u2192 minimal loop (symbolic skills) \u2014 batch=`same_task_subset` (same-task-like when applicable) \u2014 not official CALVIN benchmark.",
          "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
          "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success."
        }
      }
    },
    "experiment_id": "e2_doc_refresh_same_task",
    "run_artifacts": {
      "status": "missing",
      "latest_dir": "results/experiments/e2_ablation/e2_doc_refresh_same_task",
      "config_snapshot_path": null,
      "run_manifest_path": null,
      "git_commit": null,
      "config_snapshot_sha256": null
    }
  }
}
```

## RLBench Bridge Status

```json
{
  "status": "ok",
  "path": "results/rlbench_dev_smoke.json",
  "import_ok": false,
  "bridge_mode": "fixture_file",
  "task_name": "ReachTarget",
  "sim_message_head": "using_fixture:tests/fixtures/rlbench_observation_like.json; prior_sim_note=",
  "layer_status": {
    "import": false,
    "simulator_locate": false,
    "env_create": false,
    "reset": false,
    "observation": false,
    "memory_bridge": true,
    "planner_smoke": true
  },
  "import_layer": false,
  "simulator_locate_layer": false,
  "env_create_layer": false,
  "reset_layer": false,
  "observation_layer": false,
  "memory_bridge": true,
  "planner_smoke": true,
  "stages_present": [
    "diagnostics",
    "fixture_file",
    "memory_planner",
    "sim_env_create",
    "sim_import_only",
    "sim_reset"
  ],
  "deepest_reached_stage": "import_fail",
  "blocker_summary": "rlbench import blocked: rlbench not available: No module named 'rlbench'",
  "stack_diagnosis_path": "results/rlbench_stack_diagnosis.json"
}
```

## Hybrid Replanner Status

```json
{
  "status": "available",
  "strongest_artifact": {
    "kind": "eval_batch",
    "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z",
    "metrics_headline": {
      "replan_parse_success_rate": 0.0,
      "validated_revision_rate": 0.0,
      "fallback_rate": 1.0,
      "repair_success_rate": 1.0,
      "unknown_failure_rate": 0.6,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "fallback_reason_counts": {
      "null field: success_check": 3
    },
    "fallback_stage_counts": {
      "parse_validate": 3
    },
    "parse_error_kind_counts": {
      "missing_required_keys": 3
    },
    "acceptance_rejection_reason_counts": {},
    "episode_failure_label_counts": {},
    "terminal_failure_label_counts": {},
    "hybrid_replanner_batch_headline": {
      "replan_parse_success_rate": 0.0,
      "validated_revision_rate": 0.0,
      "fallback_rate": 1.0,
      "repair_success_rate": 1.0,
      "unknown_failure_rate": 0.6,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "hybrid_parse_error_breakdown": {
      "missing_required_keys": 3
    },
    "backend": "mock",
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z",
      "config_snapshot_path": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z/config.snapshot.json",
      "run_manifest_path": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "462c5a759642e0c4281e491b7427ad76ca55cfc3a41a1fe6f5a6feb590336562"
    }
  },
  "eval_batch": {
    "kind": "eval_batch",
    "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z",
    "metrics_headline": {
      "replan_parse_success_rate": 0.0,
      "validated_revision_rate": 0.0,
      "fallback_rate": 1.0,
      "repair_success_rate": 1.0,
      "unknown_failure_rate": 0.6,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "fallback_reason_counts": {
      "null field: success_check": 3
    },
    "fallback_stage_counts": {
      "parse_validate": 3
    },
    "parse_error_kind_counts": {
      "missing_required_keys": 3
    },
    "acceptance_rejection_reason_counts": {},
    "episode_failure_label_counts": {},
    "terminal_failure_label_counts": {},
    "hybrid_replanner_batch_headline": {
      "replan_parse_success_rate": 0.0,
      "validated_revision_rate": 0.0,
      "fallback_rate": 1.0,
      "repair_success_rate": 1.0,
      "unknown_failure_rate": 0.6,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "hybrid_parse_error_breakdown": {
      "missing_required_keys": 3
    },
    "backend": "mock",
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z",
      "config_snapshot_path": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z/config.snapshot.json",
      "run_manifest_path": "results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "462c5a759642e0c4281e491b7427ad76ca55cfc3a41a1fe6f5a6feb590336562"
    }
  },
  "eval_batch_calvin_debug_real": {
    "kind": "eval_batch",
    "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun",
    "metrics_headline": {
      "replan_parse_success_rate": 1.0,
      "validated_revision_rate": 1.0,
      "fallback_rate": 0.0,
      "repair_success_rate": 0.0,
      "unknown_failure_rate": 0.375,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "fallback_reason_counts": {
      "target_absent_from_scene_memory": 1
    },
    "fallback_stage_counts": {
      "validated": 2,
      "semantic_acceptance": 1
    },
    "parse_error_kind_counts": {},
    "acceptance_rejection_reason_counts": {
      "target_absent_from_scene_memory": 1
    },
    "episode_failure_label_counts": {
      "repeated_no_effect_fallback_exhausted": 3
    },
    "terminal_failure_label_counts": {
      "repeated_no_effect_fallback_exhausted": 3
    },
    "hybrid_replanner_batch_headline": {
      "replan_parse_success_rate": 1.0,
      "validated_revision_rate": 1.0,
      "fallback_rate": 0.0,
      "repair_success_rate": 0.0,
      "unknown_failure_rate": 0.375,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "hybrid_parse_error_breakdown": {},
    "backend": "calvin_debug_real",
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun",
      "config_snapshot_path": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun/config.snapshot.json",
      "run_manifest_path": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "9ea7d8b1a42968af68676d90c44731d4877f911fa40d46e67fb135f9ae96917d"
    }
  },
  "eval_batch_calvin_debug_real_aligned": {
    "kind": "eval_batch",
    "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun",
    "metrics_headline": {
      "replan_parse_success_rate": 1.0,
      "validated_revision_rate": 1.0,
      "fallback_rate": 0.0,
      "repair_success_rate": 0.0,
      "unknown_failure_rate": 0.375,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "fallback_reason_counts": {
      "target_absent_from_scene_memory": 1
    },
    "fallback_stage_counts": {
      "validated": 2,
      "semantic_acceptance": 1
    },
    "parse_error_kind_counts": {},
    "acceptance_rejection_reason_counts": {
      "target_absent_from_scene_memory": 1
    },
    "episode_failure_label_counts": {
      "repeated_no_effect_fallback_exhausted": 3
    },
    "terminal_failure_label_counts": {
      "repeated_no_effect_fallback_exhausted": 3
    },
    "hybrid_replanner_batch_headline": {
      "replan_parse_success_rate": 1.0,
      "validated_revision_rate": 1.0,
      "fallback_rate": 0.0,
      "repair_success_rate": 0.0,
      "unknown_failure_rate": 0.375,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "hybrid_parse_error_breakdown": {},
    "backend": "calvin_debug_real",
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun",
      "config_snapshot_path": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun/config.snapshot.json",
      "run_manifest_path": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "9ea7d8b1a42968af68676d90c44731d4877f911fa40d46e67fb135f9ae96917d"
    }
  },
  "eval_batch_calvin_debug_same_task": {
    "kind": "eval_batch",
    "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_same_task_20260326T095232Z",
    "metrics_headline": {
      "replan_parse_success_rate": 0.5,
      "validated_revision_rate": 0.5,
      "fallback_rate": 0.5,
      "repair_success_rate": 0.0,
      "unknown_failure_rate": 0.1,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "fallback_reason_counts": {
      "null field: success_check": 1
    },
    "fallback_stage_counts": {
      "validated": 1,
      "parse_validate": 1
    },
    "parse_error_kind_counts": {
      "missing_required_keys": 1
    },
    "acceptance_rejection_reason_counts": {},
    "episode_failure_label_counts": {},
    "terminal_failure_label_counts": {},
    "hybrid_replanner_batch_headline": {
      "replan_parse_success_rate": 0.5,
      "validated_revision_rate": 0.5,
      "fallback_rate": 0.5,
      "repair_success_rate": 0.0,
      "unknown_failure_rate": 0.1,
      "unknown_skill_rate": 0.0,
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "hybrid_parse_error_breakdown": {
      "missing_required_keys": 1
    },
    "backend": "calvin_debug_real",
    "run_artifacts": {
      "status": "missing",
      "latest_dir": "results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_same_task_20260326T095232Z",
      "config_snapshot_path": null,
      "run_manifest_path": null,
      "git_commit": null,
      "config_snapshot_sha256": null
    }
  },
  "smoke": {
    "kind": "smoke",
    "latest_dir": "results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260331T084216Z",
    "success": true,
    "replan_count": 1,
    "first_replan_audit": {
      "original_subgoal": "deliberate verifier-unknown skill for hybrid smoke",
      "failure_type": "unknown_failure",
      "repair_strategy": "delegate_rule_planner_with_failure_context",
      "revised_subgoal": "Open the drawer fully.",
      "whether_rule_based": true,
      "notes": "rule_planner_fallback;failed:FailureType.UNKNOWN_FAILURE:diagnostic unknown skill branch;llm_failed_fallback_to_rules",
      "llm_replanner_called": true,
      "replanner_parse_ok": false,
      "revised_plan_validated": false,
      "fallback_reason": "null field: success_check",
      "fallback_stage": "parse_validate",
      "replanner_parse_error_kind": "missing_required_keys",
      "skill_alias_normalized_from": null
    },
    "fallback_stats": {
      "llm_replanner_calls": 1,
      "replanner_parse_ok_count": 0,
      "revised_plan_validated_count": 0,
      "fallback_reason_counts": {
        "null field: success_check": 1
      },
      "fallback_stage_counts": {
        "parse_validate": 1
      },
      "parse_error_kind_counts": {
        "missing_required_keys": 1
      },
      "alias_normalization_count": 0,
      "invalid_skill_count": 0
    },
    "run_artifacts": {
      "status": "ready",
      "latest_dir": "results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260331T084216Z",
      "config_snapshot_path": "results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260331T084216Z/config.snapshot.json",
      "run_manifest_path": "results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260331T084216Z/run_manifest.json",
      "git_commit": "92893731767651c6aae29d02da8a27b54c277100",
      "config_snapshot_sha256": "88cb81e2b8d67dfa42a239d79dbd026c40654ad9ca257632e955cb89d2ed6c04"
    }
  },
  "strongest_hybrid_case_path": "results/demos/hybrid_replanner_cases/case_llm_repair_success.json"
}
```

## Eval metrics (JSONL proxy)

```json
{
  "n": 73,
  "format_compliance_rate_base": 1.0,
  "format_compliance_rate_tuned": 1.0,
  "tool_use_accuracy_base": 0.0821917808219178,
  "tool_use_accuracy_tuned": 0.2191780821917808,
  "target_match_rate_base": 0.3287671232876712,
  "target_match_rate_tuned": 0.4794520547945205,
  "task_completion_rate_base": 0.0684931506849315,
  "task_completion_rate_tuned": 0.2054794520547945,
  "error_recovery_rate_tuned": 0.0,
  "recovery_eval_rows": 8,
  "notes": "tool_use_accuracy compares final Skill: line to reference JSONL target_text; target_match_rate is an action-target string proxy (last Target: line). task_completion_rate is a strict proxy: format_compliance AND tool_skill_match AND target_match. error_recovery_rate_tuned is recovery_style_ok rate on rows with trajectory_type==recovery only; not CALVIN env success."
}
```

## Reproducibility snapshot

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

## Curated demo links

- **e2_cases**: `docs/failure_cases/e2_ablation_cases.md`
- **e2_demos**: `results/demos/e2_ablation_cases/`
- **rlbench_demos**: `results/demos/rlbench_fixture_bridge/`
- **mock_demos**: `results/demos/success_put_block/`
- **hybrid_experiments_smoke**: `results/experiments/hybrid_replanner_smoke/`
- **hybrid_experiments_eval**: `results/experiments/hybrid_replanner_eval/`
- **e2_mock_vs_calvin_table**: `docs/tables/e2_ablation_mock_vs_calvin_fixture.md`
- **e2_three_backend_table**: `docs/tables/e2_ablation_mock_vs_calvin_fixture_vs_calvin_debug_real.md`
- **calvin_debug_real_planner_stats**: `docs/calvin_debug_real_data_stats.md`
- **calvin_debug_alignment_stats**: `docs/calvin_debug_alignment_stats.md`
- **calvin_debug_alignment_audit**: `docs/calvin_debug_alignment_audit.md`
- **calvin_debug_same_task_subset**: `docs/calvin_debug_same_task_subset.md`
- **skill_schema_audit**: `docs/skill_schema_audit.md`
- **calvin_debug_alignment_comparison**: `docs/tables/calvin_debug_alignment_comparison.md`
- **hybrid_replanner_cases**: `docs/failure_cases/hybrid_replanner_cases.md`

## Open gaps / honest limitations

- Official CALVIN / RLBench leaderboard numbers: not claimed.
- RLBench full sim: blocked without CoppeliaSim + PyRep (see docs/rlbench_install_log.md) unless bridge_mode=sim_reset.
- A100 7B production training: template only.
- VLABench: planning doc only.
- RLBench Python import: false on this machine — using fixture bridge for cognition smoke.

## Failure taxonomy (registry snapshot)

| failure_type | condition (short) | replan hint |
|---|---|---|
| `target_not_found` | Planned target object id absent from post-action scene memory. | Re-ground from instruction + memory; optional LLM planner (hybrid path). |
| `wrong_object_grounded` | Action applied to an object inconsistent with instruction or planner target. | Rule: ``reselect_target_reach`` — reposition / reselect correct instance. |
| `precondition_unsatisfied` | Necessary state tags or spatial preconditions not met before skill. | Insert prerequisite subtask (open drawer, grasp) via rule replanner. |
| `state_unchanged` | Skill ran but relevant object tags unchanged (same as legacy ``action_no_effect` | Retry with alternate fallback wording or approach vector. |
| `action_no_effect` | Legacy wire value; treat as :attr:`FailureType.STATE_UNCHANGED` in new code. | Same as ``state_unchanged``. |
| `blocked_or_collision` | Physical blocking or collision prevents progress (reserved for sim hooks). | Retreat / clear path / alternate skill ordering. |
| `occlusion_or_low_confidence` | Target has low visibility or confidence in memory. | Observe or reposition sensor before acting. |
| `unknown_failure` | Verifier cannot classify; unhandled skill or ambiguous diff. | Hybrid LLM replanner if configured; else delegate to planner with failure_log. |

## Hybrid episode failure refinement

| failure_label | condition (short) | replan hint |
|---|---|---|
| `schema_valid_but_semantically_bad_replan` | Hybrid replanner emitted a schema-valid plan, but scene grounding or task semant | Tighten target grounding / semantic checks before accepting the revised plan. |
| `precondition_not_satisfied_after_replan` | Replanned skill still failed due to unmet prerequisites after the recovery step. | Insert prerequisite recovery subtasks before re-attempting the skill. |
| `no_state_change_after_valid_replan` | Replan ran, but the relevant scene state did not change. | Treat as an ineffective execution path, not a generic horizon bucket. |
| `repeated_no_effect_fallback_exhausted` | Rule fallback repeated the same action/target with consecutive no-effect verifie | Stop early with explicit exhaustion evidence instead of spending horizon on iden |
| `execution_not_effective` | Executor reports failure or no useful effect even when the taxonomy cannot pin i | Capture executor-side evidence and avoid collapsing directly to `unknown_failure |
| `environment_or_horizon_limit` | Episode reaches the horizon without a stronger semantic or execution-side explan | Treat as residual environment/horizon pressure, not a semantic planner failure. |
| `residual_unknown_failure` | Remaining ambiguous failure after applying the refinement rules. | Keep for audit follow-up; avoid overclaiming a more specific class. |

## Artifact index

- **episode_log_schema**: `docs/episode_log_schema.md`
- **scene_memory_contract_v2**: `docs/scene_memory_contract_v2.md`
- **failure_taxonomy_doc**: `docs/failure_taxonomy.md`
- **architecture_figure**: `docs/figures/architecture_v2.svg`
- **demo_assets**: `results/demos/`
- **sample_episode_logs**: `results/episode_logs/`
- **case_studies**: `results/eval/base_vs_tuned_case_studies.md`
- **e2_table**: `docs/tables/e2_ablation_summary.md`
- **hybrid_results_doc**: `docs/replanner_hybrid_results.md`
- **calvin_debug_dataset_audit**: `docs/calvin_debug_dataset_audit.md`