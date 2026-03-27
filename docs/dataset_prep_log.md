# 数据与资源准备日志（可复现）

**用途**：记录本仓库训练/仿真准备阶段**真实**下载与落盘位置；**不**包含 token 或 benchmark 分数。

---

## 2026-03-22

| 资源 | 来源 | 落盘路径 | 安装方式 |
|------|------|----------|----------|
| `calvin_env` 源码 | [mees/calvin_env](https://github.com/mees/calvin_env) | `data/raw/calvin_env` | `git clone`（目录在 `.gitignore` 的 `data/raw/**` 下） |
| `calvin_env` Python 包 | 同上 | （editable 指向上述路径） | `conda` 环境 **`embodied-scene-agent`** 内 `pip install -e data/raw/calvin_env` |
| Planner SFT 样例 JSONL | 本仓库 `build_planner_data`（fixture minimal loop） | `data/processed/planner_sft/calvin_minimal_dev.jsonl` | `python -m embodied_scene_agent.training.build_planner_data --out ...` |

**说明**：

- 未在本阶段从 Hugging Face 拉取 CALVIN 数据集；若后续需要，应另起一行记录 repo id、目标目录与大致体积。
- Live probe 摘要 JSON 默认写入 `results/calvin_live_probe_summary.json`（该目录通常被 `.gitignore` 忽略）。

---

## 2026-03-24（Assignment-3 最小真实子集 + planner SFT）

| 资源 | 来源 | 落盘路径 | 安装方式 |
|------|------|----------|----------|
| CALVIN 官方 **语言** YAML（无图像帧） | [mees/calvin](https://github.com/mees/calvin) `new_playtable.yaml` + `new_playtable_validation.yaml` | `data/raw/calvin_official_annotations/`（gitignore） | `python -m embodied_scene_agent.data.prepare_calvin_real_subset` |
| 真实子集 manifest | 同上 | `data/processed/calvin_real_subset/manifest.jsonl` | 同上脚本自动生成 |
| Planner SFT v1（可训练） | manifest + **mock 符号** rollout | `data/processed/planner_sft/train.jsonl` 等 | `python -m embodied_scene_agent.training.build_planner_data --source real_subset` 或 `scripts/build_planner_data_real.sh` |
| Qwen2.5-VL-3B-Instruct 权重缓存 | Hugging Face Hub | 默认 `HF_HOME`（建议仓库内 `.hf_cache/`，已 gitignore） | `scripts/pull_3b_backbone.sh` 或 `python -m embodied_scene_agent.training.prepare_backbone` |

**子集规模（真实执行）**：

- manifest：**423** 条（每条为「子任务键 + 一句真实英文指令」）。
- 经 `can_rollout_mock_symbolic` 过滤后用于 rollout 的指令见构建日志；当前 train/val/test JSONL 合计 **1166** 条 **step 级** 监督（见 `docs/planner_data_stats.md`）。

**说明**：

- 轨迹在 **MockEmbodiedEnv** 上生成，**不是** CALVIN 仿真逐步录像；映射见 `docs/calvin_dataset_mapping_log.md`。
- **未**使用 Hugging Face 上多 GB 的 CALVIN 视频 shard（避免 3090 开发机一次性下载数百 GB）；语言标注仍为 **官方 CALVIN 文本**。

---

## 2026-03-26（CALVIN 官方 dev：仓库 + debug 数据，非 benchmark）

| 资源 | 来源 | 落盘路径 | 获取方式 |
|------|------|----------|----------|
| 官方 CALVIN 仓库（含子模块） | [mees/calvin](https://github.com/mees/calvin) | `data/raw/calvin_official/`（gitignore） | `git clone --recurse-submodules`（本机；详见 `docs/calvin_official_setup_log.md`） |
| 官方 **debug** 轨迹包 | 上游 `dataset/download_data.sh debug` | `data/raw/calvin_official/dataset/calvin_debug_dataset/` | `bash scripts/download_calvin_debug_data.sh` |
| CALVIN **Python 3.8** dev 环境 | 上游 `install.sh` 思路 | conda 环境名默认 **`calvin_venv`** | `bash scripts/setup_calvin_dev_env.sh`（新日志 `results/logs/calvin_official_install_*.log`；样例归档见 `results/archive/logs/calvin_official_install_20260326T075450Z.log`） |

**说明**：

- debug 集约 **1.3GB**；顶层为 `training/`、`validation/`（`*.npz`）。探测：`bash scripts/inspect_calvin_debug_dataset.sh`。
- **未**下载 D / ABC / ABCD 全量；**未**宣称 benchmark 完成。
- 历史目录 `data/raw/calvin_env` 仍可能存在，与官方子模块 **`calvin_official/calvin_env`** 并存；仿真路径优先级见 `docs/calvin_env_factory_usage.md`。

---

## CALVIN debug → planner SFT 导出（`calvin_debug_real`，非 benchmark）

| 资源 | 来源 | 落盘路径 | 获取方式 |
|------|------|----------|----------|
| Planner SFT 行（v1 schema） | 官方 debug `robot_obs`/`scene_obs` + 最小 CALVIN 闭环（符号执行） | `data/processed/planner_sft/calvin_debug_real_{train,val,test}.jsonl` | **`bash scripts/build_calvin_debug_planner_data.sh`** 或 `python -m embodied_scene_agent.training.build_planner_data --source calvin_debug_real …` |
| 行数与 lineage 统计 | 同上 | **`docs/calvin_debug_real_data_stats.md`**（脚本自动生成） | 同上 |

**说明**：指令文本 **不**来自 debug npz（该 zip 无 `lang_annotations`），而来自 **`calvin_real_subset/manifest.jsonl`** 中官方 YAML 指令池轮换绑定；详见 **`docs/calvin_debug_dataset_audit.md`**。
