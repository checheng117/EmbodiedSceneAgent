# EmbodiedSceneAgent

**一句话定位**：以 **对象级 3D scene memory** 为中间表示、驱动 **具身高层认知（high-level cognition）** 的规划—执行—验证—重规划闭环；**不是**端到端低层策略（VLA），也**不是**从零关节级控制栈。

课程语境：CSC5051 NLP Assignment-3 旗舰仓库；设计真源见 `docs/EmbodiedSceneAgent_Project_Blueprint_CheCheng.docx`。

---

## Start here（最值得先打开）

| 入口 | 路径 |
|------|------|
| 自动看板 | `results/reports/latest_project_dashboard.md` |
| 机器可读报告快照 | `results/reports/latest_project_report.json` |
| 执行摘要（汇报） | `docs/final_report_assets/executive_summary.md` |
| 主结果表（指针） | `docs/final_report_assets/tables/current_main_results_table.md` |
| E2 三后端对照 | `docs/tables/e2_ablation_mock_vs_calvin_fixture_vs_calvin_debug_real.md` |
| Hybrid replanner 结果与 artifact 路径 | `docs/replanner_hybrid_results.md` |
| 官方 CALVIN dev 接入事实 | `docs/calvin_official_setup_log.md` |
| 阅读顺序索引 | `docs/final_report_assets/artifact_index.md` |
| 展示页入口 | `docs/project_page/README.md` |

一键生成/刷新最终汇报资产包：

```bash
bash scripts/build_final_report_assets.sh
```

产出：`docs/final_report_assets/**`、`results/final_report_assets/unified_headlines.json`（与 `README` 中统一标题栏同步）。

### GitHub 上会包含什么 / 默认不包含什么

**意图随仓库版本控制的**：`src/`、`scripts/`、`configs/`、`tests/`、`docs/`（含 `final_report_assets`、设计/审计文档）、`environment.yml`、`pyproject.toml`、`requirements/`、`demos/`、`examples/`、`LICENSE`、`README.md`；以及轻量 **`results/reports/*.md` / `*.json`**、**`results/final_report_assets/**`**、**`results/rlbench_dev_smoke.json`**、**`results/rlbench_stack_diagnosis.json`**（已脱敏机器路径）。可选提交 **`results/eval/planner_base_vs_tuned/metrics.json`** 与 **`summary.md`** 作为叙事指针（**不含** `per_sample_results.jsonl`，见 `.gitignore`）。

**`.gitignore` 排除的（需在 A100 另备）**：`.env`、模型权重扩展名、**`.hf_cache/`**、**`data/raw/**`**（官方 CALVIN 克隆 + debug 数据集）、**`data/processed/**/*.jsonl`**、**`results/checkpoints/`**、**`results/experiments/`**、**`results/demos/`**、**`results/archive/`**、**`results/logs/`** 等。细则与理由见 **`docs/github_a100_readiness_audit.md`**。

**数据策略（简表）**：official CALVIN repo / debug zip → **在目标机重新 clone / 下载**（或整树 rsync）；processed JSONL → **可重建**（脚本见下文 README）或 **scp/rsync**；checkpoints → **勿依赖 GitHub**，单独备份；`docs/final_report_assets` 与 `results/reports` 可与仓库同步，也可在机器上 **`make_project_report` + `build_final_report_assets`** 再生。

### 环境变量约定（脚本实际使用）

| 变量 | 用途 |
|------|------|
| `HF_TOKEN` / `HUGGING_FACE_HUB_TOKEN` | 拉取 Qwen 等 Hugging Face 模型（写入仓库根 `.env` 或 export，**勿提交**） |
| `HF_HOME` | 模型缓存目录（默认可用仓库内 `.hf_cache`，已被 ignore） |
| `ESA_CALVIN_OFFICIAL_ROOT` | 官方 CALVIN 仓库根；未设置时默认 `<repo>/data/raw/calvin_official` |
| `ESA_CALVIN_CONDA_ENV` | 跑 live probe 等时使用的 **Python 3.8** 栈，默认 **`calvin_venv`** |
| `ESA_CALVIN_ENV_FACTORY` | 可选自定义 env 工厂（见 `docs/calvin_env_factory_usage.md`） |
| `COPPELIASIM_ROOT` | RLBench **真 sim**（多数开发机未配置；fixture 路径不依赖） |

