# Showcase Results

This page highlights the most important current results with explicit scope boundaries.

Companion pages:

- `docs/showcase_cases.md`
- `docs/limitations.md`

## 1) Primary quantitative comparison (base vs tuned, n=73)

Source: `results/eval/planner_base_vs_tuned/metrics.json`

| Track | Format compliance | Tool-use accuracy | Target-match rate | Strict task proxy |
|------|---:|---:|---:|---:|
| Stable baseline | 1.000 | 0.082 | 0.329 | 0.068 |
| Tuned (LoRA 3B minimal) | 1.000 | 0.219 | 0.479 | 0.205 |

Interpretation:

- Structured output compliance remains stable (`1.000 -> 1.000`).
- Action-target correctness proxies improve under the tuned path.
- The strict task metric here is a proxy metric computed from structured match conditions, not official CALVIN environment success.

## 2) Secondary controlled tiny comparison (3 fixed episodes)

Run roots:

- Baseline: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T103029Z`
- VL-3B: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`
- VL-7B: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`

Accepted revised plans:

- Baseline: `0/3`
- VL-3B: `3/3`
- VL-7B: `2/3`

Interpretation:

- VL-3B is currently the strongest secondary qualitative track in this tiny controlled setting.
- VL-7B is runnable and partially successful but does not outperform VL-3B on this tiny set.
- This is diagnostic evidence only and should not be interpreted as benchmark-scale ranking.

## 3) Failure profile note

In these tiny runs, terminal failures are still dominated by `repeated_no_effect_fallback_exhausted`, indicating a remaining execution-side bottleneck after planning/replanning validity checks.
