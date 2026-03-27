#!/usr/bin/env bash
# 自动化 base vs tuned 指标 + case studies（评测 test.jsonl 子集时可限 --max-samples）
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "${ROOT}/scripts/conda_env.sh"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
export HF_HOME="${HF_HOME:-${ROOT}/.hf_cache}"
LORA="${1:-${ROOT}/results/checkpoints/planner_sft_3b_minimal/run_latest/best_lora}"
python -m embodied_scene_agent.evaluation.eval_planner_models \
  --eval-jsonl "${ROOT}/data/processed/planner_sft/test.jsonl" \
  --base-model-id "Qwen/Qwen2.5-VL-3B-Instruct" \
  --lora-dir "${LORA}" \
  --out-dir "${ROOT}/results/eval/planner_base_vs_tuned" \
  --max-samples "${2:-12}"

python -m embodied_scene_agent.evaluation.write_case_studies \
  --per-sample "${ROOT}/results/eval/planner_base_vs_tuned/per_sample_results.jsonl" \
  --out "${ROOT}/results/eval/base_vs_tuned_case_studies.md"
