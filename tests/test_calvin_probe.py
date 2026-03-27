"""CALVIN live probe returns structured dict without claiming success."""

from __future__ import annotations

from embodied_scene_agent.envs.calvin_probe import (
    attempt_play_table_reset,
    build_calvin_live_probe_report,
)


def test_attempt_play_table_reset_returns_dict():
    r = attempt_play_table_reset(None)
    assert isinstance(r, dict)
    assert "import_play_table" in r


def test_build_calvin_live_probe_report_shape():
    r = build_calvin_live_probe_report(
        dotenv_file_loaded=False,
        hf_token_status="HF_TOKEN is not set (test).",
        factory_resolve_meta={"status": "unset", "spec": None},
        env_factory=None,
        try_step_smoke=False,
    )
    assert r["disclaimer"] == "NOT_A_BENCHMARK_RUN"
    assert "calvin" in r and isinstance(r["calvin"], dict)
