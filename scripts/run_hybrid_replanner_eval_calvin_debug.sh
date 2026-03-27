#!/usr/bin/env bash
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
extra=()
if [[ -n "${CALVIN_DEBUG_BATCH:-}" ]]; then
  extra+=(--calvin-debug-batch "$CALVIN_DEBUG_BATCH")
fi
python -m embodied_scene_agent.evaluation.hybrid_replanner_eval \
  --backend calvin_debug_real \
  --episodes "${HYBRID_CALVIN_DEBUG_EPISODES:-10}" \
  "${extra[@]}" \
  "$@"
