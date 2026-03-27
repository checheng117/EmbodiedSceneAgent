# CALVIN debug real-data planner export stats (auto)

_**Not** official CALVIN benchmark; vectors from official debug zip; language from YAML manifest pool only._

- alignment_mode: **`same_task_subset`**
- debug root: `data/raw/calvin_official/dataset/calvin_debug_dataset`（本机克隆后路径；可用 `ESA_CALVIN_OFFICIAL_ROOT` 覆盖）
- manifest (instruction pool): `data/processed/calvin_real_subset/manifest.jsonl`
- pool size (distinct instructions): **423**
- output basename: `calvin_debug_real_same_task`

## Row counts

| split | rows | npz files used |
|-------|-----:|---------------:|
| train | 3840 | 320 |
| val | 1920 | 160 |
| test | 1920 | 160 |
| **total** | **7680** | — |

## trajectory_type (step-level)

- counts: `{'recovery': 7320, 'normal': 360}`
- recovery-labeled steps: **7320** (from replan supervision in loop, not raw dataset field)

## Lineage (honest)

- counts: `{'from_official_debug_vectors': 7680, 'recovery_from_loop_replan': 7320}`
- **Pure language from npz**: **no** (debug zip lacks `lang_annotations`).
- **Observation state**: **yes** — `robot_obs` + `scene_obs` from official debug frames.
- **Execution**: symbolic skills on `CalvinEnvAdapter` initialised from vector-derived teacher — **not** physics replay of `actions` in npz.
