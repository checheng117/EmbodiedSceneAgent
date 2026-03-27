# Experiment matrix v2（与 blueprint 对齐，状态标签）

| ID | 对比 | 状态 | 证据 / 缺口 |
|----|------|------|-------------|
| E1 | image-only vs 2D symbolic vs 3D object-centric | `partially_ready` | 3D memory + mock/CALVIN fixture **有**；image-only 对照臂需固定实验脚本 |
| E2 | no verifier vs +verifier vs +verifier+replan | `partially_ready` | mock v0 闭环 **有**；系统消融需统一 episode log 批量跑 |
| E3 | GT teacher-state vs predicted memory | `partially_ready` | teacher **有**；`PredictedMemoryPlaceholder` **有**；学习感知 **future_only** |
| E4 | CALVIN train → RLBench / VLABench eval | `partially_ready` / `future_only` | CALVIN 语言 + planner SFT **有**；RLBench **stub**；VLABench **规划接口 future_only** |

**状态图例**：`implemented_now` / `partially_ready` / `future_only`。

**指标诚实**：3B LoRA 的 JSONL proxy 指标见 `results/eval/planner_base_vs_tuned/metrics.json`；**非**官方 CALVIN / RLBench 榜单。
