# 开发路线图

与蓝图一致，分为 **v0 / v1 / v2** 三档交付。

## v0：最小闭环（当前仓库基线）

- Teacher-state（或 mock）→ **对象级 scene memory**
- **RuleBasedPlanner** 结构化输出 + schema 校验
- **SkillExecutor** + 最小技能集（reach/grasp/place/open/close/move_to）
- **StateDiffVerifier** + 失败 taxonomy
- **RuleBasedReplanner** 接口落地
- **MockEmbodiedEnv** 跑通单 episode；`scripts/run_smoke_v0.sh` 可执行
- 单测：memory / planner IO / verifier / smoke v0

**验收**：一条可复现的 episode trace（JSON/log），含 success 或 replan 路径。

## v1：主页展示版

- CALVIN **dev** 接入路径：teacher-state adapter 接真实状态字段（分步实现）
- 可视化：scene graph / episode 文本或 graphviz 导出
- RLBench 子集 adapter 雏形与统一评测脚本
- 实验报告：`report_builder` 生成汇总表（指标占位，不伪造数值）

## v2：面试强化版

- 3090：**Qwen2.5-VL-3B** LoRA 实验管线稳定；schema 固定
- A100：**Qwen2.5-VL-7B** 正式训练/评测入口；批量 rollout
- VLABench 子集：planner/replan 压测
- 可选：predicted memory 替代部分 teacher-state；核心消融实验矩阵

**正式结果**：以 A100 产出的配置快照与日志为准（与 blueprint 一致）。
