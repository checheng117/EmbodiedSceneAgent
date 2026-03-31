# Tiny 3-case qualitative summary (CALVIN debug-real, fixed setting)

## Controlled setup equivalence

The three compared runs use the same setup:
- backend=`calvin_debug_real`
- calvin_debug_batch=`grouped_sequence`
- episodes=`3`
- seed=`42`
- verifier_mode=`verifier_plus_replan`
- replanner_mode=`hybrid`

Run IDs:
- stable baseline: `hybrid_calvin_debug_real_aligned_20260331T103029Z`
- Qwen2.5-VL-3B rerun: `hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`
- Qwen2.5-VL-7B rerun: `hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`

## Fixed comparison facts (must-read)

- stable baseline accepted revised plans = **0/3**
- Qwen2.5-VL-3B accepted revised plans = **3/3**
- Qwen2.5-VL-7B accepted revised plans = **2/3**

## What bad grounding looked like

- `target_absent_from_scene_memory`: generated target (e.g., `workspace` or `blue_block`) is absent from current memory objects (`drawer`, `red_block`, `table`).
- `drawer_goal_target_mismatch`: text expresses drawer/slider intent, but target is grounded to a non-drawer object (e.g., `table`).

## Honest interpretation for Assignment 3

- Why VL-3B is the strongest secondary comparison track now:
  - It has the best semantic-acceptance outcome on the same tiny set (3/3 accepted).
  - It demonstrates that improvements are not just parse-level; they survive semantic gating.
- Why VL-7B should not be oversold:
  - It is runnable and mostly valid (2/3 accepted), but it does **not** outperform VL-3B on this fixed tiny set.
  - The sample size is only 3 episodes, so findings are qualitative and diagnostic, not statistically conclusive.

## Terminal failure perspective

Across all three runs, terminal failures remain dominated by `repeated_no_effect_fallback_exhausted`.  
This indicates the remaining bottleneck is primarily execution-side no-effect behavior after a semantically acceptable plan, rather than pure semantic garbage output.
