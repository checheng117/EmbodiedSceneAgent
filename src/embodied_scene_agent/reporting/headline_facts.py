"""Single source of headline facts for README / project_page / dashboard / final assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def unified_headline_facts(payload: dict[str, Any], *, root: Path) -> dict[str, Any]:
    """
    Derived strictly from ``build_report_payload`` output (no hand-tuned numbers).

    Intended for JSON export + README injection + consistency audits.
    """
    ps = payload.get("project_status_snapshot") or {}
    strongest = list(payload.get("current_strongest_results") or [])
    e2 = payload.get("e2_ablation_snapshot") or {}
    e2m = e2.get("e2_on_mock") or {}
    e2c = e2.get("e2_on_calvin_fixture") or {}
    e2d = e2.get("e2_on_calvin_debug_real") or {}
    modes_m = (e2m.get("modes") or {}) if e2m.get("status") == "available" else {}
    vpr_m = modes_m.get("verifier_plus_replan") or {}

    hybrid_h = ps.get("hybrid_replanner_batch_headline") or {}
    hy_dbg = ps.get("hybrid_calvin_debug_real_batch_headline") or {}
    parse_breakdown = ps.get("hybrid_parse_error_breakdown") or {}

    def _rel(p: str | None) -> str | None:
        if not p:
            return None
        try:
            rp = Path(p).resolve()
            rr = root.resolve()
            if str(rp).startswith(str(rr)):
                return str(rp.relative_to(rr))
        except ValueError:
            pass
        return p

    first_strong = strongest[0] if strongest else None
    return {
        "generated_utc": payload.get("generated_utc"),
        "strongest_real_result": {
            "name": (first_strong or {}).get("name"),
            "path": (first_strong or {}).get("path"),
            "note": (first_strong or {}).get("note"),
        },
        "strongest_real_results_all": [
            {"name": s.get("name"), "path": _rel(s.get("path")) or s.get("path"), "note": s.get("note")}
            for s in strongest
        ],
        "strongest_hybrid_result": {
            "kind": ps.get("hybrid_strongest_kind"),
            "metrics_headline": hybrid_h,
            "case_path": _rel(ps.get("strongest_hybrid_case_path")),
            "parse_error_kind_counts": parse_breakdown,
            "parse_breakdown_empty_reason": (
                "Latest hybrid replanner eval batch had no LLM parse failures; all audited calls reached "
                "`fallback_stage=validated`. Breakdown counts are therefore empty — not a claim of "
                "infinite robustness."
                if not parse_breakdown
                else None
            ),
        },
        "e2_best_story": {
            "mock_status": e2m.get("status"),
            "mock_latest_dir": _rel(e2m.get("latest_dir")),
            "calvin_fixture_status": e2c.get("status"),
            "calvin_latest_dir": _rel(e2c.get("latest_dir")),
            "calvin_debug_real_status": e2d.get("status"),
            "calvin_debug_real_latest_dir": _rel(e2d.get("latest_dir")),
            "mock_verifier_plus_replan_task_completion_rate": vpr_m.get("task_completion_rate"),
            "mock_verifier_plus_replan_recovery_success_rate": vpr_m.get("recovery_success_rate"),
            "one_line": (
                f"E2 mock (symbolic): latest batch shows verifier_plus_replan task_completion="
                f"{vpr_m.get('task_completion_rate')!s}, recovery_success_rate="
                f"{vpr_m.get('recovery_success_rate')!s} — **fixture/smoke**, not official CALVIN."
                if modes_m
                else "E2 mock batch not available in payload."
            ),
            "calvin_debug_real_note": (
                f"E2 on official CALVIN **debug** vectors: status `{e2d.get('status')}` — **not** leaderboard."
            ),
        },
        "hybrid_calvin_debug_real_headline": hy_dbg,
        "rlbench_deepest_stage": ps.get("rlbench_deepest_reached_stage"),
        "rlbench_blocker_summary": ps.get("rlbench_blocker_summary"),
        "rlbench_bridge_mode": ps.get("rlbench_bridge_mode"),
        "rlbench_memory_bridge": ps.get("rlbench_memory_bridge"),
        "open_gaps": list(payload.get("open_gaps_limitations") or []),
        "smoke_vs_future_note": (
            "RLBench: **real** = fixture→memory→planner smoke; **sim_reset** = only if CoppeliaSim stack OK. "
            "Official CALVIN/RLBench leaderboards: **future_only**. A100 7B / VLABench: **future_only**."
        ),
    }


def render_readme_unified_markdown_table(facts: dict[str, Any]) -> str:
    """Markdown block for README injection (between HTML comment markers)."""
    h = facts.get("strongest_hybrid_result") or {}
    hh = h.get("metrics_headline") or {}
    lines = [
        "_Synced by `bash scripts/build_final_report_assets.sh` — do not edit between markers._",
        "",
        "| Unified headline | Value |",
        "|------------------|-------|",
        f"| **RLBench deepest stage** | `{facts.get('rlbench_deepest_stage')}` |",
        f"| **RLBench bridge (fixture)** | memory_bridge=`{facts.get('rlbench_memory_bridge')}`; bridge_mode=`{facts.get('rlbench_bridge_mode')}` |",
        f"| **Hybrid batch (latest)** | parse_ok=`{hh.get('replan_parse_success_rate')}`; validated=`{hh.get('validated_revision_rate')}`; repair=`{hh.get('repair_success_rate')}` |",
        f"| **Hybrid parse breakdown** | `{h.get('parse_error_kind_counts')!s}` ({'empty — see `limitations.md`' if not h.get('parse_error_kind_counts') else 'see eval `fallback_stats.json`'}) |",
        f"| **E2 mock (vpr task completion)** | `{facts.get('e2_best_story', {}).get('mock_verifier_plus_replan_task_completion_rate')}` |",
        f"| **Primary strongest artifact** | `{facts.get('strongest_real_result', {}).get('path')}` |",
        "",
        "**Honest boundaries:** official benchmark numbers not claimed; RLBench sim not past import on dev machine; "
        "E2 adds **mock + CALVIN fixture + CALVIN official debug npz (vector teacher)** — still **not** full benchmark.",
        "",
    ]
    return "\n".join(lines)
