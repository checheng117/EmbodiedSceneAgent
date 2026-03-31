# Hybrid parse / validate fallback

```json
{
  "case": "calvin_debug_hybrid_acceptance_reject",
  "backend": "calvin_debug_real",
  "calvin_debug_batch": "grouped_sequence",
  "reporting_source_tag": "calvin_debug_real_aligned",
  "experiment_id": "hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun",
  "episode_index": 1,
  "step": {
    "observation_id": "calvin_min::37a38b66-6b65-4aaa-be7a-99ff6b0f1908::0",
    "timestep": 0,
    "schema_version": "esa_episode_log/v1",
    "verifier_mode": "verifier_plus_replan",
    "replanner_mode": "hybrid",
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
            0.12867531994376558,
            -0.037740311373030334,
            0.45998932958428845
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
      "frame_id": "0358502",
      "schema_version": "esa_sm/v1",
      "timestamp_s": null,
      "source": "calvin_teacher",
      "extra": {
        "calvin_robot_meta": {
          "gripper_open": true,
          "gripper_opening_width": 0.0799995819625895,
          "held_object_uid": null,
          "tcp_pos": [
            0.1179967833966753,
            -0.07920850114092064,
            0.5686812265837504
          ],
          "gripper_action": 1
        },
        "language_instruction": "lift the blue block lying in the drawer",
        "gripper_open": true
      }
    },
    "history": [],
    "failure_log": [],
    "planner_input_summary": {
      "instruction": "lift the blue block lying in the drawer",
      "history_len": 0,
      "failure_log_len": 0
    },
    "plan": {
      "task": "smoke_unknown_skill",
      "subgoal": "deliberate verifier-unknown skill for hybrid smoke",
      "target_object": "drawer",
      "skill": "diagnostic_verifier_unknown",
      "success_check": "noop",
      "fallback": "none",
      "reasoning": "hybrid_replanner_smoke",
      "confidence": 0.1
    },
    "skill_result": {
      "success": false,
      "message": "diagnostic no-op for verifier UNKNOWN path",
      "delta": {
        "skill": "diagnostic_verifier_unknown"
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
            0.12867531994376558,
            -0.037740311373030334,
            0.45998932958428845
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
      "frame_id": "0358502",
      "schema_version": "esa_sm/v1",
      "timestamp_s": null,
      "source": "calvin_teacher",
      "extra": {
        "calvin_robot_meta": {
          "gripper_open": true,
          "gripper_opening_width": 0.0799995819625895,
          "held_object_uid": null,
          "tcp_pos": [
            0.1179967833966753,
            -0.07920850114092064,
            0.5686812265837504
          ],
          "gripper_action": 1
        },
        "language_instruction": "lift the blue block lying in the drawer",
        "gripper_open": true
      }
    },
    "verification": {
      "success": false,
      "failure_type": "unknown_failure",
      "should_replan": true,
      "details": "diagnostic unknown skill branch",
      "extras": {}
    },
    "replan": {
      "task": "open_drawer",
      "subgoal": "Open the drawer fully.",
      "target_object": "drawer",
      "skill": "open",
      "success_check": "drawer has state tag 'open'",
      "fallback": "reach handle from the right",
      "reasoning": "Drawer must be open before placing inside.",
      "confidence": 1.0
    },
    "replan_audit": {
      "original_subgoal": "deliberate verifier-unknown skill for hybrid smoke",
      "failure_type": "unknown_failure",
      "repair_strategy": "delegate_rule_planner_with_failure_context",
      "revised_subgoal": "Open the drawer fully.",
      "whether_rule_based": true,
      "notes": "rule_planner_fallback;failed:FailureType.UNKNOWN_FAILURE:diagnostic unknown skill branch;llm_rejected_before_execution",
      "llm_replanner_called": true,
      "replanner_parse_ok": true,
      "revised_plan_validated": true,
      "revised_plan_accepted": false,
      "fallback_reason": "target_absent_from_scene_memory",
      "fallback_stage": "semantic_acceptance",
      "replanner_parse_error_kind": null,
      "skill_alias_normalized_from": null,
      "raw_generation_head": "{\"task\": \"lift_blue_block\", \"subgoal\": \"grasp_blue_block\", \"target_object\": \"blue_block\", \"skill\": \"grasp\", \"success_check\": \"block_grasped\", \"fallback\": \"open_gripper\", \"optional_reasoning\": \"attempt to grasp the blue block before",
      "parser_repair_actions": [],
      "acceptance_rejection_reason": "target_absent_from_scene_memory",
      "acceptance_rejection_details": [
        "target_object `blue_block` absent from current scene memory objects=['drawer', 'red_block', 'table']"
      ],
      "repeated_no_effect_detected": false,
      "repeated_no_effect_signature": null,
      "repeated_no_effect_consecutive": null,
      "repeated_no_effect_threshold": null,
      "repeated_no_effect_stop": false
    },
    "executor_mode": "symbolic_calvin_teacher_via_CalvinEnvAdapter.apply_skill",
    "env_mode": "fixture",
    "teacher_source": "fixture_json",
    "action_mode": "fixture_symbolic",
    "live_step_executed": false,
    "loop_fallback_reason": null,
    "scene_memory_after_replan": {
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
            0.12867531994376558,
            -0.037740311373030334,
            0.45998932958428845
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
      "frame_id": "0358502",
      "schema_version": "esa_sm/v1",
      "timestamp_s": null,
      "source": "calvin_teacher",
      "extra": {
        "calvin_robot_meta": {
          "gripper_open": true,
          "gripper_opening_width": 0.0799995819625895,
          "held_object_uid": null,
          "tcp_pos": [
            0.1179967833966753,
            -0.07920850114092064,
            0.5686812265837504
          ],
          "gripper_action": 1
        },
        "language_instruction": "lift the blue block lying in the drawer",
        "gripper_open": true
      }
    },
    "skill_result_replan": {
      "success": true,
      "message": "open",
      "delta": {
        "skill": "open"
      }
    },
    "verification_replan": {
      "success": false,
      "failure_type": "state_unchanged",
      "should_replan": true,
      "details": "open had no effect",
      "extras": {}
    },
    "repeated_no_effect_guard": {
      "triggered": false,
      "signature": {
        "skill": "open",
        "target_object": "drawer"
      },
      "consecutive_no_effect_count": 1,
      "threshold": 2,
      "source": "verification_replan"
    }
  },
  "trace_summary": {
    "success": false,
    "replan_count": 2,
    "final_message": "repeated_no_effect_fallback_exhausted",
    "episode_failure_label": "repeated_no_effect_fallback_exhausted",
    "terminal_failure_label": "repeated_no_effect_fallback_exhausted",
    "validated_replan_issue_label": null,
    "label_reasons": [],
    "semantic_issue_step_index": null,
    "terminal_step_index": 1,
    "terminal_failure_type": "state_unchanged",
    "terminal_failure_details": "open had no effect"
  }
}
```

> **Source note:** Latest aligned CALVIN debug batch did not hit a parse-failure trace, so this page uses the real semantic-acceptance rejection case instead.
