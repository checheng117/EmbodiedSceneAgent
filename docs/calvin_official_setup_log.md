# CALVIN 官方 dev path 接入日志（事实记录）

**范围**：仅 **官方仓库克隆 + 独立 conda dev 环境 + debug 数据 + 本项目 probe/minimal loop 对接**。  
**不声称**：官方 CALVIN benchmark、全量训练、大规模数据已就绪。

---

## 1. 仓库现状审计（2026-03-26）

| 类别 | 结论 |
|------|------|
| **分类** | **A**：此前另有独立 `data/raw/calvin_env`；现已增加 **官方 `mees/calvin` 完整克隆（含子模块）** 于 `data/raw/calvin_official/`。 |
| `data/raw/calvin_env` | 仍存在（历史路径；与官方子模块 **并存**，职责不同）。 |
| `data/raw/calvin_official/` | **官方 CALVIN 仓库根目录**（`data/raw/**` 在 `.gitignore`，克隆体不提交）。 |

---

## 2. 官方 CALVIN 仓库（任务 A）

| 项 | 值 |
|----|-----|
| **路径** | `<EmbodiedSceneAgent>/data/raw/calvin_official`（或覆盖：`export ESA_CALVIN_OFFICIAL_ROOT=...`） |
| **克隆方式** | `git clone --recurse-submodules https://github.com/mees/calvin.git` → 落盘为上述目录（本机执行，未入 git）。 |
| **主仓库 HEAD** | `fa03f01f19c65920e18cf37398a9ce859274af76` |
| **子模块 `calvin_env`** | `1431a46bd36bde5903fb6345e68b5ccc30def666` |
| **子模块 `calvin_env/tacto`** | `dd53360d9a8c186f0d6439372ec0be0fa5e21731` |

**本项目脚本默认**：若未设置 `ESA_CALVIN_OFFICIAL_ROOT`，则使用 `<repo>/data/raw/calvin_official`。

---

## 3. CALVIN dev 环境（任务 B）

**策略**：与 **`embodied-scene-agent`**（Python 3.12）分离；按上游思路使用 **conda `python=3.8`**，环境名默认 **`calvin_venv`**。

| 项 | 值 |
|----|-----|
| **自动化脚本** | `bash scripts/setup_calvin_dev_env.sh` |
| **日志** | 新跑写入 `results/logs/calvin_official_install_<UTC>.log`；本仓库开发期样例已归档：`results/archive/logs/calvin_official_install_20260326T075450Z.log` |
| **上游等价步骤** | 与官方 `install.sh` 一致顺序：`wheel` + `cmake==3.18.4` → `calvin_env/tacto` editable → `calvin_env` editable → **`pip install 'setuptools<58'`**（官方 README：解决 `pyhash` / `use_2to3` 与过新 setuptools）→ `calvin_models` editable。 |
| **说明** | 未将上游依赖强行并入 `embodied-scene-agent`；**推荐** live 仿真探针使用：`export ESA_CALVIN_CONDA_ENV=calvin_venv` 再跑 `scripts/run_calvin_live_probe.sh`。 |

**本机验证（2026-03-26）**：`calvin_venv` 中可 `import calvin_env`、`make_calvin_env()` 实例化并重置；详见 `docs/calvin_live_validation_results.md`。

---

## 4. 官方 debug 数据集（任务 C）

| 项 | 值 |
|----|-----|
| **下载脚本** | `bash scripts/download_calvin_debug_data.sh`（在 `$ESA_CALVIN_OFFICIAL_ROOT/dataset` 调用官方 `download_data.sh debug`） |
| **探测脚本** | `bash scripts/inspect_calvin_debug_dataset.sh` |
| **落盘路径** | `data/raw/calvin_official/dataset/calvin_debug_dataset/` |
| **体量（本机 du）** | 约 **1.3G** |
| **结构** | 顶层含 `training/`、`validation/`（episode `*.npz`） |

**EmbodiedSceneAgent 引用**：训练/数据管线若需指向 debug 集，应通过配置或环境变量指向上述目录（**非** HF 镜像主路径）。当前 minimal loop / probe **不要求**挂载该目录即可做仿真 smoke。

---

## 5. 代码与脚本对接（任务 D）

| 文件 | 作用 |
|------|------|
| `src/embodied_scene_agent/envs/calvin_hydra_factory.py` | `sys.path` 优先级：`ESA_CALVIN_ENV_SRC` → `ESA_CALVIN_OFFICIAL_ROOT/calvin_env` → `data/raw/calvin_official/calvin_env`；**Hydra**：仅在 `initialize_config_dir` 签名含 `version_base` 时传入（兼容官方栈 Hydra 1.1 与新版）。 |
| `scripts/run_calvin_live_probe.sh` | 默认 `ESA_CALVIN_OFFICIAL_ROOT`；可选 `ESA_CALVIN_CONDA_ENV` |
| `scripts/run_calvin_minimal_loop_smoke.sh` | 同上 |
| `scripts/setup_calvin_dev_env.sh` | 创建/复用 conda + 上游等价安装 |
| `scripts/download_calvin_debug_data.sh` | 官方 `debug` 数据 |
| `scripts/inspect_calvin_debug_dataset.sh` | 目录与体量检查 |

---

## 6. 仍未完成（不得夸大）

- **未**跑官方 CALVIN **benchmark** 或长程 rollout 评测。
- **未**下载 D / ABC / ABCD 全量 split。
- **未**将 `calvin_debug_dataset` 接入默认训练管线（仅落盘与探测脚本就绪）。
- Minimal loop 在 `symbolic_fallback` 下 **`whether_live_step_executed`: false** 为设计行为（符号技能 + live 观测），**不是**「全物理逐步执行已打通」。

---

## 7. 下一步建议（3 条）

1. 在 `calvin_venv` 中固定工作流：`ESA_CALVIN_CONDA_ENV=calvin_venv` + 文档化 `ESA_CALVIN_OFFICIAL_ROOT`。
2. 若训练需真实帧：在数据配置中显式指向 `dataset/calvin_debug_dataset`，并记录体积与版本。
3. 需要官方评估协议时：另开文档与脚本，与本文 **dev path** 区分。
