# 仓库清理审计（EmbodiedSceneAgent）

_生成：2026-03-27 — 在删除/归档前完成引用核对；执行记录见文末「清理执行记录」。_

## 一、审计范围与方法

- 已核对引用：`README.md`、`docs/project_page/README.md`、`results/reports/latest_project_dashboard.md`、`results/reports/latest_project_report.*`、`docs/final_report_assets/**`、`docs/tables/**`、`docs/failure_cases/**`、`docs/replanner_hybrid_results.md`、`docs/tables/calvin_debug_alignment_comparison.md`、`docs/evidence_consistency_audit.md`。
- 原则：凡被上述文档或 `latest_project_report.json` 中**硬编码路径**指向的实验目录，**不删除**；仅将**无任何引用**的重复 run 移至 `results/archive/`。

## 二、分类总览

### A. 必留核心资产

| 区域 | 说明 |
|------|------|
| `src/embodied_scene_agent/**` | 六段式 cognition loop、CALVIN 工厂/探针、E2/hybrid 评测、报告管线 |
| `configs/**`、`pyproject.toml`、`environment.yml` | 训练/实验配置与依赖真源 |
| `scripts/**` | setup、CALVIN dev、数据构建、训练/评测/报告脚本（含 `setup_calvin_dev_env.sh`、`download_calvin_debug_data.sh`、`inspect_calvin_debug_dataset.sh`、`run_calvin_live_probe.sh`、`run_calvin_minimal_loop_smoke.sh` 等） |
| `data/processed/**` | `planner_sft/*.jsonl`、`calvin_debug_same_task_subset/*`、`calvin_real_subset/manifest.jsonl` 等当前主线 JSONL |
| `data/raw/`（约定路径，多被 gitignore） | `calvin_official/`、官方 debug dataset、上游 `calvin_env` — **不删数据集本体** |
| `results/checkpoints/planner_sft_3b_minimal/run_latest/` | 当前 3B LoRA 主 checkpoint |
| `results/eval/planner_base_vs_tuned/` | base vs tuned proxy 指标 |
| `results/experiments/e2_ablation/`（保留子目录） | `e2_mock_20260325T090753Z`、`e2_calvin_fixture_20260325T090754Z`、`e2_doc_refresh_same_task`、`e2_doc_refresh_aligned`、`e2_calvin_debug_real_aligned_20260326T094535Z`、`e2_calvin_debug_same_task_20260326T094540Z`（与 alignment 对照表一致） |
| `results/experiments/hybrid_replanner_eval/`（保留子目录） | `hybrid_replanner_eval_20260325T084014Z`（失败对照）、`hybrid_replanner_eval_20260325T090504Z`（主 batch）、`hybrid_calvin_debug_real_20260326T083447Z`、`hybrid_calvin_debug_real_aligned_20260326T094544Z`、`hybrid_calvin_debug_same_task_20260326T094718Z`、`hybrid_calvin_debug_same_task_20260326T095232Z`（与 `current_main_results_table` 一致） |
| `results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260325T084505Z/` | 保留 **1 套** smoke 代表（时间最新） |
| `results/demos/**`、`results/episode_logs/**` | 演示与 schema 样例 |
| `results/reports/latest_project_*`、`results/final_report_assets/`、`results/rlbench_*.json` | 报告与 RLBench 诊断 |
| `docs/**`（除下文归档建议） | 契约、CALVIN 审计、project_page、final_report_assets、tables、failure_cases |
| `tests/**` | 核心契约与管线测试（未删） |

### B. 建议保留但可归档的资产

| 路径 | 说明 |
|------|------|
| 大型一次性下载/安装日志 | 移至 `results/archive/logs/`，避免根下 `results/logs/` 堆积；**新跑脚本仍写入 `results/logs/`** |
| 重复 E2 / hybrid batch（无文档引用） | 移至 `results/archive/experiments/...`，保留可追溯性 |

### C. 可删除/归档的过程性文件（本次策略：**归档**，不直接删）

以下目录经 grep **无** README / dashboard / report / final_report_assets / tables / failure_cases / replanner_hybrid_results / calvin_debug_alignment_comparison 引用：

**E2 重复 run（旧时间戳，已被 `e2_mock_20260325T090753Z` 等覆盖）**

- `results/experiments/e2_ablation/e2_mock_20260325T084011Z`
- `results/experiments/e2_ablation/e2_mock_20260325T084657Z`
- `results/experiments/e2_ablation/e2_calvin_fixture_20260325T084011Z`
- `results/experiments/e2_ablation/e2_20260325T075516Z`
- `results/experiments/e2_ablation/e2_calvin_debug_real_20260326T083122Z`（早期 pooled；当前报告主线为 `e2_doc_refresh_*` 与 alignment 表中的 094535Z/094540Z）

**Hybrid 重复 run**

