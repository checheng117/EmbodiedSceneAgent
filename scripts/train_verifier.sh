#!/usr/bin/env bash
# Verifier 训练占位（规则版为默认）
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
python -m embodied_scene_agent.training.train_verifier --config "${ROOT}/configs/verifier/base.yaml"
