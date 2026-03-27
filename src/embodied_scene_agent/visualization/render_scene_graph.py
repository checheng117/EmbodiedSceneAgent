"""Scene graph export (text / graphviz / JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from embodied_scene_agent.memory.schema import SceneMemory


def render_scene_graph(
    memory: SceneMemory,
    fmt: Literal["text", "json", "graphviz"] = "text",
) -> str:
    """
    Render scene memory for debugging.

    TODO: optional pygraphviz / graphviz CLI integration for PNG export.
    """
    if fmt == "json":
        return json.dumps(memory.to_json_dict(), indent=2)
    if fmt == "graphviz":
        lines = ["digraph G {"]
        for oid, obj in memory.objects.items():
            label = f"{oid}\\n{obj.name or obj.class_name}"
            lines.append(f'  "{oid}" [label="{label}"];')
        for rel in memory.relations:
            lines.append(f'  "{rel.subject_id}" -> "{rel.object_id}" [label={rel.relation.value}];')
        lines.append("}")
        return "\n".join(lines)
    return memory.pretty_print()


def write_scene_graph(path: Path, memory: SceneMemory, fmt: Literal["text", "json", "graphviz"] = "text") -> None:
    """Write render output to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_scene_graph(memory, fmt=fmt), encoding="utf-8")
