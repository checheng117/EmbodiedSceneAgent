# E2 ablation summary (markdown figure)

_No PNG under `results/experiments/e2_ablation/` on this snapshot — table from latest JSON._

## Mock symbolic

| mode | task_completion | failure_detected_rate | recovery_success | avg_steps |
|------|----------------:|----------------------:|-----------------:|----------:|
| `none` | 1.0 | 0.0 | 0.0 | 4.0 |
| `verifier_only` | 1.0 | 0.25 | 0.0 | 4.0 |
| `verifier_plus_replan` | 1.0 | 0.2 | 0.6666666666666666 | 3.3333333333333335 |

## CALVIN fixture

| mode | task_completion | failure_detected_rate | recovery_success | avg_steps |
|------|----------------:|----------------------:|-----------------:|----------:|
| `none` | 1.0 | 0.0 | 0.0 | 2.3333333333333335 |
| `verifier_only` | 1.0 | 0.0 | 0.0 | 2.3333333333333335 |
| `verifier_plus_replan` | 1.0 | 0.0 | 0.0 | 2.3333333333333335 |

## CALVIN official debug (vector teacher)

| mode | task_completion | failure_detected_rate | recovery_success | avg_steps |
|------|----------------:|----------------------:|-----------------:|----------:|
| `none` | 0.0 | 0.0 | 0.0 | 12.0 |
| `verifier_only` | 0.0 | 0.9583333333333334 | 0.0 | 12.0 |
| `verifier_plus_replan` | 0.0 | 0.9583333333333334 | 0.0 | 12.0 |
