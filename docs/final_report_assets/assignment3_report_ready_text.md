# Assignment 3 report-ready text

## 1) Experimental Results

Our reporting uses only repository-backed artifacts and separates directly comparable metrics from tiny-set qualitative evidence. For the main quantitative comparison, we use `results/eval/planner_base_vs_tuned/metrics.json` (`n=73`): both base and tuned models keep 1.000 format compliance, while the tuned variant improves tool-use accuracy from 0.082 to 0.219, target-match rate from 0.329 to 0.479, and strict task proxy from 0.068 to 0.205. This forms the primary base-vs-tuned evidence.  

For hybrid replanner qualitative comparison, we use three fixed CALVIN debug-real runs with identical setup (`backend=calvin_debug_real`, `batch=grouped_sequence`, `episodes=3`, `seed=42`). The stable baseline run accepts 0/3 revised plans, Qwen2.5-VL-3B accepts 3/3, and Qwen2.5-VL-7B accepts 2/3. All three runs parse and validate at 3/3, so the distinguishing factor is semantic acceptance rather than JSON formatting.

## 2) Analysis & Discussion

The evidence shows two consistent layers of progress. First, the tuned planner improves structured action-target correctness in the JSONL proxy evaluation without sacrificing format compliance. Second, on the tiny controlled hybrid rerun, model differences mainly emerge at semantic acceptance: the baseline repeatedly generates semantically rejectable grounding, whereas VL-3B consistently stays within scene-memory constraints and VL-7B does so in most cases.  

At the same time, the terminal failure label remains `repeated_no_effect_fallback_exhausted` across tracks, including runs with accepted revised plans. This suggests that remaining errors are increasingly execution-side/no-effect issues after semantic filtering, not only planner output validity issues.

## 3) Tiny qualitative comparison paragraph

Under the same backend/batch/seed/episode setting, the fixed 3-case CALVIN debug-real comparison gives a clear ordering for semantic acceptance quality: stable baseline 0/3 accepted revised plans, Qwen2.5-VL-3B 3/3, and Qwen2.5-VL-7B 2/3. The baseline rejections are primarily `target_absent_from_scene_memory` and `drawer_goal_target_mismatch`, while VL-7B still shows one `target_absent_from_scene_memory` rejection. Therefore, VL-3B is currently the strongest secondary comparison track for this assignment-style qualitative section, and VL-7B should be reported as runnable but not superior on this tiny set.

## 4) Honest limitation paragraph

These results do not claim official CALVIN leaderboard performance. The base-vs-tuned table is a proxy evaluation on structured planner outputs, and the hybrid model comparison is based on only 3 fixed episodes, which is useful for diagnosis but not for statistical significance. We therefore treat the tiny comparison as qualitative evidence for semantic-grounding behavior and keep claims scoped to the observed artifacts.
