# Hybrid replanner — side-by-side case studies (Assignment 3)

_来源限定为仓库真实产物；CALVIN debug vector-teacher 轨道仅用于课程作业诊断，不是官方 leaderboard。_

## Tiny 3-case shared setup

- backend=`calvin_debug_real`
- batch=`grouped_sequence`
- episodes=`3`
- seed=`42`
- verifier_mode=`verifier_plus_replan`
- replanner_mode=`hybrid`

Run roots:
- baseline: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_20260331T103029Z`
- VL-3B: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun`
- VL-7B: `results/experiments/hybrid_replanner_eval/hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun`

## Case 1 — baseline bad-plan rejected before execution

- episode id: `episode_0358502.npz` (run row `episode_index=1`)
- revised-plan evidence (raw head): `{"task":"move_to","subgoal":"place_blue_block_in_drawer","target_object":"table","skill":"place","success_check":null,...}`
- semantic acceptance outcome: rejected (`drawer_goal_target_mismatch`)
- interpretation: 计划文本提“drawer”，但目标却落到 `table`，属于语义 grounding 错位；系统在 semantic acceptance 阶段拦截，避免直接执行错误计划。
- one-sentence takeaway: 基线并非 parse 崩溃，而是“可解析但语义不成立”的修订计划被稳定拒绝。

## Case 2 — VL-3B accepted-plan example

- episode id: `episode_0358522.npz` (run row `episode_index=2`)
- revised-plan evidence (raw head): `{"task":"grasp","subgoal":"grasp the pink block","target_object":"red_block","skill":"grasp","success_check":"red_block.is_grasped",...}`
- semantic acceptance outcome: accepted (`revised_plan_accepted=true`, fallback stage=`validated`)
- interpretation: 目标对象与场景记忆一致（`red_block` 可见），semantic gate 放行；后续失败主要来自 repeated no-effect，属于执行有效性问题。
- one-sentence takeaway: VL-3B 在 tiny 集合上提供了最稳定的“语义可接受修订计划”证据（3/3）。

## Case 3 — VL-7B partially degraded case

- episode id: `episode_0358502.npz` (run row `episode_index=1`)
- revised-plan evidence (raw head): `{"task":"lift_blue_block","subgoal":"grasp_blue_block","target_object":"blue_block","skill":"grasp",...}`
- semantic acceptance outcome: rejected (`target_absent_from_scene_memory`)
- interpretation: 计划尝试抓取 `blue_block`，但当前 scene memory 仅含 `drawer/red_block/table`，因此被 semantic gate 拒绝。
- one-sentence takeaway: VL-7B 在 tiny 集合可运行但出现 1/3 语义拒绝，不应被表述为优于 VL-3B。

## Tiny comparison conclusion (fixed 3-case)

| Track | Accepted revised plans | Main rejection pattern | Terminal failure label |
|------|---:|------|------|
| Stable baseline | 0/3 | `target_absent_from_scene_memory` (2), `drawer_goal_target_mismatch` (1) | `repeated_no_effect_fallback_exhausted` |
| Qwen2.5-VL-3B | 3/3 | none | `repeated_no_effect_fallback_exhausted` |
| Qwen2.5-VL-7B | 2/3 | `target_absent_from_scene_memory` (1) | `repeated_no_effect_fallback_exhausted` |
