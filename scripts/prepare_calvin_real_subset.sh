#!/usr/bin/env bash
# 下载官方 CALVIN playtable YAML 标注并生成 manifest.jsonl
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.data.prepare_calvin_real_subset "$@"
