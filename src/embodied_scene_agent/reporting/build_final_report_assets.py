"""One-shot final report asset pack: docs/final_report_assets/ + results/final_report_assets/."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from embodied_scene_agent.reporting.headline_facts import (
    render_readme_unified_markdown_table,
    unified_headline_facts,
)
from embodied_scene_agent.reporting.make_project_report import build_report_payload
from embodied_scene_agent.utils.paths import repo_root

README_MARKERS = (
    "<!-- ESA_UNIFIED_HEADLINES_BEGIN -->",
    "<!-- ESA_UNIFIED_HEADLINES_END -->",
)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(root: Path, p: str | Path | None) -> str:
    if p is None:
        return ""
    pp = Path(p)
    if not pp.is_absolute():
        return str(pp).replace("\\", "/")
    try:
        return str(pp.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(pp)


def _ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fmt_num(x: Any) -> str:
    if isinstance(x, float):
        return f"{x:.4f}".rstrip("0").rstrip(".")
    return repr(x)


def build_main_results_table(root: Path, payload: dict[str, Any]) -> str:
    eval_m = payload.get("eval_metrics_proxy") or {}
    train = payload.get("train_run_meta") or {}
    ps = payload.get("project_status_snapshot") or {}
    e2 = payload.get("e2_ablation_snapshot") or {}
    hy = payload.get("hybrid_replanner_status") or {}
    evb = (hy.get("eval_batch") or {}) if isinstance(hy, dict) else {}
    mh = evb.get("metrics_headline") or {}

    rows: list[tuple[str, str, str, str]] = []

    def add(cat: str, metric: str, value: str, artifact: str) -> None:
        rows.append((cat, metric, value, artifact))

    add(
        "Planner SFT (3B minimal)",
        "checkpoint + run_meta",
        "see run_meta.json",
        _rel(root, payload.get("experiment_metadata", {}).get("planner_sft_checkpoint_dir")),
    )
    if train:
        add("Planner SFT", "notes", str(train.get("notes", ""))[:80], _rel(root, train.get("path")))
    if eval_m:
        add(
            "Base vs tuned (JSONL proxy)",
            "primary metric (file)",
            str(list(eval_m.keys())[:3]),
            "results/eval/planner_base_vs_tuned/metrics.json",
        )
    for be_key, label in (
        ("e2_on_mock", "E2 mock symbolic"),
        ("e2_on_calvin_fixture", "E2 CALVIN fixture"),
        ("e2_on_calvin_debug_real", "E2 CALVIN debug real-data (latest any batch)"),
        ("e2_on_calvin_debug_real_aligned", "E2 CALVIN debug grouped_sequence batch"),
        ("e2_on_calvin_debug_same_task", "E2 CALVIN debug same_task_subset batch"),
    ):
        block = (e2.get(be_key) or {})
        if block.get("status") != "available":
            add(label, "status", block.get("status", "n/a"), _rel(root, block.get("path")))
            continue
        modes = block.get("modes") or {}
        vpr = modes.get("verifier_plus_replan") or {}
        add(
            label,
            "task_completion (verifier_plus_replan)",
            _fmt_num(vpr.get("task_completion_rate")),
            _rel(root, block.get("latest_dir")) + "/metrics.json",
        )
    hy_latest = (evb.get("latest_dir") or "") if evb else ""
    add(
        "Hybrid replanner batch",
        "parse / validated / repair rates",
        f"{mh}",
        (_rel(root, hy_latest) + "/metrics.json") if hy_latest else "results/experiments/hybrid_replanner_eval/",
    )
    evb_dbg = (hy.get("eval_batch_calvin_debug_real") or {}) if isinstance(hy, dict) else {}
    mh_dbg = evb_dbg.get("metrics_headline") or {}
    hy_dbg_latest = (evb_dbg.get("latest_dir") or "") if evb_dbg else ""
    add(
        "Hybrid replanner (CALVIN debug real)",
        "parse / validated / repair rates",
        f"{mh_dbg}",
        (_rel(root, hy_dbg_latest) + "/metrics.json") if hy_dbg_latest else "results/experiments/hybrid_replanner_eval/",
    )
    add(
        "CALVIN debug planner SFT export",
        "row counts + lineage",
        "see stats md",
        "docs/calvin_debug_real_data_stats.md",
    )
    add(
        "RLBench bridge",
        "deepest_reached_stage",
        str(ps.get("rlbench_deepest_reached_stage")),
        "results/rlbench_dev_smoke.json; results/rlbench_stack_diagnosis.json",
    )

    lines = [
        "# Current main results (auto)",
        "",
        "_All numbers trace to `results/` or `docs/` paths — not official leaderboards._",
        "",
        "| Category | Metric | Value | Artifact |",
        "|----------|--------|-------|----------|",
    ]
    for cat, metric, value, art in rows:
        lines.append(f"| {cat} | {metric} | {value} | `{art}` |")
    lines.append("")
    return "\n".join(lines)


def build_benchmark_coverage_table() -> str:
    return "\n".join(
        [
            "# Benchmark coverage (honest scope)",
            "",
            "| Benchmark / surface | Status | Evidence class | Notes |",
            "|---------------------|--------|----------------|-------|",
            "| CALVIN official leaderboard | **future_only** | — | Teacher-state + minimal loop exist; no claimed rank. |",
            "| CALVIN-shaped **fixture** E2 | **fixture** | `results/experiments/e2_ablation/e2_calvin_fixture_*` | Adapter reality stress; not leaderboard. |",
            "| CALVIN **official debug** npz (vector teacher) | **real (subset)** | `e2_calvin_debug_real_*`, `hybrid_calvin_debug_real_*` | Official debug zip only; not D/ABC/ABCD; not leaderboard. |",
            "| RLBench official sim | **blocked** / **future_only** | `results/rlbench_stack_diagnosis.json` | `import_fail` on dev path; fixture bridge **real**. |",
            "| RLBench cognition bridge | **smoke** / **real** (fixture) | `results/rlbench_dev_smoke.json` | memory_bridge + planner_smoke on fixture. |",
            "| VLABench | **future_only** | `docs/vlabench_plan.md` | Planning doc only. |",
            "",
        ]
    )


def build_system_status_table(payload: dict[str, Any]) -> str:
    ps = payload.get("project_status_snapshot") or {}
    rows = [
        ("Scene memory + contracts", "ready", "docs/scene_memory_contract_v2.md"),
        ("Planner output contract", "ready", "src/embodied_scene_agent/planner/planner_output_contract.py"),
        ("Verifier + taxonomy", "ready", "docs/failure_taxonomy.md"),
        ("Replanner (rule + hybrid LLM)", "ready", "docs/replanner_design_v2.md"),
        ("Episode log schema", "ready", "docs/episode_log_schema.md"),
        ("v0 loop + CALVIN minimal loop", "ready", "src/embodied_scene_agent/pipeline/"),
        ("Auto project report", "ready", "results/reports/latest_project_report.md"),
        ("E2 ablation runners", "ready", "scripts/run_ablation_e2*.sh"),
        ("Hybrid replanner eval", "ready", "scripts/run_hybrid_replanner_eval.sh"),
        ("CALVIN debug → planner JSONL", "ready", "scripts/build_calvin_debug_planner_data.sh"),
        ("RLBench stack diagnosis", "ready", "scripts/diagnose_rlbench_stack.sh"),
        ("A100 7B production training", "future_only", "configs/experiment/a100_final.yaml"),
        ("Official benchmark scores", "future_only", "—"),
    ]
    lines = [
        "# System status (module-level)",
        "",
        f"_Generated: `{datetime.now(timezone.utc).isoformat()}`_",
        "",
        "| Module / capability | Ready state | Pointer |",
        "|---------------------|-------------|---------|",
    ]
    for name, st, ptr in rows:
        lines.append(f"| {name} | **{st}** | `{ptr}` |")
    lines.extend(
        [
            "",
            f"- RLBench deepest stage (from snapshot): `{ps.get('rlbench_deepest_reached_stage')}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_report_outline_final(root: Path, payload: dict[str, Any], facts: dict[str, Any]) -> str:
    rel = lambda p: _rel(root, p)  # noqa: E731
    sections = [
        (
            "1. Title & Positioning",
            [
                "**Evidence:** `README.md`, `docs/EmbodiedSceneAgent_Project_Blueprint_CheCheng.docx` (blueprint), "
                "`docs/final_report_assets/one_page_project_brief.md`.",
                "**Strongest claim (accurate):** Object-level 3D scene memory as the **cognition layer** for "
                "high-level planning with verifier + replanner — **not** an end-to-end low-level policy.",
                "**Boundary:** Do not sell as VLA replacement or official benchmark winner.",
            ],
        ),
        (
            "2. Motivation & Core Claim",
            [
                "**Evidence:** README Motivation; `docs/scene_memory_contract_v2.md`; failure taxonomy.",
                "**Strongest:** Explicit memory improves checkability of subgoals and enables structured recovery.",
                "**Gap:** Large-scale human study / user trust metrics — not in repo.",
            ],
        ),
        (
            "3. System Architecture",
            [
                "**Evidence:** `docs/figures/architecture_v2.svg` → copied as `docs/final_report_assets/figures/architecture_final.svg`; "
                "`docs/final_report_assets/figures/planner_verifier_replanner_loop.svg`.",
                "**Strongest:** Six-stage loop implemented in `src/embodied_scene_agent/pipeline/`.",
                "**Gap:** A100-scale deployment diagram — template only.",
            ],
        ),
        (
            "4. Scene Memory Design",
            [
                "**Evidence:** `docs/scene_memory_contract_v2.md`; builder tests under `tests/`.",
                "**Strongest:** Teacher-state bootstrap is a **deliberate** engineering choice for reproducible cognition I/O.",
                "**Gap:** Predicted vs teacher-only memory ablation at scale — future.",
            ],
        ),
        (
            "5. Planner / Verifier / Replanner",
            [
                "**Evidence:** `planner_output_contract.py`; `docs/failure_taxonomy.md`; `docs/replanner_design_v2.md`; "
                "`step_log['replan_audit']`.",
                "**Strongest:** Hybrid replanner batch shows JSON contract path + audit (`results/experiments/hybrid_replanner_eval/`).",
                "**Gap:** Not a massive LLM replan benchmark.",
            ],
        ),
        (
            "6. Training Data Construction",
            [
                "**Evidence:** `docs/planner_data_stats.md`; `data/` layout; SFT checkpoint `results/checkpoints/planner_sft_3b_minimal/`.",
                "**Strongest:** Real 3B LoRA training artifact exists.",
                "**Gap:** Full rollout dataset at 7B scale — future_only.",
            ],
        ),
        (
            "7. Experimental Settings",
            [
                "**Evidence:** `configs/`; experiment scripts in `scripts/`; `environment.yml`.",
                "**Strongest:** Repro commands documented in `docs/final_report_assets/reproducibility.md`.",
                "**Gap:** Container image — not shipped.",
            ],
        ),
        (
            "8. Main Results",
            [
                "**Evidence:** `docs/final_report_assets/tables/current_main_results_table.md`; "
                f"`{rel('results/reports/latest_project_report.json')}`.",
                "**Strongest:** JSONL proxy + E2 two-layer ablation + hybrid batch + RLBench diagnosis JSON.",
                "**Gap:** Official leaderboard rows — explicitly **not** claimed.",
            ],
        ),
        (
            "9. E2 Ablation",
            [
                "**Evidence:** `results/experiments/e2_ablation/`; `docs/tables/e2_ablation_mock_vs_calvin_fixture.md`; "
                "`docs/failure_cases/e2_ablation_cases.md`.",
                f"**Strongest:** {facts.get('e2_best_story', {}).get('one_line', '')}",
                "**Gap:** E2 is symbolic + fixture — not CALVIN challenge split.",
            ],
        ),
        (
            "10. Hybrid Replanner Analysis",
            [
                "**Evidence:** `docs/replanner_hybrid_results.md`; latest eval dir under `results/experiments/hybrid_replanner_eval/`.",
                "**Strongest:** "
                + json.dumps(facts.get("strongest_hybrid_result", {}).get("metrics_headline") or {}, ensure_ascii=False),
                "**Gap:** `parse_error_kind_counts` empty in latest batch = **high success**, not proof of zero failures forever.",
            ],
        ),
        (
            "11. RLBench Bridge Status",
            [
                "**Evidence:** `results/rlbench_stack_diagnosis.json`; `results/rlbench_dev_smoke.json`; `docs/rlbench_install_log.md`.",
                f"**Strongest stage reached:** `{facts.get('rlbench_deepest_stage')}`; fixture memory bridge works.",
                "**Gap:** Real `sim_reset` — blocked at import / CoppeliaSim stack on current machine.",
            ],
        ),
        (
            "12. Failure Analysis & Limitations",
            [
                "**Evidence:** `docs/failure_taxonomy.md`; `docs/final_report_assets/limitations.md`; case studies folder.",
                "**Strongest:** Taxonomy + logged verifier failures + curated cases.",
                "**Gap:** Real-robot failure videos — not in asset pack.",
            ],
        ),
        (
            "13. Reproducibility & Engineering Notes",
            [
                "**Evidence:** `docs/final_report_assets/reproducibility.md`; `scripts/build_final_report_assets.sh`.",
                "**Strongest:** Single-command report regen + conda-resolved scripts.",
                "**Gap:** Full OS-level CoppeliaSim install — user-side.",
            ],
        ),
        (
            "14. Future Directions",
            [
                "**Evidence:** `configs/experiment/a100_final.yaml`; `docs/vlabench_plan.md`.",
                "**Strongest:** Clear staged roadmap without pretending completion.",
                "**Gap:** A100 7B runs, VLABench harness, official benchmarks — **future_only**.",
            ],
        ),
    ]
    lines = [
        "# Final report outline (blueprint-aligned)",
        "",
        f"_Generated: `{datetime.now(timezone.utc).isoformat()}`_ · Source sketch: `docs/report_outline.md`",
        "",
        "Each section lists: **Evidence paths** · **Strongest defensible statement** · **Explicit boundary / gap**.",
        "",
    ]
    for title, bullets in sections:
        lines.append(f"## {title}")
        lines.append("")
        for b in bullets:
            lines.append(f"- {b}")
        lines.append("")
    return "\n".join(lines)


def write_limitations_md(facts: dict[str, Any]) -> str:
    h = facts.get("strongest_hybrid_result") or {}
    return "\n".join(
        [
            "# Limitations (copy-paste ready)",
            "",
            "This file is **honest scope** for final reports, posters, and advisor email — **do not soften**.",
            "",
            "## RLBench",
            "",
            "- **Real sim `sim_reset` is not demonstrated** on the reference dev machine: deepest stage is "
            f"`{facts.get('rlbench_deepest_stage')}` (see `results/rlbench_stack_diagnosis.json`).",
            "- **Fixture → SceneMemory → planner** smoke **is** real evidence for the cognition adapter path.",
            "",
            "## Benchmarks",
            "",
            "- **No official CALVIN / RLBench leaderboard numbers** are claimed.",
            "- **E2** results include **mock**, **CALVIN fixture**, and **CALVIN official debug npz (vector teacher)** batches — "
            "wiring + real-vector evidence, **not** benchmark rank.",
            "",
            "## Hybrid LLM replanner",
            "",
            "- Latest **mock** batch headline (may omit skill counters): "
            + json.dumps(h.get("metrics_headline") or {}, ensure_ascii=False)
            + ".",
            "- CALVIN debug hybrid eval also records **`unknown_skill_rate`**, **`invalid_skill_count`**, "
            "**`alias_normalization_count`** under `results/experiments/hybrid_replanner_eval/*/metrics.json` "
            "(schema tightening; not a claim of semantic mastery).",
            "- **`parse_error_kind_counts` empty** only means **that run** had no counted parse-error kinds — not a general guarantee.",
            "",
            "## Training / scale",
            "",
            "- **A100 / 7B / full VLABench harness**: **future_only** (templates and docs exist; no production claim).",
            "",
            "## Teacher-state bootstrap",
            "",
            "- Using teacher-state / fixtures is a **deliberate reproducibility choice**, not claimed as self-supervised "
            "perception superiority.",
            "",
        ]
    )


def write_reproducibility_md(root: Path) -> str:
    return "\n".join(
        [
            "# Reproducibility & engineering notes",
            "",
            "## Regenerate canonical snapshots",
            "",
            "```bash",
            "bash scripts/build_final_report_assets.sh",
            "```",
            "",
            "This runs `make_project_report` then materializes `docs/final_report_assets/` and `results/final_report_assets/`.",
            "",
            "## Individual pipelines",
            "",
            "| Goal | Command |",
            "|------|---------|",
            "| Project JSON + dashboard | `python -m embodied_scene_agent.reporting.make_project_report` |",
            "| E2 mock | `bash scripts/run_ablation_e2.sh` |",
            "| E2 CALVIN fixture | `bash scripts/run_ablation_e2_calvin_fixture.sh` |",
            "| E2 CALVIN debug real | `bash scripts/run_ablation_e2_calvin_debug_real.sh` |",
            "| Hybrid batch | `bash scripts/run_hybrid_replanner_eval.sh` |",
            "| Hybrid CALVIN debug | `bash scripts/run_hybrid_replanner_eval_calvin_debug.sh` |",
            "| CALVIN debug planner JSONL | `bash scripts/build_calvin_debug_planner_data.sh` |",
            "| RLBench smoke | `bash scripts/run_rlbench_dev_smoke.sh` |",
            "| RLBench diagnosis | `bash scripts/diagnose_rlbench_stack.sh` |",
            "",
            "## Environment",
            "",
            "- Conda env from `environment.yml` (see `scripts/conda_env.sh`).",
            "- Repo root: the directory containing `pyproject.toml` (clone path on your machine / A100).",
            "",
        ]
    )


def write_appendix_notes_md() -> str:
    return "\n".join(
        [
            "# Appendix notes",
            "",
            "- **Blueprint:** `docs/EmbodiedSceneAgent_Project_Blueprint_CheCheng.docx` (authoritative design narrative).",
            "- **Contracts:** `docs/scene_memory_contract_v2.md`, `docs/episode_log_schema.md`, `docs/planner_output_contract` (code).",
            "- **Narrative audit:** `docs/narrative_consistency_audit.md`.",
            "- **Evidence audit:** `docs/evidence_consistency_audit.md` (regenerated partially by build script).",
            "",
        ]
    )


def write_executive_summary(facts: dict[str, Any]) -> str:
    sr = facts.get("strongest_real_result") or {}
    hh = (facts.get("strongest_hybrid_result") or {}).get("metrics_headline") or {}
    return "\n".join(
        [
            "# Executive summary (≤1 page)",
            "",
            "## What shipped",
            "",
            "A **3D object-level scene memory**-centered **high-level cognition loop** (planner → skills → verifier → replanner) "
            "with **logged audits**, **real** small-model training artifacts, and **repeatable** eval scripts on mock / fixture / "
            "proxy metrics.",
            "",
            "## Strongest measurable evidence (today)",
            "",
            f"- **Planner proxy:** `{sr.get('path')}` — {sr.get('note')}",
            f"- **Hybrid replanner batch:** parse={hh.get('replan_parse_success_rate')}, validated={hh.get('validated_revision_rate')}, "
            f"repair={hh.get('repair_success_rate')}.",
            f"- **E2 story:** {facts.get('e2_best_story', {}).get('one_line')}",
            f"- **CALVIN debug real-data E2:** {facts.get('e2_best_story', {}).get('calvin_debug_real_note')}",
            f"- **Hybrid (CALVIN debug batch):** {facts.get('hybrid_calvin_debug_real_headline')}",
            f"- **RLBench:** deepest stage `{facts.get('rlbench_deepest_stage')}`; fixture cognition bridge still valid.",
            "",
            "## What we explicitly do **not** claim",
            "",
            "- Official robot learning leaderboard ranks.",
            "- End-to-end continuous control policy.",
            "- Completed A100 7B production training or VLABench stress harness.",
            "",
            "## Why it still matters",
            "",
            "The repo demonstrates **contract-first embodied cognition engineering**: memory schema, planner JSON contract, "
            "verifier taxonomy, and hybrid replan auditing — a reusable substrate for future sim + benchmark scaling.",
            "",
        ]
    )


def write_abstract_candidates(facts: dict[str, Any]) -> str:
    hh = (facts.get("strongest_hybrid_result") or {}).get("metrics_headline") or {}
    return "\n".join(
        [
            "# Abstract / blurb candidates",
            "",
            "## 1) Course assignment style",
            "",
            "We implement a six-stage embodied **cognition layer** around **object-centric 3D scene memory**, with structured "
            "planning, verification, and hybrid rule/LLM replanning. Evaluation uses **in-repo** mock, CALVIN-shaped fixtures, "
            "and **official CALVIN debug** vector-backed batches plus JSONL proxy metrics; **we do not claim official benchmark scores**. "
            "RLBench integration stops at **import/fixture** "
            "evidence on our dev path; A100-scale training remains **future work**.",
            "",
            "## 2) Research project style",
            "",
            "This project studies how **explicit 3D relational memory** supports **checkable high-level plans** and **audited "
            "recovery** under verifier feedback. We provide contracts (memory, planner output, episode logs), a hybrid replanner "
            "with JSON validation, and ablations separating **no verifier / verifier-only / verifier+replan** on symbolic and "
            "adapter-shaped fixtures. **Scope is cognition-layer engineering**; large-scale sim + leaderboard evaluation is **out "
            "of scope** for the current artifact snapshot.",
            "",
            "## 3) GitHub / project page style",
            "",
            "**EmbodiedSceneAgent** — memory-driven high-level planning loop with verifier + replanner. "
            f"Latest hybrid batch: parse `{hh.get('replan_parse_success_rate')}`, repair `{hh.get('repair_success_rate')}`. "
            "E2 ablations on **mock + CALVIN fixture + CALVIN debug npz**; RLBench **fixture bridge**; official benchmarks **not** reported. "
            "See `docs/final_report_assets/one_page_project_brief.md`.",
            "",
        ]
    )


def write_one_page_brief(facts: dict[str, Any]) -> str:
    hh = (facts.get("strongest_hybrid_result") or {}).get("metrics_headline") or {}
    return "\n".join(
        [
            "# One-page project brief",
            "",
            "## 1. What this project is",
            "",
            "A **blueprint-aligned** embodied **cognition layer**: Scene Memory → Planner → (symbolic) Skills → Verifier → Replanner, "
            "with structured logging — **not** a monolithic vision-language-action policy.",
            "",
            "## 2. Why it matters",
            "",
            "Makes **grounding, legality, and failure recovery** inspectable via shared contracts instead of hiding state in weights.",
            "",
            "## 3. What is already real",
            "",
            "- Contracts + taxonomy + episode schema (docs + tests).",
            "- 3B planner SFT checkpoint + JSONL **proxy** eval.",
            "- E2 ablations (**mock** + **CALVIN fixture** + **CALVIN official debug vectors**).",
            "- Hybrid replanner **batch** with audit metrics.",
            "- RLBench **diagnosis + fixture** cognition bridge.",
            "",
            "## 4. Best current evidence",
            "",
            json.dumps(
                {
                    "strongest_artifact": facts.get("strongest_real_result"),
                    "hybrid_headline": hh,
                    "rlbench_stage": facts.get("rlbench_deepest_stage"),
                },
                indent=2,
                ensure_ascii=False,
            ),
            "",
            "## 5. What is not done yet",
            "",
            "- Official CALVIN/RLBench leaderboard runs.",
            "- RLBench `sim_reset` on this machine (import/CoppeliaSim stack).",
            "- A100 7B training, VLABench harness execution.",
            "",
            "## 6. Why it is still a strong project",
            "",
            "End-to-end **engineering proof** of a reusable cognition interface with **honest** evaluation boundaries — the right "
            "foundation before expensive sim + GPU scale-up.",
            "",
        ]
    )


def write_advisor_brief(facts: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Advisor brief (research framing)",
            "",
            "## Claim",
            "",
            "Explicit **3D object-level memory** as the interface for **verifiable** high-level robotics reasoning and recovery.",
            "",
            "## Design",
            "",
            "- Contracts reduce ambiguity between perception adapters and planning.",
            "- Verifier taxonomy anchors replan strategies (rules + optional LLM JSON).",
            "",
            "## Evidence status",
            "",
            f"- Ablations: {facts.get('e2_best_story', {}).get('one_line')}",
            f"- Hybrid metrics: {json.dumps((facts.get('strongest_hybrid_result') or {}).get('metrics_headline') or {}, ensure_ascii=False)}",
            f"- RLBench: {facts.get('rlbench_deepest_stage')} (fixture bridge documented).",
            "",
            "## Next milestones (honest)",
            "",
            "1. CoppeliaSim-backed RLBench import → env_create → reset.",
            "2. Frozen CALVIN eval split (if policy allows) — separate from fixtures.",
            "3. Optional: richer hybrid stress batches to populate parse breakdown.",
            "",
        ]
    )


def write_interview_brief(facts: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Interview brief (engineering + systems)",
            "",
            "## Architecture story (60s)",
            "",
            "We built a **typed loop** around scene memory with **Pydantic-level** planner outputs and **audited** replans — easy to "
            "extend with new env adapters because the contracts stay fixed.",
            "",
            "## Hard parts solved",
            "",
            "- Unified episode log schema across mock + CALVIN minimal loop.",
            "- Hybrid replanner: LLM JSON must pass `planner_output_contract` or fall back with explicit audit reason.",
            "- RLBench: layered diagnostics so failures are **machine-readable** (import vs sim vs reset).",
            "",
            "## Metrics you can cite without over-claiming",
            "",
            "```json",
            json.dumps(
                {
                    "hybrid_batch": (facts.get("strongest_hybrid_result") or {}).get("metrics_headline"),
                    "rlbench_deepest": facts.get("rlbench_deepest_stage"),
                },
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Future scaling",
            "",
            "Swap teacher-state adapters for predicted memory; keep contracts; add official eval harnesses — **future_only** today.",
            "",
        ]
    )


def write_artifact_index_md(root: Path, payload: dict[str, Any]) -> str:
    items: list[tuple[str, str]] = [
        ("`docs/final_report_assets/one_page_project_brief.md`", "Fastest narrative for visitors / mentors."),
        ("`docs/final_report_assets/report_outline_final.md`", "Full section-by-section evidence vs gaps."),
        ("`results/reports/latest_project_report.json`", "Machine-readable single source for dashboards."),
        ("`docs/final_report_assets/tables/current_main_results_table.md`", "Main quantitative pointers."),
        ("`docs/final_report_assets/case_studies/`", "Report-ready case templates."),
        ("`docs/final_report_assets/limitations.md`", "Non-negotiable honest boundaries."),
        ("`docs/narrative_consistency_audit.md`", "Checklist: cognition layer vs policy vs benchmarks."),
        ("`docs/evidence_consistency_audit.md`", "Paths + consistency checks."),
        ("`docs/figures/architecture_v2.svg`", "Primary architecture figure."),
        ("`results/demos/e2_ablation_cases/`", "Stable E2 demo JSON + selection meta."),
        ("`docs/calvin_debug_dataset_audit.md`", "Official debug npz layout + honest gaps."),
        ("`docs/calvin_debug_real_data_stats.md`", "Planner export from debug vectors (counts + lineage)."),
        ("`docs/tables/e2_ablation_mock_vs_calvin_fixture_vs_calvin_debug_real.md`", "Three-way E2 comparison table."),
    ]
    lines = [
        "# Artifact index (read order)",
        "",
        "_Repo: this git clone (the directory that contains `pyproject.toml`)._",
        "",
        "| Priority | Path | Why |",
        "|----------|------|-----|",
    ]
    for i, (path_s, why) in enumerate(items, 1):
        lines.append(f"| {i} | {path_s} | {why} |")
    lines.extend(["", "## Auto bundle", "", "- Run `bash scripts/build_final_report_assets.sh` after new experiments.", ""])
    return "\n".join(lines)


def _minimal_svg(title: str, lines: list[str], w: int = 900, h: int = 220) -> str:
    esc = title.replace("&", "&amp;").replace("<", "&lt;")
    tspans = []
    y = 58
    for ln in lines:
        safe = ln.replace("&", "&amp;").replace("<", "&lt;")
        tspans.append(f'<tspan x="20" y="{y}">{safe}</tspan>')
        y += 20
    body = "\n    ".join(tspans)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="100%" height="100%" fill="#fafafa" stroke="#ccc"/>
  <text x="20" y="32" font-family="sans-serif" font-size="17" font-weight="bold" fill="#111">{esc}</text>
  <text font-family="monospace" font-size="12" fill="#333">
    {body}
  </text>
</svg>
"""


