"""Export MockEmbodiedEnv + v0_loop traces to planner SFT JSONL (v1 schema)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Iterator

from embodied_scene_agent.pipeline.v0_loop import EpisodeTrace, run_v0_episode
from embodied_scene_agent.training.agent_prompt import (
    DEFAULT_TOOL_DEFINITIONS,
    build_user_prompt,
    format_plan_block,
    format_recovery_supervision,
)


PLANNER_SFT_V1 = "planner_sft/v1"


def _trajectory_labels(
    *,
    step_index: int,
    total_steps: int,
    has_replan: bool,
) -> str:
    """Per-step label: recovery overrides; long-horizon follow-ups are multi_step; else normal."""
    if has_replan:
        return "recovery"
    if total_steps >= 3 and step_index >= 1:
        return "multi_step"
    return "normal"


def iter_rows_from_v0_trace(
    trace: EpisodeTrace,
    *,
    source_type: str,
    split: str,
    episode_id: str,
    experiment_id: str = "",
    forced_grasp_failures_setting: int = 0,
    rollout_backend: str = "mock_symbolic_v0_loop",
    extra_metadata: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    total = len(trace.steps)
    for si, step in enumerate(trace.steps):
        sm_before = step.get("scene_memory_before") or {}
        # Reconstruct history as list of completed subgoals up to this step (approx from prior steps).
        history: list[str] = []
        for j in range(si):
            pj = trace.steps[j].get("plan") or {}
            vr = trace.steps[j].get("verification") or {}
            vr2 = trace.steps[j].get("verification_replan")
            if vr.get("success"):
                history.append(str(pj.get("subgoal", "")))
            elif isinstance(vr2, dict) and vr2.get("success"):
                rj = trace.steps[j].get("replan") or {}
                history.append(str(rj.get("subgoal", "")))

        failure_log: list[str] = []
        if si > 0:
            prev = trace.steps[si - 1]
            pv = prev.get("verification") or {}
            if not pv.get("success"):
                failure_log.append(f"failed:{pv.get('failure_type')}:{pv.get('details', '')}")
            pv2 = prev.get("verification_replan")
            if isinstance(pv2, dict) and not pv2.get("success"):
                failure_log.append(
                    f"replan_failed:{pv2.get('failure_type')}:{pv2.get('details', '')}"
                )

        plan = step.get("plan") or {}
        replan = step.get("replan")
        ver = step.get("verification") or {}
        sr = step.get("skill_result") or {}

        has_replan = replan is not None
        traj = _trajectory_labels(
            step_index=si,
            total_steps=total,
            has_replan=has_replan,
        )

        user_text = build_user_prompt(
            instruction=trace.instruction,
            scene_memory=sm_before,
            history=history,
            failure_log=failure_log,
        )

        if has_replan and replan is not None:
            assistant_text = format_recovery_supervision(
                initial_plan=plan,
                verification=ver,
                skill_result=sr,
                revised_plan=replan,
            )
        else:
            assistant_text = format_plan_block(plan)

        sample_id = f"{episode_id}::step{si}::{trace.trace_id or uuid.uuid4().hex[:8]}"

        row: dict[str, Any] = {
            "sample_id": sample_id,
            "schema_version": PLANNER_SFT_V1,
            "source_type": source_type,
            "trajectory_type": traj,
            "split": split,
            "task": trace.instruction,
            "instruction": trace.instruction,
            "serialized_scene_memory": json.dumps(sm_before, ensure_ascii=False),
            "available_tools": DEFAULT_TOOL_DEFINITIONS,
            "user_prompt": user_text,
            "target_text": assistant_text,
            "messages": [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_text},
            ],
            "metadata": {
                "episode_id": episode_id,
                "step_index": si,
                "episode_step_count": total,
                "trace_id": trace.trace_id,
                "experiment_id": experiment_id or None,
                "episode_success": trace.success,
                "replan_on_step": has_replan,
                "forced_grasp_failures_setting": forced_grasp_failures_setting,
                "rollout_backend": rollout_backend,
                **(extra_metadata or {}),
            },
        }
        yield row


def run_export_episode(
    instruction: str,
    *,
    episode_id: str,
    split: str,
    forced_grasp_failures: int,
    max_steps: int,
    source_type: str = "real_subset_mock_rollout",
) -> tuple[EpisodeTrace, list[dict[str, Any]]]:
    trace = run_v0_episode(
        instruction,
        max_steps=max_steps,
        forced_grasp_failures=forced_grasp_failures,
    )
    rows = list(
        iter_rows_from_v0_trace(
            trace,
            source_type=source_type,
            split=split,
            episode_id=episode_id,
            forced_grasp_failures_setting=forced_grasp_failures,
        )
    )
    return trace, rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
