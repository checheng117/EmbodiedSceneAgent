# Executive summary (≤1 page)

## What shipped

A **3D object-level scene memory**-centered **high-level cognition loop** (planner → skills → verifier → replanner) with **logged audits**, **real** small-model training artifacts, and **repeatable** eval scripts on mock / fixture / proxy metrics.

## Strongest measurable evidence (today)

- **Planner proxy:** `results/eval/planner_base_vs_tuned/metrics.json` — Not official CALVIN benchmark.
- **Hybrid replanner batch:** parse=0.0, validated=0.0, repair=1.0.
- **E2 story:** E2 mock (symbolic): latest batch shows verifier_plus_replan task_completion=1.0, recovery_success_rate=0.6666666666666666 — **fixture/smoke**, not official CALVIN.
- **CALVIN debug real-data E2:** E2 on official CALVIN **debug** vectors: status `available` — **not** leaderboard.
- **Hybrid (CALVIN debug batch):** {'replan_parse_success_rate': 1.0, 'validated_revision_rate': 1.0, 'fallback_rate': 0.0, 'repair_success_rate': 0.0, 'unknown_failure_rate': 0.375, 'unknown_skill_rate': 0.0, 'alias_normalization_count': 0, 'invalid_skill_count': 0}
- **RLBench:** deepest stage `import_fail`; fixture cognition bridge still valid.

## What we explicitly do **not** claim

- Official robot learning leaderboard ranks.
- End-to-end continuous control policy.
- Completed A100 7B production training or VLABench stress harness.

## Why it still matters

The repo demonstrates **contract-first embodied cognition engineering**: memory schema, planner JSON contract, verifier taxonomy, and hybrid replan auditing — a reusable substrate for future sim + benchmark scaling.
