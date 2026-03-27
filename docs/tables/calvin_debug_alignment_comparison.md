# CALVIN debug：对齐方式对照（pooled vs grouped vs same-task）

_下列 E2 / hybrid 数字来自一次本地跑通的 artifact（**非** leaderboard）；pooled 行若未单独重跑可标 n/a。_

**Planner JSONL 行数**：见 `docs/calvin_debug_alignment_stats.md`。

## E2（`verifier_plus_replan` 模式）

| 批次 | experiment_id | n_episodes | task_completion_rate | failure_detected_rate | replan_trigger_rate | recovery_success_rate | average_steps |
|------|---------------|------------|------------------------|------------------------|---------------------|----------------------|---------------|
| grouped_sequence（aligned） | `e2_calvin_debug_real_aligned_20260326T094535Z` | 16 | 0.0 | 0.948 | 11.375 | 0.0 | 12.0 |
| same_task_subset | `e2_calvin_debug_same_task_20260326T094540Z` | 8 | 0.0 | 0.958 | 11.5 | 0.0 | 12.0 |

## Hybrid（本机 CPU replanner）

| 批次 | experiment_id | n_episodes | repair_success_rate | unknown_skill_rate | invalid_skill_count | alias_normalization_count |
|------|---------------|------------|---------------------|--------------------|-----------------------|---------------------------|
| grouped_sequence | `hybrid_calvin_debug_real_aligned_20260326T094544Z` | 6 | 0.0 | 0.167 | 1 | 1 |
| same_task_subset | `hybrid_calvin_debug_same_task_20260326T094718Z` | 4 | 0.0 | 0.0 | 0 | 1 |

**解读（克制）**：same-task hybrid 子批上 **`invalid_skill_count` 降为 0**，说明 schema 类失败减少；`repair_success_rate` 仍为 0，**不得**解释为「语义已修好」。E2 指标在两批上仍接近，主要仍受符号闭环与指令–布局关系支配，而非官方任务标签。

**Artifact 根目录**：`results/experiments/e2_ablation/`、`results/experiments/hybrid_replanner_eval/`。
