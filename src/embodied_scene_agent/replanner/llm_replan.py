"""LLM-based local replan: JSON output validated by planner_output_contract."""

from __future__ import annotations

import json
import os
from typing import Any, Callable

from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.planner.planner_output_contract import (
    PlannerParseError,
    PlannerParseErrorCode,
    validate_planner_output_dict,
)
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.skills.vocabulary import allowed_skills_prompt_sentence
from embodied_scene_agent.verifier.schema import VerificationResult

_ALLOWED_PLANNER_KEYS = frozenset(
    {"task", "subgoal", "target_object", "skill", "success_check", "fallback", "reasoning", "confidence"}
)


def _strip_markdown_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def _extract_json_object(text: str) -> dict[str, Any]:
    """First balanced JSON object; raises on failure."""
    t = _strip_markdown_fences(text)
    start = t.find("{")
    if start < 0:
        raise ValueError("no JSON object in model output")
    decoder = json.JSONDecoder()
    try:
        obj, _end = decoder.raw_decode(t[start:])
    except json.JSONDecodeError as e:
        raise ValueError(f"json decode failed: {e}") from e
    if not isinstance(obj, dict):
        raise ValueError("JSON root must be an object")
    return obj


def classify_replan_parse_error(exc: BaseException, generated_text: str) -> str:
    """Stable labels for hybrid batch / dashboard (planner_output_contract path)."""
    g = (generated_text or "").strip()
    if not g:
        return "generation_empty"
    em = str(exc).lower()
    if "no json object" in em:
        return "no_json_object_found"
    if isinstance(exc, json.JSONDecodeError) or "json decode failed" in em:
        if "unterminated" in em or "unclosed" in em or "expecting" in em:
            return "truncated_json"
        return "truncated_json"
    if isinstance(exc, PlannerParseError):
        if exc.code == PlannerParseErrorCode.INVALID_SKILL:
            return "invalid_skill"
        if exc.code == PlannerParseErrorCode.MISSING_FIELD:
            return "missing_required_keys"
        if exc.code == PlannerParseErrorCode.EMPTY_VALUE:
            return "missing_required_keys"
        if exc.code == PlannerParseErrorCode.VALIDATION:
            errs = exc.details.get("errors") if exc.details else None
            if isinstance(errs, list) and any(
                isinstance(x, dict) and "loc" in x and "skill" in str(x.get("loc", ()))
                for x in errs
            ):
                return "invalid_skill"
            return "schema_validation_failed"
        return "schema_validation_failed"
    return "schema_validation_failed"


def _sanitize_planner_dict(raw: dict[str, Any]) -> dict[str, Any]:
    """Drop unknown keys so Pydantic does not carry prompt pollution forward."""
    return {k: raw[k] for k in _ALLOWED_PLANNER_KEYS if k in raw}


_LLM_ENGINE: tuple[
    Callable[..., tuple[PlannerOutput | None, dict[str, Any]]] | None,
    dict[str, Any],
] | None = None