### Start here on A100（最少可跑命令）

```bash
git clone <YOUR_REPO_URL> EmbodiedSceneAgent && cd EmbodiedSceneAgent
bash scripts/setup_env.sh && conda activate embodied-scene-agent
pip install -e ".[train]"          # 训练/评测按需
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
pytest -q                          # 可选：验证契约（约 80+ tests）
bash scripts/run_smoke_v0.sh       # 无外部数据的最小闭环
```

需要 **CALVIN debug 向量 / E2 / hybrid 全链路** 时，在仓库根继续：`git clone --recurse-submodules https://github.com/mees/calvin.git data/raw/calvin_official` → `bash scripts/setup_calvin_dev_env.sh` → `bash scripts/download_calvin_debug_data.sh` → `bash scripts/build_calvin_debug_planner_data.sh`（或从 3090 **rsync `data/processed/**/*.jsonl`**）。报告刷新：`python -m embodied_scene_agent.reporting.make_project_report && bash scripts/build_final_report_assets.sh`。

**clone 后缺什么、是否阻塞**：见 **`docs/github_clone_simulation.md`**。

---

## 核心主张

- **解决什么问题**：长程语言条件操作中，单次图像或一次性语言规划难以稳定完成 grounding、子任务合法性与失败恢复；本项目把 **显式 3D 对象级记忆** 放进闭环，使规划、验证与重规划都基于 **可解释、可审计** 的结构化状态。
- **为什么不是 end-to-end low-level policy**：职责边界在 **认知层**（场景记忆、高层计划、失败类型、修订策略），低层技能仍通过注册表/执行器路由，而非单模型直接输出连续控制。
- **为什么需要 Scene Memory / Verifier / Replanner**：Memory 提供可检查的 world 状态；Verifier 将「是否偏离意图」结构化为 `FailureType` 等契约；Replanner 在检测到失败时产生可追踪的修订（规则优先 + 可选 LLM），形成闭环。

---

## 架构（六段式）

![Architecture](docs/figures/architecture_v2.svg)

```text
Observation → Scene Memory → Planner → Skill Executor → Verifier → Replanner
     ↑___________________________________________________________________|
```

<!-- ESA_UNIFIED_HEADLINES_BEGIN -->
_Synced by `bash scripts/build_final_report_assets.sh` — do not edit between markers._

| Unified headline | Value |
|------------------|-------|
| **RLBench deepest stage** | `import_fail` |
| **RLBench bridge (fixture)** | memory_bridge=`True`; bridge_mode=`fixture_file` |
| **Hybrid batch (latest)** | parse_ok=`1.0`; validated=`1.0`; repair=`1.0` |
| **Hybrid parse breakdown** | `{}` (empty — see `limitations.md`) |
| **E2 mock (vpr task completion)** | `1.0` |
| **Primary strongest artifact** | `results/eval/planner_base_vs_tuned/metrics.json` |

**Honest boundaries:** official benchmark numbers not claimed; RLBench sim not past import on dev machine; E2 adds **mock + CALVIN fixture + CALVIN official debug npz (vector teacher)** — still **not** full benchmark.

<!-- ESA_UNIFIED_HEADLINES_END -->

---

## 当前真实完成内容（按层次）

### 1) 核心系统

- **六段式 cognition loop** 已在 mock / CALVIN fixture / CALVIN debug 向量 teacher 路径上跑通（统一 episode / step 日志契约）。
- **Scene Memory**（`esa_sm/v1`）、**Planner I/O 契约**、**Verifier taxonomy**、**Hybrid replanner**（规则 + LLM JSON，带 `replan_audit`）均已进入主线代码。

### 2) 训练与评测（3090 阶段事实）

- **Qwen2.5-VL-3B** 最小 LoRA SFT 与 **base vs tuned** JSONL proxy 评测已完成；checkpoint：`results/checkpoints/planner_sft_3b_minimal/run_latest/`；指标：`results/eval/planner_base_vs_tuned/metrics.json`（**非**官方 CALVIN 榜单）。
- **E2 消融**：mock 符号 batch、CALVIN **fixture** batch、官方 **debug** 向量后端（含 `grouped_sequence` / `same_task` / 报告用 `e2_doc_refresh_*` 目录）均有落盘结果；入口见 `docs/tables/` 与 `docs/failure_cases/e2_ablation_cases.md`。
- **Hybrid replanner**：smoke + 轻量 batch eval；CALVIN debug 上具备结构化 `metrics.json` / `fallback_stats.json`；入口 `docs/replanner_hybrid_results.md`。

