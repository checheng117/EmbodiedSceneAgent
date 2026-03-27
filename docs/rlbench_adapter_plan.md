# RLBench adapter 计划（辅助泛化，非第二套 planner）

## 目标

- **换 adapter，不推翻认知层**：同一套 `SceneMemory`、`PlannerOutput`、failure taxonomy、`esa_episode_log`。
- 证明高层 **3D object-centric memory + planner + verifier + replanner** 不绑定 CALVIN 单一数据分布。

## 当前实现阶段（诚实）

| 阶段 | 状态 |
|------|------|
| Observation→SceneMemory 映射 | **已实现** — `numpy_observation_to_dict` + `observation_like_dict_to_scene_memory` |
| Fixture qualitative episode | **已实现** — `python -m embodied_scene_agent.evaluation.rlbench_smoke` |
| `try_rlbench_reset_observation`（真 sim） | **代码已写**；需 CoppeliaSim + PyRep + `rlbench`（见 `docs/rlbench_install_log.md`） |
| 10–18 任务子集硬接线 | **部分**：`RLBenchAdapterConfig.task_names` + `docs/rlbench_task_subset.md` |
| 正式 RLBench 数字报告 | **未做** |

## Smoke

- `bash scripts/run_rlbench_dev_smoke.sh` → `results/rlbench_dev_smoke.json` + `results/episode_logs/rlbench_qualitative_episode.json` + `results/demos/rlbench_fixture_bridge/`。
- 安装尝试记录：`docs/rlbench_install_log.md`。

## 下一步（工程）

1. 选 2–4 个低耦合任务（如 Reach / PickUpCup / OpenDrawer）。
2. 观测 → 与 CALVIN 对齐的 teacher 字典 → `SceneMemoryBuilder`。
3. 复用 `SkillExecutor` 路由或薄包装 RLBench `action` API（仍非端到端 VLA）。
