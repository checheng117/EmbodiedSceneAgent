from __future__ import annotations

from pathlib import Path

from embodied_scene_agent.evaluation.rlbench_smoke import run_layered_stages
from embodied_scene_agent.utils.paths import repo_root


def test_run_layered_stages_fixture_file_structure() -> None:
    root = repo_root()
    payload, episode_step, bridge_mode = run_layered_stages(
        root=root, task="ReachTarget", mode="fixture_file", headless=True
    )
    assert "layer_status" in payload
    assert "stages" in payload
    assert payload["layer_status"]["import"] in (True, False)
    assert "simulator_locate" in payload["layer_status"]
    assert "deepest_reached_stage" in payload
    assert "blocker_summary" in payload
    assert bridge_mode == "fixture_file"
    assert episode_step is not None
    assert episode_step.get("schema_version") == "esa_episode_log/v1"


def test_run_layered_stages_sim_import_only_no_fixture_episode() -> None:
    root = repo_root()
    payload, episode_step, _bm = run_layered_stages(
        root=root, task="ReachTarget", mode="sim_import_only", headless=True
    )
    assert "sim_import_only" in payload["stages"]
    if not payload["import_ok"]:
        assert episode_step is None
