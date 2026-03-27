"""Per-episode demo assets: tables, graphviz, state diffs (blueprint B1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.visualization.render_scene_graph import render_scene_graph


def object_table_markdown(mem: SceneMemory) -> str:
    lines = [
        "| object_id | display_name | class | position (x,y,z) | state_tags | vis | conf |",
        "|---|---|---|---|---|---|---|",
    ]
    for oid, o in sorted(mem.objects.items()):
        pos = f"{o.position[0]:.3f},{o.position[1]:.3f},{o.position[2]:.3f}"
        tags = ",".join(o.state_tags)
        dn = o.display_name or o.name or oid
        lines.append(
            f"| `{oid}` | {dn} | {o.class_name} | {pos} | {tags} | {o.visibility:.2f} | {o.confidence:.2f} |"
        )
    return "\n".join(lines)


def state_diff_markdown(before: SceneMemory, after: SceneMemory, title: str = "State diff") -> str:
    lines = [f"## {title}", ""]
    all_ids = sorted(set(before.objects) | set(after.objects))
    for oid in all_ids:
        b = before.objects.get(oid)
        a = after.objects.get(oid)
        if b is None:
            lines.append(f"- **{oid}**: *(new in after)* `{a.state_tags if a else []}`")
            continue
        if a is None:
            lines.append(f"- **{oid}**: *(removed after)* was `{b.state_tags}`")
            continue
        if b.state_tags != a.state_tags or b.position != a.position:
            lines.append(
                f"- **{oid}**: tags `{b.state_tags}` → `{a.state_tags}` ; "
                f"pos `{b.position}` → `{a.position}`"
            )
    if len(lines) == 2:
        lines.append("_No object-level diff detected._")
    return "\n".join(lines)


def write_memory_snapshot(out_dir: Path, mem: SceneMemory, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{name}_memory_snapshot.json"
    p.write_text(json.dumps(mem.to_json_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def write_scene_graph_dot(out_dir: Path, mem: SceneMemory, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{name}_scene_graph.dot"
    p.write_text(render_scene_graph(mem, fmt="graphviz"), encoding="utf-8")
    return p


def export_step_visual_bundle(
    out_dir: Path,
    *,
    mem_before: SceneMemory,
    mem_after: SceneMemory,
    prefix: str = "step",
) -> dict[str, str]:
    """Write JSON + graphviz + object table + diff; returns relative paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    paths["memory_before_json"] = write_memory_snapshot(
        out_dir, mem_before, f"{prefix}_before"
    ).name
    paths["memory_after_json"] = write_memory_snapshot(out_dir, mem_after, f"{prefix}_after").name
    write_scene_graph_dot(out_dir, mem_before, f"{prefix}_before")
    write_scene_graph_dot(out_dir, mem_after, f"{prefix}_after")
    paths["object_table_before_md"] = f"{prefix}_object_table_before.md"
    (out_dir / paths["object_table_before_md"]).write_text(
        object_table_markdown(mem_before), encoding="utf-8"
    )
    paths["state_diff_md"] = f"{prefix}_state_diff.md"
    (out_dir / paths["state_diff_md"]).write_text(
        state_diff_markdown(mem_before, mem_after), encoding="utf-8"
    )
    return paths


def trace_to_demo_case_summary(
    trace_summary: dict[str, Any],
    *,
    case_label: str,
    out_path: Path,
) -> None:
    lines = [
        f"# Demo case: {case_label}",
        "",
        f"- success: `{trace_summary.get('success')}`",
        f"- final_message: `{trace_summary.get('final_message')}`",
        f"- replan_count: `{trace_summary.get('replan_count')}`",
        f"- instruction: {trace_summary.get('instruction', '')[:500]!r}",
        "",
        "## Timeline",
        "",
    ]
    for i, st in enumerate(trace_summary.get("steps") or []):
        lines.append(f"### Step {i}")
        plan = st.get("plan") or {}
        ver = st.get("verification") or {}
        lines.append(f"- skill: `{plan.get('skill')}` target: `{plan.get('target_object')}`")
        lines.append(f"- verifier success: `{ver.get('success')}` failure_type: `{ver.get('failure_type')}`")
        if st.get("replan"):
            lines.append(f"- replanned: `{st['replan'].get('skill')}`")
        lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
