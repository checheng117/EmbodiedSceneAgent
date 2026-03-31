from __future__ import annotations

import json

from embodied_scene_agent.utils.experiment import (
    normalize_experiment_id,
    read_run_artifact_status,
    write_run_artifacts,
)


def test_normalize_experiment_id_respects_explicit() -> None:
    assert normalize_experiment_id(prefix="e2_mock", explicit_id="manual_id") == "manual_id"


def test_write_and_read_run_artifacts(tmp_path) -> None:
    out_dir = tmp_path / "results" / "experiments" / "e2_ablation" / "e2_mock_test"
    paths = write_run_artifacts(
        out_dir,
        root=tmp_path,
        experiment_id="e2_mock_test",
        entrypoint="python -m embodied_scene_agent.evaluation.run_ablation_e2",
        config_snapshot={"backend": "mock", "episodes": 4, "max_steps": 12},
        argv=["python", "-m", "embodied_scene_agent.evaluation.run_ablation_e2"],
        notes=["unit test"],
    )
    assert paths["config_snapshot_path"].endswith("config.snapshot.json")
    assert paths["run_manifest_path"].endswith("run_manifest.json")

    status = read_run_artifact_status(tmp_path, out_dir)
    assert status["status"] == "ready"
    assert status["latest_dir"] == "results/experiments/e2_ablation/e2_mock_test"

    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["experiment_id"] == "e2_mock_test"
    assert manifest["config_snapshot_path"] == "results/experiments/e2_ablation/e2_mock_test/config.snapshot.json"
