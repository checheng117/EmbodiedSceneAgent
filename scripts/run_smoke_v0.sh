#!/usr/bin/env bash
# v0 最小闭环 smoke：mock env + rule planner + verifier + replan 路径
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.cli.run_v0 --instruction "Put the red block in the drawer."
python -m embodied_scene_agent.cli.run_v0 --instruction "Put the red block in the drawer." --forced-grasp-failures 1
pytest -q \
  tests/test_smoke_v0.py \
  tests/test_v0_replan.py \
  tests/test_scene_memory.py \
  tests/test_planner_io.py \
  tests/test_verifier.py
