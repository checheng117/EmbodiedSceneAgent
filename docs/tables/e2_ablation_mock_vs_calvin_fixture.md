# E2 ablation: mock symbolic vs CALVIN fixture batch

_**Fixture / dev batch only** — not official CALVIN ablation or leaderboard._

| mode | metric | mock | calvin_fixture | same? |
|------|--------|------|----------------|-------|
| `none` | task_completion_rate | 1.0 | 1.0 | yes |
| `none` | failure_detected_rate | 0.0 | 0.0 | yes |
| `none` | replan_trigger_rate | 0.0 | 0.0 | yes |
| `none` | recovery_success_rate | 0.0 | 0.0 | yes |
| `none` | average_steps | 4.0 | 2.3333333333333335 | no |
| `verifier_only` | task_completion_rate | 1.0 | 1.0 | yes |
| `verifier_only` | failure_detected_rate | 0.25 | 0.0 | no |
| `verifier_only` | replan_trigger_rate | 0.0 | 0.0 | yes |
| `verifier_only` | recovery_success_rate | 0.0 | 0.0 | yes |
| `verifier_only` | average_steps | 4.0 | 2.3333333333333335 | no |
| `verifier_plus_replan` | task_completion_rate | 1.0 | 1.0 | yes |
| `verifier_plus_replan` | failure_detected_rate | 0.2 | 0.0 | no |
| `verifier_plus_replan` | replan_trigger_rate | 0.6666666666666666 | 0.0 | no |
| `verifier_plus_replan` | recovery_success_rate | 0.6666666666666666 | 0.0 | no |
| `verifier_plus_replan` | average_steps | 3.3333333333333335 | 2.3333333333333335 | no |

## Interpretation (honest)

- **Consistent** rows suggest verifier/replan wiring behaves similarly across mock vs CALVIN teacher-state fixture.
- **Divergent** `task_completion_rate` / `average_steps` usually reflect **different symbolic physics** (mock discrete vs CALVIN teacher mutation) and **scene layout**, not benchmark ranking.
- **failure_detected_rate** may shift when CALVIN steps emit different verifier failure mixes (`state_unchanged` vs others).

### Mock vs CALVIN fixture（可直接进最终报告）

- **Mock symbolic** 更“干净”：状态转移集中在单进程符号环境里，verifier 触发的失败类型更容易按设计复现，适合隔离「仅验证器 / +replan」机制差异。
- **CALVIN fixture** 更接近 **adapter reality**：观测与 teacher 字段来自与 CALVIN 同形的 JSON fixture + 最小闭环，能暴露解析与状态同步上的边角，但仍是 **fixture/smoke**，不是官方 CALVIN 排行榜。
- **仅在符号层成立的结论**：例如 mock 上精确的步数对比、某些 `failure_taxonomy` 计数比例；换到 fixture 后应视为「趋势一致 /  wiring 一致」而非数值 1:1 推广。

- Mock artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/e2_ablation/e2_mock_20260331T083930Z`
- CALVIN fixture artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/e2_ablation/e2_calvin_fixture_20260331T084742Z`
