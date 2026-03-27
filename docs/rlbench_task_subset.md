# RLBench 任务子集（本轮固定 2–4 个）

_诚实边界：无 CoppeliaSim + `rlbench` import 时，**仅** `fixture_file` + 映射代码可用；**不**声称官方任务分数。_

## 固定最小子集

| 任务 | sim_reset（真实） | fixture / 映射 | blocked / 备注 |
|------|-------------------|----------------|----------------|
| **ReachTarget** | 若 `import_ok` 且 PyRep+CoppeliaSim 可用，可由 `try_rlbench_reset_observation` 跑通 reset→低维 obs | **fixture**：`tests/fixtures/rlbench_observation_like.json`；**memory_bridge + planner_smoke**：在 smoke 中验证 | 否则卡在 **import** 或 **env_create**（见 `results/rlbench_dev_smoke.json` 的 `stages`） |
| **OpenDrawer** | 未在本轮单测 sim_reset 成功路径中固化 | 任务类可通过 `resolve_task_class` 解析（若包已装）；**SceneMemory** 仍缺专用物体字段 | **memory_bridge** 对 drawer 语义为 **partial / 推断不足** |
| **PickUpCup** | 同上 | 同上 | 同上 |

> 代码中历史列表若含 `CloseDrawer`，与 OpenDrawer 同属 **manipulation 类**；本轮文档只强调 **ReachTarget** 为唯一「低维→目标点」对齐较好的代表，其余为 **blocked 或 partial**，直至接好任务专用低维或视觉字段。

## 依赖

- 分层诊断与日志：`docs/rlbench_install_log.md`、`bash scripts/run_rlbench_dev_smoke.sh`（`--mode all` 推荐）。
- 映射审计：`docs/rlbench_memory_mapping_audit.md`。
