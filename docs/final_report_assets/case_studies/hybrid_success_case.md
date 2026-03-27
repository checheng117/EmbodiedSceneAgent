# Hybrid replanner — LLM path success

## Context
Mock v0 episode; latest batch artifact.

## Input / Setup
```json
{}
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
      "category": null,
      "aliases": [],
      "position": [
        0.5,
        0.0,
        0.0
      ],
      "bbox": [
        0.0,
        0.0,
        0.0,
        1.0,
        0.1,
        0.5
      ],
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
      "class_name": "drawer",
      "category": null,
      "aliases": [],
      "position": [
        0.6,
        0.0,
        0.35
      ],
      "bbox": [
        0.55,
        -0.05,
        0.25,
        0.65,
        0.05,
        0.45
      ],
      "oriented_bbox": null,
      "state_tags": [
        "closed"
      ],
      "visibility": 1.0,
      "confidence": 1.0,
      "last_seen_step": null,
      "metadata": {}
    },
    "red_block": {
      "object_id": "red_block",
      "name": "red block",
      "display_name": "red block",
      "class_name": "red block",
      "category": null,
      "aliases": [],
      "position": [
        0.45,
        0.0,
        0.12
      ],
      "bbox": [
        0.42,
        -0.02,
        0.08,
        0.48,
        0.02,
        0.16
      ],
      "oriented_bbox": null,
      "state_tags": [
        "on_table"
      ],
      "visibility": 1.0,
      "confidence": 1.0,
      "last_seen_step": null,
      "metadata": {}
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
  "frame_id": "0",
  "schema_version": "esa_sm/v1",
  "timestamp_s": null,
  "source": "mock_teacher",
  "extra": {}
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
  "revised_subgoal": "put_red_block_in_drawer",
  "whether_rule_based": false,
  "notes": "hybrid_after_rules;delegate_rule_planner_with_failure_context",
  "llm_replanner_called": true,
  "replanner_parse_ok": true,
  "revised_plan_validated": true,
  "fallback_reason": null,
  "fallback_stage": "validated",
  "replanner_parse_error_kind": null
}
```

## Outcome
{"success": true, "replan_count": 1, "final_message": "task_success"}

## Why this case matters
_Demonstrates verifier + replan wiring on symbolic mock; numbers are not official CALVIN._

## Artifact links
`results/demos/hybrid_replanner_cases/case_llm_repair_success.json`
