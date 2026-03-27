"""Build markdown/HTML summaries from experiment outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_markdown_stub(path: Path, title: str, extra: dict[str, Any] | None = None) -> None:
    """Write a minimal report skeleton (no fabricated benchmark results)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}",
        "",
        "This report is auto-generated. **Do not** fill benchmark numbers without real runs.",
        "",
        "```json",
        json.dumps(extra or {}, indent=2),
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
