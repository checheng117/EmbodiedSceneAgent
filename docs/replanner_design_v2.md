# Replanner design v2（rule-first + optional LLM）

## 定位（blueprint）

- **局部修订**为主，避免每次失败重写整段计划。
- **规则优先**覆盖高频、可解释失败；**复杂/未知**才走 `HybridReplanner` 的可选 LLM 回调。

## 实现

| 组件 | 路径 | 说明 |
|------|------|------|
| RuleBasedReplanner | `replanner/rule_based.py` | 前置子任务插入、state_unchanged 重试、wrong_object / occlusion 规则分支、最后委托 RuleBasedPlanner |
| HybridReplanner | `replanner/hybrid.py` | `unknown_failure` / `target_not_found` 可注入 `llm_replan` |
| 审计 | `replanner/audit.py` → `ReplannerAuditLog` | `original_subgoal`, `failure_type`, `repair_strategy`, `revised_subgoal`, `whether_rule_based` |

## 审计落盘

`pipeline/v0_loop.py` 在 replan 时写入 `step_log["replan_audit"]`（JSON）。

## 与 failure taxonomy 的映射（摘要）

- `precondition_unsatisfied` + `place` → 插入 `open` 或 `grasp`。
- `state_unchanged` + `grasp`/`open` → 同技能重试 + 换 fallback 文案。
- `wrong_object_grounded` → reach / 重选 target。
- `occlusion_or_low_confidence` → observe / reposition 占位计划。

## 未完成（诚实）

- 真实 LLM replan 需与 `planner_output_contract` 及 JSON 约束生成对齐；当前 **默认未接 LLM**。
