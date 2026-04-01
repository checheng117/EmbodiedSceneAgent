# Showcase Cases

This page summarizes three controlled tiny cases used for side-by-side diagnosis.

Companion pages:

- `docs/showcase_results.md`
- `docs/limitations.md`

## Controlled setup

- `backend=calvin_debug_real`
- `calvin_debug_batch=grouped_sequence`
- `episodes=3`
- `seed=42`
- `verifier_mode=verifier_plus_replan`
- `replanner_mode=hybrid`

## Case A: baseline semantic rejection pattern

- Run: `hybrid_calvin_debug_real_aligned_20260331T103029Z`
- Accepted revised plans: `0/3`
- Typical rejection reasons:
  - `target_absent_from_scene_memory`
  - `drawer_goal_target_mismatch`

Takeaway: schema-valid revised plans can still fail semantic grounding checks without stronger model grounding behavior.

## Case B: VL-3B accepted track

- Run: `hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`
- Accepted revised plans: `3/3`
- Semantic rejection reasons observed: none in this tiny set.

Takeaway: in this controlled tiny setting, VL-3B revisions consistently pass semantic acceptance.

## Case C: VL-7B partial degradation

- Run: `hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`
- Accepted revised plans: `2/3`
- Semantic rejection reasons observed:
  - `target_absent_from_scene_memory` (one case)

Takeaway: VL-7B runs successfully but does not outperform VL-3B on this tiny diagnostic set.

## Shared terminal bottleneck

Across all three runs, terminal failures are dominated by `repeated_no_effect_fallback_exhausted`. This indicates the main remaining bottleneck is repeated no-effect execution dynamics, not merely schema formatting.
