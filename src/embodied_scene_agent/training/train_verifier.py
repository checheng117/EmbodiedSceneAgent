"""Verifier training entry (classifier head — optional future work)."""

from __future__ import annotations

import argparse
from pathlib import Path

from embodied_scene_agent.utils.config import load_yaml_dict


def main() -> None:
    parser = argparse.ArgumentParser(description="Train verifier classifier (skeleton).")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    cfg = load_yaml_dict(args.config)
    print("[train_verifier] stub OK; config keys:", ", ".join(cfg.keys()))
    print("[train_verifier] TODO: optional classifier; v0 uses StateDiffVerifier.")


if __name__ == "__main__":
    main()
