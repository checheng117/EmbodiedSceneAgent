"""Force one UNKNOWN_FAILURE step so hybrid LLM replan path runs (real model load + generate)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from embodied_scene_agent.planner.base import BasePlanner
from embodied_scene_agent.planner.schema import PlannerInput, PlannerOutput
from embodied_scene_agent.planner.rule_based import RuleBasedPlanner
from embodied_scene_agent.pipeline.v0_loop import run_v0_episode
from embodied_scene_agent.utils.paths import repo_root


def _fallback_stats_from_traces(traces: list) -> dict:
    from collections import Counter

    reason_c: Counter[str] = Counter()
    stage_c: Counter[str] = Counter()
    kind_c: Counter[str] = Counter()
    llm_calls = 0
    parse_ok = 0
    validated = 0
    alias_normalization_count = 0
    invalid_skill_count = 0
    for tr in traces:
        for st in tr.steps:
            a = st.get("replan_audit")
            if not isinstance(a, dict) or not a.get("llm_replanner_called"):
                continue
            llm_calls += 1
            if a.get("replanner_parse_ok") is True:
                parse_ok += 1
            if a.get("revised_plan_validated") is True:
                validated += 1
            if a.get("skill_alias_normalized_from"):
                alias_normalization_count += 1
            if a.get("replanner_parse_error_kind") == "invalid_skill":
                invalid_skill_count += 1
            fr = a.get("fallback_reason")
            if fr:
                reason_c[str(fr)[:200]] += 1
            stg = a.get("fallback_stage")
            if stg:
                stage_c[str(stg)] += 1
            pk = a.get("replanner_parse_error_kind")
            if pk:
                kind_c[str(pk)] += 1
    return {
        "llm_replanner_calls": llm_calls,
        "replanner_parse_ok_count": parse_ok,
        "revised_plan_validated_count": validated,
        "fallback_reason_counts": dict(reason_c),
        "fallback_stage_counts": dict(stage_c),
        "parse_error_kind_counts": dict(kind_c),
        "alias_normalization_count": alias_normalization_count,
        "invalid_skill_count": invalid_skill_count,
    }


class _FirstStepUnknownSkillPlanner(BasePlanner):
    """First plan uses an unhandled skill → StateDiffVerifier returns UNKNOWN_FAILURE."""

    def __init__(self) -> None:
        self._base = RuleBasedPlanner()
        self._n = 0

    def plan(self, inp: PlannerInput) -> PlannerOutput:
        self._n += 1
        if self._n == 1:
            b = self._base.plan(inp)
            return PlannerOutput(
                task="smoke_unknown_skill",
                subgoal="deliberate verifier-unknown skill for hybrid smoke",
                target_object=b.target_object,
                skill="diagnostic_verifier_unknown",
                success_check="noop",
                fallback="none",
                reasoning="hybrid_replanner_smoke",
                confidence=0.1,
            )
        return self._base.plan(inp)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    args, _ = parser.parse_known_args()
    root = args.root or repo_root()
    eid = datetime.now(timezone.utc).strftime("hybrid_replanner_%Y%m%dT%H%M%SZ")
    out_dir = root / "results" / "experiments" / "hybrid_replanner_smoke" / eid
    out_dir.mkdir(parents=True, exist_ok=True)

    trace = run_v0_episode(
        "put the red block in the drawer",
        max_steps=8,
        forced_grasp_failures=0,
        verifier_mode="verifier_plus_replan",
        replanner_mode="hybrid",
        experiment_id=eid,
        planner=_FirstStepUnknownSkillPlanner(),
    )

    row = {
        "experiment_id": eid,
        "success": trace.success,
        "replan_count": trace.replan_count,
        "final_message": trace.final_message,
        "steps": len(trace.steps),
    }
    (out_dir / "per_episode.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (out_dir / "trace_full.json").write_text(
        json.dumps(
            {
                "instruction": trace.instruction,
                "success": trace.success,
                "replan_count": trace.replan_count,
                "final_message": trace.final_message,
                "steps": trace.steps,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    audit = None
    for st in trace.steps:
        if st.get("replan_audit"):
            audit = st["replan_audit"]
            break

    summary = [
        f"# Hybrid replanner smoke ({eid})",
        "",
        "_Real LLM forward when transformers+model load succeed; otherwise audit shows fallback_reason._",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(row, indent=2),
        "```",
        "",
        "## First replan audit",
        "",
        "```json",
        json.dumps(audit or {}, indent=2),
        "```",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary), encoding="utf-8")

    fb = _fallback_stats_from_traces([trace])
    (out_dir / "fallback_stats.json").write_text(
        json.dumps(fb, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(json.dumps({"wrote": str(out_dir), "replan_audit": audit, "fallback_stats": fb}, indent=2))


if __name__ == "__main__":
    main()
