#!/usr/bin/env bash
# Rebuild pooled + grouped_sequence + same_task_subset planner JSONL and alignment stats doc.
# Set CALVIN_ALIGNMENT_QUICK=1 to cap samples (faster smoke).
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"

MT="${MAX_CALVIN_DEBUG_TRAIN:-48}"
MV="${MAX_CALVIN_DEBUG_VAL:-16}"
MTE="${MAX_CALVIN_DEBUG_TEST:-16}"
same_task_groups=(--same-task-max-groups-train 8 --same-task-max-groups-val 4 --same-task-max-groups-test 4)
if [[ "${CALVIN_ALIGNMENT_QUICK:-}" == "1" ]]; then
  MT=3
  MV=2
  MTE=2
  same_task_groups=(--same-task-max-groups-train 1 --same-task-max-groups-val 1 --same-task-max-groups-test 1)
fi

common=(--source calvin_debug_real --out-dir "${ROOT}/data/processed/planner_sft"
  --manifest "${ROOT}/data/processed/calvin_real_subset/manifest.jsonl"
  --max-train-samples "$MT" --max-val-samples "$MV" --max-test-samples "$MTE"
  --rollout-max-steps 12 --seed 42 --experiment-id calvin_debug_alignment_bundle)

python -m embodied_scene_agent.training.build_planner_data "${common[@]}" \
  --alignment-mode pooled_manifest --output-basename calvin_debug_real

python -m embodied_scene_agent.training.build_planner_data "${common[@]}" \
  --alignment-mode grouped_sequence --output-basename calvin_debug_real_aligned

python -m embodied_scene_agent.training.build_planner_data "${common[@]}" \
  --alignment-mode same_task_subset --output-basename calvin_debug_real_same_task \
  "${same_task_groups[@]}"

python "${ROOT}/scripts/write_calvin_debug_alignment_stats_md.py" --root "$ROOT"
