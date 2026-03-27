#!/usr/bin/env bash
# Build planner SFT JSONL from official CALVIN calvin_debug_dataset (vector teacher + minimal loop).
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
python -m embodied_scene_agent.training.build_planner_data \
  --source calvin_debug_real \
  --out-dir "${ROOT}/data/processed/planner_sft" \
  --manifest "${ROOT}/data/processed/calvin_real_subset/manifest.jsonl" \
  --max-train-samples "${MAX_CALVIN_DEBUG_TRAIN:-48}" \
  --max-val-samples "${MAX_CALVIN_DEBUG_VAL:-16}" \
  --max-test-samples "${MAX_CALVIN_DEBUG_TEST:-16}" \
  --rollout-max-steps 12 \
  --seed 42 \
  --experiment-id calvin_debug_planner_export \
  "$@"
