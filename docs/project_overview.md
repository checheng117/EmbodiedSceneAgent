# Project Overview

EmbodiedSceneAgent studies structured replanning for language-conditioned embodied tasks. The focus is not on adding more benchmark tasks, but on making planning failures auditable and recoverable in a closed loop.

## System loop

The implemented runtime loop is:

`Observation -> Scene Memory -> Planner -> Executor -> Verifier -> Replanner`

Reference architecture:

- `assets/architecture_overview.svg`

Key behavior:

- `Scene Memory` keeps grounded object/state fields used by planning and checks.
- `Planner` emits structured plan fields under a strict schema.
- `Verifier` classifies execution outcomes into failure signals.
- `Replanner` revises plans with rule-first or hybrid logic.
- A semantic acceptance filter blocks unsafe-but-schema-valid revisions.
- A repeated-no-effect guard prevents horizon waste on ineffective retries.

## Current implementation scope

- End-to-end cognition loop is implemented and testable.
- Planner contract, parser/repair, and validation are integrated.
- Replanning audit fields are persisted for diagnosis.
- Minimal LoRA tuning path for `Qwen/Qwen2.5-VL-3B-Instruct` is included.
- Tiny controlled side-by-side runs are included for baseline vs VL-3B vs VL-7B diagnostics.

## Evidence model

- Primary quantitative evidence: base-vs-tuned proxy metrics on `n=73`.
- Secondary qualitative evidence: fixed tiny 3-case comparison under controlled settings.
- Reproducibility evidence: config snapshots, run manifests, and run directories under `results/`.
- Fast verification path: `scripts/setup_env.sh`, `scripts/showcase_smoke.sh`, `scripts/run_minimal_eval.sh`.

This repository intentionally separates verified evidence from future-only plans.
