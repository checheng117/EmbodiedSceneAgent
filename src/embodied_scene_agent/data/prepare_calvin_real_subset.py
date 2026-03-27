"""
Download official CALVIN playtable language annotations (mees/calvin YAML) and emit a manifest.

These YAML files contain **subtask keys → natural language instructions** only (no RGB/depth frames).
Rollouts in this repo use **MockEmbodiedEnv + rule planner** with real CALVIN text; see
docs/calvin_dataset_mapping_log.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from embodied_scene_agent.utils.paths import repo_root

# Pinned to default branch paths; upstream may move — script records resolved URL in each row.
CALVIN_ANNOTATION_SOURCES: tuple[dict[str, str], ...] = (
    {
        "split_role": "train_pool",
        "url": "https://raw.githubusercontent.com/mees/calvin/main/calvin_models/conf/annotations/new_playtable.yaml",
        "filename": "new_playtable.yaml",
    },
    {
        "split_role": "validation_pool",
        "url": "https://raw.githubusercontent.com/mees/calvin/main/calvin_models/conf/annotations/new_playtable_validation.yaml",
        "filename": "new_playtable_validation.yaml",
    },
)


def _mock_rollout_compatible(instruction: str) -> bool:
    t = instruction.lower()
    keys = (
        "drawer",
        "block",
        "red",
        "blue",
        "pink",
        "place",
        "put",
        "open",
        "grasp",
        "pick",
        "take",
        "slide",
        "cabinet",
        "store",
        "stack",
        "lift",
        "push",
        "handle",
    )
    return any(k in t for k in keys)


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "EmbodiedSceneAgent-calvin-subset/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310 — fixed official URLs
        dest.write_bytes(resp.read())


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected mapping at root of {path}")
    return raw


def build_manifest_rows(
    *,
    raw_dir: Path,
    manifest_version: str = "calvin_real_subset/v1",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for src in CALVIN_ANNOTATION_SOURCES:
        path = raw_dir / src["filename"]
        data = _load_yaml(path)
        split_role = src["split_role"]
        url = src["url"]
        for subtask_key, ann in data.items():
            if not isinstance(subtask_key, str):
                continue
            phrases: list[str]
            if isinstance(ann, str):
                phrases = [ann]
            elif isinstance(ann, list):
                phrases = [str(x) for x in ann if x is not None]
            else:
                raise TypeError(
                    f"unexpected annotation type for {subtask_key!r} in {path}: {type(ann).__name__}"
                )
            for i, instruction in enumerate(phrases):
                eid = f"{split_role}::{subtask_key}::{i}"
                try:
                    raw_rel = str(path.relative_to(repo_root()))
                except ValueError:
                    raw_rel = str(path)
                rows.append(
                    {
                        "manifest_version": manifest_version,
                        "episode_id": eid,
                        "subtask_key": subtask_key,
                        "instruction": instruction,
                        "annotation_index": i,
                        "split_role": split_role,
                        "source_url": url,
                        "raw_yaml_relpath": raw_rel,
                        "obs_frame_path": None,
                        "obs_source": "none_yaml_only",
                        "can_rollout_mock_symbolic": _mock_rollout_compatible(instruction),
                        "can_synthetic_recovery": True,
                        "can_multi_step_episode": True,
                    }
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare CALVIN real language subset manifest (official YAML).")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory to store downloaded YAML (default: <repo>/data/raw/calvin_official_annotations)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for manifest (default: <repo>/data/processed/calvin_real_subset)",
    )
    parser.add_argument("--download-only", action="store_true", help="Only fetch YAML; skip manifest write.")
    args = parser.parse_args()

    root = repo_root()
    raw_dir = args.raw_dir or (root / "data" / "raw" / "calvin_official_annotations")
    out_dir = args.out_dir or (root / "data" / "processed" / "calvin_real_subset")

    for src in CALVIN_ANNOTATION_SOURCES:
        path = raw_dir / src["filename"]
        if not path.is_file():
            _download(src["url"], path)

    if args.download_only:
        print(f"[prepare_calvin_real_subset] downloaded YAML under {raw_dir}")
        return

    rows = build_manifest_rows(raw_dir=raw_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    man_path = out_dir / "manifest.jsonl"
    with man_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    h = hashlib.sha256()
    h.update(man_path.read_bytes())
    (out_dir / "manifest.sha256").write_text(h.hexdigest() + "  manifest.jsonl\n", encoding="utf-8")
    print(f"[prepare_calvin_real_subset] wrote {len(rows)} rows to {man_path}")


if __name__ == "__main__":
    main()
