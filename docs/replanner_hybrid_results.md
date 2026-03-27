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