def materialize_figures(root: Path, dest: Path) -> None:
    _ensure_dirs(dest)
    arch = root / "docs" / "figures" / "architecture_v2.svg"
    if arch.is_file():
        shutil.copy2(arch, dest / "architecture_final.svg")
    _write(
        dest / "scene_memory_schema_diagram.svg",
        _minimal_svg(
            "Scene memory (conceptual)",
            [
                "Objects: id, class, position, bbox, state_tags",
                "Relations: subject — relation — object",
                "Source: teacher-state / RLBench-like observation → SceneMemoryBuilder",
                "Contract: docs/scene_memory_contract_v2.md",
            ],
            h=260,
        ),
    )
    _write(
        dest / "planner_verifier_replanner_loop.svg",
        _minimal_svg(
            "Closed loop",
            [
                "PlannerOutput (JSON contract) → SkillExecutor",
                "→ StateDiffVerifier → FailureType",
                "→ RuleReplanner / Hybrid LLM (validated JSON) → next step",
            ],
            h=200,
        ),
    )
    _write(
        dest / "benchmark_scope_map.svg",
        _minimal_svg(
            "Benchmark scope",
            [
                "real: proxy JSONL, 3B SFT, hybrid batch, E2 mock, E2 fixture, E2 CALVIN debug npz, hybrid debug batch, RLBench fixture bridge",
                "fixture/smoke: CALVIN minimal loop, RLBench layered smoke",
                "future_only: official leaderboards, A100 7B prod, VLABench harness",
            ],
            h=260,
        ),
    )
    _write(
        dest / "project_roadmap_final.svg",
        _minimal_svg(
            "Roadmap (honest)",
            [
                "Done: contracts, v0 loop, audits, E2+hybrid+RLBench diagnosis assets",
                "Next: CoppeliaSim stack, official eval harnesses",
                "Future: predicted memory, 7B scale, VLABench stress",
            ],
            h=220,
        ),
    )
    _write(
        dest / "hybrid_replanner_status.md",
        "_Generated figure substitute — see `results/experiments/hybrid_replanner_eval/*/metrics.json` after batch run._\n",
    )


