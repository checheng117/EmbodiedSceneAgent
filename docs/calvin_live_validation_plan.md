# CALVIN 运行级验证计划（live env）

**状态**：本文件描述**如何**在真实安装 `calvin_env` 的环境中做运行级核对；**不**表示本仓库已在 CI 或默认环境中完成 live integration。

**原则**：区分 **代码层已验证**（单测 mock / 类型契约）、**计划运行验证**（本机 `calvin_env`）、**仍待确认**（依赖具体 Hydra 场景与版本）。

---

## 1. 目标实例：PlayTableSimEnv

**本地构造方式**：必须通过 **`ESA_CALVIN_ENV_FACTORY`** 提供可 import 的工厂（见 `docs/calvin_env_factory_usage.md`）；仓库内不猜测 Hydra 参数。

**计划使用的类**（与 `mees/calvin_env` 一致）：

- 模块路径（常见）：`calvin_env.envs.play_table_env` → `PlayTableSimEnv`

**仍待确认**：

- 你本地 fork / 版本里构造函数签名（是否必须经 Hydra 实例化、是否支持 `use_scene_info=True` 等）。
- 无头 / 离屏渲染参数名（`show_gui`、`useegl` 等）。

**代码层已验证**：

- `CalvinEnvAdapter` 对 **duck-typed** 对象调用 `reset` → `get_info`，并对返回的 `obs`/`info` 走 `map_live_calvin_to_teacher_bundle` 的契约（见单测 `_FakePlayTableEnv`）。

---

## 2. reset 前：配置 / 参数 / 初始状态

**计划运行验证**：

- `PlayTableSimEnv(..., use_scene_info=True)`（或等价配置），确保 `get_info()["scene_info"]` 非空，否则 `calvin_field_mapper` 无法构建物体级 teacher。
- 若官方流程要求 `reset(robot_obs=..., scene_obs=...)`，从数据集或 benchmark loader 提供种子向量（见 `docs/calvin_real_fields_audit.md` §1.5）。

**仍待确认**：

- 当前任务对应的默认 `scene.yaml` / 相机 / 物体集合。
- `reset()` 无参调用在你安装中是否合法。

---

## 3. reset 后预期可得的字段

**计划运行验证（建议打印 / 写入 summary JSON）**：

| 来源 | 字段 | 用途 |
|------|------|------|
| `get_obs()` | `rgb_obs`, `depth_obs`, `robot_obs`, `scene_obs` | 视觉与状态向量；teacher 物体级映射当前主要用 `info`，`scene_obs` 逐维语义仍待对齐 |
| `get_info()` | `robot_info` | TCP、gripper 宽度、关节等 → `calvin_teacher_v0.robot` |
| `get_info()` | `scene_info` | `doors`, `movable_objects`, … → `calvin_teacher_v0.scene_objects` |

**代码层已验证**：

- `summarize_live_calvin_obs_info()`（`envs/calvin_live_summary.py`）仅输出键名与 shape 元信息，不转储大数组。

**仍待确认**：

- `scene_obs` 各切片与物体实例的一一映射（依赖场景配置）。

---

## 4. get_obs / get_info / step：建议核对项

**计划运行验证**：

1. `reset` 返回的 `obs` 与随后 `get_obs()` 是否同形。
2. `step(a)` 的返回值：`(obs, reward, done, info)` 或仅 `obs`（需与你的 `calvin_env` 版本一致）。
3. `step` 后再次 `get_obs()` / `get_info()` 是否与返回值一致（本仓库 adapter 在 `step` 后会优先 `get_obs()` + `get_info()` 刷新 teacher）。

**代码层已验证**：

- `CalvinEnvAdapter.step` 在 live 路径下对动作长度与 `docs/calvin_action_contract.md` 一致时调用 `env.step`，并刷新 teacher（见实现与单测）。

---

## 5. instruction 来源

**已验证（源码审计）**：自然语言 **不**来自 `get_obs()`；须由数据集 / 评测脚本与观测并排传入（见 `docs/calvin_real_fields_audit.md` §2）。

**本仓库行为**：`CalvinEnvAdapter.reset(instruction=...)` 将 instruction 写入 `calvin_teacher_v0.language.instruction`。

---

## 6. 推荐执行顺序（本机）

1. `bash scripts/run_calvin_live_probe.sh`（加载 `.env`，尝试 import / 可选 reset，导出 obs/info summary）。
2. 若 import 失败：先按 CALVIN 官方文档安装 `calvin_env` 与依赖，再重试；**不要**在报告中写「已集成」。
3. 若 reset 失败：记录异常类型与信息（勿包含 token），对照本文件调整构造函数与 Hydra 配置。
4. 将 probe 输出的 summary JSON 与 `docs/calvin_real_fields_audit.md` 对照，更新「运行级已验证」备注（在后续 PR / 笔记中显式记录）。

---

## 7. 小结表

| 类别 | 内容 |
|------|------|
| **代码层已验证** | Adapter + mapper 契约；假 env 单测；`step` 最小动作长度契约；summary 脱敏 |
| **计划运行验证** | 真实 `PlayTableSimEnv` import、构造、reset、get_obs/get_info/step、instruction 并排传入 |
| **仍待确认** | Hydra 场景差异、`scene_obs` 索引、动作维度的官方定义与训练数据一致版本 |
