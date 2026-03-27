# 项目展示页（EmbodiedSceneAgent）

面向导师、答辩与 GitHub Pages 的**展示入口**，与 `README.md`、自动看板使用**同一套事实**（见 `results/reports/latest_project_report.json` 中的 `unified_headline_facts`）。

## 一键生成最终资产包

```bash
bash scripts/build_final_report_assets.sh
```

产出：

- **1 页简报**：[`docs/final_report_assets/one_page_project_brief.md`](../final_report_assets/one_page_project_brief.md)
- **完整大纲 + 证据/缺口**：[`docs/final_report_assets/report_outline_final.md`](../final_report_assets/report_outline_final.md)
- **主结果表**：[`docs/final_report_assets/tables/current_main_results_table.md`](../final_report_assets/tables/current_main_results_table.md)
- **案例**：[`docs/final_report_assets/case_studies/`](../final_report_assets/case_studies/)
- **诚实边界**：[`docs/final_report_assets/limitations.md`](../final_report_assets/limitations.md)

## 主图与架构

- [`docs/figures/architecture_v2.svg`](../figures/architecture_v2.svg)（与 `docs/final_report_assets/figures/architecture_final.svg` 同步副本）

## 自动看板（勿手改）

- 生成：`python -m embodied_scene_agent.reporting.make_project_report`
- 输出：`results/reports/latest_project_dashboard.md`
- 镜像：[`status_board.md`](status_board.md)（与 dashboard **内容一致**）

## 三条证据主线（非官方 benchmark）

| 主线 | 入口 | 性质 |
|------|------|------|
| E2 消融 | `docs/failure_cases/e2_ablation_cases.md` | **mock** + **CALVIN fixture** |
| Hybrid replanner | `docs/failure_cases/hybrid_replanner_cases.md` | **mock batch** + smoke |
| RLBench 桥接 | `results/rlbench_dev_smoke.json` | **import_fail**；fixture cognition **real** |

**未宣称**：官方 CALVIN/RLBench 榜单、A100 7B 生产训练、VLABench 跑分 — 均为 **future_only** 或文档级。

## 叙事与证据审计

- [`docs/narrative_consistency_audit.md`](../narrative_consistency_audit.md)
- [`docs/evidence_consistency_audit.md`](../evidence_consistency_audit.md)（随 `build_final_report_assets` 更新）
