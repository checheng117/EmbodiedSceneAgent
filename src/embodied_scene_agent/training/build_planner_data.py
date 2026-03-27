"""Export planner SFT rows from CALVIN minimal-loop traces or real CALVIN-lang mock rollouts."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

from embodied_scene_agent.data.calvin_debug_alignment import (
    AlignmentMode,
    grouped_path_assignments,
    rows_by_group_ordered,
    same_task_subset_splits,
    write_same_task_manifests,
)
from embodied_scene_agent.data.calvin_debug_dataset import (
    default_calvin_debug_root,
    instruction_pool_from_manifest,
    iter_npz_frames,
    load_debug_npz,
)
from embodied_scene_agent.perception.calvin_debug_vector_teacher import (
    build_initial_observation_from_debug_vectors,
)
from embodied_scene_agent.pipeline.run_calvin_minimal_loop import run_calvin_minimal_episode
from embodied_scene_agent.pipeline.v0_loop import EpisodeTrace
from embodied_scene_agent.training.mock_rollout_export import (
    iter_rows_from_v0_trace,
    run_export_episode,
    write_jsonl,
)
from embodied_scene_agent.utils.paths import repo_root

PLANNER_SFT_SCHEMA_VERSION = "planner_sft/v0"


def _data_lineage_for_step(
    *,
    row_env: str,
    row_action: str,
    episode_live_step: bool,
    step_live: bool,
) -> str:
    if row_env == "fixture":
        return "fixture"
    if step_live or episode_live_step or row_action == "live_zero_action_smoke":
        return "live_observation_live_step"
    if row_env == "live_env":
        return "live_observation_symbolic_action"
    return "symbolic"


def iter_planner_rows_from_calvin_trace(
    trace: EpisodeTrace,
    *,
    source: str = "calvin",
    schema_version: str = PLANNER_SFT_SCHEMA_VERSION,
) -> Iterator[dict[str, Any]]:
    """Yield one dict per step (legacy planner_sft/v0 schema)."""
    trace_id = getattr(trace, "trace_id", "") or ""
    experiment_id = getattr(trace, "experiment_id", "") or ""
    env_mode = getattr(trace, "env_mode", "") or ""
    teacher_source = getattr(trace, "teacher_source", "") or ""
    action_mode = getattr(trace, "action_mode", "") or ""
    whether_live = getattr(trace, "whether_live_step_executed", False)
    live_probe_status = getattr(trace, "live_probe_status", None) or {}
    live_reset_ok = getattr(trace, "live_reset_succeeded", False)
    live_step_attempted_ep = getattr(trace, "live_step_attempted", False)
    loop_fb = getattr(trace, "loop_fallback_reason", "") or ""

    for step in trace.steps:
        row_env = step.get("env_mode") or env_mode
        row_teacher = step.get("teacher_source") or teacher_source
        row_action = step.get("action_mode") or action_mode
        step_live = bool(step.get("live_step_executed"))
        lineage = _data_lineage_for_step(
            row_env=row_env,
            row_action=row_action,
            episode_live_step=whether_live,
            step_live=step_live,
        )

        yield {
            "instruction": trace.instruction,
            "scene_memory": step.get("scene_memory_before"),
            "history": step.get("history", []),
            "failure_log": step.get("failure_log", []),
            "planner_output": step.get("plan"),
            "target_subgoal": (step.get("plan") or {}).get("subgoal"),
            "verification": step.get("verification"),
            "skill_execution": step.get("skill_result"),
            "metadata": {
                "source": source,
                "schema_version": schema_version,
                "env_mode": row_env,
                "teacher_source": row_teacher,
                "action_mode": row_action,
                "data_lineage": lineage,
                "live_probe_status": live_probe_status,
                "live_reset_succeeded": live_reset_ok,
                "live_step_attempted_episode": live_step_attempted_ep,
                "loop_fallback_reason": loop_fb or None,
                "trace_id": trace_id,
                "experiment_id": experiment_id or None,
                "episode_whether_live_step_executed": whether_live,
                "step_live_step_executed": step_live,
                "executor_mode": step.get("executor_mode", ""),
                "episode_success": trace.success,
                "episode_final_message": trace.final_message,
            },
        }


def export_trace_to_jsonl(trace: EpisodeTrace, path: Path | str, **kwargs: Any) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with p.open("w", encoding="utf-8") as f:
        for row in iter_planner_rows_from_calvin_trace(trace, **kwargs):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def _load_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _build_real_subset_splits(
    manifest_rows: list[dict[str, Any]],
    *,
    seed: int,
    max_train_episodes: int,
    max_val_episodes: int,
    max_test_episodes: int,
) -> dict[str, list[dict[str, Any]]]:
    """
    Train rows come only from ``train_pool`` (new_playtable.yaml).
    Val/test rows come only from ``validation_pool`` (new_playtable_validation.yaml), split by hash.
    """
    rng = random.Random(seed)
    eligible = [r for r in manifest_rows if r.get("can_rollout_mock_symbolic")]
    train_pool = [r for r in eligible if r.get("split_role") == "train_pool"]
    val_pool = [r for r in eligible if r.get("split_role") == "validation_pool"]
    rng.shuffle(train_pool)
    rng.shuffle(val_pool)

    buckets: dict[str, list[dict[str, Any]]] = {
        "train": train_pool[:max_train_episodes],
        "val": [],
        "test": [],
    }
    for r in val_pool:
        if len(buckets["val"]) >= max_val_episodes and len(buckets["test"]) >= max_test_episodes:
            break
        eid = str(r.get("episode_id", ""))
        h = int(hashlib.sha256(eid.encode()).hexdigest(), 16)
        prefer_val = h % 2 == 0
        if prefer_val and len(buckets["val"]) < max_val_episodes:
            buckets["val"].append(r)
        elif not prefer_val and len(buckets["test"]) < max_test_episodes:
            buckets["test"].append(r)
        elif len(buckets["val"]) < max_val_episodes:
            buckets["val"].append(r)
        elif len(buckets["test"]) < max_test_episodes:
            buckets["test"].append(r)

    return buckets


def _write_stats_md(
    path: Path,
    *,
    splits: dict[str, list[dict[str, Any]]],
    flat_rows: dict[str, list[dict[str, Any]]],
) -> None:
    lines = ["# Planner SFT dataset stats (auto)", ""]
    for name in ("train", "val", "test"):
        rows = flat_rows.get(name, [])
        c = Counter(r.get("trajectory_type", "?") for r in rows)
        lines.append(f"## {name}")
        lines.append(f"- samples: {len(rows)}")
        lines.append(f"- by trajectory_type: {dict(c)}")
        lines.append(f"- manifest episodes used: {len(splits.get(name, []))}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_fixture_export(args: argparse.Namespace) -> None:
    from embodied_scene_agent.pipeline.run_calvin_minimal_loop import run_calvin_minimal_episode

    trace = run_calvin_minimal_episode(
        args.instruction,
        fixture_path=args.fixture,
        max_steps=args.max_steps,
        experiment_id=args.experiment_id,
    )
    n = export_trace_to_jsonl(trace, args.out)
    print(f"[build_planner_data fixture] wrote {n} rows (v0) to {args.out}")


def _sample_npz_paths(split_dir: Path, max_n: int, rng: random.Random) -> list[Path]:
    all_p = list(iter_npz_frames(split_dir))
    if not all_p:
        return []
    k = min(max_n, len(all_p))
    pick = rng.sample(all_p, k=k)
    return sorted(pick, key=lambda p: p.name)


def _split_val_test(paths: list[Path], rng: random.Random) -> tuple[list[Path], list[Path]]:
    val: list[Path] = []
    test: list[Path] = []
    for p in paths:
        h = int(hashlib.md5(p.name.encode(), usedforsecurity=False).hexdigest(), 16)
        if h % 2 == 0:
            val.append(p)
        else:
            test.append(p)
    return val, test


def _split_val_test_by_groups(
    val_dir: Path,
    pool: list[str],
    *,
    window: int,
    stride: int,
    max_val_samples: int,
    max_test_samples: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Whole temporal groups only; fill val first then test until path budgets."""
    pairs = rows_by_group_ordered(val_dir, pool, window, stride)
    val_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []
    for _gid, rows in pairs:
        if len(val_rows) < max_val_samples:
            val_rows.extend(rows)
        elif len(test_rows) < max_test_samples:
            test_rows.extend(rows)
        else:
            break
    return val_rows, test_rows


