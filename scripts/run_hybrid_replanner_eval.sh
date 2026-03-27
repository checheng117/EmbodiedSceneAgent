#!/usr/bin/env bash
# Batch hybrid replanner eval (mock v0); CPU-friendly default via ESA_FORCE_CPU_REPLANNER=1 optional.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
export ESA_REPLANNER_MAX_NEW="${ESA_REPLANNER_MAX_NEW:-256}"
python -m embodied_scene_agent.evaluation.hybrid_replanner_eval "$@"
python -m embodied_scene_agent.reporting.make_project_report
echo "[run_hybrid_replanner_eval] done (results/experiments/hybrid_replanner_eval/*/)"