def get_llm_replan_engine(
    *,
    model_id: str | None = None,
) -> tuple[Callable[..., tuple[PlannerOutput | None, dict[str, Any]]] | None, dict[str, Any]]:
    """Lazy singleton: load model once per process."""
    global _LLM_ENGINE
    if _LLM_ENGINE is not None:
        return _LLM_ENGINE

    mid = model_id or os.environ.get("ESA_REPLANNER_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
    device = "cpu" if os.environ.get("ESA_FORCE_CPU_REPLANNER") == "1" else "cuda"
    meta: dict[str, Any] = {"model_id": mid, "device": device, "load_error": None}

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as e:  # noqa: BLE001
        meta["load_error"] = str(e)
        _LLM_ENGINE = (None, meta)
        return _LLM_ENGINE

    try:
        tokenizer = AutoTokenizer.from_pretrained(mid, trust_remote_code=True)
        dtype = torch.float16 if device == "cuda" and torch.cuda.is_available() else torch.float32
        kwargs: dict[str, Any] = {"torch_dtype": dtype, "trust_remote_code": True}
        if device == "cuda" and torch.cuda.is_available():
            kwargs["device_map"] = "auto"
        model = AutoModelForCausalLM.from_pretrained(mid, **kwargs)
        if device == "cpu" or not torch.cuda.is_available():
            model = model.to("cpu")
            device = "cpu"
        model.eval()
        meta["loaded"] = True
        meta["device_resolved"] = device
    except Exception as e:  # noqa: BLE001
        meta["load_error"] = str(e)
        _LLM_ENGINE = (None, meta)
        return _LLM_ENGINE

    allowed_skills = allowed_skills_prompt_sentence()
    allowed_targets = "drawer, red_block, table, gripper, rlbench_target, workspace"

    def llm_replan(
        instruction: str,
        history: list[str],
        scene_memory: SceneMemory,
        failure: VerificationResult,
        previous: PlannerOutput,
    ) -> tuple[PlannerOutput | None, dict[str, Any]]:
        mem_json = scene_memory.to_json_dict()
        base_user = (
            "You are a robot planner. Output EXACTLY one JSON object and NOTHING else "
            "(no markdown, no prose, no code fences).\n"
            "Allowed keys ONLY: task, subgoal, target_object, skill, success_check, fallback, "
            "optional reasoning, optional confidence (number).\n"
            f"Allowed skills: {allowed_skills}.\n"
            f"target_object must be an object_id from scene memory or one of: {allowed_targets}.\n"
            f"Instruction: {instruction}\n"
            f"Recent history: {history[-5:]!s}\n"
            f"Previous plan JSON: {previous.model_dump()!s}\n"
            f"Verifier failure JSON: {failure.model_dump()!s}\n"
            f"Scene memory JSON (truncated): {json.dumps(mem_json)[:4000]}\n"
        )
        hard_user = (
            "Return ONE JSON object only. Keys: task, subgoal, target_object, skill, success_check, fallback. "
            "All string values non-empty. skill MUST be one of: open, close, grasp, place, reach, move_to.\n"
            f"target_object one of: {allowed_targets}.\n"
            f"Instruction: {instruction}\n"
            f"Verifier failure: {failure.model_dump()!s}\n"
            f"Previous plan: {previous.model_dump()!s}\n"
        )
        max_new = int(os.environ.get("ESA_REPLANNER_MAX_NEW", "256"))
        last_meta: dict[str, Any] = {
            "parse_error_kind": "schema_validation_failed",
            "fallback_reason": "llm_replan_failed",
            "raw_generation_head": "",
        }
        for attempt in range(2):
            user_content = hard_user if attempt == 1 else base_user
            messages = [{"role": "user", "content": user_content}]
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            inputs = tokenizer(prompt, return_tensors="pt")
            if device == "cuda" and torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            with torch.no_grad():
                out = model.generate(**inputs, max_new_tokens=max_new, do_sample=False)
            gen = tokenizer.decode(out[0, inputs["input_ids"].shape[1] :], skip_special_tokens=True)
            gen_stripped = gen.strip()
            if not gen_stripped:
                last_meta = {
                    "parse_error_kind": "generation_empty",
                    "fallback_reason": "empty model generation",
                    "raw_generation_head": "",
                }
                continue
            try:
                raw = _extract_json_object(gen_stripped)
                cleaned = _sanitize_planner_dict(raw)
                parse_audit: dict[str, Any] = {}
                plan = validate_planner_output_dict(cleaned, parse_audit=parse_audit)
                return plan, {
                    "parse_error_kind": None,
                    "fallback_reason": None,
                    "raw_generation_head": gen_stripped[:240],
                    "skill_alias_normalized_from": parse_audit.get("skill_alias_normalized_from"),
                }
            except (PlannerParseError, ValueError, json.JSONDecodeError, TypeError) as e:
                kind = classify_replan_parse_error(e, gen_stripped)
                last_meta = {
                    "parse_error_kind": kind,
                    "fallback_reason": str(e)[:500],
                    "raw_generation_head": gen_stripped[:500],
                }
        return None, last_meta

    _LLM_ENGINE = (llm_replan, meta)
    return _LLM_ENGINE


def try_llm_replan_planner_output(
    *,
    instruction: str,
    history: list[str],
    scene_memory: SceneMemory,
    failure: VerificationResult,
    previous: PlannerOutput,
    model_id: str | None = None,
) -> tuple[PlannerOutput | None, dict[str, Any]]:
    audit: dict[str, Any] = {"llm_replanner_called": True, "fallback_stage": None}
    fn, meta = get_llm_replan_engine(model_id=model_id)
    if fn is None:
        audit["replanner_parse_ok"] = False
        audit["revised_plan_validated"] = False
        audit["fallback_reason"] = meta.get("load_error", "no_fn")
        audit["fallback_stage"] = "model_load"
        audit["replanner_parse_error_kind"] = "model_load_failed"
        audit["whether_rule_based"] = None
        return None, audit
    try:
        plan, inner = fn(instruction, history, scene_memory, failure, previous)
        if plan is not None:
            audit["replanner_parse_ok"] = True
            audit["revised_plan_validated"] = True
            audit["whether_rule_based"] = False
            audit["fallback_stage"] = "validated"
            audit["replanner_parse_error_kind"] = inner.get("parse_error_kind")
            if inner.get("skill_alias_normalized_from"):
                audit["skill_alias_normalized_from"] = inner["skill_alias_normalized_from"]
            return plan, audit
        audit["replanner_parse_ok"] = False
        audit["revised_plan_validated"] = False
        audit["fallback_reason"] = inner.get("fallback_reason", "llm_replan_failed")
        audit["fallback_stage"] = "parse_validate"
        audit["replanner_parse_error_kind"] = inner.get("parse_error_kind")
        audit["whether_rule_based"] = None
        return None, audit
    except Exception as e:  # noqa: BLE001
        audit["replanner_parse_ok"] = False
        audit["revised_plan_validated"] = False
        audit["fallback_reason"] = f"{type(e).__name__}:{e!s}"[:500]
        audit["fallback_stage"] = "generate"
        audit["replanner_parse_error_kind"] = "generation_exception"
        audit["whether_rule_based"] = None
        return None, audit