def write_e2_summary_figure_md(payload: dict[str, Any]) -> str:
    e2 = payload.get("e2_ablation_snapshot") or {}
    lines = [
        "# E2 ablation summary (markdown figure)",
        "",
        "_No PNG under `results/experiments/e2_ablation/` on this snapshot — table from latest JSON._",
        "",
        "## Mock symbolic",
        "",
        "| mode | task_completion | failure_detected_rate | recovery_success | avg_steps |",
        "|------|----------------:|----------------------:|-----------------:|----------:|",
    ]
    m = (e2.get("e2_on_mock") or {}).get("modes") or {}
    for mode in ("none", "verifier_only", "verifier_plus_replan"):
        s = m.get(mode) or {}
        lines.append(
            f"| `{mode}` | {s.get('task_completion_rate')} | {s.get('failure_detected_rate')} | "
            f"{s.get('recovery_success_rate')} | {s.get('average_steps')} |"
        )
    lines.extend(["", "## CALVIN fixture", "", "| mode | task_completion | failure_detected_rate | recovery_success | avg_steps |", "|------|----------------:|----------------------:|-----------------:|----------:|"])
    c = (e2.get("e2_on_calvin_fixture") or {}).get("modes") or {}
    for mode in ("none", "verifier_only", "verifier_plus_replan"):
        s = c.get(mode) or {}
        lines.append(
            f"| `{mode}` | {s.get('task_completion_rate')} | {s.get('failure_detected_rate')} | "
            f"{s.get('recovery_success_rate')} | {s.get('average_steps')} |"
        )
    lines.extend(
        [
            "",
            "## CALVIN official debug (vector teacher)",
            "",
            "| mode | task_completion | failure_detected_rate | recovery_success | avg_steps |",
            "|------|----------------:|----------------------:|-----------------:|----------:|",
        ]
    )
    d = (e2.get("e2_on_calvin_debug_real") or {}).get("modes") or {}
    for mode in ("none", "verifier_only", "verifier_plus_replan"):
        s = d.get(mode) or {}
        lines.append(
            f"| `{mode}` | {s.get('task_completion_rate')} | {s.get('failure_detected_rate')} | "
            f"{s.get('recovery_success_rate')} | {s.get('average_steps')} |"
        )
    lines.append("")
    return "\n".join(lines)


