# E2 ablation: mock vs CALVIN fixture vs CALVIN debug real-data

_**Not** official CALVIN leaderboard — three **dev** evidence layers._

| mode | metric | mock | calvin_fixture | calvin_debug_real |
|------|--------|------|----------------|-------------------|
| `none` | task_completion_rate | 1.0 | 1.0 | 0.0 |
| `none` | failure_detected_rate | 0.0 | 0.0 | 0.0 |
| `none` | replan_trigger_rate | 0.0 | 0.0 | 0.0 |
| `none` | recovery_success_rate | 0.0 | 0.0 | 0.0 |
| `none` | average_steps | 4.0 | 2.3333333333333335 | 12.0 |
| `verifier_only` | task_completion_rate | 1.0 | 1.0 | 0.0 |
| `verifier_only` | failure_detected_rate | 0.25 | 0.0 | 0.9583333333333334 |
| `verifier_only` | replan_trigger_rate | 0.0 | 0.0 | 0.0 |
| `verifier_only` | recovery_success_rate | 0.0 | 0.0 | 0.0 |
| `verifier_only` | average_steps | 4.0 | 2.3333333333333335 | 12.0 |
| `verifier_plus_replan` | task_completion_rate | 1.0 | 1.0 | 0.0 |
| `verifier_plus_replan` | failure_detected_rate | 0.2 | 0.0 | 0.9583333333333334 |
| `verifier_plus_replan` | replan_trigger_rate | 0.6666666666666666 | 0.0 | 11.5 |
| `verifier_plus_replan` | recovery_success_rate | 0.6666666666666666 | 0.0 | 0.0 |
| `verifier_plus_replan` | average_steps | 3.3333333333333335 | 2.3333333333333335 | 12.0 |

## 三层证据各自意味着什么

- **mock**：符号环境，最适合隔离 verifier / replan 机制，数值最“干净”。
- **CALVIN fixture**：JSON fixture + 与 CALVIN 同形的 teacher，测 adapter / 解析应力，**仍非**官方轨迹。
- **CALVIN debug real-data**：官方 **debug** 包中的 **robot_obs/scene_obs** 向量重构 teacher，再跑同一套最小认知闭环；**不是** D/ABC/ABCD 全量，也**不是** leaderboard。

## 不能解读为

- 官方 CALVIN benchmark 排名、成功率可比全论文设置、或与仿真逐步物理回放等价。

### Artifact paths（相对仓库根）

- mock: `results/experiments/e2_ablation/e2_mock_20260331T083930Z`
- calvin_fixture: `results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z`
- calvin_debug_real: `results/experiments/e2_ablation/e2_calvin_debug_real_aligned_20260331T084633Z`
