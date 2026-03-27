#!/usr/bin/env bash
# 官方 CALVIN 语言 manifest → mock 符号 rollout → planner_sft/v1 train/val/test
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.training.build_planner_data \
  --source real_subset \
  --manifest "${ROOT}/data/processed/calvin_real_subset/manifest.jsonl" \
  --out-dir "${ROOT}/data/processed/planner_sft" \
  --seed 42 \
  --max-train-episodes 220 \
  --max-val-episodes 45 \
  --max-test-episodes 45 \
  --rollout-max-steps 16
