"""CLI: run mock v0 episode."""

from __future__ import annotations

import argparse
import json

from embodied_scene_agent.evaluation.metrics import metrics_to_dict, summarize_v0_trace
from embodied_scene_agent.pipeline.v0_loop import run_v0_episode
from embodied_scene_agent.utils.logging import setup_logging


def main() -> None:
    setup_logging()
    p = argparse.ArgumentParser(description="Run EmbodiedSceneAgent v0 mock episode.")
    p.add_argument(
        "--instruction",
        type=str,
        default="Put the red block in the drawer.",
        help="Natural language task for mock env.",
    )
    p.add_argument("--max-steps", type=int, default=12)
    p.add_argument(
        "--forced-grasp-failures",
        type=int,
        default=0,
        help="First N grasp attempts do not change state (exercises replanner + retry).",
    )
    args = p.parse_args()

    trace = run_v0_episode(
        args.instruction,
        max_steps=args.max_steps,
        forced_grasp_failures=args.forced_grasp_failures,
    )
    metrics = summarize_v0_trace(trace)
    print(json.dumps(metrics_to_dict(metrics), indent=2))
    print("success:", trace.success, "steps:", len(trace.steps), "replans:", trace.replan_count)


if __name__ == "__main__":
    main()
