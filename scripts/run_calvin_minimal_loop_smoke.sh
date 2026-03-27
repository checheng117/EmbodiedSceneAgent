#!/usr/bin/env bash
# CALVIN minimal loop smoke（非 benchmark）。默认 fixture；若已配置 ESA_CALVIN_ENV_FACTORY 可加：
#   bash scripts/run_calvin_minimal_loop_smoke.sh --try-local-factory --live-action-strategy symbolic_fallback
#
# 与 run_calvin_live_probe.sh 相同：可选 ESA_CALVIN_CONDA_ENV=calvin_venv + ESA_CALVIN_OFFICIAL_ROOT
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

python -m embodied_scene_agent.cli.run_calvin_minimal_loop "$@"
