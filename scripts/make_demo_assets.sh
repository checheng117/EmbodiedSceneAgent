#!/usr/bin/env bash
# Generate demo folders + episode samples + project report (conda env from environment.yml).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.reporting.export_demo_assets
mkdir -p "${ROOT}/results/episode_logs"
cp -f "${ROOT}/results/demos/success_put_block/episode_log_steps.json" \
  "${ROOT}/results/episode_logs/sample_v0_episode_steps.json" 2>/dev/null || true
python -m embodied_scene_agent.reporting.make_project_report
echo "[make_demo_assets] done (includes dashboard)"
