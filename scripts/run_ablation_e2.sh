#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.evaluation.run_ablation_e2 "$@"
python -m embodied_scene_agent.reporting.make_project_report