CASE_TEMPLATE = """# {title}

## Context
{context}

## Input / Setup
{setup}

## Memory Snapshot
{memory}

## Planner Output
{planner}

## Verifier Decision
{verifier}

## Replanner Behavior
{replanner}

## Outcome
{outcome}

## Why this case matters
{why}

## Artifact links
{links}
"""


def _case_from_step_json(data: dict[str, Any], *, title: str, context: str, links: str) -> str:
    st = data.get("step") if isinstance(data.get("step"), dict) else data
    if not isinstance(st, dict):
        st = {}
    mem = st.get("scene_memory_before") or st.get("plan")
    setup_obj = {k: data.get(k) for k in ("episode_meta", "backend", "mode") if data.get(k) is not None}
    return CASE_TEMPLATE.format(
        title=title,
        context=context,
        setup=f"```json\n{json.dumps(setup_obj, indent=2, ensure_ascii=False)[:2000]}\n```",
        memory=f"```json\n{json.dumps(mem, indent=2, ensure_ascii=False)[:3500] if mem else '_n/a_'}\n```",
        planner=f"```json\n{json.dumps(st.get('plan'), indent=2, ensure_ascii=False) if st.get('plan') else '_n/a_'}\n```",
        verifier=f"```json\n{json.dumps(st.get('verification'), indent=2, ensure_ascii=False) if st.get('verification') else '_n/a_'}\n```",
        replanner=f"```json\n{json.dumps(st.get('replan_audit'), indent=2, ensure_ascii=False) if st.get('replan_audit') else '_n/a_'}\n```",
        outcome=json.dumps(data.get("trace_summary") or {}, ensure_ascii=False),
        why="_Demonstrates verifier + replan wiring on symbolic mock; numbers are not official CALVIN._",
        links=links,
    )


