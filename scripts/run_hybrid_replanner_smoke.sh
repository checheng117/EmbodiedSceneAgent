#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
export HF_HOME="${HF_HOME:-${ROOT}/.hf_cache}"
# 可用 ESA_REPLANNER_MODEL_ID 覆盖；默认较小模型以加快 smoke（仍为真实 generate）
export ESA_REPLANNER_MODEL_ID="${ESA_REPLANNER_MODEL_ID:-Qwen/Qwen2.5-0.5B-Instruct}"
export ESA_REPLANNER_MAX_NEW="${ESA_REPLANNER_MAX_NEW:-192}"
python -m embodied_scene_agent.evaluation.hybrid_replanner_smoke "$@"
python -m embodied_scene_agent.reporting.make_project_report
