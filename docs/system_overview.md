# 系统总览（EmbodiedSceneAgent）

**项目名称**：EmbodiedSceneAgent  
**副标题**：3D-aware Vision-Language Planning for Long-Horizon Manipulation  

## 1. 定位

面向多模态大模型 / 具身智能岗位的**旗舰研究工程**：重点不是从零训练端到端 VLA，而是构建**对象级 3D scene memory + 结构化 planner + skill executor + verifier + replanner + benchmark 评测**的完整认知层闭环。

- **主 benchmark**：CALVIN（长程语言条件操作）
- **辅助**：RLBench 子集（泛化）、VLABench 子集（reasoning 压测）
- **算力**：3090 24G — 日常开发、调试、3B planner 与小规模实验；A100 80G — 7B planner 最终训练/测试与批量 rollout。**不考虑 T4 作为主流程。**

## 2. 六段式流水线

```
Observation → Scene Memory → Planner → Skill Executor → Verifier → Replanner
     ↑___________________________________________________________________|
```

| 阶段 | 作用 |
|------|------|
| **Observation** | 原始观测或仿真器状态入口（v0：mock；**CALVIN-grounded 开发**：`calvin_teacher_v0` 风格 teacher dict，见 `docs/calvin_adapter_plan.md`） |
| **Scene Memory** | 将观测整理为**对象级**图结构：物体、位姿、状态标签、对象间关系 |
| **Planner** | 输出**结构化**下一步：subgoal、target、skill、success_check、fallback（非自由文本为主流程） |
| **Skill Executor** | 将高层技能映射到环境可执行动作（预置技能库 / 适配器，非从零 joint policy） |
| **Verifier** | 根据前后状态与子目标判断是否成功，并给出**失败类型** |
| **Replanner** | 在失败时基于 memory + 历史 + 失败信息**局部修订**下一步计划 |

## 3. 为何采用对象级 3D memory

- **可解释**：便于向 reviewer/面试官说明规划依据。
- **可操作**：planner 直接读写物体名、3D、关系，输出固定 schema。
- **可验证**：verifier 可对 before/after 做可检查的差异与失败分类。
- **可迁移**：换 benchmark 时主要替换 perception/adapter，不必推翻认知层。

## 4. 为何 teacher-state 先行

v0/v1 优先使用仿真器提供的 teacher-state 构建高质量 scene memory，把研究焦点放在**高层认知层如何利用 3D 中间表示**；待 schema 与闭环稳定后，再接入 RGB-D predictor 等 **predicted memory**（见路线图）。

## 5. 为何主 benchmark 是 CALVIN

CALVIN 面向 **long-horizon language-conditioned manipulation**，与「scene memory + 子目标规划 + 验证 + 重规划」的叙事一致，适合作为**主实验场**；RLBench/VLABench 用于泛化与 reasoning 补充，避免单环境过拟合叙事。

## 6. 与仓库代码的对应关系

| 概念 | 包路径 |
|------|--------|
| Scene Memory | `embodied_scene_agent.memory` |
| Teacher-state / 适配 | `embodied_scene_agent.perception` |
| Planner | `embodied_scene_agent.planner` |
| Skills | `embodied_scene_agent.skills` |
| Verifier | `embodied_scene_agent.verifier` |
| Replanner | `embodied_scene_agent.replanner` |
| 环境 / Benchmark 适配 | `embodied_scene_agent.envs` |
| 训练入口（占位） | `embodied_scene_agent.training` |
| 评测与报告 | `embodied_scene_agent.evaluation` |
| 可视化 | `embodied_scene_agent.visualization` |

详见 `docs/module_contracts.md`。  
**CALVIN 最小接入**（非官方评测）：`CalvinEnvAdapter` + `CalvinTeacherStateAdapter`，`tests/fixtures/calvin_mock_observation.json` 为结构模拟样本。
