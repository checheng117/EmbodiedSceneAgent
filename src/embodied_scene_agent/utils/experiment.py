"""Helpers for reproducible experiment directories and run manifests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from embodied_scene_agent.utils.paths import rel_repo_path

RUN_MANIFEST_SCHEMA_VERSION = "esa_experiment_run/v1"


def experiment_timestamp(when: datetime | None = None) -> str:
    """UTC timestamp used in experiment directory names."""
    dt = when or datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def normalize_experiment_id(*, prefix: str, explicit_id: str = "", when: datetime | None = None) -> str:
    """Respect an explicit id, otherwise emit ``<prefix>_<UTC timestamp>``."""
    candidate = explicit_id.strip()
    if candidate:
        return candidate
    return f"{prefix}_{experiment_timestamp(when)}"


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(v) for v in value]
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if hasattr(value, "value") and type(value).__module__ == "enum":
        return getattr(value, "value")
    return value


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        _json_ready(payload),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _git_capture(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    out = proc.stdout.strip()
    return out or None


def git_snapshot(root: Path) -> dict[str, Any]:
    """Best-effort git metadata for later reproducibility checks."""
    commit = _git_capture(root, "rev-parse", "HEAD")
    branch = _git_capture(root, "rev-parse", "--abbrev-ref", "HEAD")
    status = _git_capture(root, "status", "--short")
    return {
        "commit": commit,
        "branch": branch,
        "is_dirty": bool(status) if status is not None else None,
    }


def write_run_artifacts(
    out_dir: Path,
    *,
    root: Path,
    experiment_id: str,
    entrypoint: str,
    config_snapshot: Mapping[str, Any],
    argv: Sequence[str] | None = None,
    notes: Sequence[str] | None = None,
    source_config_paths: Sequence[str | Path] | None = None,
    config_filename: str = "config.snapshot.json",
    manifest_filename: str = "run_manifest.json",
) -> dict[str, str]:
    """
    Persist a config snapshot and run manifest under ``out_dir``.

    The config snapshot captures the effective runtime parameters. The run manifest captures
    the provenance needed by the 3090-only roadmap: ``experiment_id``, snapshot path, CLI args,
    and best-effort git metadata.
    """
    root_resolved = root.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    config_payload = _json_ready(dict(config_snapshot))
    config_bytes = _canonical_json_bytes(config_payload)
    config_sha = hashlib.sha256(config_bytes).hexdigest()

    config_path = out_dir / config_filename
    config_path.write_text(
        json.dumps(config_payload, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )

    git_meta = git_snapshot(root_resolved)
    manifest_payload = {
        "schema_version": RUN_MANIFEST_SCHEMA_VERSION,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_id": experiment_id,
        "entrypoint": entrypoint,
        "root_relative_out_dir": rel_repo_path(root_resolved, out_dir),
        "config_snapshot_path": rel_repo_path(root_resolved, config_path),
        "config_snapshot_sha256": config_sha,
        "source_config_paths": [
            rel_repo_path(root_resolved, p) for p in (source_config_paths or [])
        ],
        "argv": list(argv) if argv is not None else list(sys.argv),
        "git_commit": git_meta.get("commit"),
        "git_branch": git_meta.get("branch"),
        "git_is_dirty": git_meta.get("is_dirty"),
        "notes": list(notes or []),
    }
    manifest_path = out_dir / manifest_filename
    manifest_path.write_text(
        json.dumps(manifest_payload, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "config_snapshot_path": rel_repo_path(root_resolved, config_path),
        "run_manifest_path": rel_repo_path(root_resolved, manifest_path),
    }


def read_run_artifact_status(
    root: Path,
    out_dir: Path | None,
    *,
    config_filename: str = "config.snapshot.json",
    manifest_filename: str = "run_manifest.json",
) -> dict[str, Any]:
    """Summarize whether a run directory satisfies the experiment artifact contract."""
    if out_dir is None:
        return {
            "status": "missing",
            "latest_dir": None,
            "config_snapshot_path": None,
            "run_manifest_path": None,
            "git_commit": None,
            "config_snapshot_sha256": None,
        }

    root_resolved = root.resolve()
    config_path = out_dir / config_filename
    manifest_path = out_dir / manifest_filename
    manifest_payload: dict[str, Any] | None = None
    if manifest_path.is_file():
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    if config_path.is_file() and manifest_path.is_file():
        status = "ready"
    elif config_path.is_file() or manifest_path.is_file():
        status = "partial"
    else:
        status = "missing"

    return {
        "status": status,
        "latest_dir": rel_repo_path(root_resolved, out_dir),
        "config_snapshot_path": (
            rel_repo_path(root_resolved, config_path) if config_path.is_file() else None
        ),
        "run_manifest_path": (
            rel_repo_path(root_resolved, manifest_path) if manifest_path.is_file() else None
        ),
        "git_commit": (manifest_payload or {}).get("git_commit"),
        "config_snapshot_sha256": (manifest_payload or {}).get("config_snapshot_sha256"),
    }
