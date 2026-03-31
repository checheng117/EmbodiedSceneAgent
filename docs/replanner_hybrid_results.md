# Hybrid replanner（LLM + 规则）— 结果入口

## 事实源

- 每次 smoke 写入：`results/experiments/hybrid_replanner_smoke/<experiment_id>/`
  - `summary.md`、`trace_full.json`、`per_episode.jsonl`
- 运行：`bash scripts/run_hybrid_replanner_smoke.sh`（默认 `Qwen/Qwen2.5-0.5B-Instruct`，可通过 `ESA_REPLANNER_MODEL_ID` 覆盖）
- Episode 中 `replan_audit` 含：`llm_replanner_called`、`replanner_parse_ok`、`fallback_reason`、`replanner_parse_error_kind`、`skill_alias_normalized_from`（若发生 alias 归一化）等。
- `metrics.json` / `fallback_stats.json`（batch eval）另含：`unknown_skill_rate`、`invalid_skill_count`、`alias_normalization_count`（LLM 调用粒度，见 `hybrid_replanner_smoke._fallback_stats_from_traces`）。

## 行为摘要

1. **规则 replanner** 先产生局部修订。  
2. 对 **delegate / 特定 failure_type**，尝试 **LLM JSON** 输出，经 `planner_output_contract` 校验。  
3. 校验失败则 **回退规则计划**，并在 audit 中记录 `fallback_reason`。

## 不能夸大

- 非大规模成功率实验；**仅证明** LLM 路径已进入统一 cognition loop 且可审计。

## Assignment 3 packaging snapshot (fixed runs, no fabrication)

### Run mapping used in this round

- Stable baseline (tiny 3-case anchor): `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T103029Z`
- Qwen2.5-VL-3B tiny qualitative rerun: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`
- Qwen2.5-VL-7B tiny qualitative rerun: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`
- Base vs tuned main quantitative comparator: `results/eval/planner_base_vs_tuned/metrics.json`

### Shared tiny-3 setup consistency

The three tiny runs above share:
- backend=`calvin_debug_real`
- calvin_debug_batch=`grouped_sequence`
- episodes=`3`
- seed=`42`
- verifier_mode=`verifier_plus_replan`
- replanner_mode=`hybrid`

Evidence: each run's `config.snapshot.json` and `run_manifest.json`.

### Tiny-3 key comparison conclusion

| track | parse_ok | validated | accepted revised plans | semantic rejection |
|------|---:|---:|---:|---:|
| stable baseline | 3/3 | 3/3 | 0/3 | 3/3 |
| VL-3B rerun | 3/3 | 3/3 | 3/3 | 0/3 |
| VL-7B rerun | 3/3 | 3/3 | 2/3 | 1/3 |

Interpretation (Assignment-3 aligned):
- 全部轨道在 parse/validate 层面都稳定，不是“格式问题”主导。
- 差异来自 semantic acceptance：基线全部被拒，VL-3B 全部通过，VL-7B 部分通过。
- 终止失败标签仍集中在 `repeated_no_effect_fallback_exhausted`，说明后续瓶颈更多是执行无效/状态不变，而非纯语义垃圾计划。

## Batch eval snapshot (`hybrid_replanner_eval_20260325T084014Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 0.000 |
| validated_revision_rate | 0.000 |
| fallback_rate | 1.000 |
| repair_success_rate | 1.000 |
| unknown_failure_rate | 0.600 |

### fallback_reason_counts

```json
{
  "json decode failed: Unterminated string starting at: line 6 column 20 (char 207)": 6
}
```

### fallback_stage_counts

```json
{
  "parse_validate": 6
}
```

_Artifact: `results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260325T084014Z`_

## Batch eval snapshot (`hybrid_replanner_eval_20260325T090504Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 1.000 |
| unknown_failure_rate | 0.615 |

### parse_error_kind_counts

```json
{}
```

### fallback_reason_counts

```json
{}
```

### fallback_stage_counts

```json
{
  "validated": 8
}
```

