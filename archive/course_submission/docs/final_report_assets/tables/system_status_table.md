# System status (module-level)

_Generated: `2026-03-31T11:48:18.064013+00:00`_

| Module / capability | Ready state | Pointer |
|---------------------|-------------|---------|
| Scene memory + contracts | **ready** | `docs/scene_memory_contract_v2.md` |
| Planner output contract | **ready** | `src/embodied_scene_agent/planner/planner_output_contract.py` |
| Verifier + taxonomy | **ready** | `docs/failure_taxonomy.md` |
| Replanner (rule + hybrid LLM) | **ready** | `docs/replanner_design_v2.md` |
| Episode log schema | **ready** | `docs/episode_log_schema.md` |
| v0 loop + CALVIN minimal loop | **ready** | `src/embodied_scene_agent/pipeline/` |
| Auto project report | **ready** | `results/reports/latest_project_report.md` |
| E2 ablation runners | **ready** | `scripts/run_ablation_e2*.sh` |
| Hybrid replanner eval | **ready** | `scripts/run_hybrid_replanner_eval.sh` |
| CALVIN debug → planner JSONL | **ready** | `scripts/build_calvin_debug_planner_data.sh` |
| RLBench stack diagnosis | **ready** | `scripts/diagnose_rlbench_stack.sh` |
| A100 7B production training | **future_only** | `configs/experiment/a100_final.yaml` |
| Official benchmark scores | **future_only** | `—` |

- RLBench deepest stage (from snapshot): `import_fail`
