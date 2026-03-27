# CALVIN Live 运行级验证结果（事实回填）

**本文档只记录在本机真实运行 probe / minimal loop 后的结果。**  
**不写**「已集成 CALVIN」或 benchmark 结论。

---

## 如何使用本模板（后续追加新行）

1. 运行 `bash scripts/run_calvin_live_probe.sh`（reset 成功后再加 `--step-smoke`）。
2. 将 `results/calvin_live_probe_summary.json` 摘要进下方「运行记录」表（勿粘贴 token）。
3. 对照 `docs/calvin_real_fields_audit.md` 填写一致性表。

---

## 运行记录

| 日期 | 机器/OS | Python / Conda | `ESA_CALVIN_ENV_FACTORY` | probe 命令 |
|------|---------|----------------|---------------------------|------------|
| 2026-03-26 | Linux（本机） | conda **`calvin_venv`** / Python **3.8**；`ESA_CALVIN_OFFICIAL_ROOT=<repo>/data/raw/calvin_official` | 脚本默认 `embodied_scene_agent.envs.calvin_hydra_factory:make_calvin_env` | `ESA_CALVIN_CONDA_ENV=calvin_venv bash scripts/run_calvin_live_probe.sh --no-write-json`；`--step-smoke` **通过**（7 维 ndarray 相对动作烟测） |
| 2026-03-26 | Linux（本机） | 同上 | 同上 | `ESA_CALVIN_CONDA_ENV=calvin_venv bash scripts/run_calvin_minimal_loop_smoke.sh --try-local-factory --live-action-strategy symbolic_fallback` → **`live_reset_succeeded`: true**；`whether_live_step_executed`: false（符号 fallback 预期） |
| 2026-03-22 | Linux（本机） | 见下文 | **未设置**（`unset`） | `cd <repo> && conda activate embodied-scene-agent && PYTHONPATH=src python -m embodied_scene_agent.cli.run_calvin_live_probe --no-write-json` |
| 2026-03-22 | Linux（本机） | conda **`embodied-scene-agent`** / Python 3.12 | 脚本默认（见下） | `bash scripts/run_calvin_live_probe.sh`；`--step-smoke` 同上 |

**说明（本机环境事实，非叙事结论）**：

- **历史（2026-03-22 前）**：`environment.yml` 曾定义名 **`esa-py310`**，本机未创建该目录。
- **当前策略（仓库已对齐）**：`environment.yml` 的 `name:` 已改为 **`embodied-scene-agent`**（与 pip 包名一致）；开发统一使用该 conda 环境。
- 在 **`embodied-scene-agent`**（Python **3.12.x**，conda-forge）中，在**未** `pip install` `mees/calvin_env` 之前：`import calvin_env` → **`ModuleNotFoundError`**（见下方「本次 probe」表；安装成功后请追加新行）。
- 系统默认 `python3`（版本因机器而异）同样可能 **`ModuleNotFoundError: No module named 'calvin_env'`**（若未安装官方栈）。
- 在未克隆 `calvin_env` / `calvin_official` 的目录树内 `find … -name calvin_env`（有限深度）**未发现** CALVIN 源码目录。
- 因此**未实现**基于本机安装的 `make_calvin_env()`（**无可验证的 import 路径与构造方式，禁止猜测 Hydra**）。

---

## 2026-03-22 环境名对齐与 `calvin_env` 安装（本机事实）

| 项 | 内容 |
|----|------|
| 仓库 `environment.yml` 的 `name:` | 已改为 **`embodied-scene-agent`**（与统一开发环境一致；Python **3.12.***） |
| `calvin_env` 源码位置 | `data/raw/calvin_env`（`data/raw/**` 已 `.gitignore`，不提交克隆体） |
| 安装方式 | `git clone https://github.com/mees/calvin_env.git`，在 conda **`embodied-scene-agent`** 中执行 `pip install -e data/raw/calvin_env` |
| 官方 README 另含 `tacto` 子模块 | 本次**未** `--recursive`；仅验证 **`import calvin_env`** 与 `PlayTableSimEnv` 可 import；触觉相关若报错需再补 `tacto` |
| `python -c "import calvin_env"` | **成功**（本机 `conda run -n embodied-scene-agent`） |
| 运行时提示 | Gym 对 NumPy 2.x 的弃用警告、Hydra `version_base` 警告（来自上游，非安装失败） |

**说明**：下方「首次 probe（import 失败）」表为 **未安装 `calvin_env` 前** 的历史记录。安装 Hydra 工厂与 `calvin_env` 后，以 **「第二次 probe（工厂 + reset + step smoke）」** 为准。

---

## 2026-03-22 第二次 probe（`embodied_scene_agent.envs.calvin_hydra_factory:make_calvin_env`）

| 项 | 结果 |
|----|------|
| `factory_resolve.status` | **`resolved`**（`run_calvin_live_probe.sh` 未设置时默认 `ESA_CALVIN_ENV_FACTORY=embodied_scene_agent.envs.calvin_hydra_factory:make_calvin_env`） |
| `calvin.import_play_table` | **`true`** |
| `calvin.instantiated` | **`true`** |
| `calvin.reset_ok` | **`true`** |
| `calvin.teacher_mapping_eligible` | **`true`**（`get_info()` 含 `robot_info` + `scene_info`） |
| `calvin.observation_summary.obs_top_level_keys` | `depth_obs`, `rgb_obs`, `robot_obs`, `scene_obs`（`no_cameras` 时 rgb/depth 字典可为空） |
| `calvin.instruction_external_expected` | **`true`**（instruction 仍由外部传入，不在 obs） |
| `calvin.step_smoke.step_called` | **`true`**（动作格式与 `calvin_env` 官方 `run_env` 一致：`cartesian_rel` + 7 维向量） |
| `calvin.step_smoke.tuple_length` | **4**（`obs, reward, done, info`） |
| `calvin.teacher_refresh_after_step_ok` | **`true`** |

