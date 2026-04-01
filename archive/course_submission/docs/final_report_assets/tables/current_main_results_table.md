# Assignment 3 main results table

_只使用仓库内已有产物；不混淆官方 benchmark 与代理评测。_

## A) Primary quantitative table (base vs tuned, directly comparable)

Source: `results/eval/planner_base_vs_tuned/metrics.json` (`n=73`)

| Track | Format compliance | Tool-use accuracy | Target-match rate | Strict task proxy |
|------|---:|---:|---:|---:|
| Stable baseline (planner base) | 1.000 | 0.082 | 0.329 | 0.068 |
| Tuned / improved mainline (planner tuned, LoRA 3B minimal) | 1.000 | 0.219 | 0.479 | 0.205 |

Notes:
- `strict task proxy = format_compliance AND tool_skill_match AND target_match`（JSONL 代理，不等价于 CALVIN 环境成功率）。
- 该表用于“base vs tuned”主对照，是当前最稳妥的可比定量证据。

## B) Tiny 3-case qualitative comparison table (same setup, side-by-side)

Shared setup: backend=`calvin_debug_real`, batch=`grouped_sequence`, episodes=`3`, seed=`42`, verifier_mode=`verifier_plus_replan`, replanner_mode=`hybrid`  
Config source: each run `config.snapshot.json` + `run_manifest.json`.

| Track | Run ID | Parse success | Validated revisions | Accepted revised plans | Semantic rejection (count) | Fallback stage summary | Terminal failure label |
|------|------|---:|---:|---:|---:|------|------|
| Stable baseline (hybrid mainline stable anchor) | `hybrid_calvin_debug_real_aligned_20260331T103029Z` | 3/3 | 3/3 | 0/3 | 3/3 | `semantic_acceptance: 3` | `repeated_no_effect_fallback_exhausted` (3) |
| Qwen2.5-VL-3B tiny qualitative rerun | `hybrid_calvin_debug_real_aligned_3b_qual_pilot_rerun` | 3/3 | 3/3 | 3/3 | 0/3 | `validated: 3` | `repeated_no_effect_fallback_exhausted` (3) |
| Qwen2.5-VL-7B tiny qualitative rerun | `hybrid_calvin_debug_real_aligned_7b_qual_pilot_rerun` | 3/3 | 3/3 | 2/3 | 1/3 (`target_absent_from_scene_memory`) | `validated: 2`, `semantic_acceptance: 1` | `repeated_no_effect_fallback_exhausted` (3) |

Notes:
- tiny 3-case 只用于定性诊断与“可接受修订计划”比较，不能外推为统计显著结论。
- 三条轨道在 parse/validate 上均稳定；差异主要体现在 semantic acceptance（0/3 vs 3/3 vs 2/3）。
