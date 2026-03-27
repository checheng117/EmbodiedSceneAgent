"""Central planner prompt / target format (training and eval must stay aligned)."""

from __future__ import annotations

import json
from typing import Any

# Full spec: docs/agent_prompt_template.md
PLANNER_OUTPUT_HEADER = "Plan:"

DEFAULT_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {"name": "reach", "description": "Move end-effector toward a target object (non-grasping approach)."},
    {"name": "grasp", "description": "Grasp / pick up the target object."},
    {"name": "place", "description": "Place the held object at the target (e.g. drawer)."},
    {"name": "open", "description": "Open articulated target (e.g. drawer)."},
    {"name": "close", "description": "Close articulated target."},
    {"name": "move_to", "description": "Navigate base / arm to a named region or object."},
]


def tool_definitions_json() -> str:
    return json.dumps(DEFAULT_TOOL_DEFINITIONS, ensure_ascii=False, indent=2)


def build_user_prompt(
    *,
    instruction: str,
    scene_memory: dict[str, Any],
    history: list[str],
    failure_log: list[str],
) -> str:
    """Single-turn user content for planner SFT / eval."""
    hist = "\n".join(f"- {h}" for h in history) if history else "(none)"
    flog = "\n".join(f"- {x}" for x in failure_log) if failure_log else "(none)"
    sm = json.dumps(scene_memory, ensure_ascii=False, indent=2)
    tools = tool_definitions_json()
    return (
        "You are a structured manipulation planner. Use only the listed skills.\n"
        f"Available tools (JSON):\n{tools}\n\n"
        f"Instruction:\n{instruction}\n\n"
        f"Scene memory (JSON, esa_sm/v1 object graph):\n{sm}\n\n"
        f"Completed subgoals (history):\n{hist}\n\n"
        f"Failure log:\n{flog}\n\n"
        "Respond with exactly the following fields and headers (no markdown fences):\n"
        "Plan:\n"
        "Task: <short id>\n"
        "Subgoal: <one sentence>\n"
        "Target: <object_id>\n"
        "Skill: <skill name from tools>\n"
        "Success_Check: <verifiable condition>\n"
        "Fallback: <short recovery hint>\n"
    )


def format_plan_block(plan: dict[str, Any]) -> str:
    """Serialize PlannerOutput-like dict to training target text."""
    return (
        f"{PLANNER_OUTPUT_HEADER}\n"
        f"Task: {plan.get('task', '')}\n"
        f"Subgoal: {plan.get('subgoal', '')}\n"
        f"Target: {plan.get('target_object', '')}\n"
        f"Skill: {plan.get('skill', '')}\n"
        f"Success_Check: {plan.get('success_check', '')}\n"
        f"Fallback: {plan.get('fallback', '')}\n"
    )


def format_recovery_supervision(
    *,
    initial_plan: dict[str, Any],
    verification: dict[str, Any],
    skill_result: dict[str, Any],
    revised_plan: dict[str, Any],
) -> str:
    """Failure → observation → revised plan (explicit recovery chain)."""
    obs = (
        f"Observation:\n"
        f"Skill_result: {json.dumps(skill_result, ensure_ascii=False)}\n"
        f"Verification: {json.dumps(verification, ensure_ascii=False)}\n"
    )
    return (
        f"{format_plan_block(initial_plan)}"
        f"{obs}"
        f"Thought: Initial plan failed verification; replan before continuing.\n"
        f"{format_plan_block(revised_plan)}"
    )


def parse_planner_completion(text: str) -> dict[str, Any] | None:
    """
    Best-effort parse of model output into planner fields.

    Returns None if required keys are missing.
    """
    if not text or PLANNER_OUTPUT_HEADER not in text:
        return None
    after = text.split(PLANNER_OUTPUT_HEADER, 1)[-1]
    fields: dict[str, str] = {}
    for line in after.splitlines():
        line = line.strip()
        for key in ("Task", "Subgoal", "Target", "Skill", "Success_Check", "Fallback"):
            prefix = f"{key}:"
            if line.startswith(prefix):
                fields[key.lower()] = line[len(prefix) :].strip()
    req = ("subgoal", "target", "skill")
    if not all(fields.get(k) for k in req):
        return None
    return {
        "task": fields.get("task", ""),
        "subgoal": fields["subgoal"],
        "target_object": fields.get("target", ""),
        "skill": fields["skill"],
        "success_check": fields.get("success_check", ""),
        "fallback": fields.get("fallback", ""),
    }
