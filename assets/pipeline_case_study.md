# Pipeline Case Study

## Controlled tiny comparison snapshot

| Track | Accepted revised plans | Quick interpretation |
|------|---:|---|
| Baseline | 0/3 | Revisions are rejected by semantic checks in all tiny cases |
| VL-3B | 3/3 | Best current secondary qualitative behavior on this tiny set |
| VL-7B | 2/3 | Runnable and mostly valid, but below VL-3B on this tiny set |

## Case sequence summary

1. **Baseline semantic rejection case**
   - Typical reasons: `target_absent_from_scene_memory`, `drawer_goal_target_mismatch`.
   - Meaning: schema validity alone is insufficient for safe execution.

2. **VL-3B accepted case**
   - Revised plans pass semantic acceptance in all three tiny episodes.
   - Meaning: improved grounding quality under controlled tiny conditions.

3. **VL-7B partial degradation case**
   - One of three tiny episodes is rejected by semantic acceptance.
   - Meaning: larger model path is functional, but does not outperform VL-3B here.

## Honest scope

- This is a diagnostic tiny comparison, not a benchmark-scale ranking.
- Primary quantitative support remains the `n=73` base-vs-tuned proxy table.
