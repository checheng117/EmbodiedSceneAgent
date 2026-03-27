#!/usr/bin/env bash
# v0 mock 评测 JSON 输出到 results/
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -c "
from pathlib import Path
from embodied_scene_agent.evaluation.eval_v0 import run_eval_v0
run_eval_v0(out_path=Path('results') / 'v0_mock_summary.json')
print('wrote results/v0_mock_summary.json')
"
