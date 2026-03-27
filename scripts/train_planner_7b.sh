#!/usr/bin/env bash
# A100 / 7B planner training template — **do not claim results until actually run**.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
export HF_HOME="${HF_HOME:-${ROOT}/.hf_cache}"
EXPERIMENT_ID="${EXPERIMENT_ID:-esa_planner_7b_$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${ROOT}/results/checkpoints/planner_sft_7b/${EXPERIMENT_ID}"
mkdir -p "${OUT}"
cp "${ROOT}/configs/planner/qwen25vl_7b_lora.yaml" "${OUT}/config.snapshot.yaml"
echo "{\"experiment_id\":\"${EXPERIMENT_ID}\",\"status\":\"template_only_not_executed\",\"note\":\"Run on A100 after schema/data lock.\"}" > "${OUT}/run_intent.json"
echo "[train_planner_7b] template prepared at ${OUT} (no training invoked by default)."
echo "To run: set EXPERIMENT_ID, ensure GPU memory, then invoke run_planner_sft with 7b config and paths."
exit 0