### 3) Official CALVIN dev / debug 接入

- 官方仓库约定路径：`data/raw/calvin_official/`（gitignore）；独立 conda **`calvin_venv`**（Python 3.8）：`bash scripts/setup_calvin_dev_env.sh`。
- 官方 **debug** 数据集（~1.3GB）：`bash scripts/download_calvin_debug_data.sh` → `data/raw/calvin_official/dataset/calvin_debug_dataset/`；审计见 `docs/calvin_debug_dataset_audit.md`。
- **Probe / minimal loop**：`scripts/run_calvin_live_probe.sh`、`scripts/run_calvin_minimal_loop_smoke.sh`；运行事实回填 `docs/calvin_live_validation_results.md`。
- **安装 / 下载日志**：新跑仍写入 `results/logs/`；本仓库已归档样例见 `results/archive/logs/`（含 `calvin_official_install_20260326T075450Z.log`、debug 下载 log）。

### 4) 报告与展示资产

- `results/reports/latest_project_report.{md,json}`、`results/reports/latest_project_dashboard.md`、`docs/project_page/status_board.md`（与看板一致）。
- `docs/final_report_assets/**`、`docs/figures/**`、`docs/tables/**`、`docs/failure_cases/**`、`results/final_report_assets/`。

---

## 标志性结论（克制表述）

- 在 **mock + CALVIN fixture** 设定下，**verifier + replanner** 形成可展示的闭环证据（E2 三模式对比表）。
- **官方 CALVIN debug 的向量观测** 已进入统一 cognition loop，并与 **hybrid replanner** 的审计字段对齐（仍属 **debug / 子集** 证据，非 leaderboard）。
- **Hybrid replanner** 在 mock batch 上展示 **parse → validate → repair** 全链路可达；在 debug 子集上指标受 **对齐方式与子集构造** 影响，**不得**读作官方任务成功率。

---

## 当前未完成、不能夸大的部分

- **非** official CALVIN leaderboard；**非**全量 D / ABC / ABCD。
- **RLBench** 真机仿真在本开发机上 **import 未通过**；证据以 **fixture 桥接** 为主（见 `docs/rlbench_install_log.md`）。
- **A100 / 7B** 正式训练与主结果：**模板与脚本存在**，默认**未**宣称已跑通生产训练（`scripts/train_planner_7b.sh`、`configs/experiment/a100_final.yaml`）。
- **VLABench**：规划文档级（`docs/vlabench_plan.md`），**未**实跑压测。
- **debug-real** 类数字受 **YAML manifest 轮换、帧—指令对齐限制** 影响，见 `docs/calvin_debug_alignment_audit.md`；**不能**直接解读为 benchmark success rate。

---

## 仓库结构（简化）

```text
EmbodiedSceneAgent/
├── src/embodied_scene_agent/    # 主线代码（memory / planner / verifier / replanner / envs / evaluation / reporting …）
├── scripts/                     # 环境、数据、训练、评测、报告
├── configs/                     # planner / experiment（含 3B 与 7B 模板）
├── docs/                        # 契约、审计、final_report_assets、project_page、figures、tables
├── data/processed/              # planner_sft JSONL、calvin_debug 对齐产物、manifest（raw 多在 gitignore）
├── data/raw/                    # calvin_official、debug 数据等（默认不提交）
├── results/                     # checkpoints、eval、experiments、demos、reports（默认 gitignore）
│   └── archive/                 # 本次清理归档：重复 run、过程性大日志
└── tests/                       # 核心契约与管线测试
```

---

## 本机复现（conda）

**主环境**（训练/评测/报告）：名称由 `environment.yml` 定义，当前为 **`embodied-scene-agent`**（Python 3.12）。

```bash
bash scripts/setup_env.sh
conda activate embodied-scene-agent
cd /path/to/EmbodiedSceneAgent
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"

bash scripts/run_smoke_v0.sh
bash scripts/run_calvin_dev_smoke.sh
bash scripts/run_calvin_minimal_loop_smoke.sh
# Live 探针（需 CALVIN 工厂 / 官方栈；见 docs/calvin_env_factory_usage.md）
bash scripts/run_calvin_live_probe.sh

pytest -q
```

