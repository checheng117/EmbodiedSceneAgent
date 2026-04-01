# Reproducibility & engineering notes

## Regenerate canonical snapshots

```bash
bash scripts/build_final_report_assets.sh
```

This runs `make_project_report` then materializes `docs/final_report_assets/` and `results/final_report_assets/`.

## Individual pipelines

| Goal | Command |
|------|---------|
| Project JSON + dashboard | `python -m embodied_scene_agent.reporting.make_project_report` |
| E2 mock | `bash scripts/run_ablation_e2.sh` |
| E2 CALVIN fixture | `bash scripts/run_ablation_e2_calvin_fixture.sh` |
| E2 CALVIN debug real | `bash scripts/run_ablation_e2_calvin_debug_real.sh` |
| Hybrid batch | `bash scripts/run_hybrid_replanner_eval.sh` |
| Hybrid CALVIN debug | `bash scripts/run_hybrid_replanner_eval_calvin_debug.sh` |
| CALVIN debug planner JSONL | `bash scripts/build_calvin_debug_planner_data.sh` |
| RLBench smoke | `bash scripts/run_rlbench_dev_smoke.sh` |
| RLBench diagnosis | `bash scripts/diagnose_rlbench_stack.sh` |

## Environment

- Conda env from `environment.yml` (see `scripts/conda_env.sh`).
- Repo root: the directory containing `pyproject.toml` (clone path on your machine / A100).
