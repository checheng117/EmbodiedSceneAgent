#!/usr/bin/env bash
# Official CALVIN debug dataset (~1.3GB): upstream dataset/download_data.sh debug
# Run inside ESA_CALVIN_CONDA_ENV (optional; only needs wget/unzip).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ESA_CALVIN_OFFICIAL_ROOT="${ESA_CALVIN_OFFICIAL_ROOT:-$ROOT/data/raw/calvin_official}"
DS="$ESA_CALVIN_OFFICIAL_ROOT/dataset"
LOG_DIR="$ROOT/results/logs"
mkdir -p "$LOG_DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/calvin_debug_download_${TS}.log"

if [[ ! -f "$DS/download_data.sh" ]]; then
  echo "missing $DS/download_data.sh" | tee "$LOG_FILE"
  exit 1
fi

{
  echo "=== download debug $TS ==="
  echo "cd $DS && sh download_data.sh debug"
} | tee "$LOG_FILE"

(
  cd "$DS"
  sh download_data.sh debug
) 2>&1 | tee -a "$LOG_FILE"

echo "expected folder: $DS/calvin_debug_dataset" | tee -a "$LOG_FILE"
