# EmbodiedSceneAgent

This project is submitted as an Assignment 3 study on agent-oriented LLM post-training for structured replanning.

EmbodiedSceneAgent is maintained as an Assignment 3-aligned LLM post-training project: a structured, agent-style cognition loop for language-conditioned embodied planning with scene-memory grounding, verifier feedback, and failure-aware replanning.

---

## 1) Research Topic / Problem Statement

**Downstream task.**  
Given an instruction (for example, placing a block into a drawer), the system must generate and revise high-level executable subtasks under changing scene state.

**Why this is LLM post-training.**  
The planner output is a strict structured format; the project studies whether a minimally tuned model improves action/target correctness over a stable baseline under the same contract.

**Why this is agent-oriented.**  
The planner is only one component in a closed loop: `Observation -> Scene Memory -> Planner -> Executor -> Verifier -> Replanner`. Decisions are tool-like, stateful, and failure-conditioned rather than one-shot text generation.

**Problem being solved.**  
One-shot plans often fail due to grounding mismatch, missing preconditions, or repeated no-effect execution. This project focuses on making failure handling auditable and recoverable at the cognition layer.

---

## 2) Task Formulation

| Item | Definition in this repository |
|------|-------------------------------|
| Input | Natural-language instruction + current observation-derived scene state + recent history |
| Intermediate state | Structured `SceneMemory` (object ids, attributes, relations, traceable state fields) |
| Model output | Structured `PlannerOutput`: `task`, `subgoal`, `target_object`, `skill`, `success_check`, `fallback` (+ optional `reasoning`, `confidence`) |
| Verifier/replanner role | Detect failure type from before/after state, then revise plan with rule or hybrid rule+LLM path |
| Success/failure | Success: episode completes objective under loop policy. Failure: verifier/replanner cannot achieve effective progress before termination |

---

## 3) Why this fits Assignment 3

- **Fine-tuning pre-trained LLM**: includes a real minimal SFT run for `Qwen/Qwen2.5-VL-3B-Instruct` with LoRA config and saved checkpoint artifacts.
- **Baseline comparison**: provides direct base-vs-tuned quantitative comparison on the same planner-output proxy metrics.
- **Agent-oriented post-training**: integrates model output into local executable loop components (memory, verifier, replanner, executor interface).
- **Local executable interfaces/tools**: reproducible scripts, contract validation, and run manifests are provided for each experiment run.
- **Result analysis + case studies**: includes quantitative table, tiny fixed 3-case side-by-side comparison, and curated failure analyses.

---

## 4) Model and Training Setup (honest scope)

Base model: stable baseline planner path used for main quantitative comparison.  
Tuned model: `Qwen2.5-VL-3B-Instruct` with minimal LoRA SFT.

| Item | Current implemented status |
|------|----------------------------|
| Stable baseline path | Baseline planner and stable hybrid baseline run used as anchor in tiny comparison |
| Tuned model | `Qwen/Qwen2.5-VL-3B-Instruct` minimal SFT with LoRA (`r=8`, `alpha=16`, `dropout=0.05`, target modules `q_proj`, `v_proj`) |
| Main training artifact | `results/checkpoints/planner_sft_3b_minimal/run_latest/` |
| 3090-only strategy | Minimal-step, small-batch development training/eval designed for RTX 3090 constraints |
| Not claimed | No official CALVIN/RLBench leaderboard claims; no large-scale significance claim from tiny qualitative runs |

---

## 5) Agent-Oriented Components / Tool-like Interfaces

| Component | Inputs | Outputs | Why it matters |
|-----------|--------|---------|----------------|
| Scene memory interface | Observations/teacher state | `SceneMemory` object graph | Provides grounded object vocabulary for planning and semantic checks |
| Planner contract | `instruction`, `scene_memory`, `history`, optional `failure_log` | `PlannerOutput` schema | Enforces parseable, auditable plan structure instead of free-form text |
| Verifier | before/after state + planned intent | `VerificationResult` with taxonomy failure type | Converts execution outcomes into explicit failure evidence |
| Hybrid replanner | previous plan + failure + scene memory + history | revised plan + `ReplannerAuditLog` | Supports rule-first repair with optional LLM revision and explicit fallback records |
| Semantic acceptance filter | candidate revised plan + current memory | accept/reject reason (`target_absent_from_scene_memory`, `drawer_goal_target_mismatch`, etc.) | Blocks schema-valid but semantically unsafe replans before execution |
| Repeated-no-effect guard | consecutive no-effect signatures | guard trigger + terminal label evidence | Prevents wasting horizon on repeated ineffective retries |

