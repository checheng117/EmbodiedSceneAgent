"""CALVIN env factory loader (no real CALVIN required)."""

from __future__ import annotations

import sys
import types

import pytest

from embodied_scene_agent.envs.calvin_factory_load import resolve_calvin_env_factory_from_env


def test_factory_unset_returns_none(monkeypatch):
    monkeypatch.delenv("ESA_CALVIN_ENV_FACTORY", raising=False)
    fn, meta = resolve_calvin_env_factory_from_env()
    assert fn is None
    assert meta["status"] == "unset"


def test_factory_invalid_spec_no_colon(monkeypatch):
    monkeypatch.setenv("ESA_CALVIN_ENV_FACTORY", "nocolon")
    fn, meta = resolve_calvin_env_factory_from_env()
    assert fn is None
    assert meta["status"] == "invalid_spec"


def test_factory_resolves_callable(monkeypatch):
    mod = types.ModuleType("esa_test_calvin_factory_mod")

    def _make():
        return object()

    mod.build = _make
    monkeypatch.setitem(sys.modules, "esa_test_calvin_factory_mod", mod)
    monkeypatch.setenv("ESA_CALVIN_ENV_FACTORY", "esa_test_calvin_factory_mod:build")
    fn, meta = resolve_calvin_env_factory_from_env()
    assert callable(fn)
    assert meta["status"] == "resolved"
    assert fn() is not None
