# Benchmark coverage (honest scope)

| Benchmark / surface | Status | Evidence class | Notes |
|---------------------|--------|----------------|-------|
| CALVIN official leaderboard | **future_only** | — | Teacher-state + minimal loop exist; no claimed rank. |
| CALVIN-shaped **fixture** E2 | **fixture** | `results/experiments/e2_ablation/e2_calvin_fixture_*` | Adapter reality stress; not leaderboard. |
| CALVIN **official debug** npz (vector teacher) | **real (subset)** | `e2_calvin_debug_real_*`, `hybrid_calvin_debug_real_*` | Official debug zip only; not D/ABC/ABCD; not leaderboard. |
| RLBench official sim | **blocked** / **future_only** | `results/rlbench_stack_diagnosis.json` | `import_fail` on dev path; fixture bridge **real**. |
| RLBench cognition bridge | **smoke** / **real** (fixture) | `results/rlbench_dev_smoke.json` | memory_bridge + planner_smoke on fixture. |
| VLABench | **future_only** | `docs/vlabench_plan.md` | Planning doc only. |
