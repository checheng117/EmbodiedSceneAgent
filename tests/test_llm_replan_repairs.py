from __future__ import annotations

from embodied_scene_agent.planner.planner_output_contract import validate_planner_output_dict
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.replanner.llm_replan import (
    _recover_partial_json_object,
    _repair_planner_dict,
    _select_loader_from_model_type,
    try_llm_replan_planner_output,
)
from embodied_scene_agent.verifier.schema import FailureType, VerificationResult


def _previous_open_plan() -> PlannerOutput:
    return PlannerOutput(
        task="open_drawer",
        subgoal="Open the drawer fully.",
        target_object="drawer",
        skill="open",
        success_check="drawer has state tag 'open'",
        fallback="reach handle from the right",
    )


def test_repair_planner_dict_infers_missing_success_check() -> None:
    repaired, actions = _repair_planner_dict(
        {
            "task": "open_drawer",
            "subgoal": "Open the drawer fully.",
            "target_object": "drawer",
            "skill": "open",
            "success_check": None,
            "fallback": "retry",
        },
        previous=_previous_open_plan(),
    )
    plan = validate_planner_output_dict(repaired)
    assert plan.success_check == "drawer has state tag 'open'"
    assert "success_check:inferred_from_skill_target" in actions


def test_recover_partial_json_object_handles_truncated_tail() -> None:
    raw = (
        '{"task":"open_drawer","subgoal":"Open the drawer fully.",'
        '"target_object":"drawer","skill":"open","success_check":"drawer has state tag \\"open\\"",'
        '"fallback":"reach handle'
    )
    partial = _recover_partial_json_object(raw)
    assert partial["task"] == "open_drawer"
    assert partial["skill"] == "open"
    repaired, actions = _repair_planner_dict(partial, previous=_previous_open_plan())
    plan = validate_planner_output_dict(repaired)
    assert plan.fallback == ""
    assert "fallback:missing_to_empty" in actions


def test_try_llm_replan_planner_output_keeps_repair_metadata(monkeypatch) -> None:
    previous = _previous_open_plan()

    def fake_get_llm_replan_engine(*, model_id=None):  # noqa: ARG001
        def fake_fn(instruction, history, scene_memory, failure, previous):  # noqa: ARG001
            return previous, {
                "parse_error_kind": None,
                "fallback_reason": None,
                "raw_generation_head": '{"task":"open_drawer"}',
                "repair_actions": ["success_check:inferred_from_skill_target"],
            }

        return fake_fn, {"loaded": True}

    monkeypatch.setattr(
        "embodied_scene_agent.replanner.llm_replan.get_llm_replan_engine",
        fake_get_llm_replan_engine,
    )
    plan, audit = try_llm_replan_planner_output(
        instruction="open the drawer",
        history=[],
        scene_memory=type("S", (), {"to_json_dict": lambda self: {}})(),
        failure=VerificationResult(
            success=False,
            failure_type=FailureType.UNKNOWN_FAILURE,
            should_replan=True,
            details="x",
        ),
        previous=previous,
    )
    assert plan is not None
    assert audit["raw_generation_head"] == '{"task":"open_drawer"}'
    assert audit["parser_repair_actions"] == ["success_check:inferred_from_skill_target"]


def test_loader_selection_defaults_to_causal_path() -> None:
    kind, err = _select_loader_from_model_type("qwen2", has_image_text_loader=True)
    assert kind == "causal_lm"
    assert err is None


def test_loader_selection_for_qwen25_vl_path() -> None:
    kind, err = _select_loader_from_model_type("qwen2_5_vl", has_image_text_loader=True)
    assert kind == "image_text_to_text"
    assert err is None


def test_loader_selection_fails_explicitly_for_unknown_vl_family() -> None:
    kind, err = _select_loader_from_model_type("custom_vl", has_image_text_loader=True)
    assert kind is None
    assert err == "unsupported_model_family:custom_vl:no_loader_mapping"