def _alignment_extra_metadata(
    *,
    alignment_mode: AlignmentMode,
    manifest_path: Path,
    rel_npz: str,
    stem: str,
    assignment: dict[str, Any],
) -> dict[str, Any]:
    strat = {
        "pooled_manifest": "round_robin_index_in_split_sample_order",
        "grouped_sequence": "stable_hash_per_temporal_window",
        "same_task_subset": "stable_hash_per_temporal_window_same_task_like_subset",
    }[alignment_mode]
    note = {
        "pooled_manifest": (
            "Weak alignment: instruction cycles with sample index; observation may not match language."
        ),
        "grouped_sequence": (
            "Stronger alignment: one instruction per consecutive-npz window; still not official lang labels."
        ),
        "same_task_subset": (
            "Same-task-like subset: first N temporal windows per split; smallest, most batch-coherent export."
        ),
    }[alignment_mode]
    return {
        "alignment_mode": alignment_mode,
        "instruction_source": "calvin_yaml_manifest_pool",
        "instruction_assignment_strategy": strat,
        "episode_key": assignment["episode_key"],
        "clip_key": assignment["clip_key"],
        "npz_group_key": assignment["npz_group_key"],
        "temporal_group_id": assignment["temporal_group_id"],
        "whether_same_task_subset": alignment_mode == "same_task_subset",
        "lineage_note": note,
        "calvin_debug_npz_relpath": rel_npz,
        "instruction_lineage": "yaml_manifest_pool_not_npz_lang",
        "observation_lineage": "calvin_debug_dataset_robot_scene_vectors",
        "symbolic_execution_lineage": "calvin_minimal_loop_symbolic_skills_on_vector_teacher",
        "npz_frame_stem": stem,
        "instruction_manifest_path": str(manifest_path.resolve()),
    }


