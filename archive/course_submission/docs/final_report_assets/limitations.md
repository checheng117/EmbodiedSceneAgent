# Limitations (copy-paste ready)

This file is **honest scope** for final reports, posters, and advisor email — **do not soften**.

## RLBench

- **Real sim `sim_reset` is not demonstrated** on the reference dev machine: deepest stage is `import_fail` (see `results/rlbench_stack_diagnosis.json`).
- **Fixture → SceneMemory → planner** smoke **is** real evidence for the cognition adapter path.

## Benchmarks

- **No official CALVIN / RLBench leaderboard numbers** are claimed.
- **E2** results include **mock**, **CALVIN fixture**, and **CALVIN official debug npz (vector teacher)** batches — wiring + real-vector evidence, **not** benchmark rank.

## Hybrid LLM replanner

- Latest **mock** batch headline (may omit skill counters): {"replan_parse_success_rate": 0.0, "validated_revision_rate": 0.0, "fallback_rate": 1.0, "repair_success_rate": 1.0, "unknown_failure_rate": 0.6, "unknown_skill_rate": 0.0, "alias_normalization_count": 0, "invalid_skill_count": 0}.
- CALVIN debug hybrid eval also records **`unknown_skill_rate`**, **`invalid_skill_count`**, **`alias_normalization_count`** under `results/experiments/hybrid_replanner_eval/*/metrics.json` (schema tightening; not a claim of semantic mastery).
- **`parse_error_kind_counts` empty** only means **that run** had no counted parse-error kinds — not a general guarantee.

## Training / scale

- **A100 / 7B / full VLABench harness**: **future_only** (templates and docs exist; no production claim).

## Teacher-state bootstrap

- Using teacher-state / fixtures is a **deliberate reproducibility choice**, not claimed as self-supervised perception superiority.
