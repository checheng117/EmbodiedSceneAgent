# Hybrid replanner — curated cases (auto)

_**Fixture / mock batch** — 非官方 benchmark。JSON 见 `results/demos/hybrid_replanner_cases/`。_

## 1) LLM replan 后任务恢复
- 文件：[`case_llm_repair_success.json`](../../results/demos/hybrid_replanner_cases/case_llm_repair_success.json)
- 本 batch 内命中：见 JSON `source=eval_batch`。

## 2) Parse / 校验失败 → 规则回退
- 文件：[`case_parse_fallback.json`](../../results/demos/hybrid_replanner_cases/case_parse_fallback.json)
- 本 batch 未命中 parse 回退（可能全部解析成功或未调用 LLM）。

## 3) LLM 计划通过校验但后续 verification_replan 仍失败
- 文件：[`case_validated_repair_failed.json`](../../results/demos/hybrid_replanner_cases/case_validated_repair_failed.json)
- 本 batch 内命中该组合。

## CALVIN debug real-data backed hybrid (not benchmark)

_下列分节对应不同 `CALVIN_DEBUG_BATCH` / `--calvin-debug-batch`，互不覆盖。_

## Hybrid CALVIN debug — grouped_sequence (aligned)

_官方 debug ``*.npz`` 向量 teacher + hybrid replanner；**非** leaderboard；来源 **`calvin_debug_real_aligned`**（batch=`grouped_sequence`）。_

### A) 最近似成功（LLM 校验修订）
- [`case_calvin_debug_real_aligned_hybrid_success.json`](../../results/demos/hybrid_replanner_cases/case_calvin_debug_real_aligned_hybrid_success.json)

### B) Fallback（解析失败）
- [`case_calvin_debug_real_aligned_hybrid_fallback.json`](../../results/demos/hybrid_replanner_cases/case_calvin_debug_real_aligned_hybrid_fallback.json)

## Hybrid CALVIN debug — same_task_subset

_官方 debug ``*.npz`` 向量 teacher + hybrid replanner；**非** leaderboard；来源 **`calvin_debug_same_task`**（batch=`same_task_subset`）。_

### A) 最近似成功（LLM 校验修订）
- [`case_calvin_debug_same_task_hybrid_success.json`](../../results/demos/hybrid_replanner_cases/case_calvin_debug_same_task_hybrid_success.json)

### B) Fallback（解析失败）
- [`case_calvin_debug_same_task_hybrid_fallback.json`](../../results/demos/hybrid_replanner_cases/case_calvin_debug_same_task_hybrid_fallback.json)
