# One-page project brief

## 1. What this project is

A **blueprint-aligned** embodied **cognition layer**: Scene Memory → Planner → (symbolic) Skills → Verifier → Replanner, with structured logging — **not** a monolithic vision-language-action policy.

## 2. Why it matters

Makes **grounding, legality, and failure recovery** inspectable via shared contracts instead of hiding state in weights.

## 3. What is already real

- Contracts + taxonomy + episode schema (docs + tests).
- 3B planner SFT checkpoint + JSONL **proxy** eval.
- E2 ablations (**mock** + **CALVIN fixture** + **CALVIN official debug vectors**).
- Hybrid replanner **batch** with audit metrics.
- RLBench **diagnosis + fixture** cognition bridge.

## 4. Best current evidence

{
  "strongest_artifact": {
    "name": "planner JSONL proxy (base vs tuned)",
    "path": "results/eval/planner_base_vs_tuned/metrics.json",
    "note": "Not official CALVIN benchmark."
  },
  "hybrid_headline": {
    "replan_parse_success_rate": 0.0,
    "validated_revision_rate": 0.0,
    "fallback_rate": 1.0,
    "repair_success_rate": 1.0,
    "unknown_failure_rate": 0.6,
    "unknown_skill_rate": 0.0,
    "alias_normalization_count": 0,
    "invalid_skill_count": 0
  },
  "rlbench_stage": "import_fail"
}

## 5. What is not done yet

- Official CALVIN/RLBench leaderboard runs.
- RLBench `sim_reset` on this machine (import/CoppeliaSim stack).
- A100 7B training, VLABench harness execution.

## 6. Why it is still a strong project

End-to-end **engineering proof** of a reusable cognition interface with **honest** evaluation boundaries — the right foundation before expensive sim + GPU scale-up.
