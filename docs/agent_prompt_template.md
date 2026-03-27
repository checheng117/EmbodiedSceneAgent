# Planner 提示模板（训练 / 评测一致）

实现真源：`src/embodied_scene_agent/training/agent_prompt.py`（`build_user_prompt`、`format_plan_block`、`format_recovery_supervision`、`parse_planner_completion`）。

## User 模板（摘要）

1. 说明角色：结构化操作 planner，仅使用所列技能。  
2. `Available tools (JSON)`：`reach` / `grasp` / `place` / `open` / `close` / `move_to`。  
3. `Instruction`、`Scene memory (JSON)`、`Completed subgoals (history)`、`Failure log`。  
4. 要求输出 **固定英文键名**（无 markdown 围栏）。

## Assistant 模板（单步成功）

```
Plan:
Task: <short id>
Subgoal: <one sentence>
Target: <object_id>
Skill: <skill name from tools>
Success_Check: <verifiable condition>
Fallback: <short recovery hint>
```

## Assistant 模板（失败恢复一步）

在 **首个** `Plan:` 块后追加：

```
Observation:
Skill_result: {... JSON ...}
Verification: {... JSON ...}
Thought: Initial plan failed verification; replan before continuing.
Plan:
Task: ...
Subgoal: ...
...
```

（第二个 `Plan:` 块为修订计划；`parse_planner_completion` 对多段 `Plan:` 取 **最后一次**出现的字段。）

## Qwen2.5-VL 输入

- 训练/推理均在 user 侧附带 **一张占位 RGB 图像**（224×224 纯色），由 `qwen_vl_utils.process_vision_info` 与 `AutoProcessor` 处理；**不**声称与 CALVIN 相机对齐。

## 完整样例（节选）

**User**（结构示意）：

```text
You are a structured manipulation planner...
Available tools (JSON):
[ { "name": "grasp", ... }, ... ]
Instruction:
Put the red block in the drawer.
Scene memory (JSON):
{ "schema_version": "esa_sm/v1", "objects": { ... } }
...
```

**Assistant**：

```text
Plan:
Task: open_drawer
Subgoal: Open the drawer fully.
Target: drawer
Skill: open
Success_check: drawer has state tag 'open'
Fallback: reach handle from the right
```

（字段大小写以 `agent_prompt.py` 中 `build_user_prompt` 为准：`Success_Check:` 带下划线。）