**CALVIN 官方栈环境**：**`calvin_venv`**（Python 3.8），`bash scripts/setup_calvin_dev_env.sh`；与主环境隔离。

**Hugging Face**：仓库根目录 `.env` 中 `HF_TOKEN`（或 `HUGGING_FACE_HUB_TOKEN`）— 用于 **拉取 Qwen 等模型权重**；**勿**写入代码或提交 `.env`。

**最小训练 / 评测链**（与历史事实一致；需 GPU 与 `pip install -e ".[train]"`）：

```bash
conda activate embodied-scene-agent
bash scripts/pull_3b_backbone.sh          # 可选；需 HF_TOKEN
bash scripts/prepare_calvin_real_subset.sh
bash scripts/build_planner_data_real.sh
bash scripts/run_planner_sft_3b_minimal.sh
bash scripts/run_eval_base_vs_tuned.sh "$(pwd)/results/checkpoints/planner_sft_3b_minimal/run_latest/best_lora" 0
```

**看板与资产包**：

```bash
python -m embodied_scene_agent.reporting.make_project_report   # → results/reports/latest_project_dashboard.md
bash scripts/build_final_report_assets.sh
bash scripts/make_demo_assets.sh    # 可选
```

---

## A100 阶段将做什么（计划边界清晰）

目标：在 **80G A100** 上完成 **7B planner / replanner** 相关正式实验，并**沿用当前已收口的数据分层**，把新结果写回 **dashboard / final_report_assets**，且 **不把 official benchmark 与 debug-real eval 混谈**。

**数据分层（沿用）**

- **主训练风格**：`grouped_sequence`（aligned）→ `data/processed/planner_sft/calvin_debug_real_aligned_{train,val,test}.jsonl`（见 `docs/calvin_debug_alignment_stats.md`）。
- **解释性验证集**：`same_task_subset` → `calvin_debug_real_same_task_*.jsonl` 与 `data/processed/calvin_debug_same_task_subset/`。
- **弱对齐对照**：`pooled_manifest` → `calvin_debug_real_{train,val,test}.jsonl`（仅作对照，不替代主训练叙事）。

**实验**

- 7B LoRA / QLoRA 训练（起点配置：`configs/planner/qwen25vl_7b_lora.yaml`；契约模板：`configs/experiment/a100_final.yaml`）。
- 重跑 **base vs tuned**、**E2**（mock / fixture / debug 向量）、**hybrid replanner** batch。
- 更新 `python -m embodied_scene_agent.reporting.make_project_report` 与 `bash scripts/build_final_report_assets.sh`。

---

## A100 上具体怎么做（可执行清单）

### A. 代码仓库同步

```bash
git clone <your-fork-or-upstream> EmbodiedSceneAgent && cd EmbodiedSceneAgent
# 或 rsync/scp 整个工作树；保持 src/、configs/、scripts/ 一致。
```

### B. 官方 CALVIN 仓库与 debug 数据

**推荐在 A100 上按文档重新拉取**（避免从旧机拷贝不完整子模块）：

```bash
git clone --recurse-submodules https://github.com/mees/calvin.git data/raw/calvin_official
bash scripts/setup_calvin_dev_env.sh    # 生成 calvin_venv；日志在 results/logs/
bash scripts/download_calvin_debug_data.sh
bash scripts/inspect_calvin_debug_dataset.sh
```

若必须从旧机拷贝：同步 `data/raw/calvin_official/` 全树（含子模块 `calvin_env`、`tacto`）以及 `dataset/calvin_debug_dataset/`；并在新机上仍跑一次 `inspect` 脚本做完整性烟测。

### C. processed planner 数据：拷贝还是重建？

- **建议直接 rsync/scp**：`data/processed/planner_sft/*.jsonl`、`data/processed/calvin_debug_same_task_subset/`、`data/processed/calvin_real_subset/manifest.jsonl` — 重建依赖上游 debug 与构建脚本，**拷贝最快且可复现 hash 可写在 run_meta**。
- **可重建**：若 A100 上已有官方 debug 与 `calvin_official`，可运行 `bash scripts/build_calvin_debug_planner_data.sh`、`bash scripts/refresh_calvin_debug_alignment_bundle.sh`（与 `docs/calvin_debug_alignment_audit.md` 一致）再生 JSONL；注意与当前审计文档中的 **行数统计** 对齐校验。

