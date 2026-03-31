"""Lightweight batch eval for hybrid replanner: parse / validate / fallback / repair stats."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from embodied_scene_agent.evaluation.hybrid_replanner_smoke import (
    _FirstStepUnknownSkillPlanner,
    _fallback_stats_from_traces,
)
from embodied_scene_agent.evaluation.run_ablation_e2 import calvin_debug_real_scenario_list
from embodied_scene_agent.pipeline.run_calvin_minimal_loop import run_calvin_minimal_episode
from embodied_scene_agent.pipeline.v0_loop import run_v0_episode
from embodied_scene_agent.utils.experiment import normalize_experiment_id, write_run_artifacts
from embodied_scene_agent.utils.paths import repo_root
from embodied_scene_agent.verifier.taxonomy import classify_hybrid_episode_failure


def _audits_from_trace(trace: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for st in trace.steps:
        ra = st.get("replan_audit")
        if isinstance(ra, dict) and ra.get("llm_replanner_called"):
            out.append(ra)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--episodes", type=int, default=8)
    parser.add_argument(
        "--backend",
        type=str,
        choices=["mock", "calvin_debug_real"],
        default="mock",
    )
    parser.add_argument(
        "--calvin-debug-batch",
        type=str,
        choices=["pooled_manifest", "grouped_sequence", "same_task_subset"],
        default="grouped_sequence",
    )
    parser.add_argument("--experiment-id", type=str, default="")
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    args, _ = parser.parse_known_args()
    root = args.root or repo_root()
    if args.backend == "calvin_debug_real":
        b = args.calvin_debug_batch
        if b == "grouped_sequence":
            prefix = "hybrid_calvin_debug_real_aligned"
        elif b == "same_task_subset":
            prefix = "hybrid_calvin_debug_same_task"
        else:
            prefix = "hybrid_calvin_debug_real"
    else:
        prefix = "hybrid_replanner_eval"
    eid = normalize_experiment_id(prefix=prefix, explicit_id=args.experiment_id)
    out_dir = root / "results" / "experiments" / "hybrid_replanner_eval" / eid
    out_dir.mkdir(parents=True, exist_ok=True)

    traces: list[Any] = []
    rows: list[dict[str, Any]] = []
    unknown_fail_steps = 0
    total_fail_steps = 0
    episode_failure_counts: Counter[str] = Counter()
    terminal_failure_counts: Counter[str] = Counter()

    n_ep = max(1, int(args.episodes))
    scenarios: list[dict[str, Any]] = []
    if args.backend == "calvin_debug_real":
        scenarios = calvin_debug_real_scenario_list(
            n_episodes=max(n_ep, 12),
            seed=args.seed,
            batch=args.calvin_debug_batch,  # type: ignore[arg-type]
        )[:n_ep]

    for i in range(n_ep):
        if args.backend == "mock":
            tr = run_v0_episode(
                "put the red block in the drawer",
                max_steps=max(1, int(args.max_steps)),
                forced_grasp_failures=i % 3,
                verifier_mode="verifier_plus_replan",
                replanner_mode="hybrid",
                experiment_id=eid,
                planner=_FirstStepUnknownSkillPlanner(),
            )
            scen: dict[str, Any] | None = None
        else:
            scen = scenarios[i]
            tr = run_calvin_minimal_episode(
                scen["instruction"],
                max_steps=max(1, int(args.max_steps)),
                initial_observation=scen["initial_observation"],
                verifier_mode="verifier_plus_replan",
                replanner_mode="hybrid",
                experiment_id=eid,
                planner=_FirstStepUnknownSkillPlanner(),
            )
        traces.append(tr)
        audits = _audits_from_trace(tr)
        fa0 = audits[0] if audits else None
        failure_summary = classify_hybrid_episode_failure(tr.steps, final_message=tr.final_message)
        row_base: dict[str, Any] = {
            "episode_index": i,
            "success": tr.success,
            "replan_count": tr.replan_count,
            "num_steps": len(tr.steps),
            "final_message": tr.final_message,
            "llm_audit_count": len(audits),
            "first_llm_audit": fa0,
            "replanner_parse_error_kind": (fa0 or {}).get("replanner_parse_error_kind"),
            "acceptance_rejection_reason": (fa0 or {}).get("acceptance_rejection_reason"),
            "acceptance_rejection_details": (fa0 or {}).get("acceptance_rejection_details"),
            "episode_failure_label": failure_summary["episode_failure_label"],
            "terminal_failure_label": failure_summary["terminal_failure_label"],
            "validated_replan_issue_label": failure_summary["validated_replan_issue_label"],
            "failure_label_reasons": failure_summary["label_reasons"],
            "terminal_failure_type": failure_summary["terminal_failure_type"],
            "terminal_failure_details": failure_summary["terminal_failure_details"],
        }
        if scen is not None:
            row_base["npz_path"] = scen.get("npz_path")
            row_base["backend"] = "calvin_debug_real"
        rows.append(row_base)
        if not tr.success:
            episode_failure_counts[row_base["episode_failure_label"]] += 1
            terminal_failure_counts[row_base["terminal_failure_label"]] += 1
        for st in tr.steps:
            v = st.get("verification") or {}
            if v.get("success") is False:
                total_fail_steps += 1
                if str(v.get("failure_type") or "") == "unknown_failure":
                    unknown_fail_steps += 1

    fb = _fallback_stats_from_traces(traces)
    llm_calls = int(fb["llm_replanner_calls"])
    if llm_calls:
        parse_rate = fb["replanner_parse_ok_count"] / llm_calls
        val_rate = fb["revised_plan_validated_count"] / llm_calls
        fb_rate = 1.0 - parse_rate
    else:
        parse_rate = None
        val_rate = None
        fb_rate = None
    llm_calls = int(fb["llm_replanner_calls"])
    inv_skill = int(fb.get("invalid_skill_count") or 0)
    alias_n = int(fb.get("alias_normalization_count") or 0)
    metrics = {
        "experiment_id": eid,
        "n_episodes": len(traces),
        "replan_parse_success_rate": parse_rate,
        "validated_revision_rate": val_rate,
        "fallback_rate": fb_rate,
        "repair_success_rate": sum(1 for t in traces if t.success) / max(1, len(traces)),
        "unknown_failure_rate": unknown_fail_steps / max(1, total_fail_steps),
        "unknown_skill_rate": inv_skill / max(1, llm_calls),
        "alias_normalization_count": alias_n,
        "invalid_skill_count": inv_skill,
        "parse_error_kind_counts": fb.get("parse_error_kind_counts") or {},
        "acceptance_rejection_reason_counts": fb.get("acceptance_rejection_reason_counts") or {},
        "episode_failure_label_counts": dict(episode_failure_counts),
        "terminal_failure_label_counts": dict(terminal_failure_counts),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "honest_scope": (
            "CALVIN official debug npz → vector teacher + hybrid replanner batch — not official benchmark."
            if args.backend == "calvin_debug_real"
            else "MockEmbodiedEnv batch — not official benchmark; measures JSON/audit plumbing."
        ),
        "backend": args.backend,
        "calvin_debug_batch": args.calvin_debug_batch if args.backend == "calvin_debug_real" else None,
    }
    run_artifacts = write_run_artifacts(
        out_dir,
        root=root,
        experiment_id=eid,
        entrypoint="python -m embodied_scene_agent.evaluation.hybrid_replanner_eval",
        config_snapshot={
            "backend": args.backend,
            "calvin_debug_batch": args.calvin_debug_batch if args.backend == "calvin_debug_real" else None,
            "episodes": n_ep,
            "max_steps": max(1, int(args.max_steps)),
            "seed": args.seed,
            "planner_fixture": "first_step_unknown_skill",
            "verifier_mode": "verifier_plus_replan",
            "replanner_mode": "hybrid",
        },
        notes=[
            "Batch hybrid eval for schema/audit stability under the 3090-only roadmap.",
            "Not an official benchmark run.",
        ],
    )

    (out_dir / "metrics.json").write_text(
        json.dumps({**metrics, "fallback_detail": fb, "run_artifacts": run_artifacts}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    (out_dir / "fallback_stats.json").write_text(
        json.dumps(fb, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    per_path = out_dir / "per_episode.jsonl"
    with per_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    scope_note = (
        "_CALVIN debug real-data backend — same metrics contract as mock batch._"
        if args.backend == "calvin_debug_real"
        else "_Mock v0 — measures parse/validate/fallback/repair rates from `replan_audit`._"
    )
    summary_lines = [
        f"# Hybrid replanner batch eval ({eid})",
        "",
        scope_note,
        "",
        "## metrics.json (headline)",
        "",
        "```json",
        json.dumps({**metrics, "run_artifacts": run_artifacts}, indent=2),
        "```",
        "",
        "## fallback_stats.json",
        "",
        "```json",
        json.dumps(fb, indent=2),
        "```",
        "",
        "## refined_failure_labels",
        "",
        "```json",
        json.dumps(
            {
                "episode_failure_label_counts": metrics.get("episode_failure_label_counts") or {},
                "terminal_failure_label_counts": metrics.get("terminal_failure_label_counts") or {},
                "acceptance_rejection_reason_counts": metrics.get("acceptance_rejection_reason_counts") or {},
            },
            indent=2,
        ),
        "```",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    _append_replanner_hybrid_results_doc(root, metrics, fb, out_dir)

    if args.backend == "mock":
        _write_case_artifacts(root, traces, eid)
    else:
        _write_case_artifacts_calvin_debug(
            root, traces, eid, calvin_debug_batch=args.calvin_debug_batch
        )
    print(json.dumps({"wrote": str(out_dir), "metrics": metrics}, indent=2))


def _fmt_rate(x: object) -> str:
    if isinstance(x, (int, float)):
        return f"{float(x):.3f}"
    return "n/a"


def _append_replanner_hybrid_results_doc(root: Path, metrics: dict, fb: dict, out_dir: Path) -> None:
    path = root / "docs" / "replanner_hybrid_results.md"
    if not path.is_file():
        return
    block = [
        "",
        f"## Batch eval snapshot (`{out_dir.name}`)",
        "",
        "| metric | value |",
        "|--------|------:|",
        f"| replan_parse_success_rate | {_fmt_rate(metrics.get('replan_parse_success_rate'))} |",
        f"| validated_revision_rate | {_fmt_rate(metrics.get('validated_revision_rate'))} |",
        f"| fallback_rate | {_fmt_rate(metrics.get('fallback_rate'))} |",
        f"| repair_success_rate | {_fmt_rate(metrics.get('repair_success_rate'))} |",
        f"| unknown_failure_rate | {_fmt_rate(metrics.get('unknown_failure_rate'))} |",
        f"| unknown_skill_rate | {_fmt_rate(metrics.get('unknown_skill_rate'))} |",
        f"| alias_normalization_count | {metrics.get('alias_normalization_count')!s} |",
        f"| invalid_skill_count | {metrics.get('invalid_skill_count')!s} |",
        "",
        "### parse_error_kind_counts",
        "",
        "```json",
        json.dumps(metrics.get("parse_error_kind_counts") or {}, indent=2),
        "```",
        "",
        "### episode_failure_label_counts",
        "",
        "```json",
        json.dumps(metrics.get("episode_failure_label_counts") or {}, indent=2),
        "```",
        "",
        "### terminal_failure_label_counts",
        "",
        "```json",
        json.dumps(metrics.get("terminal_failure_label_counts") or {}, indent=2),
        "```",
        "",
        "### acceptance_rejection_reason_counts",
        "",
        "```json",
        json.dumps(metrics.get("acceptance_rejection_reason_counts") or {}, indent=2),
        "```",
        "",
        "### fallback_reason_counts",
        "",
        "```json",
        json.dumps(fb.get("fallback_reason_counts") or {}, indent=2),
        "```",
        "",
        "### fallback_stage_counts",
        "",
        "```json",
        json.dumps(fb.get("fallback_stage_counts") or {}, indent=2),
        "```",
        "",
        f"_Artifact: `{out_dir}`_",
        "",
    ]
    path.write_text(path.read_text(encoding="utf-8").rstrip() + "\n" + "\n".join(block), encoding="utf-8")


def _find_llm_success_from_latest_smoke(root: Path) -> tuple[int, Any, dict] | None:
    """If batch eval had no LLM-validated success, point to latest smoke trace (real artifact)."""
    from embodied_scene_agent.reporting.make_project_report import _latest_subdir

    base = root / "results" / "experiments" / "hybrid_replanner_smoke"
    latest = _latest_subdir(base)
    if latest is None:
        return None
    tr_path = latest / "trace_full.json"
    if not tr_path.is_file():
        return None
    data = json.loads(tr_path.read_text(encoding="utf-8"))
    steps = data.get("steps") or []
    for st in steps:
        ra = st.get("replan_audit") or {}
        if (
            ra.get("revised_plan_validated")
            and ra.get("whether_rule_based") is False
            and data.get("success")
        ):
            class _T:
                success = data.get("success")
                replan_count = data.get("replan_count", 0)
                final_message = data.get("final_message", "")

            return (-1, _T(), st)
    return None


def _write_case_artifacts_calvin_debug(
    root: Path,
    traces: list[Any],
    eid: str,
    *,
    calvin_debug_batch: str,
) -> None:
    """Dedicated JSON + markdown section for CALVIN debug real hybrid batch (does not overwrite mock case files)."""
    demo = root / "results" / "demos" / "hybrid_replanner_cases"
    demo.mkdir(parents=True, exist_ok=True)
    if calvin_debug_batch == "same_task_subset":
        tag = "calvin_debug_same_task"
        succ_f = "case_calvin_debug_same_task_hybrid_success.json"
        fb_f = "case_calvin_debug_same_task_hybrid_fallback.json"
        reject_f = "case_calvin_debug_same_task_hybrid_acceptance_reject.json"
    elif calvin_debug_batch == "grouped_sequence":
        tag = "calvin_debug_real_aligned"
        succ_f = "case_calvin_debug_real_aligned_hybrid_success.json"
        fb_f = "case_calvin_debug_real_aligned_hybrid_fallback.json"
        reject_f = "case_calvin_debug_real_aligned_hybrid_acceptance_reject.json"
    else:
        tag = "calvin_debug_real_pooled"
        succ_f = "case_calvin_debug_hybrid_success.json"
        fb_f = "case_calvin_debug_hybrid_fallback.json"
        reject_f = "case_calvin_debug_hybrid_acceptance_reject.json"

    success_llm = None
    parse_fallback = None
    acceptance_reject = None
    for idx, tr in enumerate(traces):
        for st in tr.steps:
            ra = st.get("replan_audit") or {}
            if (
                success_llm is None
                and ra.get("revised_plan_validated")
                and ra.get("whether_rule_based") is False
            ):
                success_llm = (idx, tr, st)
            if parse_fallback is None and ra.get("llm_replanner_called") and ra.get("replanner_parse_ok") is False:
                parse_fallback = (idx, tr, st)
            if acceptance_reject is None and ra.get("acceptance_rejection_reason"):
                acceptance_reject = (idx, tr, st)

    succ_audit = (success_llm[2].get("replan_audit") or {}) if success_llm is not None else {}
    fb_audit = (parse_fallback[2].get("replan_audit") or {}) if parse_fallback is not None else {}
    reject_audit = (acceptance_reject[2].get("replan_audit") or {}) if acceptance_reject is not None else {}
    succ_summary = (
        classify_hybrid_episode_failure(success_llm[1].steps, final_message=success_llm[1].final_message)
        if success_llm is not None
        else {}
    )
    episode_failure_counts = Counter(
        classify_hybrid_episode_failure(tr.steps, final_message=tr.final_message)["episode_failure_label"]
        for tr in traces
        if not tr.success
    )
    terminal_failure_counts = Counter(
        classify_hybrid_episode_failure(tr.steps, final_message=tr.final_message)["terminal_failure_label"]
        for tr in traces
        if not tr.success
    )
    acceptance_rejection_counts = Counter(
        str((st.get("replan_audit") or {}).get("acceptance_rejection_reason"))
        for tr in traces
        for st in tr.steps
        if (st.get("replan_audit") or {}).get("acceptance_rejection_reason")
    )

    def _dump(
        tup: tuple[int, Any, dict] | None,
        fname: str,
        label: str,
        miss_note: str,
    ) -> None:
        if tup is None:
            payload = {
                "case": label,
                "note": miss_note,
                "experiment_id": eid,
                "backend": "calvin_debug_real",
                "calvin_debug_batch": calvin_debug_batch,
                "reporting_source_tag": tag,
            }
        else:
            ep_i, tr, st = tup
            trace_summary = {
                "success": tr.success,
                "replan_count": tr.replan_count,
                "final_message": tr.final_message,
                **classify_hybrid_episode_failure(tr.steps, final_message=tr.final_message),
            }
            payload = {
                "case": label,
                "backend": "calvin_debug_real",
                "calvin_debug_batch": calvin_debug_batch,
                "reporting_source_tag": tag,
                "experiment_id": eid,
                "episode_index": ep_i,
                "step": st,
                "trace_summary": trace_summary,
            }
        (demo / fname).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    _dump(
        success_llm,
        succ_f,
        "calvin_debug_hybrid_nearest_success",
        "本 batch 未找到 LLM revised_plan_validated（可能全为规则路径或未调用 LLM）。",
    )
    _dump(
        parse_fallback,
        fb_f,
        "calvin_debug_hybrid_parse_fallback",
        "本 batch 未找到 parse 失败步骤。",
    )
    _dump(
        acceptance_reject,
        reject_f,
        "calvin_debug_hybrid_acceptance_reject",
        "本 batch 未找到 semantic acceptance reject 样例。",
    )

    md_path = root / "docs" / "failure_cases" / "hybrid_replanner_cases.md"
    section_heading = {
        "pooled_manifest": "## Hybrid CALVIN debug — pooled_manifest",
        "grouped_sequence": "## Hybrid CALVIN debug — grouped_sequence (aligned)",
        "same_task_subset": "## Hybrid CALVIN debug — same_task_subset",
    }[calvin_debug_batch]
    block = "\n".join(
        [
            section_heading,
            "",
            f"_官方 debug ``*.npz`` 向量 teacher + hybrid replanner；**非** leaderboard；来源 **`{tag}`**（batch=`{calvin_debug_batch}`）。_",
            "",
            "### A) Semantic reject before execution",
            f"- [`{reject_f}`](../../results/demos/hybrid_replanner_cases/{reject_f})",
            (
                f"- acceptance_rejection_reason=`{reject_audit.get('acceptance_rejection_reason')}`; "
                f"details=`{reject_audit.get('acceptance_rejection_details')}`"
                if reject_audit
                else "- _本 batch 未命中 semantic acceptance reject 样例。_"
            ),
            (
                f"- raw_generation_head=`{(reject_audit.get('raw_generation_head') or '')[:120]}`; "
                f"parser_repair_actions=`{reject_audit.get('parser_repair_actions')}`"
                if reject_audit
                else ""
            ),
            "",
            "### B) 最近似成功（LLM 校验修订）",
            f"- [`{succ_f}`](../../results/demos/hybrid_replanner_cases/{succ_f})",
            (
                f"- parser_repair_actions=`{succ_audit.get('parser_repair_actions')}`; "
                f"raw_generation_head=`{(succ_audit.get('raw_generation_head') or '')[:120]}`"
                if succ_audit
                else "- _本 batch 未命中 LLM validated success 样例。_"
            ),
            (
                f"- episode_failure_label=`{succ_summary.get('episode_failure_label')}`; "
                f"terminal_failure_label=`{succ_summary.get('terminal_failure_label')}`; "
                f"terminal_failure_type=`{succ_summary.get('terminal_failure_type')}`"
                if succ_summary
                else ""
            ),
            "",
            "### C) Fallback（解析失败）",
            f"- [`{fb_f}`](../../results/demos/hybrid_replanner_cases/{fb_f})",
            (
                f"- parse_error_kind=`{fb_audit.get('replanner_parse_error_kind')}`; "
                f"fallback_reason=`{fb_audit.get('fallback_reason')}`"
                if fb_audit
                else "- _本 batch 未命中 parse fallback 样例。_"
            ),
            (
                f"- raw_generation_head=`{(fb_audit.get('raw_generation_head') or '')[:120]}`; "
                f"parser_repair_actions=`{fb_audit.get('parser_repair_actions')}`"
                if fb_audit
                else ""
            ),
            "",
            "### D) Refined failure counts",
            "```json",
            json.dumps(
                {
                    "acceptance_rejection_reason_counts": dict(acceptance_rejection_counts),
                    "episode_failure_label_counts": dict(episode_failure_counts),
                    "terminal_failure_label_counts": dict(terminal_failure_counts),
                },
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
        ]
    )
    hybrid_calvin_markers = (
        "## Hybrid CALVIN debug — pooled_manifest",
        "## Hybrid CALVIN debug — grouped_sequence (aligned)",
        "## Hybrid CALVIN debug — same_task_subset",
    )
    parent = (
        "## CALVIN debug real-data backed hybrid (not benchmark)\n\n"
        "_下列分节对应不同 `CALVIN_DEBUG_BATCH` / `--calvin-debug-batch`，互不覆盖。_\n"
    )

    def _splice_hybrid_calvin(text: str, heading: str, body: str) -> str:
        if heading not in text:
            return text.rstrip() + "\n\n" + body
        i = text.index(heading)
        after = text[i + len(heading) :]
        cut = len(after)
        for m in hybrid_calvin_markers:
            if m == heading:
                continue
            pos = after.find(m)
            if pos != -1:
                cut = min(cut, pos)
        tail = after[cut:]
        return text[:i] + body + tail

    md_path.parent.mkdir(parents=True, exist_ok=True)
    t = md_path.read_text(encoding="utf-8") if md_path.is_file() else "# Hybrid replanner — curated cases (auto)\n"
    if "## CALVIN debug real-data backed hybrid (not benchmark)" not in t:
        t = t.rstrip() + "\n\n" + parent
    t = _splice_hybrid_calvin(t, section_heading, block)
    md_path.write_text(t, encoding="utf-8")


def _write_case_artifacts(root: Path, traces: list[Any], eid: str) -> None:
    demo = root / "results" / "demos" / "hybrid_replanner_cases"
    demo.mkdir(parents=True, exist_ok=True)

    success_llm = None
    parse_fallback = None
    validated_no_repair = None

    for idx, tr in enumerate(traces):
        for st in tr.steps:
            ra = st.get("replan_audit") or {}
            vr = st.get("verification_replan") or {}
            if (
                success_llm is None
                and ra.get("revised_plan_validated")
                and ra.get("whether_rule_based") is False
                and tr.success
            ):
                success_llm = (idx, tr, st)
            if parse_fallback is None and ra.get("llm_replanner_called") and ra.get("replanner_parse_ok") is False:
                parse_fallback = (idx, tr, st)
            if (
                validated_no_repair is None
                and ra.get("revised_plan_validated")
                and isinstance(vr, dict)
                and vr.get("success") is False
            ):
                validated_no_repair = (idx, tr, st)

    notes: dict[str, str] = {}

    def dump(
        label: str,
        tup: tuple[int, Any, dict] | None,
        fname: str,
        *,
        source: str = "eval_batch",
        extra_note: str | None = None,
    ) -> None:
        if tup is None:
            payload: dict[str, Any] = {
                "case": label,
                "note": extra_note or f"no {label} case found in this batch",
                "experiment_id": eid,
            }
        else:
            ep_i, tr, st = tup
            payload = {
                "case": label,
                "source": source,
                "experiment_id": eid,
                "episode_index": ep_i,
                "step": st,
                "trace_summary": {
                    "success": tr.success,
                    "replan_count": tr.replan_count,
                    "final_message": tr.final_message,
                    **classify_hybrid_episode_failure(tr.steps, final_message=tr.final_message),
                },
            }
        (demo / fname).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    smoke_tup = _find_llm_success_from_latest_smoke(root) if success_llm is None else None
    if success_llm is not None:
        dump("llm_replan_success", success_llm, "case_llm_repair_success.json", source="eval_batch")
        notes["llm"] = "本 batch 内命中：见 JSON `source=eval_batch`。"
    elif smoke_tup is not None:
        dump("llm_replan_success", smoke_tup, "case_llm_repair_success.json", source="hybrid_replanner_smoke_latest")
        notes["llm"] = (
            "本 batch 未命中 LLM 校验成功；JSON 回退引用 **最近一次 hybrid_replanner_smoke** 产物（`source` 字段已标注，非本 batch）。"
        )
    else:
        dump(
            "llm_replan_success",
            None,
            "case_llm_repair_success.json",
            extra_note="batch 与 smoke 均未找到 LLM validated 成功样例",
        )
        notes["llm"] = "batch 与 `hybrid_replanner_smoke` 均未找到可用样例（未伪造）。"

    if parse_fallback is None:
        dump(
            "parse_fallback",
            None,
            "case_parse_fallback.json",
            extra_note="本 batch 中不存在「llm_replanner_called 且 replanner_parse_ok=false」的步骤",
        )
        notes["parse"] = "本 batch 未命中 parse 回退（可能全部解析成功或未调用 LLM）。"
    else:
        dump("parse_fallback", parse_fallback, "case_parse_fallback.json")
        notes["parse"] = "本 batch 内命中 parse/校验回退。"

    if validated_no_repair is None:
        dump(
            "validated_repair_ineffective",
            None,
            "case_validated_repair_failed.json",
            extra_note="无 revised_plan_validated 且 verification_replan.success=false 的步骤",
        )
        notes["validated"] = "本 batch 未命中「校验通过但 replan 后仍失败」组合。"
    else:
        dump("validated_repair_ineffective", validated_no_repair, "case_validated_repair_failed.json")
        notes["validated"] = "本 batch 内命中该组合。"

    md = root / "docs" / "failure_cases" / "hybrid_replanner_cases.md"
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(
        "\n".join(
            [
                "# Hybrid replanner — curated cases (auto)",
                "",
                "_**Fixture / mock batch** — 非官方 benchmark。JSON 见 `results/demos/hybrid_replanner_cases/`。_",
                "",
                "## 1) LLM replan 后任务恢复",
                f"- 文件：[`case_llm_repair_success.json`](../../results/demos/hybrid_replanner_cases/case_llm_repair_success.json)",
                f"- {notes['llm']}",
                "",
                "## 2) Parse / 校验失败 → 规则回退",
                f"- 文件：[`case_parse_fallback.json`](../../results/demos/hybrid_replanner_cases/case_parse_fallback.json)",
                f"- {notes['parse']}",
                (
                    f"- observed parse_error_kind=`{((parse_fallback or (None, None, {}))[2].get('replan_audit') or {}).get('replanner_parse_error_kind')}` "
                    f"fallback_reason=`{((parse_fallback or (None, None, {}))[2].get('replan_audit') or {}).get('fallback_reason')}`"
                    if parse_fallback is not None
                    else "- _n/a_"
                ),
                "",
                "## 3) LLM 计划通过校验但后续 verification_replan 仍失败",
                f"- 文件：[`case_validated_repair_failed.json`](../../results/demos/hybrid_replanner_cases/case_validated_repair_failed.json)",
                f"- {notes['validated']}",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