---

## 6) Data Construction / Supervision Design

This repository uses structured planner supervision and failure-aware replanning traces rather than pure free-text QA data.

Training sample shape (report-ready shorthand): input = instruction + scene memory + history + failure evidence; target = structured revised plan JSON.

- **Planner supervision format**: train/val JSONL under `data/processed/planner_sft/` with line-structured planning targets mapped into `PlannerOutput` fields.
- **State-grounded context**: scene memory, recent history, and failure evidence are included in planning/replanning context.
- **Recovery-oriented examples**: evaluation and case assets include verifier-detected failure steps and post-failure revisions.
- **Output representation**: strict key set for planning, plus auditable replan metadata (`llm_replanner_called`, parse/validation status, fallback reason/stage, repair actions).
- **Current implementation vs future**: current evidence is from mock/CALVIN fixture/CALVIN debug-vector-teacher tracks; official benchmark-scale claims are intentionally excluded.

---

## 7) Prompt / Structured Output Design

**Structured planner/replanner schema.**  
The active schema requires: `task`, `subgoal`, `target_object`, `skill`, `success_check`, `fallback` (with optional `reasoning`, `confidence`).

**Why schema consistency matters.**  
Verifier routing, executor dispatch, logging, and metric computation all depend on stable keys and canonical skill vocabulary.

**Parser/repair/validation flow (implemented).**
1. Generate JSON-like output.
2. Extract or partially recover JSON fields when possible.
3. Sanitize unknown keys.
4. Apply targeted repair (for example infer missing `success_check` in constrained cases).
5. Validate via planner contract and canonical skill checks.
6. If invalid, record parse error kind and fallback to rule path.
7. If valid, apply semantic acceptance checks before execution.

**Train/inference consistency.**  
Both training/eval packaging and runtime replanning enforce the same core planner field contract.

---

## 8) Experimental Setup

### Mainline quantitative setup

- Source: `results/eval/planner_base_vs_tuned/metrics.json`
- Sample count: `n=73`
- Comparison: stable baseline planner vs tuned planner (same proxy metric definitions)
- Metrics reported: format compliance, tool-use accuracy, target-match rate, strict task proxy

### Tiny 3-case qualitative setup (fixed side-by-side)

- backend=`calvin_debug_real`
- calvin_debug_batch=`grouped_sequence`
- episodes=`3`
- seed=`42`
- verifier_mode=`verifier_plus_replan`
- replanner_mode=`hybrid`
- Run IDs:
  - baseline anchor: `hybrid_calvin_debug_real_aligned_20260331T103029Z`
  - VL-3B rerun: `hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`
  - VL-7B rerun: `hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`

### Evidence hierarchy used in this README

1. **Mainline quantitative evidence**: base vs tuned table (`n=73`).
2. **Tiny qualitative evidence**: fixed 3-case side-by-side hybrid comparison.
3. **Engineering evidence**: run manifests, config snapshots, parser/audit/failure-taxonomy logs.
4. **Not claimed**: benchmark significance or leaderboard-level generalization.

---

## 9) Main Results

### A) Main quantitative comparison (primary evidence)

Source table: `docs/final_report_assets/tables/current_main_results_table.md`

| Track | Format compliance | Tool-use accuracy | Target-match rate | Strict task proxy |
|------|---:|---:|---:|---:|
| Stable baseline | 1.000 | 0.082 | 0.329 | 0.068 |
| Tuned mainline (LoRA 3B minimal) | 1.000 | 0.219 | 0.479 | 0.205 |

Interpretation: tuned improves structured action/target correctness proxies while keeping format compliance unchanged.

### B) Tiny 3-case side-by-side (secondary qualitative evidence)

Source summary: `docs/final_report_assets/case_studies/tiny_3case_qualitative_summary.md`

- stable baseline accepted revised plans = **0/3**
- VL-3B = **3/3**
- VL-7B = **2/3**

Interpretation: VL-3B is currently the strongest **secondary qualitative comparison track** on this tiny controlled set. VL-7B is runnable and partially successful, but it does **not** outperform VL-3B on this tiny set.

