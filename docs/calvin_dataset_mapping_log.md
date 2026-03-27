# CALVIN 真实子集 → 本仓库 rollout 映射说明

## 数据源（真实、非 fixture）

- **来源**：官方仓库 [mees/calvin](https://github.com/mees/calvin) 中 **语言标注 YAML**（仅文本，无 RGB/depth 帧）：
  - `calvin_models/conf/annotations/new_playtable.yaml` → manifest `split_role=train_pool`
  - `calvin_models/conf/annotations/new_playtable_validation.yaml` → manifest `split_role=validation_pool`
- **下载方式**：`python -m embodied_scene_agent.data.prepare_calvin_real_subset`（或 `scripts/prepare_calvin_real_subset.sh`）通过固定 `raw.githubusercontent.com` URL 拉取到 `data/raw/calvin_official_annotations/`（该目录在 `.gitignore` 中）。

## 字段差异（显式说明）

| CALVIN YAML | 本仓库 manifest / SFT |
|-------------|------------------------|
| `subtask_key` → 若干自然语言 `instruction` | `episode_id` = `{split_role}::{subtask_key}::{annotation_index}` |
| **无**观测路径、无 `robot_obs` / `scene_obs` | `obs_source: none_yaml_only`，`obs_frame_path: null` |
| 官方评测从 **别处的** 配置取子任务序列 | 本仓库 **不** 重放官方 episode 序列；仅用 **真实句子** 作为 `instruction` |

## Rollout 后端（诚实标签）

- **执行环境**：`MockEmbodiedEnv` + `run_v0_episode`（规则 planner + `SkillExecutor` + `StateDiffVerifier` + `RuleBasedReplanner`）。
- **含义**：轨迹在 **mock 桌面 + red_block + drawer** 上可执行；**不是** CALVIN 仿真器中的物理 rollout。
- **metadata**：`rollout_backend: mock_symbolic_v0_loop`；`source_type: real_subset_mock_rollout`。

## Manifest 路径

- `data/processed/calvin_real_subset/manifest.jsonl`（及 `manifest.sha256`）。

## 与 `docs/calvin_real_fields_audit.md` 的关系

- 该审计描述 **calvin_env 观测字典**；本阶段 YAML **不包含**这些字段。若未来将 **HDF5 / 帧数据** 接入 manifest，应在本文件追加一节「帧级字段映射」，**禁止静默 fallback**。
