# v0 范围说明

## 1. 目标

实现**可运行**的最小闭环（smoke），证明模块边界与数据契约正确，而非追求 CALVIN 全量分数或 7B 训练完成。

## 2. 包含

- **对象级** `SceneMemory` + JSON 序列化 + builder  
- **Teacher-state** 适配：`MockTeacherStateAdapter` + 可扩展 `BaseTeacherStateAdapter`  
- **RuleBasedPlanner** + `PlannerOutput` Pydantic 校验 + JSON 序列化工具  
- **SkillRegistry** + **SkillExecutor** + 最小技能（含 mock 语义）  
- **StateDiffVerifier** + `FailureType`  
- **RuleBasedReplanner**  
- **MockEmbodiedEnv**：单指令玩具场景，可模拟失败以触发 replan  
- **eval_v0**：success、subgoal 步数、replan 次数、失败类型统计（单机 mock）  
- **CLI**：`esa-run-v0` / `python -m embodied_scene_agent.cli.run_v0`  
- **测试**：memory、planner IO、verifier、smoke  

## 3. 不包含（明确推迟）

- CALVIN/RLBench/VLABench **完整**仿真连接与官方排行榜数字  
- 端到端训练 Qwen2.5-VL（仅脚本与配置占位）  
- 稠密 NeRF/3DGS 场景表示  
- 真实机器人控制栈  

## 4. 验收

- `bash scripts/run_smoke_v0.sh` 退出码 0  
- `pytest tests/test_smoke_v0.py` 通过  
