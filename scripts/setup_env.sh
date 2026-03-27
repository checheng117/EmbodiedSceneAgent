#!/usr/bin/env bash
# 使用 conda 创建/更新环境（名称来自 environment.yml），并编辑安装本仓库
set -eo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v conda >/dev/null 2>&1; then
  echo "错误: 未找到 conda。请先安装 Miniconda/Anaconda，并确保 conda 在 PATH 中。" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "${ROOT}/scripts/resolve_conda_env.sh"
if [[ -z "${ESA_CONDA_ENV_NAME:-}" ]]; then
  echo "错误: 无法从 environment.yml 解析环境名" >&2
  exit 1
fi
ENV_NAME="$ESA_CONDA_ENV_NAME"

eval "$(conda shell.bash hook)"

if conda env list | grep -qE "^${ENV_NAME}[[:space:]]"; then
  echo "更新 conda 环境: ${ENV_NAME}"
  conda env update -n "${ENV_NAME}" -f "${ROOT}/environment.yml" --prune
else
  echo "创建 conda 环境: ${ENV_NAME}"
  conda env create -f "${ROOT}/environment.yml"
fi

conda activate "${ENV_NAME}"
pip install -U pip
pip install -e ".[dev]"
echo "完成: conda 环境 ${ENV_NAME} 已就绪，仓库已可编辑安装于 ${ROOT}"
echo "使用: conda activate ${ENV_NAME}"
