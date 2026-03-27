"""Structure checks for build_planner_data calvin_debug_real (skips if no dataset)."""

from __future__ import annotations

from pathlib import Path

import pytest

from embodied_scene_agent.data.calvin_debug_dataset import default_calvin_debug_root
from embodied_scene_agent.training import build_planner_data as bpd


@pytest.mark.skipif(
    not (default_calvin_debug_root() / "training").is_dir(),
    reason="calvin_debug_dataset not present",
)
def test_calvin_debug_real_export_writes_jsonl(tmp_path: Path) -> None:
    ns = type(
        "Args",
        (),
        {
            "manifest": Path(__file__).resolve().parents[1]
            / "data"
            / "processed"
            / "calvin_real_subset"
            / "manifest.jsonl",
            "out_dir": tmp_path,
            "seed": 0,
            "rollout_max_steps": 4,
            "calvin_debug_root": None,
            "max_train_samples": 2,
            "max_val_samples": 1,
            "max_test_samples": 1,
            "stats_md": tmp_path / "stats.md",
            "experiment_id": "pytest_calvin_debug",
            "alignment_mode": "pooled_manifest",
            "alignment_window": 40,
            "alignment_stride": 20,
            "output_basename": "calvin_debug_real",
            "same_task_manifest_dir": None,
            "same_task_max_groups_train": 8,
            "same_task_max_groups_val": 4,
            "same_task_max_groups_test": 4,
        },
    )()
    bpd.run_calvin_debug_real_export(ns)
    for name in ("calvin_debug_real_train.jsonl", "calvin_debug_real_val.jsonl", "calvin_debug_real_test.jsonl"):
        p = tmp_path / name
        assert p.is_file(), f"missing {name}"
        text = p.read_text(encoding="utf-8").strip()
        if text:
            line = text.split("\n")[0]
            assert "calvin_debug_real" in line
            assert "sample_id" in line
    assert (tmp_path / "stats.md").is_file()
