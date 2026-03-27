# Interview brief (engineering + systems)

## Architecture story (60s)

We built a **typed loop** around scene memory with **Pydantic-level** planner outputs and **audited** replans — easy to extend with new env adapters because the contracts stay fixed.

## Hard parts solved

- Unified episode log schema across mock + CALVIN minimal loop.
- Hybrid replanner: LLM JSON must pass `planner_output_contract` or fall back with explicit audit reason.
- RLBench: layered diagnostics so failures are **machine-readable** (import vs sim vs reset).

## Metrics you can cite without over-claiming

```json
{
  "hybrid_batch": {
    "replan_parse_success_rate": 1.0,
    "validated_revision_rate": 1.0,
    "fallback_rate": 0.0,
    "repair_success_rate": 1.0,
    "unknown_failure_rate": 0.6153846153846154,
    "unknown_skill_rate": null,
    "alias_normalization_count": null,
    "invalid_skill_count": null
  },
  "rlbench_deepest": "import_fail"
}
```

## Future scaling

Swap teacher-state adapters for predicted memory; keep contracts; add official eval harnesses — **future_only** today.
