# Hybrid replanner — LLM path success

## Context
CALVIN debug real-data batch; latest aligned artifact, not official benchmark.

## Input / Setup
```json
{
  "backend": "calvin_debug_real"
}
```

## Memory Snapshot
```json
{
  "objects": {
    "table": {
      "object_id": "table",
      "name": "table",
      "display_name": "table",
      "class_name": "table",
      "category": "support_surface",
      "aliases": [
        "table_top"
      ],
      "position": [
        0.5,
        0.0,
        0.0
      ],
      "bbox": null,
      "oriented_bbox": null,
      "state_tags": [
        "static"
      ],
      "visibility": 1.0,
      "confidence": 1.0,
      "last_seen_step": null,
      "metadata": {}
    },
    "drawer": {
      "object_id": "drawer",
      "name": "drawer",
      "display_name": "drawer",
      "class_name": "slider",
      "category": "slider",
      "aliases": [
        "base__drawer"
      ],
      "position": [
        0.0,
        0.0,
        0.0
      ],
      "bbox": null,
      "oriented_bbox": null,
      "state_tags": [
        "closed"
      ],
      "visibility": 1.0,
      "confidence": 1.0,
      "last_seen_step": null,
      "metadata": {
        "calvin_uid": "base__drawer"
      }
    },
    "red_block": {
      "object_id": "red_block",
      "name": "block_pink",
      "display_name": "block_pink",
      "class_name": "block",
      "category": "block",
      "aliases": [
        "block_pink"
      ],
      "position": [
        0.12866198927029296,
        -0.03777561047838666,
        0.4599892656024076
      ],
      "bbox": null,
      "oriented_bbox": null,
      "state_tags": [
        "on_table"
      ],
      "visibility": 1.0,
      "confidence": 1.0,
      "last_seen_step": null,
      "metadata": {
        "calvin_uid": "block_pink"
      }
    }
  },
  "relations": [
    {
      "subject_id": "red_block",
      "object_id": "table",
      "relation": "on",
      "confidence": 1.0
    }
  ],
  "frame_id": "0358482",
  "schema_version": "esa_sm/v1",
  "timestamp_s": null,
  "source": "calvin_teacher",
  "extra": {
    "calvin_robot_meta": {
      "gripper_open": true,
      "gripper_opening_width": 0.07999973934844062,
      "held_object_uid": null,
      "tcp_pos": [
        0.10036144835553709,
        -0.09143668381757282,
        0.570872717878888
      ],
      "gripper_action": 1
    },
    "language_instruction": "place the object in the slider",
    "gripper_open": true
  }
}
```

## Planner Output
```json
{
  "task": "smoke_unknown_skill",
  "subgoal": "deliberate verifier-unknown skill for hybrid smoke",
  "target_object": "drawer",
  "skill": "diagnostic_verifier_unknown",
  "success_check": "noop",
  "fallback": "none",
  "reasoning": "hybrid_replanner_smoke",
  "confidence": 0.1
}
```

## Verifier Decision
```json
{
  "success": false,
  "failure_type": "unknown_failure",
  "should_replan": true,
  "details": "diagnostic unknown skill branch",
  "extras": {}
}
```

## Replanner Behavior
```json
{
  "original_subgoal": "deliberate verifier-unknown skill for hybrid smoke",
  "failure_type": "unknown_failure",
  "repair_strategy": "llm_planner_fallback",
  "revised_subgoal": "place_red_block_in_drawer",
  "whether_rule_based": false,
  "notes": "hybrid_after_rules;delegate_rule_planner_with_failure_context",
  "llm_replanner_called": true,
  "replanner_parse_ok": true,
  "revised_plan_validated": true,
  "revised_plan_accepted": true,
  "fallback_reason": null,
  "fallback_stage": "validated",
  "replanner_parse_error_kind": null,
  "skill_alias_normalized_from": null,
  "raw_generation_head": "{\"task\": \"place_object_in_slider\", \"subgoal\": \"place_red_block_in_drawer\", \"target_object\": \"drawer\", \"skill\": \"place\", \"success_check\": \"object_in_drawer\", \"fallback\": \"open_drawer_and_place\", \"optional_reasoning\": \"The red block needs to ",
  "parser_repair_actions": [],
  "acceptance_rejection_reason": null,
  "acceptance_rejection_details": [],
  "repeated_no_effect_detected": false,
  "repeated_no_effect_signature": null,
  "repeated_no_effect_consecutive": null,
  "repeated_no_effect_threshold": null,
  "repeated_no_effect_stop": false
}
```

## Outcome
{"success": false, "replan_count": 3, "final_message": "repeated_no_effect_fallback_exhausted", "episode_failure_label": "repeated_no_effect_fallback_exhausted", "terminal_failure_label": "repeated_no_effect_fallback_exhausted", "validated_replan_issue_label": null, "label_reasons": [], "semantic_issue_step_index": null, "terminal_step_index": 2, "terminal_failure_type": "state_unchanged", "terminal_failure_details": "open had no effect"}

## Why this case matters
_Shows a real CALVIN debug hybrid replan artifact with refined failure labels; not an official benchmark result._

## Artifact links
`results/demos/hybrid_replanner_cases/case_calvin_debug_real_aligned_hybrid_success.json`
