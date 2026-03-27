"""Same-task manifest rows are JSON-serializable and carry required keys."""

from __future__ import annotations

import json
from pathlib import Path

from embodied_scene_agent.data.calvin_debug_alignment import (
    SUBSET_NAME_DEFAULT,
    same_task_subset_splits,
    write_same_task_manifests,
)
from embodied_scene_agent.data.calvin_debug_dataset import (
    default_calvin_debug_root,
    instruction_pool_from_manifest,
)
from embodied_scene_agent.utils.paths import repo_root


def test_same_task_manifest_schema(tmp_path: Path) -> None:
    root = repo_root()
    manifest = root / "data" / "processed" / "calvin_real_subset" / "manifest.jsonl"
    pool = instruction_pool_from_manifest(manifest)
    dbg = default_calvin_debug_root()
    train_dir = dbg / "training"
    val_dir = dbg / "validation"
    if not train_dir.is_dir():
        return
    splits = same_task_subset_splits(
        train_dir,
        val_dir,
        pool=pool,
        window=40,
        stride=20,
        max_groups_train=1,
        max_groups_val=1,
        max_groups_test=1,
    )
    write_same_task_manifests(tmp_path, splits, subset_name=SUBSET_NAME_DEFAULT)
    p = tmp_path / "train_manifest.jsonl"
    assert p.is_file()
    line = p.read_text(encoding="utf-8").strip().split("\n")[0]
    row = json.loads(line)
    for k in (
        "sample_id",
        "source_npz",
        "temporal_group_id",
        "instruction",
        "alignment_mode",
        "subset_name",
        "metadata",
    ):
        assert k in row
    assert row["alignment_mode"] == "same_task_subset"
