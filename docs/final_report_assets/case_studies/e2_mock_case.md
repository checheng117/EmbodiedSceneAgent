# E2 mock — verifier + replan

## Context
Symbolic mock grid; **not** official CALVIN.

## Input / Setup
```json
{
  "episode_meta": {
    "episode_index": 1,
    "instruction": "put the red block in the drawer",
    "forced_grasp_failures": 1,
    "calvin_variant": null,
    "success": true,
    "replan_count": 1,
    "num_steps": 3,
    "final_message": "task_success",
    "env_mode": "",
    "teacher_source": ""
  },
  "backend": "mock",
  "mode": "verifier_plus_replan"
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
        "open"
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
  "frame_id": "1",
  "schema_version": "esa_sm/v1",
  "timestamp_s": null,
  "source": "mock_teacher",
  "extra": {}
}
```

## Planner Output
```json
{
  "task": "grasp_block",
  "subgoal": "Grasp the red block.",
  "target_object": "red_block",
  "skill": "grasp",
  "success_check": "red_block has state tag 'held'",
  "fallback": "realign gripper above block",
  "reasoning": "Need the object before placing.",
  "confidence": 1.0
}
```

## Verifier Decision
```json
{
  "success": false,
  "failure_type": "state_unchanged",
  "should_replan": true,
  "details": "grasp had no effect",
  "extras": {}
}
```

## Replanner Behavior
```json
{
  "original_subgoal": "Grasp the red block.",
  "failure_type": "state_unchanged",
  "repair_strategy": "retry_same_skill_alternate_fallback",
  "revised_subgoal": "Retry grasp on the red block.",
  "whether_rule_based": true,
  "notes": "failed:FailureType.STATE_UNCHANGED:grasp had no effect;hint:retry_grasp",
  "llm_replanner_called": false,
  "replanner_parse_ok": null,
  "revised_plan_validated": null,
  "fallback_reason": null,
  "fallback_stage": null,
  "replanner_parse_error_kind": null
}
```

## Outcome
{"success": true, "replan_count": 1, "num_steps": 3}

## Why this case matters
_Demonstrates verifier + replan wiring on symbolic mock; numbers are not official CALVIN._

## Artifact links
`results/demos/e2_ablation_cases/case3_plus_replan.json`, `mock_selection_meta.json`
