# E2 CALVIN fixture case


## Side-by-side

```json
{
  "backend": "calvin_fixture",
  "episode_index": 1,
  "verifier_only_trace": {
    "success": true,
    "replan_count": 0,
    "steps": [
      {
        "observation_id": "calvin_min::f644be63-abb4-4519-b1c6-d1a28df7b7a1::0",
        "timestep": 0,
        "schema_version": "esa_episode_log/v1",
        "verifier_mode": "verifier_only",
        "replanner_mode": "rule",
        "scene_memory_before": {
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
              "aliases": [],
              "position": [
                0.6,
                0.0,
                0.35
              ],
              "bbox": null,
              "oriented_bbox": null,
              "state_tags": [
                "open"
              ],
              "visibility": 1.0,
              "confidence": 1.0,
              "last_seen_step": null,
              "metadata": {
                "calvin_uid": "drawer"
              }
            },
            "red_block": {
              "object_id": "red_block",
              "name": "red block",
              "display_name": "red block",
              "class_name": "block",
              "category": "block",
              "aliases": [],
              "position": [
                0.45,
                0.0,
                0.12
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
                "calvin_uid": "red_block"
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
          "frame_id": "0",
          "schema_version": "esa_sm/v1",
          "timestamp_s": 0.0,
          "source": "calvin_teacher",
          "extra": {
            "calvin_robot_meta": {
              "held_object_uid": null,
              "gripper_open": true
            },
            "language_instruction": "put the red block in the drawer",
            "gripper_open": true
          }
        },
        "history": [],
        "failure_log": [],
        "planner_input_summary": {
          "instruction": "put the red block in the drawer",
          "history_len": 0,
          "failure_log_len": 0
        },
        "plan": {
          "task": "grasp_block",
          "subgoal": "Grasp the red block.",
          "target_object": "red_block",
          "skill": "grasp",
          "success_check": "red_block has state tag 'held'",
          "fallback": "realign gripper above block",
          "reasoning": "Need the object before placing.",
          "confidence": 1.0
        },
        "skill_result": {
          "success": true,
          "message": "grasp",
          "delta": {
            "skill": "grasp"
          }
        },
        "scene_memory_after_first": {
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
              "aliases": [],
              "position": [
                0.6,
                0.0,
                0.35
              ],
              "bbox": null,
              "oriented_bbox": null,
              "state_tags": [
                "open"
              ],
              "visibility": 1.0,
              "confidence": 1.0,
              "last_seen_step": null,
              "metadata": {
                "calvin_uid": "drawer"
              }
            },
            "red_block": {
              "object_id": "red_block",
              "name": "red block",
              "display_name": "red block",
              "class_name": "block",
              "category": "block",
              "aliases": [],
              "position": [
                0.45,
                0.0,
                0.12
              ],
              "bbox": null,
              "oriented_bbox": null,
              "state_tags": [
                "held"
              ],
              "visibility": 1.0,
              "confidence": 1.0,
              "last_seen_step": null,
              "metadata": {
                "calvin_uid": "red_block"
              }
            },
            "gripper": {
              "object_id": "gripper",
              "name": "gripper",
              "display_name": "gripper",
              "class_name": "end_effector",
              "category": "gripper",
              "aliases": [],
              "position": [
                0.5,
                0.0,
                0.2
              ],
              "bbox": null,
              "oriented_bbox": null,
              "state_tags": [
                "end_effector"
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
              "object_id": "gripper",
              "relation": "on",
              "confidence": 1.0
            }
          ],
          "frame_id": "0",
          "schema_version": "esa_sm/v1",
          "timestamp_s": 0.0,
          "source": "calvin_teacher",
          "extra": {
            "calvin_robot_meta": {
              "held_object_uid": "red_block",
              "gripper_open": true
            },
            "language_instruction": "put the red block in the drawer",
            "gripper_open": true
          }
        },
        "verification": {
          "success": true,
          "failure_type": null,
          "should_replan": false,
          "details": "red_block grasped",
          "extras": {}
        },
        "replan": null,
        "replan_audit": null,
        "executor_mode": "symbolic_calvin_teacher_via_CalvinEnvAdapter.apply_skill",
        "env_mode": "fixture",
        "teacher_source": "fixture_json",
        "action_mode": "fixture_symbolic",
        "live_step_executed": false,
        "loop_fallback_reason": null
      },
      {
        "observation_id": "calvin_min::f644be63-abb4-4519-b1c6-d1a28df7b7a1::1",
        "timestep": 1,
        "schema_version": "esa_episode_log/v1",
        "verifier_mode": "verifier_only",
        "re
```
