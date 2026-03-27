"""Repository path helpers."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return absolute path to repository root (contains `pyproject.toml`)."""
    here = Path(__file__).resolve()
    for p in [here] + list(here.parents):
        if (p / "pyproject.toml").exists():
            return p
    raise RuntimeError("Could not locate repository root (pyproject.toml).")


def rel_repo_path(root: Path, path: Path | str) -> str:
    """Return a POSIX path relative to ``root`` when possible (for portable JSON / reports)."""
    root_r = root.resolve()
    p = Path(path)
    try:
        p_r = p.resolve()
    except OSError:
        return p.as_posix()
    try:
        return p_r.relative_to(root_r).as_posix()
    except ValueError:
        return p.as_posix()
