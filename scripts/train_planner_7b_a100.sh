#!/usr/bin/env bash
# A100 80G：Qwen2.5-VL-7B 正式训练 / 评测入口（仅应在 A100 上跑正式实验）
# 用法示例（在目标机器上）：
#   CUDA_VISIBLE_DEVICES=0 bash scripts/train_planner_7b_a100.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
echo "A100 final run: configs/planner/qwen25vl_7b_lora.yaml + configs/experiment/a100_final.yaml"
echo "TODO: wire distributed launch + experiment_id logging."
python -m embodied_scene_agent.training.train_planner --config "${ROOT}/configs/planner/qwen25vl_7b_lora.yaml"
