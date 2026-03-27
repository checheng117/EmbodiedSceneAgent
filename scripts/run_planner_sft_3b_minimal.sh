#!/usr/bin/env bash
# 最小 LoRA SFT（需 pip install -e '.[train]' 与 GPU 推荐）
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
# 避免 ~/.local 中另一套 torch/torchvision 与 conda 内 wheel 混载导致 nvshmem / libc10 符号错误
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
export HF_HOME="${HF_HOME:-${ROOT}/.hf_cache}"
mkdir -p "${HF_HOME}"
OUT="${ROOT}/results/checkpoints/planner_sft_3b_minimal/run_latest"
python -m embodied_scene_agent.training.run_planner_sft \
  --config "${ROOT}/configs/planner/qwen25vl_3b_lora_minimal.yaml" \
  --train-jsonl "${ROOT}/data/processed/planner_sft/train.jsonl" \
  --val-jsonl "${ROOT}/data/processed/planner_sft/val.jsonl" \
  --output-dir "${OUT}" \
  "$@"
