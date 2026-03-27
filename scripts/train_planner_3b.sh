#!/usr/bin/env bash
# 3090：Qwen2.5-VL-3B LoRA 训练入口（需自行安装 torch/transformers/peft）
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.training.train_planner --config "${ROOT}/configs/planner/qwen25vl_3b_lora.yaml"
