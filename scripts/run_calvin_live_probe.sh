#!/usr/bin/env bash
# Live CALVIN 探针（非 benchmark）。可选：export ESA_CALVIN_ENV_FACTORY='module:callable' 做 reset/summary。
# 默认写入 results/calvin_live_probe_summary.json；仅打印：加 --no-write-json
#
# 官方 mees/calvin + Python 3.8 环境（与 embodied-scene-agent 分离）：
#   export ESA_CALVIN_CONDA_ENV=calvin_venv
#   export ESA_CALVIN_OFFICIAL_ROOT="$PWD/data/raw/calvin_official"   # 可选，有默认值
#   bash scripts/run_calvin_live_probe.sh
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export ESA_CALVIN_OFFICIAL_ROOT="${ESA_CALVIN_OFFICIAL_ROOT:-$ROOT/data/raw/calvin_official}"
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
export ESA_CALVIN_ENV_FACTORY="${ESA_CALVIN_ENV_FACTORY:-embodied_scene_agent.envs.calvin_hydra_factory:make_calvin_env}"

if [[ -n "${ESA_CALVIN_CONDA_ENV:-}" ]]; then
  if ! command -v conda >/dev/null 2>&1; then
    echo "ESA_CALVIN_CONDA_ENV set but conda not found" >&2
    exit 1
  fi
  _esa_restore_nounset=0
  if [[ -o nounset ]]; then
    _esa_restore_nounset=1
  fi
  set +u
  # shellcheck disable=SC1091
  eval "$(conda shell.bash hook)"
  conda activate "$ESA_CALVIN_CONDA_ENV"
  if [[ "$_esa_restore_nounset" -eq 1 ]]; then
    set -u
  fi
  unset _esa_restore_nounset
else
  # shellcheck disable=SC1091
  source "${ROOT}/scripts/conda_env.sh"
fi

python -m embodied_scene_agent.cli.run_calvin_live_probe "$@"
