# Episode log schema（`esa_episode_log/v1`）

统一 rollout 日志，供可视化、报告、跨 benchmark 消费。

## 顶层（episode）

沿用 `EpisodeTrace`（`pipeline/v0_loop.py`）：`instruction`, `success`, `steps[]`, `replan_count`, `final_message`, 以及 CALVIN 线特有的 `env_mode` / `teacher_source` 等。

## 单步记录（`EpisodeStepLog`）

代码：`pipeline/episode_log_schema.py`。

| 字段 | 说明 |
|------|------|
| `schema_version` | `esa_episode_log/v1` |
| `observation_id` | 可选跨系统 id |
| `timestep` | 步索引 |
| `scene_memory_before` | `SceneMemory.to_json_dict()` |
| `planner_output` | `PlannerOutput.model_dump` |
| `executor_receipt` | `skill_result` |
| `scene_memory_after` | 执行后记忆 |
| `verifier_decision` | `VerificationResult` |
| `failure_type` | 冗余字符串便于聚合 |
| `replanner_output` | 若有 replan |
| `replan_audit` | `ReplannerAuditLog` |
| `scene_memory_after_replan` | replan 后再执行 |
| `executor_receipt_replan` / `verifier_decision_replan` | 可选 |
| `final_step_outcome` | 粗粒度结果枚举字符串 |

## 样例文件

- `results/episode_logs/sample_v0_episode_steps.json`（由 `scripts/make_demo_assets.sh` 生成）

## 映射工具

- `step_dict_to_episode_step_log`：将 legacy v0 step dict 升为 `EpisodeStepLog`。