_Artifact: `results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260325T090504Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_20260326T083447Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.111 |

### parse_error_kind_counts

```json
{}
```

### fallback_reason_counts

```json
{}
```

### fallback_stage_counts

```json
{
  "validated": 10
}
```

_Artifact: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_20260326T083447Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_20260326T094544Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 0.667 |
| validated_revision_rate | 0.667 |
| fallback_rate | 0.333 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.103 |
| unknown_skill_rate | 0.167 |
| alias_normalization_count | 1 |
| invalid_skill_count | 1 |

### parse_error_kind_counts

```json
{
  "missing_required_keys": 1,
  "invalid_skill": 1
}
```

### fallback_reason_counts

```json
{
  "null field: success_check": 1,
  "skill not in canonical vocabulary after alias normalize: 'open_drawer'": 1
}
```

### fallback_stage_counts

```json
{
  "validated": 4,
  "parse_validate": 2
}
```

_Artifact: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260326T094544Z`_

## Batch eval snapshot (`hybrid_calvin_debug_same_task_20260326T094718Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 0.750 |
| validated_revision_rate | 0.750 |
| fallback_rate | 0.250 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.105 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 1 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{
  "missing_required_keys": 1
}
```

### fallback_reason_counts

```json
{
  "null field: success_check": 1
}
```

### fallback_stage_counts

```json
{
  "validated": 3,
  "parse_validate": 1
}
```

_Artifact: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_same_task_20260326T094718Z`_

## Batch eval snapshot (`hybrid_calvin_debug_same_task_20260326T095232Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 0.500 |
| validated_revision_rate | 0.500 |
| fallback_rate | 0.500 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.100 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{
  "missing_required_keys": 1
}
```

### fallback_reason_counts

```json
{
  "null field: success_check": 1
}
```

### fallback_stage_counts

```json
{
  "validated": 1,
  "parse_validate": 1
}
```

_Artifact: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_same_task_20260326T095232Z`_

