"""CLI: CALVIN-grounded minimal loop (structured trace JSON, no benchmark score)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from embodied_scene_agent.pipeline.run_calvin_minimal_loop import run_calvin_minimal_episode


def _trace_to_json_dict(trace: object) -> dict:
    from dataclasses import asdict

    return asdict(trace)


def main() -> None:
    p = argparse.ArgumentParser(
        description="CALVIN minimal loop: fixture or local factory (ESA_CALVIN_ENV_FACTORY). No scores."
    )
    p.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="CALVIN-style observation JSON (default: tests/fixtures/calvin_mock_observation.json).",
    )
    p.add_argument(
        "--instruction",
        type=str,
        default="Put the red block in the drawer.",
    )
    p.add_argument("--max-steps", type=int, default=12)
    p.add_argument("--experiment-id", type=str, default="", help="Optional id on EpisodeTrace / JSONL export.")
    p.add_argument(
        "--try-local-factory",
        action="store_true",
        help="Use ESA_CALVIN_ENV_FACTORY='module:callable' when set; else fall back to fixture with reason in trace.",
    )
    p.add_argument(
        "--live-action-strategy",
        choices=("symbolic_fallback", "live_zero_action_smoke"),
        default="symbolic_fallback",
        help="symbolic_fallback: live reset + symbolic skills; live_zero_action_smoke: call env.step (zeros) each iter.",
    )
    args = p.parse_args()

    trace = run_calvin_minimal_episode(
        args.instruction,
        fixture_path=args.fixture,
        max_steps=args.max_steps,
        experiment_id=args.experiment_id,
        try_local_factory=args.try_local_factory,
        live_action_strategy=args.live_action_strategy,
    )
    print(json.dumps(_trace_to_json_dict(trace), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
