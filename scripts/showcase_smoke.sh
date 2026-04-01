#!/usr/bin/env bash
# Public-facing minimal smoke for the closed cognition loop.
# Expected output artifact: results/showcase/showcase_smoke.log
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v python >/dev/null 2>&1; then
  echo "ERROR: python not found in PATH." >&2
  exit 1
fi

# Try to activate the project conda env when conda exists.
if command -v conda >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source "${ROOT}/scripts/conda_env.sh"
fi

export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
OUT_DIR="${ROOT}/results/showcase"
OUT_LOG="${OUT_DIR}/showcase_smoke.log"
mkdir -p "${OUT_DIR}"

# Fail loudly if the package cannot be imported.
python - <<'PY'
import importlib.util
import sys

if importlib.util.find_spec("embodied_scene_agent") is None:
    print("ERROR: embodied_scene_agent package is not importable.", file=sys.stderr)
    print("Hint: run `bash scripts/setup_env.sh` first.", file=sys.stderr)
    raise SystemExit(1)
PY

echo "[showcase] running closed-loop smoke..." | tee "${OUT_LOG}"
python -m embodied_scene_agent.cli.run_v0 \
  --instruction "Put the red block in the drawer." | tee -a "${OUT_LOG}"

echo "[showcase] running forced-failure path to exercise replanning..." | tee -a "${OUT_LOG}"
python -m embodied_scene_agent.cli.run_v0 \
  --instruction "Put the red block in the drawer." \
  --forced-grasp-failures 1 | tee -a "${OUT_LOG}"

echo "[showcase] running two focused smoke tests..." | tee -a "${OUT_LOG}"
if ! command -v pytest >/dev/null 2>&1; then
  echo "ERROR: pytest not found. Install dev dependencies via scripts/setup_env.sh." >&2
  exit 1
fi
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
pytest -q tests/test_smoke_v0.py tests/test_v0_replan.py | tee -a "${OUT_LOG}"

echo "[showcase] done. Log written to: ${OUT_LOG}" | tee -a "${OUT_LOG}"
