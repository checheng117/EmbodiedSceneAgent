# E2 ablation — curated cases

## Mock symbolic

_稳定选例策略：`scenario_id_whitelist_relaxed`，episode_index=`1`（见 `results/demos/e2_ablation_cases/mock_selection_meta.json`）。_

### 1) Verifier missing → missed failure handling
- mode `none`, episode_index `0`: verifier disabled so failures not surfaced in verification channel.
- Demo: [`results/demos/e2_ablation_cases/case1_none.json`](../../results/demos/e2_ablation_cases/case1_none.json)

### 2) Verifier without replan
- mode `verifier_only`, episode `1`: success=True, replan_count=0.
- Demo: [`results/demos/e2_ablation_cases/case2_verifier_only.json`](../../results/demos/e2_ablation_cases/case2_verifier_only.json)

### 3) Verifier + replan recovery
- mode `verifier_plus_replan`, episode `1`: success=True, replans=1.
- Demo: [`results/demos/e2_ablation_cases/case3_plus_replan.json`](../../results/demos/e2_ablation_cases/case3_plus_replan.json)

## CALVIN fixture batch (dev — not official benchmark)

_选例元数据：`results/demos/e2_ablation_cases/calvin_selection_meta.json`（与 mock 案例同目录便于引用）。_

### 4) `verifier_only` 卡住；`verifier_plus_replan` 在同一 episode 设定下恢复
- episode_index `1`；对比 trace：
  - [`results/demos/e2_ablation_calvin_cases/calvin_case_replan_fixes_stuck_verifier_only.json`](../../results/demos/e2_ablation_calvin_cases/calvin_case_replan_fixes_stuck_verifier_only.json)
  - 同内容镜像：[`results/demos/e2_ablation_cases/calvin_case_replan_fixes_stuck_verifier_only.json`](../../results/demos/e2_ablation_cases/calvin_case_replan_fixes_stuck_verifier_only.json)

### 5) 检出 failure 但 repair / 后续仍失败
- episode_index `0`：
  - [`results/demos/e2_ablation_calvin_cases/calvin_case_repair_failed_after_failure_detected.json`](../../results/demos/e2_ablation_calvin_cases/calvin_case_repair_failed_after_failure_detected.json)
  - 镜像：[`results/demos/e2_ablation_cases/calvin_case_repair_failed_after_failure_detected.json`](../../results/demos/e2_ablation_cases/calvin_case_repair_failed_after_failure_detected.json)

## CALVIN debug real-data backed (not benchmark)

_官方 debug npz 向量 teacher + 最小闭环；**非** leaderboard。下列分节对应不同 `CALVIN_DEBUG_BATCH` / `--calvin-debug-batch`，互不覆盖。_

## CALVIN debug — grouped_sequence (aligned)

_选例：`results/demos/e2_ablation_cases/calvin_debug_real_aligned_selection_meta.json`；来源标签 **`calvin_debug_real_aligned`**._

### verifier_only（debug 向量 teacher）
- episode_index `0`；[`calvin_debug_real_aligned_case_verifier_only.json`](../../results/demos/e2_ablation_cases/calvin_debug_real_aligned_case_verifier_only.json)

### verifier_plus_replan（同一设定族）
- episode_index `0`；[`calvin_debug_real_aligned_case_verifier_plus_replan.json`](../../results/demos/e2_ablation_cases/calvin_debug_real_aligned_case_verifier_plus_replan.json)

## CALVIN debug — same_task_subset

_选例：`results/demos/e2_ablation_cases/calvin_debug_same_task_selection_meta.json`；来源标签 **`calvin_debug_same_task`**._

### verifier_only（debug 向量 teacher）
- episode_index `0`；[`calvin_debug_same_task_case_verifier_only.json`](../../results/demos/e2_ablation_cases/calvin_debug_same_task_case_verifier_only.json)

### verifier_plus_replan（同一设定族）
- episode_index `0`；[`calvin_debug_same_task_case_verifier_plus_replan.json`](../../results/demos/e2_ablation_cases/calvin_debug_same_task_case_verifier_plus_replan.json)
