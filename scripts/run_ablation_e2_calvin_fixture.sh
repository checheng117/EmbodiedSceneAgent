#!/usr/bin/env bash
# E2 ablation on CALVIN **fixture** batch (not official CALVIN benchmark).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.evaluation.run_ablation_e2 --backend calvin_fixture "$@"
python -m embodied_scene_agent.reporting.make_project_report
echo "[run_ablation_e2_calvin_fixture] done (results/experiments/e2_ablation/e2_calvin_fixture_*/ + comparison table)"
