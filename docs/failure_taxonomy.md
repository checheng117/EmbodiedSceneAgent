# Failure taxonomy（验证器 / 重规划共用）

与 `embodied_scene_agent.verifier.schema.FailureType` 及 `verifier/taxonomy.py` 注册表 **一致**。旧日志中的 `action_no_effect` 与 `state_unchanged` 语义等价，**新代码优先 emit `state_unchanged`**。

| failure_type | 判定要点 | 触发示例 | 推荐 replan |
|--------------|----------|----------|-------------|
| `target_not_found` | after 中缺少计划目标对象 | target id 不在 `after.objects` | 重 ground；Hybrid 可走 LLM |
| `wrong_object_grounded` | 动作对象与指令/plan 不一致 | 抓了错误实例 | `reselect_target_reach`（规则） |
| `precondition_unsatisfied` | 技能前置 tag 不满足 | drawer 未开却 place | 插入 open / grasp 子任务 |
| `state_unchanged` | 执行前后相关 tag 不变 | grasp 无效果 | 重试 + 换 fallback / approach |
| `action_no_effect` | **遗留 wire 值** | 旧 JSONL | 同 `state_unchanged` |
| `blocked_or_collision` | 物理阻塞（预留） | 夹爪卡死 | 退避 / 换序 |
| `occlusion_or_low_confidence` | 可见度/置信过低 | visibility 低 | 先观察 / 重定位传感器 |
| `unknown_failure` | 未覆盖技能或模糊 diff | 新 skill 字符串 | Hybrid LLM 或 planner+failure_log |

**非 CALVIN 官方成功率**：本 taxonomy 服务 **认知层闭环日志与重规划**，不替代 benchmark 协议。