**落盘**：`bash scripts/run_calvin_live_probe.sh --step-smoke` 默认写入 `results/calvin_live_probe_summary.json`（若仓库忽略 `results/`，仅本机保留）。

---

## 2026-03-26 官方栈（`calvin_venv` + `data/raw/calvin_official`）

| 项 | 结果 |
|----|------|
| 官方仓库 | `data/raw/calvin_official`，commit `fa03f01f19c65920e18cf37398a9ce859274af76`；子模块见 `docs/calvin_official_setup_log.md` |
| `factory_resolve.status` | **`resolved`** |
| `calvin.import_play_table` / `instantiated` / `reset_ok` | **`true`** |
| `calvin.step_smoke` | **`step_called`: true**；`tuple_length`: **4**；`teacher_refresh_after_step_ok`: **true**（此前误用 dict 动作导致 `AssertionError`，已改为 **7 维 `ndarray`**，与 `robot.relative_to_absolute` 一致） |
| Hydra | 工厂内对 **`version_base`** 按签名探测，兼容 Hydra **1.1**（官方 3.8 栈）与新版 |
| minimal loop | **`live_reset_succeeded`: true**；**非**全量物理逐步执行声明（`symbolic_fallback`） |

**未声称**：官方 benchmark、debug 数据集驱动的端到端训练已默认接通。

---

## 2026-03-22 首次 probe 输出摘要（JSON 要点，历史：未安装 calvin_env）

| 项 | 结果 |
|----|------|
| `disclaimer` | `NOT_A_BENCHMARK_RUN` |
| `dotenv_file_loaded` | `true` |
| `hf_token_status` | 已设置（值未写入本文档） |
| `factory_resolve.status` | `unset`（`ESA_CALVIN_ENV_FACTORY` 未配置） |
| `calvin.import_play_table` | **`false`** |
| `calvin.import_error` | **`ModuleNotFoundError: No module named 'calvin_env'`** |
| `calvin.instantiated` | **false**（import 失败，未进入 factory） |
| `calvin.reset_ok` | **false** |
| `calvin.teacher_mapping_eligible` | **false** |
| `calvin.instruction_external_expected` | **true**（与源码审计一致：instruction 应由外部传入，非 obs） |
| `calvin.instruction_in_observation` | **false**（未拿到 obs，此字段为 probe 默认值） |

**未执行（因 import 失败而中止）**：

- **Step 3** `--step-smoke`：**未运行**（前提：reset 成功）。
- **Step 5** minimal loop `--try-local-factory`：**未运行**（前提：live probe 打通 import + factory + reset）。

---

## 与 `docs/calvin_real_fields_audit.md` 的一致性（本次）

| 审计项 | 本次运行是否一致 | 备注 |
|--------|------------------|------|
| `get_obs` 键等 | **未验证** | 未安装 `calvin_env`，无 obs |
| `get_info` / `robot_info` | **未验证** | 同上 |
| `scene_info` | **未验证** | 同上 |
| instruction 不在 `obs` 内 | **未验证 live obs** | 设计上仍预期由外部提供；与 `instruction_external_expected: true` 不矛盾 |

---

## 仍未确认

- 本机安装 CALVIN / `calvin_env` 后的真实 `PlayTableSimEnv` 构造方式与 `get_obs`/`get_info` 键集合。
- `scene_obs` 逐维语义、动作维度与官方数据集对齐。

---

## 最小修复建议（按顺序）

1. **安装 CALVIN 仿真依赖**：按官方仓库（如 `mees/calvin_env`）克隆并安装到**选定**的 conda 环境；确保该环境中 `python -c "import calvin_env"` **无报错**。
2. **对齐本仓库 conda 名**：统一使用 **`embodied-scene-agent`**（`environment.yml`）；执行 `bash scripts/setup_env.sh` 创建/更新该环境，并 `pip install -e .` 与 **`calvin_env`** 装在同一环境。
3. **实现本地 factory**（仅在实际能 `import calvin_env` 之后）：在**不提交密钥/机器路径**的前提下，于本机模块中实现 `make_calvin_env()`，并设置：  
   `export ESA_CALVIN_ENV_FACTORY='你的模块:make_calvin_env'`  
   详见 `docs/calvin_env_factory_usage.md`。
4. **重跑**：仅当 import + factory + **reset 成功**后，再运行 `bash scripts/run_calvin_live_probe.sh --step-smoke`，最后才尝试 `run_calvin_minimal_loop_smoke.sh --try-local-factory --live-action-strategy symbolic_fallback`。

---

## `ESA_CALVIN_ENV_FACTORY` 当前应设为什么？

- **推荐默认**（已安装 `calvin_env`、且使用本仓库 Hydra 工厂时）：  
  `embodied_scene_agent.envs.calvin_hydra_factory:make_calvin_env`  
  `scripts/run_calvin_live_probe.sh` / `scripts/run_calvin_minimal_loop_smoke.sh` 在未导出该变量时会自动采用此值。
- **自定义**：若需其它场景 / GUI / EGL，自行实现 `make_calvin_env` 并 `export ESA_CALVIN_ENV_FACTORY='模块:函数'` 覆盖（见 `docs/calvin_env_factory_usage.md`）。
