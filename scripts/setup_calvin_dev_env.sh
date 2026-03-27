#!/usr/bin/env bash
# Official CALVIN (mees/calvin) dev environment per upstream README:
#   conda create -n calvin_venv python=3.8
#   conda activate calvin_venv
#   cd $CALVIN_ROOT && sh install.sh
# This script runs an install.sh-equivalent sequence plus setuptools<58 before calvin_models (README pyhash note).
#
# Does NOT merge into embodied-scene-agent. Logs to results/logs/.
#
# Env:
#   ESA_CALVIN_CONDA_ENV  conda env name (default: calvin_venv)
#   ESA_CALVIN_OFFICIAL_ROOT  path to cloned mees/calvin (default: <repo>/data/raw/calvin_official)
#   ESA_SKIP_INSTALL  if set to 1, skip install.sh (only print paths)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export ESA_CALVIN_OFFICIAL_ROOT="${ESA_CALVIN_OFFICIAL_ROOT:-$ROOT/data/raw/calvin_official}"
CONDA_ENV="${ESA_CALVIN_CONDA_ENV:-calvin_venv}"
LOG_DIR="$ROOT/results/logs"
mkdir -p "$LOG_DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/calvin_official_install_${TS}.log"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found on PATH" | tee "$LOG_FILE"
  exit 1
fi

if [[ ! -d "$ESA_CALVIN_OFFICIAL_ROOT/.git" ]]; then
  echo "ESA_CALVIN_OFFICIAL_ROOT is not a git repo: $ESA_CALVIN_OFFICIAL_ROOT" | tee "$LOG_FILE"
  echo "Run: git clone --recurse-submodules https://github.com/mees/calvin.git data/raw/calvin_official" | tee -a "$LOG_FILE"
  exit 1
fi

{
  echo "=== calvin dev setup $TS ==="
  echo "ESA_CALVIN_OFFICIAL_ROOT=$ESA_CALVIN_OFFICIAL_ROOT"
  echo "CONDA_ENV=$CONDA_ENV"
  git -C "$ESA_CALVIN_OFFICIAL_ROOT" rev-parse HEAD
  git -C "$ESA_CALVIN_OFFICIAL_ROOT" submodule status
} | tee "$LOG_FILE"

if conda env list | awk '{print $1}' | grep -qx "$CONDA_ENV"; then
  echo "conda env exists: $CONDA_ENV" | tee -a "$LOG_FILE"
else
  echo "creating conda env $CONDA_ENV python=3.8 ..." | tee -a "$LOG_FILE"
  conda create -y -n "$CONDA_ENV" python=3.8 2>&1 | tee -a "$LOG_FILE"
fi

if [[ "${ESA_SKIP_INSTALL:-0}" == "1" ]]; then
  echo "ESA_SKIP_INSTALL=1 — skipping install.sh" | tee -a "$LOG_FILE"
  exit 0
fi

echo "running upstream-equivalent install (install.sh + setuptools<58 before calvin_models; per CALVIN README pyhash note) ..." | tee -a "$LOG_FILE"
# shellcheck disable=SC1091
set +u
eval "$(conda shell.bash hook)"
conda activate "$CONDA_ENV"
set -u
(
  cd "$ESA_CALVIN_OFFICIAL_ROOT"
  # Mirrors install.sh lines 1–9, then official README fix for pyhash before calvin_models.
  pip install wheel cmake==3.18.4
  (cd calvin_env/tacto && pip install -e .)
  (cd calvin_env && pip install -e .)
  pip install "setuptools<58"
  (cd calvin_models && pip install -e .)
) 2>&1 | tee -a "$LOG_FILE"

echo "done. Log: $LOG_FILE" | tee -a "$LOG_FILE"
