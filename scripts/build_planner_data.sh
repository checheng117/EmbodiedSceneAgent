#!/usr/bin/env bash
# 将 scene_memory JSON 快照汇总为 planner SFT JSONL（占位管线）
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.training.build_sft_data \
  --in_dir "${ROOT}/data/scene_memory" \
  --out "${ROOT}/data/planner_sft/planner_stub.jsonl"