def write_case_studies(root: Path, dest: Path) -> None:
    _ensure_dirs(dest)
    demos = root / "results" / "demos"

    def load_case(fname: str) -> dict[str, Any]:
        p = demos / "e2_ablation_cases" / fname
        if not p.is_file():
            return {}
        return _read_json(p) or {}

    e2m = load_case("case3_plus_replan.json")
    if e2m:
        tr = e2m.get("trace") or {}
        steps = tr.get("steps") or []
        step_pick = steps[0] if steps else {}
        for cand in steps:
            if cand.get("replan_audit") or cand.get("replan") is not None:
                step_pick = cand
                break
        wrapped = {
            "backend": e2m.get("backend"),
            "mode": e2m.get("mode"),
            "episode_meta": e2m.get("episode_meta"),
            "step": step_pick,
            "trace_summary": {
                "success": tr.get("success"),
                "replan_count": tr.get("replan_count"),
                "num_steps": len(steps),
            },
        }
        _write(
            dest / "e2_mock_case.md",
            _case_from_step_json(
                wrapped,
                title="E2 mock — verifier + replan",
                context="Symbolic mock grid; **not** official CALVIN.",
                links="`results/demos/e2_ablation_cases/case3_plus_replan.json`, `mock_selection_meta.json`",
            ),
        )
    else:
        _write(
            dest / "e2_mock_case.md",
            "# E2 mock case\n\n_Missing `case3_plus_replan.json` — run `bash scripts/run_ablation_e2.sh`._\n",
        )

    cal = _read_json(demos / "e2_ablation_cases" / "calvin_case_replan_fixes_stuck_verifier_only.json") or {}
    if cal:
        body = "\n\n## Side-by-side\n\n```json\n" + json.dumps(cal, indent=2, ensure_ascii=False)[:8000] + "\n```\n"
        _write(dest / "e2_calvin_fixture_case.md", "# E2 CALVIN fixture case\n" + body)
    else:
        _write(dest / "e2_calvin_fixture_case.md", "# E2 CALVIN fixture case\n\n_Missing calvin case JSON._\n")

    hy_ok = _read_json(demos / "hybrid_replanner_cases" / "case_llm_repair_success.json") or {}
    if hy_ok.get("step"):
        _write(
            dest / "hybrid_success_case.md",
            _case_from_step_json(
                hy_ok,
                title="Hybrid replanner — LLM path success",
                context="Mock v0 episode; latest batch artifact.",
                links="`results/demos/hybrid_replanner_cases/case_llm_repair_success.json`",
            ),
        )
    else:
        _write(dest / "hybrid_success_case.md", "# Hybrid success\n\n_Missing case JSON._\n")

    hy_fb = _read_json(demos / "hybrid_replanner_cases" / "case_parse_fallback.json") or {}
    src_note = ""
    if hy_fb.get("note") and not hy_fb.get("step"):
        src_note = (
            "\n\n> **Source note:** This batch did not hit a parse-failure step; JSON contains explanation only. "
            "For a parse-failure **trace**, use the latest `hybrid_replanner_smoke` run if available.\n"
        )
    _write(
        dest / "hybrid_parse_fallback_case.md",
        "# Hybrid parse / validate fallback\n\n```json\n"
        + json.dumps(hy_fb, indent=2, ensure_ascii=False)
        + "\n```"
        + src_note,
    )

    rb = _read_json(root / "results" / "rlbench_dev_smoke.json") or {}
    _write(
        dest / "rlbench_bridge_case.md",
        "\n".join(
            [
                "# RLBench bridge case (fixture / diagnosis)",
                "",
                "## Layer status (last smoke)",
                "",
                "```json",
                json.dumps(rb.get("layer_status"), indent=2, ensure_ascii=False),
                "```",
                "",
                "## Deepest stage",
                "",
                f"`{rb.get('deepest_reached_stage')}` — {rb.get('blocker_summary', '')}",
                "",
                "## Artifacts",
                "",
                "- `results/rlbench_dev_smoke.json`",
                "- `results/rlbench_stack_diagnosis.json`",
                "- `tests/fixtures/rlbench_observation_like.json`",
                "",
            ]
        ),
    )


