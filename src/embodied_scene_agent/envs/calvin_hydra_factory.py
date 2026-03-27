"""
Default CALVIN ``PlayTableSimEnv`` factory using **this machine's** ``calvin_env`` tree.

**Path priority** (which ``calvin_env`` package + ``conf/`` are used):

1. ``ESA_CALVIN_ENV_SRC`` — explicit directory containing ``calvin_env/`` package and ``conf/``
   (same layout as upstream ``mees/calvin_env`` repo root).
2. ``ESA_CALVIN_OFFICIAL_ROOT/calvin_env`` — submodule inside cloned ``mees/calvin``.
3. ``<EmbodiedSceneAgent>/data/raw/calvin_official/calvin_env`` if present (official clone).
4. Otherwise: whichever ``calvin_env`` is already on ``sys.path`` (e.g. ``pip install -e``).

Prepends the chosen tree to ``sys.path`` **before** ``import calvin_env`` so Hydra ``conf/`` matches
the imported package. See ``docs/calvin_official_setup_log.md``.

Set::

    export ESA_CALVIN_ENV_FACTORY='embodied_scene_agent.envs.calvin_hydra_factory:make_calvin_env'

Optional::

    export ESA_CALVIN_OFFICIAL_ROOT=/path/to/mees/calvin
"""

from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path
from typing import Any

from embodied_scene_agent.utils.paths import repo_root


def _prepend_calvin_env_source_path() -> Path | None:
    """
    Insert official / explicit calvin_env **repo root** (parent of package ``calvin_env/``) at
    ``sys.path[0]`` when configured. Returns that root if inserted, else None.
    """
    candidates: list[Path] = []
    env_src = os.environ.get("ESA_CALVIN_ENV_SRC", "").strip()
    if env_src:
        candidates.append(Path(env_src).expanduser().resolve())
    off = os.environ.get("ESA_CALVIN_OFFICIAL_ROOT", "").strip()
    if off:
        candidates.append((Path(off).expanduser().resolve() / "calvin_env"))
    try:
        candidates.append((repo_root() / "data" / "raw" / "calvin_official" / "calvin_env").resolve())
    except RuntimeError:
        pass

    for root in candidates:
        pkg = root / "calvin_env"
        conf = root / "conf"
        if pkg.is_dir() and conf.is_dir():
            key = str(root)
            if key not in sys.path:
                sys.path.insert(0, key)
            return root
    return None


_prepend_calvin_env_source_path()

import hydra
import calvin_env  # noqa: E402  (after optional path injection)
from hydra import compose, initialize_config_dir


def _calvin_conf_dir() -> str:
    root = Path(calvin_env.__file__).resolve().parents[1]
    return str(root / "conf")


def make_calvin_env() -> Any:
    """Return ``PlayTableSimEnv`` from composed ``config_data_collection`` (no guessed YAML paths)."""
    conf_dir = _calvin_conf_dir()
    # Hydra 1.1 (CALVIN official Python 3.8 stack) has no ``version_base`` on ``initialize_config_dir``.
    _init_kw: dict[str, Any] = {"config_dir": conf_dir}
    if "version_base" in inspect.signature(initialize_config_dir).parameters:
        _init_kw["version_base"] = None
    with initialize_config_dir(**_init_kw):
        cfg = compose(
            config_name="config_data_collection",
            overrides=[
                "use_vr=false",
                "env.use_scene_info=true",
                "env.use_egl=false",
                "env.show_gui=false",
            ],
        )
    return hydra.utils.instantiate(cfg.env, use_vr=False, use_scene_info=True)
