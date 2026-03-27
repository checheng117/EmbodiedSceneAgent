#!/usr/bin/env bash
# 从仓库根 environment.yml 解析 conda 环境名（唯一真源：YAML 的 name 字段）。
# 由 conda_env.sh / setup_env.sh source；也可单独: source scripts/resolve_conda_env.sh && echo "$ESA_CONDA_ENV_NAME"
# 注意：本文件常被 source，勿使用 set -e，避免 grep 无匹配时中断用户 shell。
_RESOLVE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
_RESOLVE_YML="${_RESOLVE_ROOT}/environment.yml"
if [[ ! -f "${_RESOLVE_YML}" ]]; then
  echo "resolve_conda_env.sh: missing ${_RESOLVE_YML}" >&2
  export ESA_CONDA_ENV_NAME=""
  return 0 2>/dev/null || true
fi
_line="$(grep -E '^[[:space:]]*name:' "${_RESOLVE_YML}" | head -1 || true)"
export ESA_CONDA_ENV_NAME="$(echo "${_line}" | sed -E 's/^[[:space:]]*name:[[:space:]]*//;s/[[:space:]]+$//;s/^["'\'']//;s/["'\'']$//')"
