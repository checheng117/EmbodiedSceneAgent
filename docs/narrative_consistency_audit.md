# Narrative consistency audit (checklist)

Use this before submission / advisor send. Tick mentally — **do not** claim unchecked items externally.

## Positioning

- [ ] Always describe **3D-memory-driven high-level cognition layer**, not “our robot learns everything end-to-end”.
- [ ] Avoid implying a **continuous low-level policy** is the contribution.
- [ ] **Teacher-state / fixture bootstrap** is framed as **reproducible engineering**, not self-supervised SOTA perception.

## Benchmarks

- [ ] **CALVIN**: separate **dev / fixture** work from **official challenge** results.
- [ ] **RLBench**: distinguish **fixture bridge** vs **sim_reset** vs **leaderboard**.
- [ ] **VLABench**: **planning doc / future_only** unless a harness run exists.

## Evidence classes

- [ ] Every slide/table labels **real** vs **fixture/smoke** vs **future_only**.
- [ ] **Smoke** is not called a **benchmark score**.

## Hybrid replanner

- [ ] If `parse_error_kind_counts` is empty, explain **high success on this batch**, not infinite robustness.

## Suggested wording bans

- Avoid: “completed CALVIN benchmark”, “full RLBench integration”, “trained 7B production model”, “VLABench results”.
