"""Metrics helpers for planner base vs tuned comparison."""

from __future__ import annotations

import re
from typing import Any

from embodied_scene_agent.training.agent_prompt import parse_planner_completion


def last_skill_from_plans(text: str) -> str | None:
    found = re.findall(r"^Skill:\s*(\S+)\s*$", text, flags=re.MULTILINE)
    return found[-1] if found else None


def last_target_from_plans(text: str) -> str | None:
    found = re.findall(r"^Target:\s*(\S+)\s*$", text, flags=re.MULTILINE)
    return found[-1] if found else None


def format_compliance_ok(generated: str) -> bool:
    return parse_planner_completion(generated) is not None


def recovery_style_ok(generated: str, *, expect_recovery: bool) -> bool:
    if not expect_recovery:
        return True
    return "Observation:" in generated and generated.count("Plan:") >= 2


def score_row(
    *,
    reference_target: str,
    generated: str,
    trajectory_type: str,
) -> dict[str, Any]:
    ref_skill = last_skill_from_plans(reference_target)
    gen_skill = last_skill_from_plans(generated)
    ref_t = last_target_from_plans(reference_target)
    gen_t = last_target_from_plans(generated)
    fc = format_compliance_ok(generated)
    tool_ok = bool(ref_skill and gen_skill and ref_skill == gen_skill)
    target_ok = bool(ref_t and gen_t and ref_t == gen_t)
    rec_ok = recovery_style_ok(generated, expect_recovery=trajectory_type == "recovery")
    return {
        "format_compliance": fc,
        "tool_skill_match": tool_ok,
        "target_match": target_ok,
        "recovery_style_ok": rec_ok,
        "reference_skill": ref_skill,
        "generated_skill": gen_skill,
    }