def run_calvin_debug_real_export(args: argparse.Namespace) -> None:
    """
    Build planner SFT JSONL from official debug ``*.npz`` vectors + minimal CALVIN loop (symbolic executor).

    Instructions are **not** read from npz (debug zip lacks lang_annotations); pool comes from the
    official YAML-derived manifest — assignment strategy depends on ``--alignment-mode``.
    """
    manifest_path = Path(args.manifest)
    pool = instruction_pool_from_manifest(manifest_path)
    if not pool:
        pool = ["Put the red block in the drawer."]
    rng = random.Random(int(args.seed))
    root_debug = Path(args.calvin_debug_root).resolve() if args.calvin_debug_root else default_calvin_debug_root()
    train_dir = root_debug / "training"
    val_dir = root_debug / "validation"
    alignment_mode: AlignmentMode = str(getattr(args, "alignment_mode", "grouped_sequence"))  # type: ignore[assignment]
    window = int(getattr(args, "alignment_window", 40))
    stride = int(getattr(args, "alignment_stride", 20))

    train_assign: list[dict[str, Any]]
    val_assign: list[dict[str, Any]]
    test_assign: list[dict[str, Any]]
    npz_counts = {"train": 0, "val": 0, "test": 0}

    if alignment_mode == "pooled_manifest":
        train_paths = _sample_npz_paths(train_dir, int(args.max_train_samples), rng)
        val_pick = _sample_npz_paths(
            val_dir, int(args.max_val_samples) + int(args.max_test_samples), rng
        )
        val_paths, test_paths = _split_val_test(val_pick, rng)
        val_paths = val_paths[: int(args.max_val_samples)]
        test_paths = test_paths[: int(args.max_test_samples)]

        def _paths_to_pooled_assign(paths: list[Path], split_label: str) -> list[dict[str, Any]]:
            out: list[dict[str, Any]] = []
            for i, npz_path in enumerate(paths):
                stem = npz_path.stem
                gid = f"pooled_rr_{split_label}_{stem}"
                out.append(
                    {
                        "path": npz_path.resolve(),
                        "temporal_group_id": gid,
                        "npz_group_key": stem,
                        "clip_key": stem,
                        "episode_key": f"pooled_{split_label}",
                        "instruction": pool[i % len(pool)],
                        "split_label": split_label,
                    }
                )
            return out

        train_assign = _paths_to_pooled_assign(train_paths, "training")
        val_assign = _paths_to_pooled_assign(val_paths, "validation")
        test_assign = _paths_to_pooled_assign(test_paths, "validation")
        npz_counts = {
            "train": len(train_paths),
            "val": len(val_paths),
            "test": len(test_paths),
        }
    elif alignment_mode == "grouped_sequence":
        train_assign = grouped_path_assignments(
            train_dir,
            pool=pool,
            window=window,
            stride=stride,
            max_paths=int(args.max_train_samples),
        )
        val_assign, test_assign = _split_val_test_by_groups(
            val_dir,
            pool,
            window=window,
            stride=stride,
            max_val_samples=int(args.max_val_samples),
            max_test_samples=int(args.max_test_samples),
        )
        npz_counts = {
            "train": len(train_assign),
            "val": len(val_assign),
            "test": len(test_assign),
        }
    elif alignment_mode == "same_task_subset":
        st = same_task_subset_splits(
            train_dir,
            val_dir,
            pool=pool,
            window=window,
            stride=stride,
            max_groups_train=int(getattr(args, "same_task_max_groups_train", 8)),
            max_groups_val=int(getattr(args, "same_task_max_groups_val", 4)),
            max_groups_test=int(getattr(args, "same_task_max_groups_test", 4)),
        )
        train_assign, val_assign, test_assign = st["train"], st["val"], st["test"]
        _stdir = getattr(args, "same_task_manifest_dir", None)
        subset_dir = (
            Path(_stdir)
            if _stdir
            else repo_root() / "data" / "processed" / "calvin_debug_same_task_subset"
        )
        write_same_task_manifests(subset_dir, st, alignment_mode="same_task_subset")
        npz_counts = {
            "train": len(train_assign),
            "val": len(val_assign),
            "test": len(test_assign),
        }
    else:
        raise ValueError(f"unknown alignment_mode: {alignment_mode}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_flat: dict[str, list[dict[str, Any]]] = {"train": [], "val": [], "test": []}
    traj_c: Counter[str] = Counter()
    lineage_c: Counter[str] = Counter()

    def roll_split(assignments: list[dict[str, Any]], split_name: str) -> None:
        nonlocal traj_c, lineage_c
        for assignment in assignments:
            npz_path = Path(assignment["path"])
            inst = str(assignment["instruction"])
            data = load_debug_npz(npz_path)
            ro = data["robot_obs"]
            so = data["scene_obs"]
            stem = npz_path.stem
            obs_bundle = build_initial_observation_from_debug_vectors(
                ro, so, inst, frame_id=stem.replace("episode_", ""), npz_stem=stem
            )
            try:
                trace = run_calvin_minimal_episode(
                    inst,
                    initial_observation=obs_bundle,
                    max_steps=int(args.rollout_max_steps),
                    experiment_id=str(args.experiment_id or "calvin_debug_real_build"),
                )
            except Exception:  # noqa: BLE001
                continue
            try:
                rel_npz = str(npz_path.resolve().relative_to(repo_root().resolve()))
            except ValueError:
                rel_npz = str(npz_path.resolve())
            extra = _alignment_extra_metadata(
                alignment_mode=alignment_mode,
                manifest_path=manifest_path,
                rel_npz=rel_npz,
                stem=stem,
                assignment=assignment,
            )
            episode_id = f"{assignment['temporal_group_id']}::{stem}"
            rows = list(
                iter_rows_from_v0_trace(
                    trace,
                    source_type="calvin_debug_real",
                    split=split_name,
                    episode_id=episode_id,
                    experiment_id=str(args.experiment_id or ""),
                    forced_grasp_failures_setting=0,
                    rollout_backend="calvin_debug_real_minimal_loop",
                    extra_metadata=extra,
                )
            )
            for r in rows:
                traj_c[str(r.get("trajectory_type") or "?")] += 1
                lineage_c["from_official_debug_vectors"] += 1
                if r.get("trajectory_type") == "recovery":
                    lineage_c["recovery_from_loop_replan"] += 1
            all_flat[split_name].extend(rows)

    roll_split(train_assign, "train")
    roll_split(val_assign, "val")
    roll_split(test_assign, "test")

    basename = str(
        getattr(
            args,
            "output_basename",
            (
                "calvin_debug_real_aligned"
                if alignment_mode == "grouped_sequence"
                else (
                    "calvin_debug_real_same_task"
                    if alignment_mode == "same_task_subset"
                    else "calvin_debug_real"
                )
            ),
        )
    )
    for split_name in ("train", "val", "test"):
        write_jsonl(out_dir / f"{basename}_{split_name}.jsonl", all_flat[split_name])

    stats_path = Path(args.stats_md) if getattr(args, "stats_md", None) else repo_root() / "docs" / "calvin_debug_real_data_stats.md"
    total_rows = sum(len(v) for v in all_flat.values())
    recovery_steps = sum(1 for split in all_flat.values() for r in split if r.get("trajectory_type") == "recovery")
    lines = [
        "# CALVIN debug real-data planner export stats (auto)",
        "",
        "_**Not** official CALVIN benchmark; vectors from official debug zip; language from YAML manifest pool only._",
        "",
        f"- alignment_mode: **`{alignment_mode}`**",
        f"- debug root: `{root_debug}`",
        f"- manifest (instruction pool): `{manifest_path}`",
        f"- pool size (distinct instructions): **{len(pool)}**",
        f"- output basename: `{basename}`",
        "",
        "## Row counts",
        "",
        "| split | rows | npz files used |",
        "|-------|-----:|---------------:|",
        f"| train | {len(all_flat['train'])} | {npz_counts['train']} |",
        f"| val | {len(all_flat['val'])} | {npz_counts['val']} |",
        f"| test | {len(all_flat['test'])} | {npz_counts['test']} |",
        f"| **total** | **{total_rows}** | — |",
        "",
        "## trajectory_type (step-level)",
        "",
        f"- counts: `{dict(traj_c)}`",
        f"- recovery-labeled steps: **{recovery_steps}** (from replan supervision in loop, not raw dataset field)",
        "",
        "## Lineage (honest)",
        "",
        f"- counts: `{dict(lineage_c)}`",
        "- **Pure language from npz**: **no** (debug zip lacks `lang_annotations`).",
        "- **Observation state**: **yes** — `robot_obs` + `scene_obs` from official debug frames.",
        "- **Execution**: symbolic skills on `CalvinEnvAdapter` initialised from vector-derived teacher — **not** physics replay of `actions` in npz.",
        "",
    ]
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    stats_path.write_text("\n".join(lines), encoding="utf-8")

    print(
        f"[build_planner_data calvin_debug_real] alignment={alignment_mode} wrote {total_rows} rows under {out_dir} "
        f"({basename}_*.jsonl); stats: {stats_path}"
    )


def run_real_subset_export(args: argparse.Namespace) -> None:
    manifest = _load_manifest(args.manifest)
    splits = _build_real_subset_splits(
        manifest,
        seed=args.seed,
        max_train_episodes=args.max_train_episodes,
        max_val_episodes=args.max_val_episodes,
        max_test_episodes=args.max_test_episodes,
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_flat: dict[str, list[dict[str, Any]]] = {"train": [], "val": [], "test": []}

    for split_name, mrows in splits.items():
        for i, mr in enumerate(mrows):
            inst = str(mr["instruction"])
            eid = str(mr["episode_id"])
            h = int(hashlib.md5(eid.encode(), usedforsecurity=False).hexdigest(), 16)
            recovery = (h % 10) < 3 if split_name == "train" else (h % 10) < 5
            forced = 1 if recovery else 0
            _, rows = run_export_episode(
                inst,
                episode_id=eid,
                split=split_name,
                forced_grasp_failures=forced,
                max_steps=args.max_steps,
                source_type="real_subset_mock_rollout",
            )
            for r in rows:
                r["split"] = split_name
                r.setdefault("metadata", {})["manifest_subtask_key"] = mr.get("subtask_key")
                r.setdefault("metadata", {})["calvin_yaml_source_url"] = mr.get("source_url")
            all_flat[split_name].extend(rows)

    for split_name in ("train", "val", "test"):
        write_jsonl(out_dir / f"{split_name}.jsonl", all_flat[split_name])

    preview_path = out_dir / "preview_samples.json"
    preview: list[dict[str, Any]] = []
    for split_name in ("train", "val", "test"):
        for r in all_flat[split_name][:2]:
            preview.append(
                {
                    "split": split_name,
                    "sample_id": r.get("sample_id"),
                    "trajectory_type": r.get("trajectory_type"),
                    "instruction": r.get("instruction"),
                    "user_prompt_head": (r.get("user_prompt") or "")[:400],
                    "target_text_head": (r.get("target_text") or "")[:400],
                }
            )
    preview_path.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")

    stats_path = Path(args.stats_md) if args.stats_md else repo_root() / "docs" / "planner_data_stats.md"
    _write_stats_md(stats_path, splits=splits, flat_rows=all_flat)

    total = sum(len(v) for v in all_flat.values())
    print(f"[build_planner_data real_subset] wrote train/val/test JSONL ({total} rows) under {out_dir}")
    print(f"[build_planner_data real_subset] stats: {stats_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build planner SFT JSONL: fixture | real_subset | calvin_debug_real (see docs/calvin_debug_dataset_audit.md)."
    )
    parser.add_argument(
        "--source",
        choices=["fixture", "real_subset", "calvin_debug_real"],
        default="fixture",
        help="fixture | real_subset | calvin_debug_real (official debug npz vectors + minimal loop, see docs).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSONL path when --source fixture (required for fixture).",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json",
    )
    parser.add_argument("--instruction", type=str, default="Put the red block in the drawer.")
    parser.add_argument("--max-steps", type=int, default=12, help="Max steps for --source fixture rollouts.")
    parser.add_argument(
        "--rollout-max-steps",
        type=int,
        default=16,
        help="Max steps per episode when --source real_subset.",
    )
    parser.add_argument(
        "--experiment-id",
        type=str,
        default="",
        help="Optional id for fixture export or calvin_debug_real trace metadata.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repo_root() / "data" / "processed" / "calvin_real_subset" / "manifest.jsonl",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root() / "data" / "processed" / "planner_sft",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-train-episodes", type=int, default=220)
    parser.add_argument("--max-val-episodes", type=int, default=45)
    parser.add_argument("--max-test-episodes", type=int, default=45)
    parser.add_argument("--stats-md", type=Path, default=None)
    parser.add_argument(
        "--calvin-debug-root",
        type=Path,
        default=None,
        help="Root of official calvin_debug_dataset (default: data/raw/calvin_official/dataset/calvin_debug_dataset).",
    )
    parser.add_argument("--max-train-samples", type=int, default=48)
    parser.add_argument("--max-val-samples", type=int, default=16)
    parser.add_argument("--max-test-samples", type=int, default=16)
    parser.add_argument(
        "--alignment-mode",
        type=str,
        choices=["pooled_manifest", "grouped_sequence", "same_task_subset"],
        default="grouped_sequence",
        help="Instruction/observation assignment for --source calvin_debug_real (see docs/calvin_debug_alignment_audit.md).",
    )
    parser.add_argument("--alignment-window", type=int, default=40)
    parser.add_argument("--alignment-stride", type=int, default=20)
    parser.add_argument(
        "--output-basename",
        type=str,
        default="",
        help="JSONL filename prefix (default: by alignment_mode, e.g. calvin_debug_real_aligned).",
    )
    parser.add_argument("--same-task-manifest-dir", type=Path, default=None)
    parser.add_argument("--same-task-max-groups-train", type=int, default=8)
    parser.add_argument("--same-task-max-groups-val", type=int, default=4)
    parser.add_argument("--same-task-max-groups-test", type=int, default=4)
    args = parser.parse_args()

    if args.source == "fixture":
        if args.out is None:
            parser.error("--out is required when --source fixture")
        run_fixture_export(args)
    elif args.source == "real_subset":
        rs = argparse.Namespace(
            manifest=args.manifest,
            out_dir=args.out_dir,
            seed=args.seed,
            max_train_episodes=args.max_train_episodes,
            max_val_episodes=args.max_val_episodes,
            max_test_episodes=args.max_test_episodes,
            max_steps=args.rollout_max_steps,
            stats_md=args.stats_md,
        )
        run_real_subset_export(rs)
    else:
        out_dir = (
            Path(args.out_dir)
            if getattr(args, "out_dir", None)
            else repo_root() / "data" / "processed" / "planner_sft"
        )
        ob = (args.output_basename or "").strip()
        if not ob:
            if args.alignment_mode == "grouped_sequence":
                ob = "calvin_debug_real_aligned"
            elif args.alignment_mode == "same_task_subset":
                ob = "calvin_debug_real_same_task"
            else:
                ob = "calvin_debug_real"
        stats_out = (
            Path(args.stats_md)
            if args.stats_md
            else repo_root() / "docs" / "calvin_debug_real_data_stats.md"
        )
        cdr = argparse.Namespace(
            manifest=args.manifest,
            out_dir=out_dir,
            seed=args.seed,
            rollout_max_steps=args.rollout_max_steps,
            calvin_debug_root=args.calvin_debug_root,
            max_train_samples=args.max_train_samples,
            max_val_samples=args.max_val_samples,
            max_test_samples=args.max_test_samples,
            stats_md=stats_out,
            experiment_id=getattr(args, "experiment_id", "") or "",
            alignment_mode=args.alignment_mode,
            alignment_window=args.alignment_window,
            alignment_stride=args.alignment_stride,
            output_basename=ob,
            same_task_manifest_dir=args.same_task_manifest_dir,
            same_task_max_groups_train=args.same_task_max_groups_train,
            same_task_max_groups_val=args.same_task_max_groups_val,
            same_task_max_groups_test=args.same_task_max_groups_test,
        )
        run_calvin_debug_real_export(cdr)


if __name__ == "__main__":
    main()
