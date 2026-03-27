#!/usr/bin/env bash
# Inspect official CALVIN debug dataset layout (no training).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ESA_CALVIN_OFFICIAL_ROOT="${ESA_CALVIN_OFFICIAL_ROOT:-$ROOT/data/raw/calvin_official}"
DEBUG_DIR="${ESA_CALVIN_DEBUG_DATASET_DIR:-$ESA_CALVIN_OFFICIAL_ROOT/dataset/calvin_debug_dataset}"

echo "ESA_CALVIN_OFFICIAL_ROOT=$ESA_CALVIN_OFFICIAL_ROOT"
echo "DEBUG_DIR=$DEBUG_DIR"
if [[ ! -d "$DEBUG_DIR" ]]; then
  echo "MISSING: run bash scripts/download_calvin_debug_data.sh"
  exit 1
fi
du -sh "$DEBUG_DIR" || true
echo "--- top level ---"
ls -la "$DEBUG_DIR" | head -40
echo "--- find npy (sample) ---"
find "$DEBUG_DIR" -maxdepth 4 -type f \( -name '*.npy' -o -name '*.npz' \) 2>/dev/null | head -20 || true