def patch_readme_unified_section(readme: Path, facts: dict[str, Any]) -> list[str]:
    """Returns list of issues fixed (empty if no change needed)."""
    if not readme.is_file():
        return [f"README missing: {readme}"]
    text = readme.read_text(encoding="utf-8")
    begin, end = README_MARKERS
    if begin not in text or end not in text:
        return ["README missing ESA_UNIFIED_HEADLINES markers — no auto-patch."]
    inner = render_readme_unified_markdown_table(facts)
    new_block = f"{begin}\n{inner}\n{end}"
    pattern = re.compile(re.escape(begin) + r"[\s\S]*?" + re.escape(end), re.MULTILINE)
    new_text, n = pattern.subn(new_block, text, count=1)
    if n != 1:
        return ["README marker regex failed"]
    readme.write_text(new_text, encoding="utf-8")
    return []


def write_evidence_consistency_audit(
    root: Path,
    payload: dict[str, Any],
    facts: dict[str, Any],
    issues_from_readme: list[str],
) -> str:
    lines = [
        "# Evidence consistency audit",
        "",
        f"_Generated: `{datetime.now(timezone.utc).isoformat()}` (partially automated)_",
        "",
        "## Automated checks",
        "",
    ]
    problems: list[str] = []
    for s in facts.get("strongest_real_results_all") or []:
        p = s.get("path")
        if not p:
            continue
        raw = Path(str(p))
        pp = raw if raw.is_absolute() else root / raw
        if not pp.is_file() and not pp.is_dir():
            problems.append(f"Missing strongest artifact path: `{p}`")
    hy_path = (facts.get("strongest_hybrid_result") or {}).get("case_path")
    if hy_path:
        raw = Path(str(hy_path))
        hp = raw if raw.is_absolute() else root / raw
        if not hp.is_file():
            problems.append(f"Missing hybrid case path: `{hy_path}`")
    rep = root / "results" / "reports" / "latest_project_report.json"
    if not rep.is_file():
        problems.append("Missing `results/reports/latest_project_report.json`")
    if problems:
        lines.append("**Problems:**")
        for pr in problems:
            lines.append(f"- {pr}")
    else:
        lines.append("_All checked strongest artifact paths exist._")

    lines.extend(["", "## README patch status", ""])
    if issues_from_readme:
        for i in issues_from_readme:
            lines.append(f"- {i}")
    else:
        lines.append("_README unified table patched successfully._")

    lines.extend(
        [
            "",
            "## Cross-check: dashboard vs JSON",
            "",
            "The status board (`docs/project_page/status_board.md`) is regenerated by `make_project_report` and should match "
            "`project_status_snapshot` in `latest_project_report.json`. If you edit the board by hand, re-run "
            "`bash scripts/build_final_report_assets.sh`.",
            "",
            "## headline_facts.json",
            "",
            "Canonical derived headlines: `results/final_report_assets/unified_headlines.json`.",
            "",
        ]
    )
    rep_payload = _read_json(root / "results" / "reports" / "latest_project_report.json")
    if rep_payload:
        ps = rep_payload.get("project_status_snapshot") or {}
        hy = rep_payload.get("hybrid_replanner_status") or {}
        h1 = ps.get("hybrid_replanner_batch_headline")
        h2 = (hy.get("eval_batch") or {}).get("metrics_headline")
        lines.extend(["## Internal consistency: hybrid headlines", ""])
        if h1 != h2 and h2 is not None:
            lines.append(
                "- **WARN:** `project_status_snapshot.hybrid_replanner_batch_headline` != `eval_batch.metrics_headline` "
                f"(got `{h1!s}` vs `{h2!s}`)."
            )
        else:
            lines.append("- Hybrid batch headline aligned between snapshot and `hybrid_replanner_status.eval_batch`.")
        lines.append("")
    return "\n".join(lines)


