"""
Single source of truth for planner / executor skill names (canonical + aliases).

LLM replanner prompts, :func:`validate_planner_output_dict`, and :class:`SkillRegistry` must stay consistent.
"""

from __future__ import annotations

import re
from typing import Any

# Registered motion primitives (matches SkillRegistry defaults + diagnostic smoke skill).
CANONICAL_SKILLS: frozenset[str] = frozenset(
    {
        "reach",
        "grasp",
        "place",
        "open",
        "close",
        "move_to",
        "diagnostic_verifier_unknown",
    }
)

# Aliases → canonical (lowercase keys).
SKILL_ALIASES: dict[str, str] = {
    "open_gripper": "open",
    "close_gripper": "close",
    "gripper_open": "open",
    "gripper_close": "close",
    "pick": "grasp",
    "put": "place",
    "pick_up": "grasp",
    "put_down": "place",
}

# Skills the LLM is allowed to output (exclude diagnostic from prompt).
LLM_ALLOWED_SKILLS: tuple[str, ...] = ("open", "close", "grasp", "place", "reach", "move_to")


def _norm_key(name: str) -> str:
    return re.sub(r"[\s\-]+", "_", str(name).strip().lower())


def normalize_planner_skill(raw: str) -> tuple[str, str | None]:
    """
    Map model / legacy strings to a canonical skill name.

    Returns:
        (canonical_skill, original_alias_if_rewritten)
    """
    key = _norm_key(raw)
    if key in CANONICAL_SKILLS:
        return key, None
    if key in SKILL_ALIASES:
        return SKILL_ALIASES[key], key
    return key, None


def is_known_planner_skill(canonical: str) -> bool:
    return canonical in CANONICAL_SKILLS


def allowed_skills_prompt_sentence() -> str:
    return ", ".join(LLM_ALLOWED_SKILLS)


def normalize_planner_output_skill_inplace(data: dict[str, Any]) -> tuple[str | None, str | None]:
    """
    Mutate ``data['skill']`` to canonical when alias matches.

    Returns:
        (alias_from, invalid_canonical_if_unknown) — invalid is set when not in CANONICAL_SKILLS after normalize.
    """
    sk = data.get("skill")
    if not isinstance(sk, str):
        return None, None
    canon, alias_from = normalize_planner_skill(sk)
    data["skill"] = canon
    if canon not in CANONICAL_SKILLS:
        return alias_from, canon
    return alias_from, None
