"""Static checks: conda env name only in environment.yml + resolve script (no stale hardcoding)."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from embodied_scene_agent.utils.paths import repo_root


def _yml_env_name() -> str:
    text = (repo_root() / "environment.yml").read_text(encoding="utf-8")
    m = re.search(r"(?m)^name:\s*(\S+)", text)
    assert m, "environment.yml must contain top-level name:"
    return m.group(1)


def test_environment_yml_name_is_non_empty() -> None:
    name = _yml_env_name()
    assert name == "embodied-scene-agent"


def test_setup_and_conda_scripts_do_not_hardcode_stale_env_name() -> None:
    root = repo_root()
    stale = "esa-py310"
    for rel in ("scripts/setup_env.sh", "scripts/conda_env.sh"):
        body = (root / rel).read_text(encoding="utf-8")
        assert stale not in body, f"{rel} must not hardcode deprecated {stale!r}; use resolve_conda_env.sh"


@pytest.mark.skipif(not shutil.which("bash"), reason="bash not available")
def test_resolve_conda_env_script_exports_same_name_as_yml() -> None:
    root = repo_root()
    script = root / "scripts" / "resolve_conda_env.sh"
    cmd = f"set -e; source '{script}' && printf '%s' \"$ESA_CONDA_ENV_NAME\""
    out = subprocess.run(
        ["bash", "-c", cmd],
        check=True,
        capture_output=True,
        text=True,
    )
    assert out.stdout.strip() == _yml_env_name()