Although the fixed 3-case comparison is not statistically significant, it is still useful for diagnosing grounding quality before semantic rejection and for comparing secondary replanner tracks under a controlled setting.

---

## 10) Failure Analysis and What Improved

Observed improvements and shifts in failure profile:

- **Parser repair evidence**: malformed or partial generations can be recovered/normalized in the replan pipeline before final validation.
- **Semantic acceptance gate**: schema-valid but semantically mismatched plans are rejected early with explicit reasons.
- **Refined taxonomy**: both step-level verifier taxonomy and episode-level hybrid failure labels are encoded for reporting.
- **Repeated-no-effect guard**: repeated ineffective retries are explicitly detected and terminated with auditable labels.
- **Failure shift**: compared with earlier parse/format issues, current tiny-run terminal failures are dominated by execution-side no-effect exhaustion (`repeated_no_effect_fallback_exhausted`).

---

## 11) Honest Limitations

- Tiny 3-case comparison is diagnostic only; it is not a large-scale benchmark.
- VL-3B is a secondary qualitative track, not a replacement for the stable baseline narrative.
- VL-7B is not claimed to be better than VL-3B.
- Remaining failures are still heavily execution-side/no-effect in current loop settings.
- No official CALVIN/RLBench leaderboard or broad generalization claim is made.
- RLBench full simulator path is not currently available in this machine snapshot (fixture bridge is used for cognition-layer smoke).

---

## 12) Repository Guide for Report Writing

Use these files directly when drafting the final Assignment 3 report:

| Report need | Recommended artifact(s) |
|-------------|-------------------------|
| Main quantitative table | `docs/final_report_assets/tables/current_main_results_table.md` |
| Tiny qualitative side-by-side | `docs/final_report_assets/case_studies/tiny_3case_qualitative_summary.md` |
| Hybrid case studies | `docs/failure_cases/hybrid_replanner_cases.md` |
| Copy-ready result paragraphs | `docs/final_report_assets/assignment3_report_ready_text.md` |
| Full project snapshot (machine-readable) | `results/reports/latest_project_report.json` |
| Dashboard status narrative | `results/reports/latest_project_dashboard.md` |
| Hybrid batch history | `docs/replanner_hybrid_results.md` |
| E2 cross-backend context | `docs/tables/e2_ablation_mock_vs_calvin_fixture_vs_calvin_debug_real.md` |

---

## 13) Reproducibility / Key Artifact Paths

- Planner tuning run: `results/checkpoints/planner_sft_3b_minimal/run_latest/`
- Main base-vs-tuned metrics: `results/eval/planner_base_vs_tuned/metrics.json`
- Tiny baseline anchor run: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T103029Z`
- Tiny VL-3B run: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`
- Tiny VL-7B run: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`
- Auto report outputs: `results/reports/latest_project_dashboard.md`, `results/reports/latest_project_report.json`

---

## 14) Practical Repo Usage (still a real README)

```bash
bash scripts/setup_env.sh
conda activate embodied-scene-agent
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
pip install -e ".[train]"

# smoke and tests
bash scripts/run_smoke_v0.sh
bash scripts/run_calvin_dev_smoke.sh
bash scripts/run_calvin_minimal_loop_smoke.sh
pytest -q

# refresh report packaging
python -m embodied_scene_agent.reporting.make_project_report
bash scripts/build_final_report_assets.sh
```

---

## 15) Suggested Report Outline Mapping (README -> Assignment 3 PDF report)

| README section | Suggested report section |
|----------------|--------------------------|
| Research Topic / Problem Statement | Research Topic |
| Task Formulation | Experiment Design (task definition + success criteria) |
| Why this fits Assignment 3 | Research Topic + Experiment Design motivation |
| Model and Training Setup | Code Implementation (model/training setup) |
| Agent-Oriented Components / Tool-like Interfaces | Code Implementation (system modules/interfaces) |
| Data Construction / Supervision Design | Experiment Design (data/supervision) |
| Prompt / Structured Output Design | Code Implementation (prompt/schema/validation pipeline) |
| Experimental Setup | Experiment Design (protocol + evidence hierarchy) |
| Main Results | Result Analysis |
| Failure Analysis and What Improved | Result Analysis |
| Honest Limitations | Conclusion (limitations and scope) |
| Repository Guide for Report Writing + Reproducibility Paths | Appendix / reproducibility references |

This README is intentionally structured so each section can be expanded into a full report subsection with minimal rewriting.
