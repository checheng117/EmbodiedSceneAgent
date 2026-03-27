"""Central logging configuration (stdlib)."""

from __future__ import annotations

import logging
import os


def setup_logging(level: int | None = None) -> None:
    """Configure root logger once (idempotent enough for research scripts)."""
    lvl = level if level is not None else int(os.environ.get("ESA_LOG_LEVEL", logging.INFO))
    logging.basicConfig(level=lvl, format="%(levelname)s %(name)s: %(message)s")
