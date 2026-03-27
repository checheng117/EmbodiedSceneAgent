# 流水线模块表（自动生成友好版，真源在代码）

| 段 | 包路径 | 契约 / 备注 |
|----|--------|----------------|
| Scene Memory | `memory/schema.py`, `memory/cognitive_snapshot.py` | `esa_sm/v1` 序列化 + v2 契约文档 |
| Planner | `planner/schema.py`, `planner/planner_output_contract.py` | 固定 `PlannerOutput` 字段 |
| Skills | `skills/executor.py` | 路由到 env / adapter |
| Verifier | `verifier/state_diff.py`, `verifier/taxonomy.py` | `FailureType` 注册表 |
| Replanner | `replanner/rule_based.py`, `replanner/hybrid.py` | audit 日志 |
| Episode log | `pipeline/episode_log_schema.py` | `esa_episode_log/v1` |
| Reporting | `reporting/make_project_report.py` | 汇总 JSON+MD |
