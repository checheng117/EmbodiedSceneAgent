#!/usr/bin/env bash
# Structured RLBench / PyRep / CoppeliaSim stack diagnosis → results/rlbench_stack_diagnosis.json
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
EXTRA=()
if [[ "${ESA_RLBench_DIAGNOSE_NO_SIM:-}" == "1" ]]; then
  EXTRA+=(--diagnose-no-sim)
fi
python -m embodied_scene_agent.evaluation.rlbench_smoke --diagnose "${EXTRA[@]}" "$@"
echo "[diagnose_rlbench_stack] wrote results/rlbench_stack_diagnosis.json"