def write_narrative_consistency_audit_md() -> str:
    return "\n".join(
        [
            "# Narrative consistency audit (checklist)",
            "",
            "Use this before submission / advisor send. Tick mentally — **do not** claim unchecked items externally.",
            "",
            "## Positioning",
            "",
            "- [ ] Always describe **3D-memory-driven high-level cognition layer**, not “our robot learns everything end-to-end”.",
            "- [ ] Avoid implying a **continuous low-level policy** is the contribution.",
            "- [ ] **Teacher-state / fixture bootstrap** is framed as **reproducible engineering**, not self-supervised SOTA perception.",
            "",
            "## Benchmarks",
            "",
            "- [ ] **CALVIN**: separate **dev / fixture** work from **official challenge** results.",
            "- [ ] **RLBench**: distinguish **fixture bridge** vs **sim_reset** vs **leaderboard**.",
            "- [ ] **VLABench**: **planning doc / future_only** unless a harness run exists.",
            "",
            "## Evidence classes",
            "",
            "- [ ] Every slide/table labels **real** vs **fixture/smoke** vs **future_only**.",
            "- [ ] **Smoke** is not called a **benchmark score**.",
            "",
            "## Hybrid replanner",
            "",
            "- [ ] If `parse_error_kind_counts` is empty, explain **high success on this batch**, not infinite robustness.",
            "",
            "## Suggested wording bans",
            "",
            "- Avoid: “completed CALVIN benchmark”, “full RLBench integration”, “trained 7B production model”, “VLABench results”.",
            "",
        ]
    )


