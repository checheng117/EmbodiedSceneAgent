#!/usr/bin/env bash
# 供其它脚本 source：激活 conda 环境（名称来自 environment.yml，勿在此硬编码）。
# 覆盖：export ESA_CONDA_ENV=my-other-env 后再 source 本脚本。
# conda 的 activate.d 脚本可能引用未定义变量，故在激活期间临时关闭 nounset。
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${_SCRIPT_DIR}/resolve_conda_env.sh"
if [[ -z "${ESA_CONDA_ENV_NAME:-}" ]]; then
  echo "conda_env.sh: could not read env name from environment.yml" >&2
  exit 1
fi
ESA_CONDA_ENV="${ESA_CONDA_ENV:-$ESA_CONDA_ENV_NAME}"
if command -v conda >/dev/null 2>&1; then
  _esa_restore_nounset=0
  if [[ -o nounset ]]; then
    _esa_restore_nounset=1
  fi
  set +u
  # shellcheck disable=SC1091
  eval "$(conda shell.bash hook)"
  conda activate "$ESA_CONDA_ENV"
  if [[ "$_esa_restore_nounset" -eq 1 ]]; then
    set -u
  fi
  unset _esa_restore_nounset
fi
