"""Tests for repository .env / HF token helpers (no real secrets)."""

from __future__ import annotations

import pytest

from embodied_scene_agent.utils import env as env_utils


def _fake_root(tmp_path, monkeypatch) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0"\n', encoding="utf-8")
    monkeypatch.setattr(env_utils, "repo_root", lambda: tmp_path)
    for key in (
        "HF_TOKEN",
        "HUGGING_FACE_HUB_TOKEN",
        env_utils._DOTENV_LOADED_FLAG,
        "_ESA_DOTENV_PATH",
    ):
        monkeypatch.delenv(key, raising=False)


def test_load_project_dotenv_sets_hf_token(monkeypatch, tmp_path) -> None:
    _fake_root(tmp_path, monkeypatch)
    (tmp_path / ".env").write_text("HF_TOKEN=__TEST_PLACEHOLDER_TOKEN__\n", encoding="utf-8")
    assert env_utils.load_project_dotenv(override=True) is True
    assert env_utils.get_hf_token() == "__TEST_PLACEHOLDER_TOKEN__"


def test_get_hf_token_require_raises(monkeypatch, tmp_path) -> None:
    _fake_root(tmp_path, monkeypatch)
    assert env_utils.load_project_dotenv(override=True) is False
    with pytest.raises(RuntimeError, match="HF_TOKEN"):
        env_utils.get_hf_token(require=True)


def test_hf_token_status_message_never_contains_token(monkeypatch, tmp_path) -> None:
    _fake_root(tmp_path, monkeypatch)
    (tmp_path / ".env").write_text("HF_TOKEN=__SECRET_SHOULD_NOT_LEAK__\n", encoding="utf-8")
    env_utils.load_project_dotenv(override=True)
    msg = env_utils.hf_token_status_message()
    assert "__SECRET_SHOULD_NOT_LEAK__" not in msg
    assert "not shown" in msg or "set" in msg.lower()
