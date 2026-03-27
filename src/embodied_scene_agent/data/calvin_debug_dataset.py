"""Official CALVIN ``calvin_debug_dataset`` paths, enumeration, and npz loading (no benchmark claims)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from embodied_scene_agent.utils.paths import repo_root


def default_calvin_debug_root() -> Path:
    """Default: ``<repo>/data/raw/calvin_official/dataset/calvin_debug_dataset``."""
    return (repo_root() / "data" / "raw" / "calvin_official" / "dataset" / "calvin_debug_dataset").resolve()


def debug_split_dir(root: Path | None, split: str) -> Path:
    s = split.lower()
    if s not in ("training", "validation"):
        raise ValueError("split must be 'training' or 'validation'")
    base = default_calvin_debug_root() if root is None else Path(root).resolve()
    return base / s


def iter_npz_frames(split_dir: Path) -> Iterator[Path]:
    """Sorted ``episode_*.npz`` paths under a split directory."""
    if not split_dir.is_dir():
        return
    for p in sorted(split_dir.glob("episode_*.npz")):
        if p.is_file():
            yield p


def load_debug_npz(path: Path) -> dict[str, np.ndarray]:
    z = np.load(path, allow_pickle=True)
    try:
        return {k: z[k] for k in z.files}
    finally:
        z.close()


def load_ep_start_end_ids(split_dir: Path) -> np.ndarray | None:
    """``ep_start_end_ids.npy`` if present (shape ``(n_episodes, 2)`` start/end frame indices)."""
    p = split_dir / "ep_start_end_ids.npy"
    if not p.is_file():
        return None
    return np.load(p, allow_pickle=False)


def npz_path_for_frame_index(split_dir: Path, frame_index: int, *, n_digits: int = 7) -> Path:
    """Filename pattern ``episode_{idx:07d}.npz`` as used in official debug release."""
    return split_dir / f"episode_{frame_index:0{n_digits}d}.npz"


def instruction_pool_from_manifest(manifest_path: Path, *, max_instructions: int = 500) -> list[str]:
    """Distinct instructions from ``manifest.jsonl`` (CALVIN YAML-derived); fallback if missing."""
    if not manifest_path.is_file():
        return ["Put the red block in the drawer."]
    seen: set[str] = set()
    out: list[str] = []
    with manifest_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            inst = str(row.get("instruction") or "").strip()
            if not inst or inst in seen:
                continue
            seen.add(inst)
            out.append(inst)
            if len(out) >= max_instructions:
                break
    return out or ["Put the red block in the drawer."]
