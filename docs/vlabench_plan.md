# VLABench 在本项目中的位置（规划-only）

## 定位（blueprint）

- **主用途**：planner / replan **推理 stress**（长指令、干扰、语言陷阱），**不是**低层控制主战场。
- **不做**：声称已完成 VLABench 全量控制或官方榜单。

## 接口骨架（当前）

- 无硬依赖：可在后续增加 `envs/vlabench_planner_probe.py`（仅喂语言 + 伪观测 → `PlannerInput`），与 `planner_output_contract` 校验输出。
- 与 CALVIN/RLBench 共用：`PlannerOutput`、`failure_taxonomy`、`episode log`。

## 状态

| 项 | 标记 |
|----|------|
| 计划文档 | `implemented_now`（本文） |
| 可执行 adapter | `future_only` |
| 实验数字 | **禁止伪造** |
