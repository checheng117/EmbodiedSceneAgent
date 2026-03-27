# CALVIN debug alignment — export statistics (auto)

_Official debug vectors only; instructions from YAML manifest pool — **not** official CALVIN benchmark._

## Samples per alignment_mode

| alignment_mode | train rows | val rows | test rows | notes |
|----------------|------------|----------|-----------|-------|
| `pooled_manifest` | 36 | 24 | 24 | Loose random npz sample + round-robin instruction index (legacy-style). |
| `grouped_sequence` | 36 | 480 | 480 | Consecutive npz windows; one stable-hash instruction per window (recommended for interpretable E2/hybrid). |
| `same_task_subset` | 3840 | 1920 | 1920 | Smaller same-task-like subset; manifests under `data/processed/calvin_debug_same_task_subset/`. |

## Lineage fields (per-row `metadata`)

- `alignment_mode`, `instruction_source`, `instruction_assignment_strategy`
- `episode_key`, `clip_key`, `npz_group_key`, `temporal_group_id`
- `whether_same_task_subset`, `lineage_note`

## Recommendation

- **E2 / hybrid small-batch explainability**: prefer **`grouped_sequence`** exports + matching `--calvin-debug-batch grouped_sequence`.
- **Tightest batch coherence**: **`same_task_subset`** (smallest N; not official task labels).
