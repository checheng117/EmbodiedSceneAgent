"""
Load a user-provided CALVIN env factory from the environment (no Hydra guessing in-repo).

Set::

    export ESA_CALVIN_ENV_FACTORY='your_package.calvin_local:make_calvin_env'

The callable must be importable (``PYTHONPATH`` must include the module's parent).
"""

from __future__ import annotations

import os
from typing import Any, Callable


def resolve_calvin_env_factory_from_env() -> tuple[Callable[[], Any] | None, dict[str, Any]]:
    """
    Resolve ``ESA_CALVIN_ENV_FACTORY`` → ``(factory_fn | None, meta_dict)``.

    **Does not** instantiate the env. ``meta`` explains success or failure (no secrets).
    """
    spec = os.environ.get("ESA_CALVIN_ENV_FACTORY", "").strip()
    meta: dict[str, Any] = {"env_var": "ESA_CALVIN_ENV_FACTORY", "spec": spec or None, "status": "unset"}
    if not spec:
        return None, meta

    if ":" not in spec:
        meta["status"] = "invalid_spec"
        meta["error"] = "Expected 'module.submodule:callable_name' (colon required)."
        return None, meta

    mod_name, _, attr = spec.partition(":")
    mod_name, attr = mod_name.strip(), attr.strip()
    if not mod_name or not attr:
        meta["status"] = "invalid_spec"
        meta["error"] = "Empty module or callable in ESA_CALVIN_ENV_FACTORY."
        return None, meta

    try:
        import importlib

        module = importlib.import_module(mod_name)
    except Exception as e:  # noqa: BLE001
        meta["status"] = "import_module_failed"
        meta["error"] = f"{type(e).__name__}: {e}"[:800]
        return None, meta

    try:
        fn = getattr(module, attr)
    except AttributeError as e:
        meta["status"] = "attr_missing"
        meta["error"] = f"{type(e).__name__}: {e}"
        return None, meta

    if not callable(fn):
        meta["status"] = "not_callable"
        meta["error"] = f"{attr!r} is not callable on module {mod_name!r}"
        return None, meta

    meta["status"] = "resolved"
    return fn, meta  # type: ignore[return-value]
