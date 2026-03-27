"""CalvinEnvAdapter with mock fixture."""

from __future__ import annotations

import json
from pathlib import Path

from embodied_scene_agent.envs.calvin import CalvinEnvAdapter
from embodied_scene_agent.utils.paths import repo_root


def _fixture() -> Path:
    return repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json"


def test_calvin_env_loads_fixture_and_injects_instruction() -> None:
    env = CalvinEnvAdapter(fixture_path=_fixture())
    out = env.reset("Open the drawer.")
    assert out["instruction"] == "Open the drawer."
    obs = env.get_teacher_state()
    assert "calvin_teacher_v0" in obs
    assert obs["calvin_teacher_v0"]["language"]["instruction"] == "Open the drawer."


def test_ingest_observation_roundtrip() -> None:
    env = CalvinEnvAdapter(initial_observation=json.loads(_fixture().read_text(encoding="utf-8")))
    env.reset("task")
    env.ingest_observation(json.loads(_fixture().read_text(encoding="utf-8")))
    assert "calvin_teacher_v0" in env.get_teacher_state()
