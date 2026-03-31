# 实验计划（占位，不伪造结果）

本文件描述**计划中的**实验矩阵，用于后续论文式实验与项目页；**不包含虚构数值**。

**状态标签版矩阵（E1–E4）**：见 [`docs/experiment_matrix_v2.md`](experiment_matrix_v2.md)。

## 1. 核心主张对应的对比实验（来自蓝图）

| ID | 对比 | 核心指标 | 意图 |
|----|------|----------|------|
| E1 | image-only vs 2D symbolic vs 3D object-centric memory | success、grounding、plan validity | 验证显式 3D object memory 的价值 |
| E2 | no verifier / +verifier / +verifier+replan | recovery、task success、steps | 验证闭环必要性 |
| E3 | teacher-state vs predicted memory | success drop、failure 分布 | 验证架构在噪声感知下是否仍有效 |
| E4 | CALVIN → RLBench / VLABench | 泛化指标、定性案例 | 验证非单环境 hack |

## 2. 指标（实现于 `evaluation/metrics.py`）

- Task success rate  
- Subgoal completion rate  
- Grounding accuracy（若有人工或自动对齐）  
- Plan validity  
- Recovery rate（replan 后成功）  
- Step efficiency  
- Failure taxonomy distribution  

## 3. 产出物

- 每次正式跑：`experiment_id`、`config.snapshot.json` / `config.snapshot.yaml`、`run_manifest.json`（训练沿用 `run_meta.json`）、`metrics.json`、可选 `summary.md`
- 结果目录：`results/` 下按 benchmark / 日期分子文件夹（见 README）

## 4. TODO

- 接入 CALVIN 官方评测协议后与本文档对齐具体 split 与统计方式。

## 5. 最小 Assignment-3 管线（真实执行部分，无虚构分数）

- **数据**：官方 CALVIN 语言 YAML → manifest → mock 符号 rollout → `planner_sft/v1`（见 `docs/dataset_prep_log.md`、`docs/planner_data_stats.md`）。
- **训练**：`run_planner_sft.py` + `configs/planner/qwen25vl_3b_lora_minimal.yaml`。**2026-03-25** 已在 `embodied-scene-agent` 中真实跑通 **80** optimizer steps，checkpoint：`results/checkpoints/planner_sft_3b_minimal/run_latest/`（详见 `docs/training_run_log.md` §2026-03-25）。
- **评测**：`evaluation/eval_planner_models.py`（format / skill / target / recovery 风格 proxy）+ `write_case_studies.py`。**2026-03-25** 已在全量 **73** 条 `test.jsonl` 上写出 `results/eval/planner_base_vs_tuned/metrics.json`（数值以文件为准；**非** CALVIN 环境成功率）。