### D. 基线与 checkpoint

- **建议拷贝**：`results/checkpoints/planner_sft_3b_minimal/run_latest/`（3B 对照）、以及当前 `results/eval/planner_base_vs_tuned/`（可选，便于对比表格）。
- **HF_TOKEN**：在 A100 上用于 **7B 权重与 tokenizer 下载**（`HF_HOME` 可指向共享缓存）；**不参与**官方 CALVIN 数据下载（debug 脚本走上游 URL，见 `scripts/download_calvin_debug_data.sh`）。

### E. 7B 训练入口

1. 准备 conda 环境（与主项目一致或独立 A100 环境，但需与 `torch` CUDA 版本匹配）。
2. 以 `configs/planner/qwen25vl_7b_lora.yaml` 为起点，将 `train/val` JSONL 指向上文 **aligned** 主训练文件。
3. 调用 `python -m embodied_scene_agent.training.run_planner_sft`（参数与 3B 脚本同源风格；可参照 `scripts/run_planner_sft_3b_minimal.sh` 改写 `OUT` 与 config 路径）。
4. 落盘建议：`results/checkpoints/planner_sft_7b/<experiment_id>/`（与 `a100_final.yaml` 契约一致）；`scripts/train_planner_7b.sh` 当前为 **模板占位**，正式跑前需改为真实 `run_planner_sft` 调用并去掉默认 `exit 0`。

### F. 评测入口

```bash
bash scripts/run_eval_base_vs_tuned.sh <path_to_7b_lora_or_adapter> 0
bash scripts/run_ablation_e2.sh
bash scripts/run_ablation_e2_calvin_fixture.sh
bash scripts/run_ablation_e2_calvin_debug_real.sh    # 可用 CALVIN_DEBUG_BATCH=grouped_sequence|same_task_subset|pooled_manifest
bash scripts/run_hybrid_replanner_eval.sh
bash scripts/run_hybrid_replanner_eval_calvin_debug.sh
```

### G. 报告更新

```bash
python -m embodied_scene_agent.reporting.make_project_report
bash scripts/build_final_report_assets.sh
```

---

## 主结果与产物指针

| 类别 | 路径 |
|------|------|
| 3B LoRA checkpoint | `results/checkpoints/planner_sft_3b_minimal/run_latest/` |
| Base vs tuned（proxy） | `results/eval/planner_base_vs_tuned/metrics.json` |
| E2 / hybrid 实验根目录 | `results/experiments/e2_ablation/`、`results/experiments/hybrid_replanner_eval/` |
| 归档（重复 run / 大日志） | `results/archive/` |
| Episode / 失败类型契约 | `docs/episode_log_schema.md`、`docs/failure_taxonomy.md` |
| 模块总览 | `docs/module_contracts.md` |

---

## 文档索引（精选）

- `docs/github_a100_readiness_audit.md` — **Git 边界 / 密钥 / 可迁移性审计（push 前必读）**
- `docs/github_clone_simulation.md` — **「仅 clone」情境下缺什么、是否阻塞训练/展示**
- `docs/repo_cleanup_audit.md` — 历史清理与归档清单
- `docs/scene_memory_contract_v2.md`、`docs/replanner_design_v2.md`
- `docs/calvin_debug_dataset_audit.md`、`docs/calvin_debug_alignment_audit.md`
- `docs/conda_environment_strategy.md`、`docs/training_run_log.md`
- `docs/rlbench_install_log.md`、`docs/vlabench_plan.md`

---

## 致谢与引用

- 蓝图与设计约束：`docs/EmbodiedSceneAgent_Project_Blueprint_CheCheng.docx`
- Benchmark 与模型引用见蓝图 **§14**（CALVIN、RLBench、VLABench、Qwen2.5-VL 等）

---

_仓库状态（3090 阶段）：mock / fixture / **官方 debug 向量** 证据链已贯通；**3B 最小 SFT 与 base-vs-tuned** 已完成；**7B / official leaderboard / RLBench 全 sim / VLABench 实跑** 均 **未** 作为已完成主结果宣称。统一 conda 主环境 **`embodied-scene-agent`**；官方栈 **`calvin_venv`**。_
