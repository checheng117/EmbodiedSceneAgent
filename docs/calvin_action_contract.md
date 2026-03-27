# CALVIN live `step(action)` 最小动作契约

**范围**：`CalvinEnvAdapter.step` 与真实 `PlayTableSimEnv.step` 之间的**最小**约定；**不**覆盖完整 CALVIN 模仿学习数据管线。

---

## 1. 期望的 `action` 类型与形状

- **类型**：`list[float]`、`tuple[float, ...]`、或 `numpy.ndarray`（一维）。
- **长度**：默认 **8** 维浮点，与 `ESA_CALVIN_ACTION_DIM` 环境变量一致（若你的安装使用其他维度，在运行前导出该变量，例如 `export ESA_CALVIN_ACTION_DIM=7`）。
- **`None`**：解释为「全零向量」`[0.0] * ESA_CALVIN_ACTION_DIM`（便于 smoke；**不保证**对仿真产生有意义的运动）。

**语义（待与官方数据对齐）**：

- 当前仓库**不**将各维固定标定为「关节 / 夹爪」；以你使用的 `calvin_env` 版本与数据集文档为准 → 标记为 **仍待确认**。

---

## 2. 真正传给 env 还是 symbolic？

| 路径 | 行为 |
|------|------|
| **Live**（`CalvinEnvAdapter` 持有 `calvin_env`） | `normalize_calvin_live_action` 后调用 **`calvin_env.step(action)`**，再 **`get_obs()` + `get_info()`** 刷新 `calvin_teacher_v0` |
| **Fixture / 无 live env** | `step` 抛出 `NotImplementedError`（**不**静默退回 symbolic） |
| **Symbolic 执行** | 通过 `apply_skill` / `apply_symbolic_planner_output`；**不**调用 `env.step`；trace 中须标明 `fixture_symbolic` 或 `live_observation_symbolic_fallback` 等 |

---

## 3. Skill → 动作映射（当前阶段）

| Skill | Live `step` | Symbolic |
|-------|-------------|----------|
| `open` / `close` / `grasp` / `place` | **未**实现自动 skill→action 映射；需外部策略或显式传入 `action` | 支持（teacher 启发式更新） |
| `reach` / `move_to` | 同上 | no-op 或占位 |

**结论**：长程任务成功率不应在「仅零动作 live step」下宣称；仅用于 **管线接通** 与 **运行级验证**。

---

## 4. 与 minimal loop 的关系

- `run_calvin_minimal_episode(..., live_action_strategy="live_zero_action_smoke")`：每步在 planner 之后对 live env 执行 **一次** `step(live_action)`（默认全零，或由 `live_action_fn` 生成），然后由 adapter 刷新 teacher / SceneMemory 并跑 verifier。
- `live_action_strategy="symbolic_fallback"`（默认）：在 **live reset 成功** 时，规划仍基于 **live 观测映射的 SceneMemory**，但技能走 **符号 teacher 更新**；trace 中 `action_mode=live_observation_symbolic_fallback`，**不**伪装成 live 物理成功。
- 若 `try_local_factory=True` 但 `ESA_CALVIN_ENV_FACTORY` 未配置或失败，会 **回退 fixture**，并在 `EpisodeTrace.loop_fallback_reason` 写明原因。

---

## 5. 当前 live smoke 的 action 策略（极简）

| 模式 | 行为 | 是否声称任务成功 |
|------|------|------------------|
| `live_zero_action_smoke` | `normalize_calvin_live_action(None)` → 全零（或 `ESA_CALVIN_ACTION_DIM` 维）→ `env.step` | **否**；仅接口与 teacher 刷新验证 |
| `symbolic_fallback`（live reset 时） | **不**调用 `env.step`；`apply_skill` 改 teacher | **否**；符号语义 |

Probe 脚本可加 `--step-smoke`：在 **reset 成功后**额外打一步零动作，并在 JSON 中记录 `step_smoke` 与 `after_step_observation_summary`（**不**等价于 benchmark 成功）。

---

## 6. 错误与调试

- 动作维度不符：抛出 `ValueError`，文案指向本文件。
- 未安装 / 无 `calvin_env`：不在此文档宣称成功；使用 `scripts/run_calvin_live_probe.sh` 查看 import / reset 阶段错误。
