"""
CALVIN official debug npz: temporal grouping and instruction assignment helpers.

**Not** official CALVIN language alignment — debug zip lacks per-frame task labels.
``grouped_sequence`` / ``same_task_subset`` are **same-task-like** batches for interpretability only.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Literal

from embodied_scene_agent.data.calvin_debug_dataset import (
    iter_npz_frames,
    npz_path_for_frame_index,
)
from embodied_scene_agent.utils.paths import repo_root

AlignmentMode = Literal["pooled_manifest", "grouped_sequence", "same_task_subset"]

WINDOW_DEFAULT = 40
MIN_FRAMES_PER_GROUP = 8
STRIDE_DEFAULT = 20
SUBSET_NAME_DEFAULT = "calvin_debug_same_task_like_v1"


def stable_instruction_for_group(group_key: str, pool: list[str]) -> str:
    h = int(hashlib.sha256(group_key.encode()).hexdigest(), 16)
    return pool[h % len(pool)]


def frame_indices_sorted(split_dir: Path) -> list[int]:
    out: list[int] = []
    for p in iter_npz_frames(split_dir):
        try:
            idx = int(p.stem.split("_", 1)[1])
        except (IndexError, ValueError):
            continue
        out.append(idx)
    return sorted(set(out))


def consecutive_runs(indices: list[int]) -> list[list[int]]:
    if not indices:
        return []
    runs: list[list[int]] = [[indices[0]]]
    for x in indices[1:]:
        if x == runs[-1][-1] + 1:
            runs[-1].append(x)
        else:
            runs.append([x])
    return runs


def temporal_windows_in_run(run: list[int], *, window: int, stride: int) -> list[list[int]]:
    if len(run) < MIN_FRAMES_PER_GROUP:
        return []
    wins: list[list[int]] = []
    if len(run) >= window:
        i = 0
        while i + window <= len(run):
            wins.append(run[i : i + window])
            i += max(1, stride)
    if not wins:
        wins.append(run[: max(MIN_FRAMES_PER_GROUP, min(window, len(run)))])
    return wins


def grouped_path_assignments(
    split_dir: Path,
    *,
    pool: list[str],
    window: int = WINDOW_DEFAULT,
    stride: int = STRIDE_DEFAULT,
    max_paths: int | None = None,
) -> list[dict[str, Any]]:
    """One row per existing npz in each temporal window; shared instruction per window."""
    split_label = split_dir.name
    runs = consecutive_runs(frame_indices_sorted(split_dir))
    rows: list[dict[str, Any]] = []
    for ri, run in enumerate(runs):
        for wi, chunk in enumerate(temporal_windows_in_run(run, window=window, stride=stride)):
            gid = f"{split_label}_run{ri}_w{wi}_{chunk[0]:07d}_{chunk[-1]:07d}"
            inst = stable_instruction_for_group(gid, pool)
            ep_key = f"{split_label}_run{ri}"
            for fi in chunk:
                p = npz_path_for_frame_index(split_dir, fi)
                if not p.is_file():
                    continue
                rows.append(
                    {
                        "path": p.resolve(),
                        "temporal_group_id": gid,
                        "npz_group_key": gid,
                        "clip_key": gid,
                        "episode_key": ep_key,
                        "instruction": inst,
                        "split_label": split_label,
                    }
                )
                if max_paths is not None and len(rows) >= max_paths:
                    return rows
    return rows


def pooled_path_assignments(
    split_dir: Path,
    *,
    pool: list[str],
    max_paths: int,
    rng,
) -> list[dict[str, Any]]:
    all_p = [p.resolve() for p in iter_npz_frames(split_dir)]
    if not all_p:
        return []
    k = min(max_paths, len(all_p))
    pick = sorted(rng.sample(all_p, k=k), key=lambda x: x.name)
    rows: list[dict[str, Any]] = []
    for i, p in enumerate(pick):
        stem = p.stem
        gid = f"pooled_rr_{split_dir.name}_{stem}"
        rows.append(
            {
                "path": p,
                "temporal_group_id": gid,
                "npz_group_key": stem,
                "clip_key": stem,
                "episode_key": f"pooled_{split_dir.name}",
                "instruction": pool[i % len(pool)],
                "split_label": split_dir.name,
            }
        )
    return rows


def rows_by_group_ordered(
    split_dir: Path, pool: list[str], window: int, stride: int
) -> list[tuple[str, list[dict[str, Any]]]]:
    flat = grouped_path_assignments(
        split_dir, pool=pool, window=window, stride=stride, max_paths=None
    )
    order: list[str] = []
    by_g: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in flat:
        g = r["temporal_group_id"]
        if g not in by_g:
            order.append(g)
        by_g[g].append(r)
    return [(g, by_g[g]) for g in order]


def same_task_subset_splits(
    train_dir: Path,
    val_dir: Path,
    *,
    pool: list[str],
    window: int = WINDOW_DEFAULT,
    stride: int = STRIDE_DEFAULT,
    max_groups_train: int = 8,
    max_groups_val: int = 4,
    max_groups_test: int = 4,
) -> dict[str, list[dict[str, Any]]]:
    train_pairs = rows_by_group_ordered(train_dir, pool, window, stride)
    train_ids = [p[0] for p in train_pairs[:max_groups_train]]
    train_map = dict(train_pairs)
    train_rows = [r for gid in train_ids for r in train_map[gid]]

    val_pairs = rows_by_group_ordered(val_dir, pool, window, stride)
    val_ids = [p[0] for p in val_pairs[:max_groups_val]]
    test_ids = [p[0] for p in val_pairs[max_groups_val : max_groups_val + max_groups_test]]
    vmap = dict(val_pairs)
    val_rows = [r for gid in val_ids for r in vmap.get(gid, [])]
    test_rows = [r for gid in test_ids for r in vmap.get(gid, [])]

    return {"train": train_rows, "val": val_rows, "test": test_rows}


def write_same_task_manifests(
    out_dir: Path,
    splits: dict[str, list[dict[str, Any]]],
    *,
    alignment_mode: AlignmentMode = "same_task_subset",
    subset_name: str = SUBSET_NAME_DEFAULT,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    root = repo_root().resolve()
    for split_name, rows in splits.items():
        path = out_dir / f"{split_name}_manifest.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for r in rows:
                p = Path(r["path"])
                try:
                    rel_npz = str(p.resolve().relative_to(root))
                except ValueError:
                    rel_npz = str(p.resolve())
                obj = {
                    "sample_id": f"{subset_name}::{r['temporal_group_id']}::{p.stem}",
                    "source_npz": str(p.resolve()),
                    "temporal_group_id": r["temporal_group_id"],
                    "instruction": r["instruction"],
                    "alignment_mode": alignment_mode,
                    "subset_name": subset_name,
                    "metadata": {
                        "source_npz_relpath": rel_npz,
                        "npz_group_key": r["npz_group_key"],
                        "clip_key": r["clip_key"],
                        "episode_key": r["episode_key"],
                        "lineage_note": (
                            "Consecutive-frame windows + stable-hash instruction from YAML pool; "
                            "same-task-like, not official CALVIN task labels."
                        ),
                    },
                }
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_manifest_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def scenarios_from_manifest_rows(
    rows: list[dict[str, Any]],
    *,
    n_episodes: int,
    start_index: int = 0,
) -> list[dict[str, Any]]:
    """One row per distinct temporal_group_id (file order); then slice [start_index : start_index + n)."""
    seen: set[str] = set()
    picked: list[dict[str, Any]] = []
    for r in rows:
        g = str(r.get("temporal_group_id") or "")
        if not g or g in seen:
            continue
        seen.add(g)
        picked.append(r)
    return picked[start_index : start_index + max(0, n_episodes)]
