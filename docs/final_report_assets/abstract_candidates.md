# Abstract / blurb candidates

## 1) Course assignment style

We implement a six-stage embodied **cognition layer** around **object-centric 3D scene memory**, with structured planning, verification, and hybrid rule/LLM replanning. Evaluation uses **in-repo** mock, CALVIN-shaped fixtures, and **official CALVIN debug** vector-backed batches plus JSONL proxy metrics; **we do not claim official benchmark scores**. RLBench integration stops at **import/fixture** evidence on our dev path; A100-scale training remains **future work**.

## 2) Research project style

This project studies how **explicit 3D relational memory** supports **checkable high-level plans** and **audited recovery** under verifier feedback. We provide contracts (memory, planner output, episode logs), a hybrid replanner with JSON validation, and ablations separating **no verifier / verifier-only / verifier+replan** on symbolic and adapter-shaped fixtures. **Scope is cognition-layer engineering**; large-scale sim + leaderboard evaluation is **out of scope** for the current artifact snapshot.

## 3) GitHub / project page style

**EmbodiedSceneAgent** — memory-driven high-level planning loop with verifier + replanner. Latest hybrid batch: parse `1.0`, repair `1.0`. E2 ablations on **mock + CALVIN fixture + CALVIN debug npz**; RLBench **fixture bridge**; official benchmarks **not** reported. See `docs/final_report_assets/one_page_project_brief.md`.
