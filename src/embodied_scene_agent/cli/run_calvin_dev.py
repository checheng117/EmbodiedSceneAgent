"""CALVIN-grounded dev smoke: fixture → SceneMemory → planner one-step (no benchmark score)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from embodied_scene_agent.envs.calvin import CalvinEnvAdapter
from embodied_scene_agent.perception.calvin_teacher import CalvinTeacherStateAdapter
from embodied_scene_agent.planner.rule_based import RuleBasedPlanner
from embodied_scene_agent.planner.schema import PlannerInput
from embodied_scene_agent.utils.paths import repo_root


def _default_fixture() -> Path:
    return repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json"


def run_calvin_dev_smoke(
    *,
    fixture_path: Path | None = None,
    instruction: str = "Put the red block in the drawer.",
    with_verifier_replan: bool = False,
) -> dict[str, Any]:
    """
    Load mock CALVIN-style observation, build memory, run rule planner for one step.

    Does not claim CALVIN benchmark performance.
    """
    path = fixture_path or _default_fixture()
    env = CalvinEnvAdapter(fixture_path=path)
    env.reset(instruction)
    adapter = CalvinTeacherStateAdapter()
    mem = adapter.to_scene_memory(instruction, env.get_teacher_state())
    planner = RuleBasedPlanner()
    plan = planner.plan(
        PlannerInput(instruction=instruction, scene_memory=mem, history=[], failure_log=[])
    )
    out: dict[str, Any] = {
        "fixture": str(path),
        "instruction": instruction,
        "scene_memory": mem.to_json_dict(),
        "planner_input": PlannerInput(
            instruction=instruction,
            scene_memory=mem,
            history=[],
            failure_log=[],
        ).model_dump(mode="json"),
        "planner_output": plan.model_dump(mode="json"),
        "verifier_replan_skipped": not with_verifier_replan,
    }
    if with_verifier_replan:
        out["note"] = "Use mock v0 pipeline (run_v0) for full verifier+replan; CALVIN dev path is ingestion+plan only."
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="CALVIN-grounded dev smoke (mock fixture, no scores).")
    p.add_argument("--fixture", type=Path, default=None, help="Path to mock observation JSON.")
    p.add_argument(
        "--instruction",
        type=str,
        default="Put the red block in the drawer.",
        help="Language instruction.",
    )
    p.add_argument(
        "--with-verifier-hint",
        action="store_true",
        help="Include note about verifier/replan (not executed here).",
    )
    args = p.parse_args()
    trace = run_calvin_dev_smoke(
        fixture_path=args.fixture,
        instruction=args.instruction,
        with_verifier_replan=args.with_verifier_hint,
    )
    print(json.dumps(trace, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
