#!/usr/bin/env bash
# Base vs LoRA 各跑若干条 val 样本，写入 markdown（需 GPU 推荐）
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
export HF_HOME="${HF_HOME:-${ROOT}/.hf_cache}"
LORA="${1:-${ROOT}/results/checkpoints/planner_sft_3b_minimal/run_latest/best_lora}"
OUT="${ROOT}/results/eval/planner_inference_smoke.md"
mkdir -p "$(dirname "${OUT}")"
python -m embodied_scene_agent.training.run_planner_inference_smoke \
  --val-jsonl "${ROOT}/data/processed/planner_sft/val.jsonl" \
  --lora-dir "${LORA}" \
  --out "${OUT}" \
  --max-samples 3
