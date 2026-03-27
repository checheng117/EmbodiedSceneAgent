"""Legacy entry: use ``python -m embodied_scene_agent.training.run_planner_sft`` for real LoRA SFT."""

from __future__ import annotations

import argparse
from pathlib import Path

from embodied_scene_agent.utils.config import load_yaml_dict


def main() -> None:
    parser = argparse.ArgumentParser(description="Deprecated planner trainer stub (config check only).")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    cfg = load_yaml_dict(args.config)
    print("[train_planner] stub: config keys:", ", ".join(cfg.keys()))
    print("[train_planner] For real training run: python -m embodied_scene_agent.training.run_planner_sft --help")


if __name__ == "__main__":
    main()
