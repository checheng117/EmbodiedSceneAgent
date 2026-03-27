"""Smoke: debug dataset vector layout → teacher bundle → SceneMemory."""

from __future__ import annotations

import numpy as np
import pytest

from embodied_scene_agent.data.calvin_debug_dataset import (
    default_calvin_debug_root,
    iter_npz_frames,
    load_debug_npz,
)
from embodied_scene_agent.perception.calvin_debug_vector_teacher import (
    build_initial_observation_from_debug_vectors,
)
from embodied_scene_agent.perception.calvin_teacher import CalvinTeacherStateAdapter


def test_vector_teacher_produces_scene_memory() -> None:
    ro = np.zeros(15, dtype=np.float64)
    ro[6] = 0.08
    ro[14] = 1.0
    so = np.zeros(24, dtype=np.float64)
    so[6:9] = [0.1, 0.2, 0.3]
    bundle = build_initial_observation_from_debug_vectors(ro, so, "Put the red block in the drawer.")
    assert "calvin_teacher_v0" in bundle
    mem = CalvinTeacherStateAdapter().to_scene_memory(
        "Put the red block in the drawer.", bundle
    )
    d = mem.to_json_dict()
    assert "objects" in d


@pytest.mark.skipif(
    not (default_calvin_debug_root() / "training").is_dir(),
    reason="calvin_debug_dataset not present under data/raw/calvin_official/",
)
def test_load_first_debug_npz_if_present() -> None:
    split = default_calvin_debug_root() / "training"
    paths = list(iter_npz_frames(split))
    assert paths, "expected episode_*.npz under training/"
    data = load_debug_npz(paths[0])
    assert "robot_obs" in data and "scene_obs" in data
    build_initial_observation_from_debug_vectors(
        data["robot_obs"], data["scene_obs"], "test instruction", npz_stem=paths[0].stem
    )
