"""Aggregate metrics, taxonomy, RLBench / E2 / hybrid status → report + dashboard."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from embodied_scene_agent.reporting.headline_facts import unified_headline_facts
from embodied_scene_agent.utils.paths import rel_repo_path, repo_root
from embodied_scene_agent.verifier.taxonomy import list_taxonomy_for_report


def _as_rel(root: Path, path: Path | str | None) -> str | None:
    if path is None:
        return None
    return rel_repo_path(root, path)


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_subdir(root: Path) -> Path | None:
    if not root.is_dir():
        return None
    subs = [p for p in root.iterdir() if p.is_dir()]
    if not subs:
        return None
    return max(subs, key=lambda p: p.stat().st_mtime)


def _e2_latest_for_backend(root: Path, backend: str) -> dict:
    base = root / "results" / "experiments" / "e2_ablation"
    if not base.is_dir():
        return {"status": "not_run", "backend": backend, "path": _as_rel(root, base)}
    best: Path | None = None
    best_mtime = -1.0
    for d in base.iterdir():
        if not d.is_dir():
            continue
        mp = d / "metrics.json"
        if not mp.is_file():
            continue
        data = _read_json(mp)
        if not data:
            continue
        b = data.get("backend")
        matches = b == backend or (
            backend == "mock"
            and b is None
            and "calvin" not in d.name.lower()
            and "e2_calvin" not in d.name.lower()
        )
        if matches and mp.stat().st_mtime > best_mtime:
            best_mtime = mp.stat().st_mtime
            best = d
    if best is None:
        return {"status": "not_run", "backend": backend, "path": _as_rel(root, base)}
    m = _read_json(best / "metrics.json")
    return {
        "status": "available",
        "backend": backend,
        "latest_dir": _as_rel(root, best),
        "modes": (m or {}).get("modes", {}),
        "experiment_id": (m or {}).get("experiment_id"),
    }


def _e2_combined_snapshot(root: Path) -> dict:
    return {
        "e2_on_mock": _e2_latest_for_backend(root, "mock"),
        "e2_on_calvin_fixture": _e2_latest_for_backend(root, "calvin_fixture"),
        "e2_on_calvin_debug_real": _e2_latest_for_backend(root, "calvin_debug_real"),
        "e2_on_calvin_debug_real_aligned": _e2_latest_calvin_debug_batch(
            root, "grouped_sequence"
        ),
        "e2_on_calvin_debug_same_task": _e2_latest_calvin_debug_batch(
            root, "same_task_subset"
        ),
    }


def _rlbench_stack_diagnosis_path(root: Path) -> Path:
    return root / "results" / "rlbench_stack_diagnosis.json"


def _rlbench_snapshot(root: Path) -> dict:
    p = root / "results" / "rlbench_dev_smoke.json"
    data = _read_json(p)
    diag = _read_json(_rlbench_stack_diagnosis_path(root))
    deepest = (diag or {}).get("deepest_reached_stage")
    blocker = (diag or {}).get("blocker_summary")
    if not diag and data:
        deepest = data.get("deepest_reached_stage")
        blocker = data.get("blocker_summary")
    if not data:
        return {
            "status": "missing",
            "path": _as_rel(root, p),
            "deepest_reached_stage": deepest,
            "blocker_summary": blocker,
            "stack_diagnosis_path": _as_rel(root, _rlbench_stack_diagnosis_path(root)) if diag else None,
        }
    ls = data.get("layer_status") or {}
    return {
        "status": "ok",
        "path": _as_rel(root, p),
        "import_ok": data.get("import_ok"),
        "bridge_mode": data.get("bridge_mode"),
        "task_name": data.get("task_name"),
        "sim_message_head": str(data.get("sim_message", ""))[:200],
        "layer_status": ls,
        "import_layer": ls.get("import"),
        "simulator_locate_layer": ls.get("simulator_locate"),
        "env_create_layer": ls.get("env_create"),
        "reset_layer": ls.get("reset"),
        "observation_layer": ls.get("observation"),
        "memory_bridge": ls.get("memory_bridge"),
        "planner_smoke": ls.get("planner_smoke"),
        "stages_present": sorted((data.get("stages") or {}).keys()),
        "deepest_reached_stage": deepest,
        "blocker_summary": blocker,
        "stack_diagnosis_path": _as_rel(root, _rlbench_stack_diagnosis_path(root)) if diag else None,
    }


def _hybrid_smoke_snapshot(root: Path) -> dict | None:
    base = root / "results" / "experiments" / "hybrid_replanner_smoke"
    latest = _latest_subdir(base)
    if latest is None:
        return None
    tr = _read_json(latest / "trace_full.json")
    audit = None
    if tr:
        for st in tr.get("steps") or []:
            if st.get("replan_audit"):
                audit = st["replan_audit"]
                break
    fb = _read_json(latest / "fallback_stats.json")
    return {
        "kind": "smoke",
        "latest_dir": _as_rel(root, latest),
        "success": (tr or {}).get("success"),
        "replan_count": (tr or {}).get("replan_count"),
        "first_replan_audit": audit,
        "fallback_stats": fb,
    }


def _hybrid_eval_latest_where(
    root: Path,
    pred: object,
) -> dict | None:
    base = root / "results" / "experiments" / "hybrid_replanner_eval"
    if not base.is_dir():
        return None
    best_mtime = -1.0
    latest: Path | None = None
    for d in base.iterdir():
        if not d.is_dir():
            continue
        mp = d / "metrics.json"
        if not mp.is_file():
            continue
        metrics = _read_json(mp) or {}
        try:
            ok = bool(pred(metrics))
        except Exception:  # noqa: BLE001
            ok = False
        if not ok:
            continue
        mt = mp.stat().st_mtime
        if mt > best_mtime:
            best_mtime = mt
            latest = d
    if latest is None:
        return None
    metrics = _read_json(latest / "metrics.json") or {}
    fb = _read_json(latest / "fallback_stats.json") or {}
    keys = (
        "replan_parse_success_rate",
        "validated_revision_rate",
        "fallback_rate",
        "repair_success_rate",
        "unknown_failure_rate",
        "unknown_skill_rate",
        "alias_normalization_count",
        "invalid_skill_count",
    )
    return {
        "kind": "eval_batch",
        "latest_dir": _as_rel(root, latest),
        "metrics_headline": {k: metrics.get(k) for k in keys},
        "fallback_reason_counts": fb.get("fallback_reason_counts"),
        "fallback_stage_counts": fb.get("fallback_stage_counts"),
        "parse_error_kind_counts": fb.get("parse_error_kind_counts") or {},
        "hybrid_replanner_batch_headline": {k: metrics.get(k) for k in keys},
        "hybrid_parse_error_breakdown": fb.get("parse_error_kind_counts") or {},
        "backend": metrics.get("backend"),
    }


def _hybrid_eval_snapshot(root: Path) -> dict | None:
    """Latest **mock** hybrid eval batch (excludes ``calvin_debug_real`` so order of runs does not flip headlines)."""
    return _hybrid_eval_latest_where(
        root, lambda m: m.get("backend") in (None, "mock")
    )


def _hybrid_eval_snapshot_calvin_debug(root: Path) -> dict | None:
    return _hybrid_eval_latest_where(root, lambda m: m.get("backend") == "calvin_debug_real")


def _hybrid_eval_snapshot_calvin_debug_aligned(root: Path) -> dict | None:
    return _hybrid_eval_latest_where(
        root,
        lambda m: m.get("backend") == "calvin_debug_real"
        and m.get("calvin_debug_batch") == "grouped_sequence",
    )


def _hybrid_eval_snapshot_calvin_debug_same_task(root: Path) -> dict | None:
    return _hybrid_eval_latest_where(
        root,
        lambda m: m.get("backend") == "calvin_debug_real"
        and m.get("calvin_debug_batch") == "same_task_subset",
    )


def _e2_latest_calvin_debug_batch(root: Path, batch: str) -> dict:
    base = root / "results" / "experiments" / "e2_ablation"
    if not base.is_dir():
        return {
            "status": "not_run",
            "backend": "calvin_debug_real",
            "calvin_debug_batch": batch,
            "path": _as_rel(root, base),
        }
    best: Path | None = None
    best_mtime = -1.0
    for d in base.iterdir():
        if not d.is_dir():
            continue
        mp = d / "metrics.json"
        if not mp.is_file():
            continue
        data = _read_json(mp)
        if not data or data.get("backend") != "calvin_debug_real":
            continue
        if str(data.get("calvin_debug_batch") or "") != batch:
            continue
        mt = mp.stat().st_mtime
        if mt > best_mtime:
            best_mtime = mt
            best = d
    if best is None:
        return {
            "status": "not_run",
            "backend": "calvin_debug_real",
            "calvin_debug_batch": batch,
            "path": _as_rel(root, base),
        }
    m = _read_json(best / "metrics.json")
    return {
        "status": "available",
        "backend": "calvin_debug_real",
        "calvin_debug_batch": batch,
        "latest_dir": _as_rel(root, best),
        "modes": (m or {}).get("modes", {}),
        "experiment_id": (m or {}).get("experiment_id"),
    }


def _e2_best_case_paths(root: Path) -> dict[str, str]:
    base = root / "results" / "demos" / "e2_ablation_cases"
    names = [
        "case1_none.json",
        "case2_verifier_only.json",
        "case3_plus_replan.json",
        "mock_selection_meta.json",
        "calvin_case_replan_fixes_stuck_verifier_only.json",
        "calvin_case_repair_failed_after_failure_detected.json",
        "calvin_selection_meta.json",
        "calvin_debug_real_selection_meta.json",
        "calvin_debug_real_case_verifier_only.json",
        "calvin_debug_real_case_verifier_plus_replan.json",
        "calvin_debug_real_aligned_selection_meta.json",
        "calvin_debug_real_aligned_case_verifier_only.json",
        "calvin_debug_real_aligned_case_verifier_plus_replan.json",
        "calvin_debug_same_task_selection_meta.json",
        "calvin_debug_same_task_case_verifier_only.json",
        "calvin_debug_same_task_case_verifier_plus_replan.json",
    ]
    out: dict[str, str] = {}
    for n in names:
        p = base / n
        if p.is_file():
            out[n] = _as_rel(root, p)
    return out


def _hybrid_snapshot(root: Path) -> dict:
    ev = _hybrid_eval_snapshot(root)
    ev_dbg = _hybrid_eval_snapshot_calvin_debug(root)
    ev_dbg_al = _hybrid_eval_snapshot_calvin_debug_aligned(root)
    ev_dbg_st = _hybrid_eval_snapshot_calvin_debug_same_task(root)
    sm = _hybrid_smoke_snapshot(root)
    if ev is None and sm is None and ev_dbg is None and ev_dbg_al is None and ev_dbg_st is None:
        return {
            "status": "not_run",
            "path": _as_rel(root, root / "results/experiments/hybrid_replanner_eval"),
        }
    strongest = ev or sm or ev_dbg_al or ev_dbg_st or ev_dbg
    case_p = root / "results" / "demos" / "hybrid_replanner_cases" / "case_llm_repair_success.json"
    return {
        "status": "available",
        "strongest_artifact": strongest,
        "eval_batch": ev,
        "eval_batch_calvin_debug_real": ev_dbg,
        "eval_batch_calvin_debug_real_aligned": ev_dbg_al,
        "eval_batch_calvin_debug_same_task": ev_dbg_st,
        "smoke": sm,
        "strongest_hybrid_case_path": _as_rel(root, case_p) if case_p.is_file() else None,
    }


def build_report_payload(root: Path) -> dict:
    eval_metrics = _read_json(root / "results/eval/planner_base_vs_tuned/metrics.json")
    train_meta = _read_json(
        root / "results/checkpoints/planner_sft_3b_minimal/run_latest/run_meta.json"
    )
    if train_meta:
        train_meta = dict(train_meta)
        for _k in ("train_jsonl", "val_jsonl", "output_dir", "path"):
            if train_meta.get(_k):
                train_meta[_k] = _as_rel(root, train_meta[_k])
    e2 = _e2_combined_snapshot(root)
    rb = _rlbench_snapshot(root)
    hy = _hybrid_snapshot(root)

    strongest = []
    if eval_metrics:
        strongest.append(
            {
                "name": "planner JSONL proxy (base vs tuned)",
                "path": "results/eval/planner_base_vs_tuned/metrics.json",
                "note": "Not official CALVIN benchmark.",
            }
        )
    e2m = e2.get("e2_on_mock") or {}
    if e2m.get("status") == "available":
        strongest.append(
            {
                "name": "E2 ablation on mock (symbolic)",
                "path": e2m.get("latest_dir"),
                "note": "no_verifier vs verifier_only vs verifier_plus_replan — not official CALVIN.",
            }
        )
    e2c = e2.get("e2_on_calvin_fixture") or {}
    if e2c.get("status") == "available":
        strongest.append(
            {
                "name": "E2 ablation on CALVIN fixture batch",
                "path": e2c.get("latest_dir"),
                "note": "Fixture minimal loop — **not** official CALVIN ablation.",
            }
        )
    e2d = e2.get("e2_on_calvin_debug_real") or {}
    if e2d.get("status") == "available":
        strongest.append(
            {
                "name": "E2 ablation on CALVIN official debug npz (vector teacher)",
                "path": e2d.get("latest_dir"),
                "note": "Official debug dataset vectors + symbolic minimal loop — **not** leaderboard.",
            }
        )

    gaps = [
        "Official CALVIN / RLBench leaderboard numbers: not claimed.",
        "RLBench full sim: blocked without CoppeliaSim + PyRep (see docs/rlbench_install_log.md) unless bridge_mode=sim_reset.",
        "A100 7B production training: template only.",
        "VLABench: planning doc only.",
    ]
    if not rb.get("import_ok"):
        gaps.append("RLBench Python import: false on this machine — using fixture bridge for cognition smoke.")

    hy_strong = hy.get("strongest_artifact") or {}
    evb = hy.get("eval_batch") or {}
    payload: dict = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "project_status_snapshot": {
            "cognition_layer": "implemented (mock + CALVIN fixture + CALVIN debug vectors + RLBench observation bridge)",
            "rlbench_import": rb.get("import_layer"),
            "rlbench_simulator_locate": rb.get("simulator_locate_layer"),
            "rlbench_env_create": rb.get("env_create_layer"),
            "rlbench_reset": rb.get("reset_layer"),
            "rlbench_deepest_reached_stage": rb.get("deepest_reached_stage"),
            "rlbench_blocker_summary": rb.get("blocker_summary"),
            "rlbench_memory_bridge": rb.get("memory_bridge"),
            "rlbench_planner_smoke": rb.get("planner_smoke"),
            "rlbench_bridge_mode": rb.get("bridge_mode"),
            "e2_on_mock": (e2.get("e2_on_mock") or {}).get("status"),
            "e2_on_calvin_fixture": (e2.get("e2_on_calvin_fixture") or {}).get("status"),
            "e2_on_calvin_debug_real": (e2.get("e2_on_calvin_debug_real") or {}).get("status"),
            "e2_best_case_paths": _e2_best_case_paths(root),
            "mock_vs_calvin_short_note": (
                "Mock symbolic isolates verifier/replan mechanism; CALVIN fixture exercises adapter-shaped teacher "
                "state. Expect wiring consistency, not numeric parity with official benchmarks."
            ),
            "hybrid_replanner": hy.get("status"),
            "hybrid_strongest_kind": hy_strong.get("kind"),
            "hybrid_replanner_batch_headline": evb.get("metrics_headline"),
            "hybrid_parse_error_breakdown": evb.get("parse_error_kind_counts"),
            "strongest_hybrid_case_path": hy.get("strongest_hybrid_case_path"),
            "hybrid_calvin_debug_real_batch_headline": (hy.get("eval_batch_calvin_debug_real") or {}).get(
                "metrics_headline"
            ),
            "hybrid_calvin_debug_real_aligned_batch_headline": (
                hy.get("eval_batch_calvin_debug_real_aligned") or {}
            ).get("metrics_headline"),
            "hybrid_calvin_debug_same_task_batch_headline": (
                hy.get("eval_batch_calvin_debug_same_task") or {}
            ).get("metrics_headline"),
            "calvin_debug_alignment_stats_present": (
                root / "docs" / "calvin_debug_alignment_stats.md"
            ).is_file(),
            "skill_schema_audit_present": (root / "docs" / "skill_schema_audit.md").is_file(),
        },
        "current_strongest_results": strongest,
        "e2_ablation_snapshot": e2,
        "rlbench_bridge_status": rb,
        "hybrid_replanner_status": hy,
        "failure_taxonomy": list_taxonomy_for_report(),
        "curated_demo_links": {
            "e2_cases": "docs/failure_cases/e2_ablation_cases.md",
            "e2_demos": "results/demos/e2_ablation_cases/",
            "rlbench_demos": "results/demos/rlbench_fixture_bridge/",
            "mock_demos": "results/demos/success_put_block/",
            "hybrid_experiments_smoke": "results/experiments/hybrid_replanner_smoke/",
            "hybrid_experiments_eval": "results/experiments/hybrid_replanner_eval/",
            "e2_mock_vs_calvin_table": "docs/tables/e2_ablation_mock_vs_calvin_fixture.md",
            "e2_three_backend_table": "docs/tables/e2_ablation_mock_vs_calvin_fixture_vs_calvin_debug_real.md",
            "calvin_debug_real_planner_stats": "docs/calvin_debug_real_data_stats.md",
            "calvin_debug_alignment_stats": "docs/calvin_debug_alignment_stats.md",
            "calvin_debug_alignment_audit": "docs/calvin_debug_alignment_audit.md",
            "calvin_debug_same_task_subset": "docs/calvin_debug_same_task_subset.md",
            "skill_schema_audit": "docs/skill_schema_audit.md",
            "calvin_debug_alignment_comparison": "docs/tables/calvin_debug_alignment_comparison.md",
            "hybrid_replanner_cases": "docs/failure_cases/hybrid_replanner_cases.md",
        },
        "open_gaps_limitations": gaps,
        "experiment_metadata": {
            "repo": ".",
            "planner_sft_checkpoint_dir": _as_rel(
                root, root / "results/checkpoints/planner_sft_3b_minimal/run_latest"
            ),
            "eval_metrics_path": _as_rel(
                root, root / "results/eval/planner_base_vs_tuned/metrics.json"
            ),
        },
        "eval_metrics_proxy": eval_metrics,
        "train_run_meta": train_meta,
        "artifact_index": {
            "episode_log_schema": "docs/episode_log_schema.md",
            "scene_memory_contract_v2": "docs/scene_memory_contract_v2.md",
            "failure_taxonomy_doc": "docs/failure_taxonomy.md",
            "architecture_figure": "docs/figures/architecture_v2.svg",
            "demo_assets": "results/demos/",
            "sample_episode_logs": "results/episode_logs/",
            "case_studies": "results/eval/base_vs_tuned_case_studies.md",
            "e2_table": "docs/tables/e2_ablation_summary.md",
            "hybrid_results_doc": "docs/replanner_hybrid_results.md",
            "calvin_debug_dataset_audit": "docs/calvin_debug_dataset_audit.md",
        },
        "cost_stats": {
            "note": "Placeholder for A100 runs — populate from real jobs only.",
            "gpu_hours": None,
            "estimated_usd": None,
        },
    }
    payload["unified_headline_facts"] = unified_headline_facts(payload, root=root)
    return payload


def render_markdown(payload: dict) -> str:
    lines = [
        "# EmbodiedSceneAgent — project report (auto)",
        "",
        f"_Generated: `{payload['generated_utc']}`_",
        "",
        "## Unified headline facts (machine-derived)",
        "",
        "```json",
        json.dumps(payload.get("unified_headline_facts"), indent=2),
        "```",
        "",
        "## Project Status Snapshot",
        "",
        "```json",
        json.dumps(payload.get("project_status_snapshot"), indent=2),
        "```",
        "",
        "## Current Strongest Results",
        "",
    ]
    for s in payload.get("current_strongest_results") or []:
        lines.append(f"- **{s.get('name')}**: `{s.get('path')}` — _{s.get('note')}_")
    if not payload.get("current_strongest_results"):
        lines.append("_None indexed._")
    lines.extend(
        [
            "",
            "## E2 Ablation (mock + CALVIN fixture)",
            "",
            "```json",
            json.dumps(payload.get("e2_ablation_snapshot"), indent=2),
            "```",
            "",
            "## RLBench Bridge Status",
            "",
            "```json",
            json.dumps(payload.get("rlbench_bridge_status"), indent=2),
            "```",
            "",
            "## Hybrid Replanner Status",
            "",
            "```json",
            json.dumps(payload.get("hybrid_replanner_status"), indent=2),
            "```",
            "",
            "## Eval metrics (JSONL proxy)",
            "",
        ]
    )
    em = payload.get("eval_metrics_proxy")
    if em:
        lines.extend(["```json", json.dumps(em, indent=2), "```", ""])
    else:
        lines.append("_No eval metrics file._\n")

    lines.extend(["## Curated demo links", ""])
    for k, v in (payload.get("curated_demo_links") or {}).items():
        lines.append(f"- **{k}**: `{v}`")
    lines.extend(
        [
            "",
            "## Open gaps / honest limitations",
            "",
        ]
    )
    for g in payload.get("open_gaps_limitations") or []:
        lines.append(f"- {g}")

    lines.extend(["", "## Failure taxonomy (registry snapshot)", "", "| failure_type | condition (short) | replan hint |", "|---|---|---|"])
    for row in payload.get("failure_taxonomy") or []:
        cond = (row.get("condition") or "")[:80].replace("|", "\\|")
        rep = (row.get("replan") or "")[:80].replace("|", "\\|")
        lines.append(f"| `{row.get('failure_type')}` | {cond} | {rep} |")
    lines.extend(["", "## Artifact index", ""])
    for k, v in payload.get("artifact_index", {}).items():
        lines.append(f"- **{k}**: `{v}`")
    return "\n".join(lines)


def render_dashboard(payload: dict) -> str:
    ps = payload.get("project_status_snapshot") or {}
    rb = payload.get("rlbench_bridge_status") or {}
    hy = payload.get("hybrid_replanner_status") or {}
    lines = [
        "# Status board (auto)",
        "",
        f"_`{payload.get('generated_utc')}`_",
        "",
        "| Area | State |",
        "|------|-------|",
        f"| Cognition loop (mock/CALVIN) | implemented |",
        f"| RLBench import | {ps.get('rlbench_import')} |",
        f"| RLBench simulator_locate | {ps.get('rlbench_simulator_locate')} |",
        f"| RLBench env_create | {ps.get('rlbench_env_create')} |",
        f"| RLBench reset | {ps.get('rlbench_reset')} |",
        f"| RLBench deepest_reached_stage | `{ps.get('rlbench_deepest_reached_stage')}` |",
        f"| RLBench memory_bridge | {ps.get('rlbench_memory_bridge')} |",
        f"| RLBench planner_smoke | {ps.get('rlbench_planner_smoke')} |",
        f"| RLBench bridge_mode | `{ps.get('rlbench_bridge_mode')}` |",
        f"| E2 on mock | `{ps.get('e2_on_mock')}` |",
        f"| E2 on CALVIN fixture | `{ps.get('e2_on_calvin_fixture')}` |",
        f"| E2 on CALVIN debug real-data | `{ps.get('e2_on_calvin_debug_real')}` |",
        f"| Hybrid replanner | `{ps.get('hybrid_replanner')}` (strongest: `{ps.get('hybrid_strongest_kind')}`) |",
        f"| Hybrid batch (CALVIN debug real) headline | `{ps.get('hybrid_calvin_debug_real_batch_headline')}` |",
        "",
        "## RLBench blocker_summary",
        "",
        f"{ps.get('rlbench_blocker_summary') or '_n/a_'}",
        "",
        "## E2 best case paths (demos dir)",
        "",
        "```json",
        json.dumps(ps.get("e2_best_case_paths") or {}, indent=2),
        "```",
        "",
        "## mock_vs_calvin_short_note",
        "",
        f"{ps.get('mock_vs_calvin_short_note') or ''}",
        "",
        "## Hybrid strongest case path",
        "",
        f"`{ps.get('strongest_hybrid_case_path')}`",
        "",
        "## Hybrid parse error breakdown (eval batch)",
        "",
        "```json",
        json.dumps(ps.get("hybrid_parse_error_breakdown") or {}, indent=2),
        "```",
        "",
        "## RLBench stages present (last smoke JSON)",
        "",
        f"`{rb.get('stages_present')}`",
        "",
        "## Hybrid headline (eval batch if present)",
        "",
        "```json",
        json.dumps((hy.get("eval_batch") or {}).get("metrics_headline") or {}, indent=2),
        "```",
        "",
        "## Strongest real artifacts",
        "",
    ]
    for s in payload.get("current_strongest_results") or []:
        lines.append(f"- `{s.get('path')}`")
    lines.extend(["", "## Smoke vs future", "", "| Item | |", "|------|--|", "| RLBench fixture→memory→planner | **smoke** |", "| RLBench sim_reset | only if CoppeliaSim+rlbench OK |", "| Official benchmarks | **future_only** |", "| A100 7B | **future_only** (template exists) |", ""])
    lines.extend(["## Limitations", ""])
    for g in (payload.get("open_gaps_limitations") or [])[:6]:
        lines.append(f"- {g}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Write latest_project_report + dashboard")
    parser.add_argument("--root", type=Path, default=None)
    args, _unknown = parser.parse_known_args()
    root = args.root or repo_root()
    out_dir = root / "results" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_report_payload(root)
    (out_dir / "latest_project_report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "latest_project_report.md").write_text(render_markdown(payload), encoding="utf-8")
    (out_dir / "latest_project_dashboard.md").write_text(render_dashboard(payload), encoding="utf-8")
    board = root / "docs" / "project_page" / "status_board.md"
    board.parent.mkdir(parents=True, exist_ok=True)
    board.write_text(render_dashboard(payload), encoding="utf-8")
    print(f"[make_project_report] wrote {out_dir / 'latest_project_report.md'} + dashboard")


if __name__ == "__main__":
    main()
