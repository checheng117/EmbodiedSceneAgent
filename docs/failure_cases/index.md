# Failure / recovery 案例入口

本目录索引 **落盘资产**（不重复贴长 JSON）。

| 类型 | 路径 |
|------|------|
| Mock v0 成功 / 失败 / 恢复（自动生成） | `results/demos/success_put_block/`、`failure_no_recovery/`、`failure_then_recovery/` |
| Planner base vs tuned（JSONL proxy） | `results/eval/base_vs_tuned_case_studies.md` |
| E2 消融（mock 符号） | `docs/failure_cases/e2_ablation_cases.md`、`results/demos/e2_ablation_cases/` |
| Hybrid LLM replanner smoke | `results/experiments/hybrid_replanner_smoke/`、`docs/replanner_hybrid_results.md` |
| RLBench 桥接 smoke | `results/demos/rlbench_fixture_bridge/`、`results/episode_logs/rlbench_qualitative_episode.json` |

生成命令：`bash scripts/make_demo_assets.sh`

**无视频声明**：当前为 **状态时间线 + scene graph dot + memory_snapshot.json**。
