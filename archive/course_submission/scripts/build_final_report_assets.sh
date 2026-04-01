#!/usr/bin/env bash
# Final report asset pack: regenerates project report + docs/final_report_assets + results/final_report_assets.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.reporting.make_project_report
python -m embodied_scene_agent.reporting.build_final_report_assets "$@"
echo "[build_final_report_assets] done"
