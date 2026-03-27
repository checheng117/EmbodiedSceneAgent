#!/usr/bin/env bash
# CALVIN-grounded 最小开发通路：mock 观测 → SceneMemory → rule planner 一步（无 benchmark 分数）
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.cli.run_calvin_dev "$@"
