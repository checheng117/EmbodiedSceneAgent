#!/usr/bin/env bash
# RLBench: try sim reset if rlbench+CoppeliaSim OK; else fixture → SceneMemory → planner (see docs/rlbench_install_log.md).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.evaluation.rlbench_smoke --mode all "$@"
python -m embodied_scene_agent.reporting.make_project_report
echo "[run_rlbench_dev_smoke] done (results/rlbench_dev_smoke.json + episode_logs + report)"
