from __future__ import annotations

from pathlib import Path

import json

from embodied_scene_agent.envs.rlbench_adapter import build_rlbench_stack_diagnosis, summarize_rlbench_blocker


def test_build_rlbench_stack_diagnosis_schema() -> None:
    d = build_rlbench_stack_diagnosis(probe_sim=False)
    assert d["python_executable"]
    assert "import_status" in d
    assert "rlbench" in d["import_status"]
    assert "pip_distribution_probe" in d
    assert d["deepest_reached_stage"]
    assert isinstance(d["blocker_summary"], str)
    assert "layers" in d
    assert "env_create_probe" in d


def test_summarize_rlbench_blocker_import_fail() -> None:
    st, msg = summarize_rlbench_blocker(
        import_rlbench_ok=False,
        import_pyrep_ok=False,
        sim_locate_ok=False,
        env_attempted=False,
        env_create_ok=None,
        reset_attempted=False,
        reset_ok=None,
        import_rlbench_message="no module",
        import_pyrep_message="no module",
        env_message="",
        reset_message="",
    )
    assert st == "import_fail"


def test_rlbench_stack_diagnosis_json_file_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "rlbench_stack_diagnosis.json"
    d = build_rlbench_stack_diagnosis(probe_sim=False)
    out.write_text(json.dumps(d, indent=2), encoding="utf-8")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    for k in (
        "deepest_reached_stage",
        "blocker_summary",
        "env_create_probe",
        "reset_probe",
        "import_status",
        "pip_distribution_probe",
    ):
        assert k in loaded
