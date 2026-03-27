"""Load project `.env` and read Hugging Face token without logging secrets."""

from __future__ import annotations

import os
from pathlib import Path

from embodied_scene_agent.utils.paths import repo_root

_DOTENV_LOADED_FLAG = "_ESA_DOTENV_LOADED"


def load_project_dotenv(override: bool = False) -> bool:
    """
    If a ``.env`` file exists at the repository root, parse it into ``os.environ``.

    - Skips lines starting with ``#`` and empty lines.
    - Does **not** print keys or values.
    - By default, does not override variables already set in the process environment.
    - Safe to call multiple times (idempotent unless ``override=True``).

    Returns:
        True if a root ``.env`` file was found and read (even if empty), False otherwise.
    """
    if (
        not override
        and os.environ.get(_DOTENV_LOADED_FLAG) == "1"
        and os.environ.get("_ESA_DOTENV_PATH")
    ):
        return True

    path = repo_root() / ".env"
    if not path.is_file():
        os.environ[_DOTENV_LOADED_FLAG] = "1"
        os.environ.pop("_ESA_DOTENV_PATH", None)
        return False

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if not key:
            continue
        if override or key not in os.environ:
            os.environ[key] = val

    os.environ[_DOTENV_LOADED_FLAG] = "1"
    os.environ["_ESA_DOTENV_PATH"] = str(path)
    return True


def get_hf_token(*, require: bool = False) -> str | None:
    """
    Return Hugging Face token from the environment after loading project ``.env``.

    Checks, in order: ``HF_TOKEN``, ``HUGGING_FACE_HUB_TOKEN`` (hub library convention).

    Never logs or returns the token via side channels — callers must not print it.

    Raises:
        RuntimeError: if ``require=True`` and no token is set.
    """
    load_project_dotenv()
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        token = token.strip()
    if not token:
        if require:
            raise RuntimeError(
                "Hugging Face token not configured: set HF_TOKEN in the repository root `.env` "
                "(or export HF_TOKEN / HUGGING_FACE_HUB_TOKEN in the environment). "
                "Do not commit `.env`."
            )
        return None
    return token


def hf_token_status_message() -> str:
    """Safe, token-free hint for CLI / probes."""
    load_project_dotenv()
    if get_hf_token():
        return "HF_TOKEN is set (value not shown)."
    return "HF_TOKEN is not set; add HF_TOKEN to repository root `.env` if Hugging Face downloads are required."