- `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_20260326T083125Z`
- `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_20260326T083243Z`
- `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260326T095101Z`（与 `094544Z` 同批语义重复；文档已收口为保留 `094544Z`）

**Hybrid smoke 重复**

- `results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260325T075609Z`
- `results/experiments/hybrid_replanner_smoke/hybrid_replanner_20260325T075643Z`

**日志（体积大、过程性）**

- `results/logs/calvin_debug_download_20260326T075831Z.log`（~2.2MB）
- `results/logs/calvin_official_install_20260326T075450Z.log`（安装过程留档；引用更新为归档路径）

**不移动**：`results/logs/prepare_backbone_last.json` — `pull_3b_backbone.sh` / 文档仍约定写入该路径。

### D. 不确定 / 建议后续人工确认

| 项 | 说明 |
|----|------|
| `results/` 与 `.gitignore` | 当前 `results/**` 被忽略（仅 `results/.gitkeep` 例外）。若团队改为**选择性提交**结果，需调整 `!results/...` 规则并与本审计对齐。 |
| `docs/*_audit.md` 生成时间戳 | 与 `make_project_report` / `build_final_report_assets` 联动；清理后若需「证据一致性」刷新，可重跑脚本。 |
| `data/raw/` 实际占用 | 本审计不触碰；仅确认**不删除**官方 CALVIN 与 debug zip 内容。 |
| `e2_doc_refresh_*` 与 `e2_calvin_debug_*` 并存 | 二者服务不同叙事（报告刷新 id vs 对齐对照表）；**均保留**。 |

## 三、引用关系摘要（删除/归档前检查）

- **必须保留的 E2 路径**：`e2_mock_20260325T090753Z`、`e2_calvin_fixture_20260325T090754Z`、`e2_doc_refresh_same_task`、`e2_doc_refresh_aligned`（见 `docs/final_report_assets/tables/current_main_results_table.md`、`docs/tables/e2_ablation_mock_vs_calvin_fixture_vs_calvin_debug_real.md`）。
- **Alignment 表独占**：`e2_calvin_debug_real_aligned_20260326T094535Z`、`e2_calvin_debug_same_task_20260326T094540Z`、`hybrid_calvin_debug_real_aligned_20260326T094544Z`、`hybrid_calvin_debug_same_task_20260326T094718Z`（`docs/tables/calvin_debug_alignment_comparison.md`）。
- **Hybrid 主结果表**：`hybrid_replanner_eval_20260325T090504Z`、`hybrid_calvin_debug_same_task_20260326T095232Z`。
- **Replanner 叙事文档**：保留 `084014Z`、`090504Z`、`083447Z`、`094544Z`、`094718Z`、`095232Z` 路径；**移除**文档内 `095101Z` 重复小节（目录归档）。

## 四、最终清理策略

1. 将 **C 类**实验目录 `mv` 至 `results/archive/experiments/...`（保持相对层级，便于找回）。
2. 将 **大型日志** `mv` 至 `results/archive/logs/`。
3. 更新 **README / 相关 docs** 中「安装日志」路径为归档样例 + 说明新日志仍写入 `results/logs/`。
4. 精简 `docs/replanner_hybrid_results.md` 中重复的 `095101Z` 小节。
5. **不**修改 `.gitignore`（除非后续要提交 `results/archive` 样例；当前与 `results/**` 策略一致）。
6. **不**删除 `tests/`、**不**删除 `data/processed` 中 JSONL。

## 五、清理执行记录

**执行时间**：2026-03-27（本机工作区）。**说明**：下列路径均为 **`mv` 归档**，**无直接 `rm` 删除**（除文档内冗余小节删除外）。

| 动作 | 路径 |
|------|------|
| 归档 E2 | `results/archive/experiments/e2_ablation/{e2_mock_20260325T084011Z,e2_mock_20260325T084657Z,e2_calvin_fixture_20260325T084011Z,e2_20260325T075516Z,e2_calvin_debug_real_20260326T083122Z}` |
| 归档 hybrid eval | `results/archive/experiments/hybrid_replanner_eval/{hybrid_calvin_debug_real_20260326T083125Z,hybrid_calvin_debug_real_20260326T083243Z,hybrid_calvin_debug_real_aligned_20260326T095101Z}` |
| 归档 hybrid smoke | `results/archive/experiments/hybrid_replanner_smoke/{hybrid_replanner_20260325T075609Z,hybrid_replanner_20260325T075643Z}` |
| 归档日志 | `results/archive/logs/{calvin_debug_download_20260326T075831Z.log,calvin_official_install_20260326T075450Z.log}` |
| 文档修订 | `docs/replanner_hybrid_results.md`（删 `095101Z` 小节）；`README.md`、`docs/calvin_official_setup_log.md`、`docs/dataset_prep_log.md`（安装日志路径说明）；新增本审计文档 |
