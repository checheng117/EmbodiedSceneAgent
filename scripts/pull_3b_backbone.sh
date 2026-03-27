#!/usr/bin/env bash
# 拉取 configs/planner/qwen25vl_3b_lora.yaml 中的 3B VL backbone（需 HF_TOKEN）
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
export HF_HOME="${HF_HOME:-${ROOT}/.hf_cache}"
export HF_DATASETS_CACHE="${HF_DATASETS_CACHE:-${HF_HOME}/datasets}"
mkdir -p "${HF_HOME}"
python -m embodied_scene_agent.training.prepare_backbone \
  --model-id "Qwen/Qwen2.5-VL-3B-Instruct" \
  --log-json "${ROOT}/results/logs/prepare_backbone_last.json"
