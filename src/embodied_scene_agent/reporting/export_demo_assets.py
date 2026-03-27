"""Export success / failure / recovery demo folders under ``results/demos/`` (blueprint B2)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from embodied_scene_agent.memory.builder import SceneMemoryBuilder
from embodied_scene_agent.pipeline.v0_loop import run_v0_episode
from embodied_scene_agent.utils.paths import repo_root
from embodied_scene_agent.visualization.episode_viz import (
    trace_to_demo_case_summary,
    write_memory_snapshot,
    write_scene_graph_dot,
)
from embodied_scene_agent.visualization.render_episode import write_episode


def _mem_from_scene_dict(d: dict) -> SceneMemory:
    raw_objs = d.get("objects") or {}
    if isinstance(raw_objs, dict):
        objects = [{**{"id": k}, **v} for k, v in raw_objs.items()]
    else:
        objects = list(raw_objs)
    rels = d.get("relations") or []
    if rels and isinstance(rels[0], dict):
        pass
    else:
        rels = []
    return SceneMemoryBuilder.from_teacher_payload(
        {
            "objects": objects,
            "relations": rels,
            "frame_id": d.get("frame_id"),
        }
    )


def _export_trace_bundle(trace, out: Path, label: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    write_episode(out / f"{label}_trace.json", trace)
    summary = {
        "instruction": trace.instruction,
        "success": trace.success,
        "replan_count": trace.replan_count,
        "final_message": trace.final_message,
        "steps": trace.steps,
    }
    trace_to_demo_case_summary(summary, case_label=label, out_path=out / "case_summary.md")
    (out / "episode_log_steps.json").write_text(
        json.dumps(trace.steps, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    for i, st in enumerate(trace.steps):
        mb = st.get("scene_memory_before")
        ma = st.get("scene_memory_after_first")
        sub = out / f"step_{i}"
        sub.mkdir(parents=True, exist_ok=True)
        if isinstance(mb, dict) and mb.get("objects"):
            mem_b = _mem_from_scene_dict(mb)
            write_memory_snapshot(sub, mem_b, "before")
            write_scene_graph_dot(sub, mem_b, "before")
        if isinstance(ma, dict) and ma.get("objects"):
            mem_a = _mem_from_scene_dict(ma)
            write_memory_snapshot(sub, mem_a, "after")
            write_scene_graph_dot(sub, mem_a, "after")
        mar = st.get("scene_memory_after_replan")
        if isinstance(mar, dict) and mar.get("objects"):
            mem_ar = _mem_from_scene_dict(mar)
            write_memory_snapshot(sub, mem_ar, "after_replan")
            write_scene_graph_dot(sub, mem_ar, "after_replan")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    args, _unknown = parser.parse_known_args()
    root = args.root or repo_root()
    demos = root / "results" / "demos"
    demos.mkdir(parents=True, exist_ok=True)

    t_ok = run_v0_episode("put the red block in the drawer", max_steps=16, forced_grasp_failures=0)
    _export_trace_bundle(t_ok, demos / "success_put_block", "success")

    t_fail = run_v0_episode(
        "put the red block in the drawer", max_steps=4, forced_grasp_failures=99
    )
    _export_trace_bundle(t_fail, demos / "failure_no_recovery", "failure_stalled")

    t_rec = run_v0_episode(
        "put the red block in the drawer", max_steps=24, forced_grasp_failures=1
    )
    _export_trace_bundle(t_rec, demos / "failure_then_recovery", "recovery")

    print(f"[export_demo_assets] wrote under {demos}")


if __name__ == "__main__":
    main()