def run_build(*, root: Path | None = None, skip_readme_patch: bool = False) -> None:
    root = root or repo_root()
    payload = build_report_payload(root)
    facts = unified_headline_facts(payload, root=root)

    doc_out = root / "docs" / "final_report_assets"
    res_out = root / "results" / "final_report_assets"
    fig = doc_out / "figures"
    tbl = doc_out / "tables"
    cs = doc_out / "case_studies"
    _ensure_dirs(doc_out, res_out, fig, tbl, cs)

    manifest: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "paths": [],
    }

    def track(p: Path) -> None:
        manifest["paths"].append(str(p.relative_to(root)))

    # Core markdown
    for name, content in [
        ("report_outline_final.md", write_report_outline_final(root, payload, facts)),
        ("executive_summary.md", write_executive_summary(facts)),
        ("abstract_candidates.md", write_abstract_candidates(facts)),
        ("appendix_notes.md", write_appendix_notes_md()),
        ("limitations.md", write_limitations_md(facts)),
        ("reproducibility.md", write_reproducibility_md(root)),
        ("artifact_index.md", write_artifact_index_md(root, payload)),
        ("one_page_project_brief.md", write_one_page_brief(facts)),
        ("advisor_brief.md", write_advisor_brief(facts)),
        ("interview_brief.md", write_interview_brief(facts)),
    ]:
        p = doc_out / name
        _write(p, content)
        track(p)

    for name, content in [
        ("current_main_results_table.md", build_main_results_table(root, payload)),
        ("benchmark_coverage_table.md", build_benchmark_coverage_table()),
        ("system_status_table.md", build_system_status_table(payload)),
    ]:
        p = tbl / name
        _write(p, content)
        track(p)

    e2fig = fig / "e2_ablation_summary.md"
    _write(e2fig, write_e2_summary_figure_md(payload))
    track(e2fig)

    materialize_figures(root, fig)
    for fn in (
        "architecture_final.svg",
        "scene_memory_schema_diagram.svg",
        "planner_verifier_replanner_loop.svg",
        "benchmark_scope_map.svg",
        "project_roadmap_final.svg",
        "hybrid_replanner_status.md",
    ):
        track(fig / fn)

    write_case_studies(root, cs)
    for fn in (
        "e2_mock_case.md",
        "e2_calvin_fixture_case.md",
        "hybrid_success_case.md",
        "hybrid_parse_fallback_case.md",
        "rlbench_bridge_case.md",
    ):
        track(cs / fn)

    uh_path = res_out / "unified_headlines.json"
    _write(uh_path, json.dumps(facts, indent=2, ensure_ascii=False))
    track(uh_path)

    readme_issues: list[str] = []
    if skip_readme_patch:
        readme_issues.append("Skipped README patch (--skip-readme-patch).")
    else:
        readme_issues = patch_readme_unified_section(root / "README.md", facts)

    nar_path = root / "docs" / "narrative_consistency_audit.md"
    _write(nar_path, write_narrative_consistency_audit_md())

    ev_path = root / "docs" / "evidence_consistency_audit.md"
    _write(ev_path, write_evidence_consistency_audit(root, payload, facts, readme_issues))

    manifest_path = res_out / "manifest.json"
    _write(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"[build_final_report_assets] wrote {doc_out} and {res_out}")
    if readme_issues:
        for x in readme_issues:
            print(f"[build_final_report_assets] note: {x}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build docs/final_report_assets + results/final_report_assets")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--skip-readme-patch",
        action="store_true",
        help="Do not rewrite README unified headlines block.",
    )
    args = parser.parse_args()
    run_build(root=args.root, skip_readme_patch=args.skip_readme_patch)


if __name__ == "__main__":
    main()
