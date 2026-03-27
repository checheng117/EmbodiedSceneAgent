"""
Minimal CALVIN live action normalization.

Contract: ``docs/calvin_action_contract.md``. Do not change action semantics silently.
"""

from __future__ import annotations

import os
from typing import Any


def calvin_live_action_dim() -> int:
    """Action dimension for :meth:`CalvinEnvAdapter.step` (override with ``ESA_CALVIN_ACTION_DIM``)."""
    raw = os.environ.get("ESA_CALVIN_ACTION_DIM", "8")
    try:
        n = int(raw)
    except ValueError as e:
        raise ValueError(f"ESA_CALVIN_ACTION_DIM must be an integer, got {raw!r}") from e
    if n < 1:
        raise ValueError("ESA_CALVIN_ACTION_DIM must be >= 1")
    return n


def normalize_calvin_live_action(action: Any | None) -> Any:
    """
    Coerce ``action`` to a float vector of length :func:`calvin_live_action_dim` for ``env.step``.

    - ``None`` → zeros (smoke / minimal contract; **待确认**是否对应 CALVIN 官方 no-op).
    - Accepts ``list`` / ``tuple`` / objects with ``.tolist()`` (e.g. ``numpy.ndarray``).

    Returns:
        ``numpy.ndarray`` (float32) if NumPy is importable, else ``list[float]`` (**待确认** env 是否要求 ndarray).

    Raises:
        TypeError: unsupported action type.
        ValueError: wrong length (see ``docs/calvin_action_contract.md``).
    """
    dim = calvin_live_action_dim()
    if action is None:
        seq = [0.0] * dim
    elif hasattr(action, "tolist"):
        seq = list(action.tolist())  # type: ignore[no-untyped-call]
    elif isinstance(action, (list, tuple)):
        seq = [float(x) for x in action]
    else:
        raise TypeError(
            f"CALVIN live action must be None, sequence, or ndarray; got {type(action).__name__}. "
            "See docs/calvin_action_contract.md."
        )
    if len(seq) != dim:
        raise ValueError(
            f"CALVIN live action must have length {dim} (set ESA_CALVIN_ACTION_DIM to match your calvin_env); "
            "see docs/calvin_action_contract.md."
        )
    try:
        import numpy as np

        return np.asarray(seq, dtype=np.float32)
    except ImportError:
        return seq