## Batch eval snapshot (`hybrid_replanner_eval_20260331T084240Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 0.000 |
| validated_revision_rate | 0.000 |
| fallback_rate | 1.000 |
| repair_success_rate | 1.000 |
| unknown_failure_rate | 0.600 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{
  "missing_required_keys": 3
}
```

### fallback_reason_counts

```json
{
  "null field: success_check": 3
}
```

### fallback_stage_counts

```json
{
  "parse_validate": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_replanner_eval_20260331T084240Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_20260331T085126Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 0.333 |
| validated_revision_rate | 0.333 |
| fallback_rate | 0.667 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.100 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{
  "missing_required_keys": 1,
  "truncated_json": 1
}
```

### fallback_reason_counts

```json
{
  "null field: success_check": 1,
  "json decode failed: Unterminated string starting at: line 8 column 16 (char 171)": 1
}
```

### fallback_stage_counts

```json
{
  "validated": 1,
  "parse_validate": 2
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T085126Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_20260331T090512Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.103 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### fallback_reason_counts

```json
{}
```

### fallback_stage_counts

```json
{
  "validated": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T090512Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_20260331T090741Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.103 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### fallback_reason_counts

```json
{}
```

### fallback_stage_counts

```json
{
  "validated": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T090741Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_20260331T093956Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.103 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### episode_failure_label_counts

```json
{
  "schema_valid_but_semantically_bad_replan": 3
}
```

### terminal_failure_label_counts

```json
{
  "no_state_change_after_valid_replan": 3
}
```

### fallback_reason_counts

```json
{}
```

### fallback_stage_counts

```json
{
  "validated": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T093956Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_20260331T095352Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.100 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### episode_failure_label_counts

```json
{
  "no_state_change_after_valid_replan": 3
}
```

### terminal_failure_label_counts

```json
{
  "no_state_change_after_valid_replan": 3
}
```

### acceptance_rejection_reason_counts

```json
{
  "target_absent_from_scene_memory": 2,
  "drawer_goal_target_mismatch": 1
}
```

### fallback_reason_counts

```json
{
  "target_absent_from_scene_memory": 2,
  "drawer_goal_target_mismatch": 1
}
```

### fallback_stage_counts

```json
{
  "semantic_acceptance": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T095352Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_20260331T095511Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.100 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### episode_failure_label_counts

```json
{
  "no_state_change_after_valid_replan": 3
}
```

### terminal_failure_label_counts

```json
{
  "no_state_change_after_valid_replan": 3
}
```

### acceptance_rejection_reason_counts

```json
{
  "target_absent_from_scene_memory": 2,
  "drawer_goal_target_mismatch": 1
}
```

### fallback_reason_counts

```json
{
  "target_absent_from_scene_memory": 2,
  "drawer_goal_target_mismatch": 1
}
```

### fallback_stage_counts

```json
{
  "semantic_acceptance": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T095511Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_20260331T103029Z`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.429 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### episode_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### terminal_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### acceptance_rejection_reason_counts

```json
{
  "target_absent_from_scene_memory": 2,
  "drawer_goal_target_mismatch": 1
}
```

### fallback_reason_counts

```json
{
  "target_absent_from_scene_memory": 2,
  "drawer_goal_target_mismatch": 1
}
```

### fallback_stage_counts

```json
{
  "semantic_acceptance": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T103029Z`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_3b_qual_pilot_20260331`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 0.000 |
| validated_revision_rate | 0.000 |
| fallback_rate | 1.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.429 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{
  "model_load_failed": 3
}
```

### episode_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### terminal_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### acceptance_rejection_reason_counts

```json
{}
```

### fallback_reason_counts

```json
{
  "Unrecognized configuration class <class 'transformers.models.qwen2_5_vl.configuration_qwen2_5_vl.Qwen2_5_VLConfig'> for this kind of AutoModel: AutoModelForCausalLM.\nModel type should be one of AfmoeC": 3
}
```

### fallback_stage_counts

```json
{
  "model_load": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_3b_qual_pilot_20260331`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_7b_qual_pilot_20260331`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 0.000 |
| validated_revision_rate | 0.000 |
| fallback_rate | 1.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.429 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{
  "model_load_failed": 3
}
```

### episode_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### terminal_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### acceptance_rejection_reason_counts

```json
{}
```

### fallback_reason_counts

```json
{
  "Unrecognized configuration class <class 'transformers.models.qwen2_5_vl.configuration_qwen2_5_vl.Qwen2_5_VLConfig'> for this kind of AutoModel: AutoModelForCausalLM.\nModel type should be one of AfmoeC": 3
}
```

### fallback_stage_counts

```json
{
  "model_load": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_20260331`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_vl3b_loader_smoke_20260331`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.500 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### episode_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 1
}
```

### terminal_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 1
}
```

### acceptance_rejection_reason_counts

```json
{}
```

### fallback_reason_counts

```json
{}
```

### fallback_stage_counts

```json
{
  "validated": 1
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_vl3b_loader_smoke_20260331`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_vl7b_loader_smoke_20260331`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.333 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### episode_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 1
}
```

### terminal_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 1
}
```

### acceptance_rejection_reason_counts

```json
{}
```

### fallback_reason_counts

```json
{}
```

### fallback_stage_counts

```json
{
  "validated": 1
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_vl7b_loader_smoke_20260331`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.429 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### episode_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### terminal_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### acceptance_rejection_reason_counts

```json
{}
```

### fallback_reason_counts

```json
{}
```

### fallback_stage_counts

```json
{
  "validated": 3
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`_

## Batch eval snapshot (`hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`)

| metric | value |
|--------|------:|
| replan_parse_success_rate | 1.000 |
| validated_revision_rate | 1.000 |
| fallback_rate | 0.000 |
| repair_success_rate | 0.000 |
| unknown_failure_rate | 0.375 |
| unknown_skill_rate | 0.000 |
| alias_normalization_count | 0 |
| invalid_skill_count | 0 |

### parse_error_kind_counts

```json
{}
```

### episode_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### terminal_failure_label_counts

```json
{
  "repeated_no_effect_fallback_exhausted": 3
}
```

### acceptance_rejection_reason_counts

```json
{
  "target_absent_from_scene_memory": 1
}
```

### fallback_reason_counts

```json
{
  "target_absent_from_scene_memory": 1
}
```

### fallback_stage_counts

```json
{
  "validated": 2,
  "semantic_acceptance": 1
}
```

_Artifact: `/home/cc/Project/CC/EmbodiedSceneAgent/results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`_
