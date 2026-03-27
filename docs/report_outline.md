# 报告大纲（预填素材与缺口）

> 供最终论文 / 项目页使用；每节区分**已有证据**与**缺口**。

1. **Project Positioning** — 已有：README + blueprint 引用；缺口：对外视频摘要。
2. **Core Claim** — 已有：3D memory-driven high-level cognition；缺口：定量消融表。
3. **System Architecture** — 已有：`docs/figures/architecture_v2.svg`、本仓库六段式代码；缺口：A100 7B 规模示意图。
4. **Scene Memory Design** — 已有：`docs/scene_memory_contract_v2.md`、schema 测试；缺口：predicted memory 实验。
5. **Planner / Verifier / Replanner** — 已有：contract、`failure_taxonomy.md`、`replanner_design_v2.md`、replan audit；缺口：LLM replan 大规模评测。
6. **Training & Data Construction** — 已有：`docs/planner_data_stats.md`、`training_run_log.md`、checkpoint 路径；缺口：full rollout 数据。
7. **Benchmarks & Evaluation** — 已有：proxy eval JSONL；缺口：官方 CALVIN / RLBench 报告。
8. **Success / Failure / Recovery Cases** — 已有：`results/demos/*`、`results/eval/base_vs_tuned_case_studies.md`；缺口：真实视频 contact sheet。
9. **Ablations / Limitations** — 已有：experiment_matrix_v2 状态；缺口：系统化跑数。
10. **Engineering Reproducibility** — 已有：conda、`scripts/`、episode log schema、auto report；缺口：容器镜像。
11. **Future Directions** — 已有：A100 模板、`configs/experiment/a100_final.yaml`；缺口：真实运行回填。
