"""E2 ablation: no_verifier vs verifier_only vs verifier_plus_replan (mock, CALVIN fixture, or CALVIN debug npz)."""

from __future__ import annotations

import argparse
import copy
import json
import random
from collections import Counter
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

CalvinDebugBatch = Literal["pooled_manifest", "grouped_sequence", "same_task_subset"]

from embodied_scene_agent.data.calvin_debug_alignment import (
    grouped_path_assignments,
    load_manifest_rows,
    scenarios_from_manifest_rows,
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
from embodied_scene_agent.pipeline.v0_loop import EpisodeTrace, VerifierMode, run_v0_episode
from embodied_scene_agent.utils.paths import repo_root

Backend = Literal["mock", "calvin_fixture", "calvin_debug_real"]

# Deterministic fallback when no strict verifier contrast exists (episode_index aligned across modes).
MOCK_E2_SCENARIO_WHITELIST: tuple[int, ...] = (1, 4, 7, 10, 13, 0)
CALVIN_E2_SCENARIO_WHITELIST: tuple[int, ...] = (1, 4, 7, 0)
CALVIN_DEBUG_E2_SCENARIO_WHITELIST: tuple[int, ...] = (0, 1, 2, 3)


def _scenario_from_npz_row(i: int, npz_path: Path, inst: str, *, batch: str) -> dict[str, Any]:
    data = load_debug_npz(npz_path)
    stem = npz_path.stem
    obs = build_initial_observation_from_debug_vectors(
        data["robot_obs"],
        data["scene_obs"],
        inst,
        frame_id=stem.replace("episode_", ""),
        npz_stem=stem,
    )
    return {
        "episode_index": i,
        "instruction": inst,
        "forced_grasp_failures": 0,
        "calvin_variant": f"debug_npz:{stem}",
        "initial_observation": obs,
        "npz_path": str(npz_path.resolve()),
        "calvin_debug_batch": batch,
    }


def calvin_debug_real_scenario_list(
    *,
    n_episodes: int = 16,
    seed: int = 42,
    debug_root: Path | None = None,
    manifest_path: Path | None = None,
    batch: CalvinDebugBatch = "grouped_sequence",
    same_task_manifest: Path | None = None,
    alignment_window: int = 40,
    alignment_stride: int = 20,
) -> list[dict[str, Any]]:
    """
    Episodes from official debug ``*.npz`` + vector-derived teacher (same minimal loop as fixture path).

    **Not** leaderboard / full D split — debug subset + symbolic execution only.
    ``same_task_subset`` uses grouped manifests (same-task-like, not official task IDs).
    """
    dbg = (debug_root or default_calvin_debug_root()).resolve()
    mpath = manifest_path or (
        repo_root() / "data" / "processed" / "calvin_real_subset" / "manifest.jsonl"
    )
    pool = instruction_pool_from_manifest(Path(mpath))
    if not pool:
        pool = ["Put the red block in the drawer."]
    scenarios: list[dict[str, Any]] = []

    if batch == "pooled_manifest":
        train = list(iter_npz_frames(dbg / "training"))
        val = list(iter_npz_frames(dbg / "validation"))
        all_paths = train + val
        rng = random.Random(seed)
        rng.shuffle(all_paths)
        chosen = all_paths[: max(1, n_episodes)]
        for i, p in enumerate(chosen):
            inst = pool[i % len(pool)]
            scenarios.append(_scenario_from_npz_row(i, p, inst, batch=batch))
        return scenarios

    if batch == "same_task_subset":
        man = same_task_manifest or (
            repo_root() / "data" / "processed" / "calvin_debug_same_task_subset" / "train_manifest.jsonl"
        )
        mrows = load_manifest_rows(Path(man))
        picked = scenarios_from_manifest_rows(mrows, n_episodes=n_episodes)
        for i, r in enumerate(picked):
            p = Path(str(r.get("source_npz") or ""))
            inst = str(r.get("instruction") or pool[0])
            scenarios.append(_scenario_from_npz_row(i, p, inst, batch=batch))
        return scenarios

    # grouped_sequence (default aligned)
    rows: list[dict[str, Any]] = []
    for sd in (dbg / "training", dbg / "validation"):
        rows.extend(
            grouped_path_assignments(
                sd,
                pool=pool,
                window=alignment_window,
                stride=alignment_stride,
                max_paths=None,
            )
        )
    synthetic = [
        {
            "temporal_group_id": r["temporal_group_id"],
            "instruction": r["instruction"],
            "source_npz": str(r["path"]),
        }
        for r in rows
    ]
    picked = scenarios_from_manifest_rows(synthetic, n_episodes=n_episodes)
    for i, r in enumerate(picked):
        p = Path(str(r.get("source_npz") or ""))
        inst = str(r.get("instruction") or pool[0])
        scenarios.append(_scenario_from_npz_row(i, p, inst, batch=batch))
    return scenarios


def scenario_grid() -> Iterator[dict]:
    """Fixed symbolic grid (not CALVIN benchmark)."""
    instructions = [
        "put the red block in the drawer",
        "put the red block in the drawer",
        "store the block in the drawer",
    ]
    # Slightly stress verifier_only: more mid-episode grasp friction + repeated layouts.
    failures = [0, 1, 2, 2, 1, 0, 2, 1, 0, 1, 2, 0, 1, 2, 2, 1]
    for i, f in enumerate(failures):
        yield {
            "episode_index": i,
            "instruction": instructions[i % len(instructions)],
            "forced_grasp_failures": f,
        }


def calvin_fixture_scenario_grid() -> Iterator[dict]:
    """
    CALVIN-shaped **fixture** batch (same file family as ``calvin_mock_observation.json``).

    **Not** official CALVIN benchmark — dev fixture + minimal loop only.
    """
    base_path = repo_root() / "tests" / "fixtures" / "calvin_mock_observation.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    instructions = [
        "put the red block in the drawer",
        "put the red block in the drawer",
        "store the block in the drawer",
    ]
    failures = [0, 1, 2, 2, 1, 0, 2, 1, 0, 1, 2, 0, 1, 2, 2, 1]
    tags = ["default_init", "drawer_open_init", "block_held_init"]
    for i, f in enumerate(failures):
        obs = copy.deepcopy(base)
        teacher = obs["calvin_teacher_v0"]
        tag = tags[f % 3]
        if f % 3 == 1:
            for o in teacher["scene_objects"]:
                if o.get("uid") == "drawer":
                    o["drawer_open"] = True
        elif f % 3 == 2:
            teacher["robot"]["held_object_uid"] = "red_block"
            for o in teacher["scene_objects"]:
                if o.get("uid") == "red_block":
                    o["held"] = True
        yield {
            "episode_index": i,
            "instruction": instructions[i % len(instructions)],
            "forced_grasp_failures": f,
            "calvin_variant": tag,
            "initial_observation": obs,
        }


def summarize_episodes(
    mode: VerifierMode,
    traces: list[EpisodeTrace],
    *,
    setting_note: str,
) -> dict:
    n = len(traces)
    task_ok = sum(1 for t in traces if t.success)
    failure_detected_steps = 0
    total_steps = 0
    state_unchanged_failures = 0
    replan_triggers = 0
    recovery_ok = 0
    recovery_eligible = 0
    ft_dist: Counter[str] = Counter()

    for t in traces:
        had_failed_verify = False
        for st in t.steps:
            total_steps += 1
            v = st.get("verification") or {}
            if v.get("success") is False:
                failure_detected_steps += 1
                had_failed_verify = True
                ft = str(v.get("failure_type") or "unknown")
                ft_dist[ft] += 1
                if "state_unchanged" in ft or "action_no_effect" in ft:
                    state_unchanged_failures += 1
            if st.get("replan") is not None:
                replan_triggers += 1
            v2 = st.get("verification_replan") or {}
            if v2.get("success") is False:
                ft2 = str(v2.get("failure_type") or "unknown_replan")
                ft_dist[f"replan::{ft2}"] += 1
        if had_failed_verify:
            recovery_eligible += 1
        if t.success and t.replan_count > 0:
            recovery_ok += 1

    return {
        "verifier_mode": mode,
        "n_episodes": n,
        "task_completion_rate": task_ok / max(1, n),
        "failure_detected_rate": failure_detected_steps / max(1, total_steps)
        if mode != "none"
        else 0.0,
        "failure_detected_steps": failure_detected_steps,
        "total_steps": total_steps,
        "state_unchanged_rate": state_unchanged_failures / max(1, failure_detected_steps)
        if failure_detected_steps
        else 0.0,
        "replan_trigger_rate": replan_triggers / max(1, n),
        "recovery_success_rate": recovery_ok / max(1, n),
        "recovery_eligible_episodes": recovery_eligible,
        "recovery_success_after_replan_episodes": recovery_ok,
        "average_steps": total_steps / max(1, n),
        "failure_taxonomy_counts": dict(ft_dist),
        "notes": {
            "setting": setting_note,
            "verifier_none": "failure_detected_rate forced 0 (verifier always passes).",
            "verifier_only": "no replan branch; recovery_success_rate expected ~0 unless accidental task success.",
        },
    }


def run_all_modes(
    *,
    experiment_id: str,
    replanner_mode: str = "rule",
    backend: Backend = "mock",
    calvin_debug_batch: CalvinDebugBatch | None = None,
) -> dict:
    modes: list[VerifierMode] = ["none", "verifier_only", "verifier_plus_replan"]
    if backend == "mock":
        scenarios = list(scenario_grid())
        setting_note = "MockEmbodiedEnv symbolic — not official CALVIN benchmark."
    elif backend == "calvin_fixture":
        scenarios = list(calvin_fixture_scenario_grid())
        setting_note = (
            "CALVIN **fixture** minimal loop (``run_calvin_minimal_episode``) — not official CALVIN benchmark."
        )
    else:
        cdb: CalvinDebugBatch = calvin_debug_batch or "grouped_sequence"
        scenarios = calvin_debug_real_scenario_list(n_episodes=16, seed=42, batch=cdb)
        setting_note = (
            "CALVIN **official debug** ``*.npz`` vectors → vector teacher → minimal loop (symbolic skills) — "
            f"batch=`{cdb}` (same-task-like when applicable) — not official CALVIN benchmark."
        )

    out: dict[str, Any] = {
        "experiment_id": experiment_id,
        "backend": backend,
        "modes": {},
        "per_episode_by_mode": {},
    }
    if backend == "calvin_debug_real":
        out["calvin_debug_batch"] = calvin_debug_batch or "grouped_sequence"
    for mode in modes:
        traces: list[EpisodeTrace] = []
        rows: list[dict] = []
        for s in scenarios:
            if backend == "mock":
                tr = run_v0_episode(
                    s["instruction"],
                    max_steps=12,
                    forced_grasp_failures=s["forced_grasp_failures"],
                    verifier_mode=mode,
                    replanner_mode=replanner_mode,  # type: ignore[arg-type]
                    experiment_id=experiment_id,
                )
            else:
                tr = run_calvin_minimal_episode(
                    s["instruction"],
                    max_steps=12,
                    initial_observation=s["initial_observation"],
                    verifier_mode=mode,
                    replanner_mode=replanner_mode,  # type: ignore[arg-type]
                    experiment_id=experiment_id,
                )
            traces.append(tr)
            rows.append(
                {
                    "episode_index": s["episode_index"],
                    "instruction": s["instruction"],
                    "forced_grasp_failures": s["forced_grasp_failures"],
                    "calvin_variant": s.get("calvin_variant"),
                    "npz_path": s.get("npz_path"),
                    "success": tr.success,
                    "replan_count": tr.replan_count,
                    "num_steps": len(tr.steps),
                    "final_message": tr.final_message,
                    "env_mode": tr.env_mode,
                    "teacher_source": tr.teacher_source,
                }
            )
        out["modes"][mode] = summarize_episodes(mode, traces, setting_note=setting_note)
        out["per_episode_by_mode"][mode] = rows
    return out


def find_latest_e2_dir(
    root: Path,
    backend: Backend,
    *,
    calvin_debug_batch: str | None = None,
) -> Path | None:
    base = root / "results" / "experiments" / "e2_ablation"
    if not base.is_dir():
        return None
    candidates: list[tuple[float, Path]] = []
    for d in base.iterdir():
        if not d.is_dir():
            continue
        mpath = d / "metrics.json"
        if not mpath.is_file():
            continue
        try:
            data = json.loads(mpath.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        b = data.get("backend")
        name_l = d.name.lower()
        matches = b == backend or (
            backend == "mock"
            and b is None
            and "calvin" not in name_l
            and "e2_calvin" not in name_l
        )
        if matches and backend == "calvin_debug_real" and calvin_debug_batch:
            if (data.get("calvin_debug_batch") or "") != calvin_debug_batch:
                continue
        if matches:
            candidates.append((mpath.stat().st_mtime, d))
    if not candidates:
        return None
    return max(candidates, key=lambda x: x[0])[1]


def select_stable_mock_case_rows(
    per_by_mode: dict[str, list[dict]],
) -> tuple[dict, dict, dict, dict[str, Any]]:
    """
    Stable, reproducible mock case selection for reporting.

    1) Prefer same ``episode_index`` where verifier_only fails but verifier_plus_replan succeeds with replans.
    2) Else prefer verifier_only failure with rich trace (more steps / forced failures).
    3) Else first matching index from ``MOCK_E2_SCENARIO_WHITELIST``.
    """
    none_row = per_by_mode["none"][0]
    by_vo = {r["episode_index"]: r for r in per_by_mode["verifier_only"]}
    by_vpr = {r["episode_index"]: r for r in per_by_mode["verifier_plus_replan"]}
    meta: dict[str, Any] = {"selection_version": "e2_mock_v1"}

    for idx in sorted(by_vpr.keys()):
        vo = by_vo.get(idx)
        vpr = by_vpr.get(idx)
        if (
            vo
            and vpr
            and vo.get("success") is False
            and vpr.get("success") is True
            and int(vpr.get("replan_count") or 0) > 0
        ):
            meta["strategy"] = "verifier_only_fail_and_verifier_plus_success"
            meta["episode_index"] = idx
            return none_row, vo, vpr, meta

    best_idx: int | None = None
    best_score = -1.0
    for vo in sorted(per_by_mode["verifier_only"], key=lambda r: r["episode_index"]):
        if vo.get("success") is not False:
            continue
        score = float(vo.get("num_steps") or 0)
        score += 3.0 * float(min(3, int(vo.get("forced_grasp_failures") or 0)))
        if score > best_score:
            best_score = score
            best_idx = int(vo["episode_index"])
    if best_idx is not None:
        meta["strategy"] = "verifier_only_failure_richest_trace"
        meta["episode_index"] = best_idx
        return none_row, by_vo[best_idx], by_vpr[best_idx], meta

    for idx in MOCK_E2_SCENARIO_WHITELIST:
        if idx in by_vo and idx in by_vpr and by_vo[idx].get("success") is False:
            meta["strategy"] = "scenario_id_whitelist"
            meta["episode_index"] = idx
            return none_row, by_vo[idx], by_vpr[idx], meta
    for idx in MOCK_E2_SCENARIO_WHITELIST:
        if idx in by_vo and idx in by_vpr:
            meta["strategy"] = "scenario_id_whitelist_relaxed"
            meta["episode_index"] = idx
            return none_row, by_vo[idx], by_vpr[idx], meta

    vpr_row = per_by_mode["verifier_plus_replan"][0]
    idx = int(vpr_row["episode_index"])
    meta["strategy"] = "fallback_first_episode"
    meta["episode_index"] = idx
    return none_row, by_vo[idx], by_vpr[idx], meta


def write_mock_vs_calvin_table(root: Path, mock_dir: Path | None, calvin_dir: Path | None) -> None:
    out = root / "docs" / "tables" / "e2_ablation_mock_vs_calvin_fixture.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E2 ablation: mock symbolic vs CALVIN fixture batch",
        "",
        "_**Fixture / dev batch only** — not official CALVIN ablation or leaderboard._",
        "",
        "| mode | metric | mock | calvin_fixture | same? |",
        "|------|--------|------|----------------|-------|",
    ]
    if mock_dir is None or calvin_dir is None:
        lines.extend(
            [
                "| — | — | *missing run* | *missing run* | — |",
                "",
                "Run:",
                "",
                "- `bash scripts/run_ablation_e2.sh` (mock)",
                "- `bash scripts/run_ablation_e2_calvin_fixture.sh` (CALVIN fixture)",
                "",
            ]
        )
        out.write_text("\n".join(lines), encoding="utf-8")
        return

    mock_m = json.loads((mock_dir / "metrics.json").read_text(encoding="utf-8"))
    cal_m = json.loads((calvin_dir / "metrics.json").read_text(encoding="utf-8"))
    keys = [
        ("task_completion_rate", "task_completion_rate"),
        ("failure_detected_rate", "failure_detected_rate"),
        ("replan_trigger_rate", "replan_trigger_rate"),
        ("recovery_success_rate", "recovery_success_rate"),
        ("average_steps", "average_steps"),
    ]
    for mode in ("none", "verifier_only", "verifier_plus_replan"):
        mm = (mock_m.get("modes") or {}).get(mode) or {}
        cm = (cal_m.get("modes") or {}).get(mode) or {}
        for label, k in keys:
            a, b = mm.get(k), cm.get(k)
            same = (
                a is not None
                and b is not None
                and isinstance(a, (int, float))
                and isinstance(b, (int, float))
                and abs(float(a) - float(b)) < 1e-6
            )
            lines.append(
                f"| `{mode}` | {label} | {a!s} | {b!s} | {'yes' if same else 'no'} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation (honest)",
            "",
            "- **Consistent** rows suggest verifier/replan wiring behaves similarly across mock vs CALVIN teacher-state fixture.",
            "- **Divergent** `task_completion_rate` / `average_steps` usually reflect **different symbolic physics** (mock discrete vs "
            "CALVIN teacher mutation) and **scene layout**, not benchmark ranking.",
            "- **failure_detected_rate** may shift when CALVIN steps emit different verifier failure mixes (`state_unchanged` vs others).",
            "",
            "### Mock vs CALVIN fixture（可直接进最终报告）",
            "",
            "- **Mock symbolic** 更“干净”：状态转移集中在单进程符号环境里，verifier 触发的失败类型更容易按设计复现，适合隔离「仅验证器 / +replan」机制差异。",
            "- **CALVIN fixture** 更接近 **adapter reality**：观测与 teacher 字段来自与 CALVIN 同形的 JSON fixture + 最小闭环，能暴露解析与状态同步上的边角，但仍是 **fixture/smoke**，不是官方 CALVIN 排行榜。",
            "- **仅在符号层成立的结论**：例如 mock 上精确的步数对比、某些 `failure_taxonomy` 计数比例；换到 fixture 后应视为「趋势一致 /  wiring 一致」而非数值 1:1 推广。",
            "",
            f"- Mock artifact: `{mock_dir}`",
            f"- CALVIN fixture artifact: `{calvin_dir}`",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")


def write_e2_three_backend_table(root: Path) -> None:
    """mock vs CALVIN fixture vs CALVIN debug real-data (latest metrics.json each)."""
    out = root / "docs" / "tables" / "e2_ablation_mock_vs_calvin_fixture_vs_calvin_debug_real.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    mock_d = find_latest_e2_dir(root, "mock")
    cal_d = find_latest_e2_dir(root, "calvin_fixture")
    dbg_d = find_latest_e2_dir(root, "calvin_debug_real", calvin_debug_batch="grouped_sequence")
    lines = [
        "# E2 ablation: mock vs CALVIN fixture vs CALVIN debug real-data",
        "",
        "_**Not** official CALVIN leaderboard — three **dev** evidence layers._",
        "",
        "| mode | metric | mock | calvin_fixture | calvin_debug_real |",
        "|------|--------|------|----------------|-------------------|",
    ]
    keys = [
        ("task_completion_rate", "task_completion_rate"),
        ("failure_detected_rate", "failure_detected_rate"),
        ("replan_trigger_rate", "replan_trigger_rate"),
        ("recovery_success_rate", "recovery_success_rate"),
        ("average_steps", "average_steps"),
    ]
    if mock_d is None or cal_d is None or dbg_d is None:
        lines.append("| — | — | *missing* | *missing* | *missing* |")
        lines.extend(
            [
                "",
                "Run:",
                "",
                "- `bash scripts/run_ablation_e2.sh`",
                "- `bash scripts/run_ablation_e2_calvin_fixture.sh`",
                "- `bash scripts/run_ablation_e2_calvin_debug_real.sh`",
                "",
            ]
        )
        lines.extend(_e2_three_backend_interpretation(root, mock_d, cal_d, dbg_d))
        out.write_text("\n".join(lines), encoding="utf-8")
        return

    mock_m = json.loads((mock_d / "metrics.json").read_text(encoding="utf-8"))
    cal_m = json.loads((cal_d / "metrics.json").read_text(encoding="utf-8"))
    dbg_m = json.loads((dbg_d / "metrics.json").read_text(encoding="utf-8"))
    for mode in ("none", "verifier_only", "verifier_plus_replan"):
        mm = (mock_m.get("modes") or {}).get(mode) or {}
        cm = (cal_m.get("modes") or {}).get(mode) or {}
        dm = (dbg_m.get("modes") or {}).get(mode) or {}
        for label, k in keys:
            lines.append(
                f"| `{mode}` | {label} | {mm.get(k)!s} | {cm.get(k)!s} | {dm.get(k)!s} |"
            )

    lines.extend(_e2_three_backend_interpretation(root, mock_d, cal_d, dbg_d))
    out.write_text("\n".join(lines), encoding="utf-8")


def _e2_artifact_rel(root: Path, d: Path | None) -> str:
    if d is None:
        return "n/a"
    try:
        return str(d.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(d)


def _e2_three_backend_interpretation(
    root: Path, mock_d: Path | None, cal_d: Path | None, dbg_d: Path | None
) -> list[str]:
    return [
        "",
        "## 三层证据各自意味着什么",
        "",
        "- **mock**：符号环境，最适合隔离 verifier / replan 机制，数值最“干净”。",
        "- **CALVIN fixture**：JSON fixture + 与 CALVIN 同形的 teacher，测 adapter / 解析应力，**仍非**官方轨迹。",
        "- **CALVIN debug real-data**：官方 **debug** 包中的 **robot_obs/scene_obs** 向量重构 teacher，再跑同一套最小认知闭环；"
        "**不是** D/ABC/ABCD 全量，也**不是** leaderboard。",
        "",
        "## 不能解读为",
        "",
        "- 官方 CALVIN benchmark 排名、成功率可比全论文设置、或与仿真逐步物理回放等价。",
        "",
        "### Artifact paths（相对仓库根）",
        "",
        f"- mock: `{_e2_artifact_rel(root, mock_d)}`",
        f"- calvin_fixture: `{_e2_artifact_rel(root, cal_d)}`",
        f"- calvin_debug_real: `{_e2_artifact_rel(root, dbg_d)}`",
        "",
    ]


def pick_calvin_debug_real_cases(root: Path, payload: dict) -> None:
    """One verifier_only + one verifier_plus_replan trace JSON under unified demo dir."""
    demo = root / "results" / "demos" / "e2_ablation_cases"
    demo.mkdir(parents=True, exist_ok=True)
    batch = payload.get("calvin_debug_batch") or "grouped_sequence"
    if batch == "same_task_subset":
        file_stem = "calvin_debug_same_task"
        sel_version = "e2_calvin_debug_same_task_v1"
        source_tag = "calvin_debug_same_task"
    elif batch == "grouped_sequence":
        file_stem = "calvin_debug_real_aligned"
        sel_version = "e2_calvin_debug_real_aligned_v1"
        source_tag = "calvin_debug_real_aligned"
    else:
        file_stem = "calvin_debug_real"
        sel_version = "e2_calvin_debug_real_v1"
        source_tag = "calvin_debug_real_pooled"
    scenarios = {
        s["episode_index"]: s
        for s in calvin_debug_real_scenario_list(n_episodes=16, seed=42, batch=batch)
    }

    vo_idx = None
    for idx in CALVIN_DEBUG_E2_SCENARIO_WHITELIST:
        if idx not in scenarios:
            continue
        vo_idx = idx
        break
    if vo_idx is None:
        vo_idx = 0
    vpr_idx = vo_idx
    s_vo = scenarios[vo_idx]
    s_vpr = scenarios[vpr_idx]

    tr_vo = run_calvin_minimal_episode(
        s_vo["instruction"],
        max_steps=12,
        initial_observation=s_vo["initial_observation"],
        verifier_mode="verifier_only",
        replanner_mode="rule",
        experiment_id=payload["experiment_id"],
    )
    tr_vpr = run_calvin_minimal_episode(
        s_vpr["instruction"],
        max_steps=12,
        initial_observation=s_vpr["initial_observation"],
        verifier_mode="verifier_plus_replan",
        replanner_mode="rule",
        experiment_id=payload["experiment_id"],
    )

    meta = {
        "selection_version": sel_version,
        "calvin_debug_batch": batch,
        "reporting_source_tag": source_tag,
        "episode_index": vo_idx,
        "npz_path": s_vo.get("npz_path"),
        "honest_scope": "Official debug npz vectors + symbolic minimal loop — not benchmark.",
    }
    (demo / f"{file_stem}_selection_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    trace_common = {
        "backend": "calvin_debug_real",
        "calvin_debug_batch": batch,
        "reporting_source_tag": source_tag,
    }
    (demo / f"{file_stem}_case_verifier_only.json").write_text(
        json.dumps(
            {
                **trace_common,
                "verifier_mode": "verifier_only",
                "episode_meta": {k: s_vo[k] for k in s_vo if k != "initial_observation"},
                "trace": {"success": tr_vo.success, "replan_count": tr_vo.replan_count, "steps": tr_vo.steps},
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (demo / f"{file_stem}_case_verifier_plus_replan.json").write_text(
        json.dumps(
            {
                **trace_common,
                "verifier_mode": "verifier_plus_replan",
                "episode_meta": {k: s_vpr[k] for k in s_vpr if k != "initial_observation"},
                "trace": {"success": tr_vpr.success, "replan_count": tr_vpr.replan_count, "steps": tr_vpr.steps},
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    section_heading = {
        "pooled_manifest": "## CALVIN debug — pooled_manifest batch",
        "grouped_sequence": "## CALVIN debug — grouped_sequence (aligned)",
        "same_task_subset": "## CALVIN debug — same_task_subset",
    }[batch]
    block = "\n".join(
        [
            section_heading,
            "",
            f"_选例：`results/demos/e2_ablation_cases/{file_stem}_selection_meta.json`；来源标签 **`{source_tag}`**._",
            "",
            "### verifier_only（debug 向量 teacher）",
            f"- episode_index `{vo_idx}`；[`{file_stem}_case_verifier_only.json`]"
            f"(../../results/demos/e2_ablation_cases/{file_stem}_case_verifier_only.json)",
            "",
            "### verifier_plus_replan（同一设定族）",
            f"- episode_index `{vpr_idx}`；[`{file_stem}_case_verifier_plus_replan.json`]"
            f"(../../results/demos/e2_ablation_cases/{file_stem}_case_verifier_plus_replan.json)",
            "",
        ]
    )
    path = root / "docs" / "failure_cases" / "e2_ablation_cases.md"
    calvin_markers = (
        "## CALVIN debug — pooled_manifest batch",
        "## CALVIN debug — grouped_sequence (aligned)",
        "## CALVIN debug — same_task_subset",
    )
    parent = (
        "## CALVIN debug real-data backed (not benchmark)\n\n"
        "_官方 debug npz 向量 teacher + 最小闭环；**非** leaderboard。"
        " 下列分节对应不同 `CALVIN_DEBUG_BATCH` / `--calvin-debug-batch`，互不覆盖。_\n"
    )

    def _splice_calvin_section(text: str, heading: str, body: str) -> str:
        if heading not in text:
            return text.rstrip() + "\n\n" + body
        i = text.index(heading)
        after = text[i + len(heading) :]
        cut = len(after)
        for m in calvin_markers:
            if m == heading:
                continue
            pos = after.find(m)
            if pos != -1:
                cut = min(cut, pos)
        tail = after[cut:]
        return text[:i] + body + tail

    path.parent.mkdir(parents=True, exist_ok=True)
    t = path.read_text(encoding="utf-8") if path.is_file() else "# E2 ablation — curated cases\n"
    if "## CALVIN debug real-data backed (not benchmark)" not in t:
        t = t.rstrip() + "\n\n" + parent
    t = _splice_calvin_section(t, section_heading, block)
    path.write_text(t, encoding="utf-8")


def pick_cases(root: Path, out_dir: Path, payload: dict) -> None:
    """Write curated markdown + demo snippets (mock)."""
    demo = root / "results" / "demos" / "e2_ablation_cases"
    demo.mkdir(parents=True, exist_ok=True)
    per_by_mode = payload["per_episode_by_mode"]
    cases_path = root / "docs" / "failure_cases" / "e2_ablation_cases.md"
    calvin_tail = ""
    marker = "## CALVIN fixture batch"
    if cases_path.is_file():
        prev = cases_path.read_text(encoding="utf-8")
        if marker in prev:
            calvin_tail = "\n\n" + prev[prev.index(marker) :]

    none_row, vo_row, vpr_row, sel_meta = select_stable_mock_case_rows(per_by_mode)
    (demo / "mock_selection_meta.json").write_text(
        json.dumps(sel_meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    cases_md = [
        "# E2 ablation — curated cases",
        "",
        "## Mock symbolic",
        "",
        f"_稳定选例策略：`{sel_meta.get('strategy')}`，episode_index=`{sel_meta.get('episode_index')}`（见 `results/demos/e2_ablation_cases/mock_selection_meta.json`）。_",
        "",
        "### 1) Verifier missing → missed failure handling",
        f"- mode `none`, episode_index `{none_row.get('episode_index')}`: verifier disabled so failures not surfaced in verification channel.",
        f"- Demo: [`results/demos/e2_ablation_cases/case1_none.json`](../../results/demos/e2_ablation_cases/case1_none.json)",
        "",
        "### 2) Verifier without replan",
        f"- mode `verifier_only`, episode `{vo_row.get('episode_index')}`: success={vo_row.get('success')}, replan_count=0.",
        f"- Demo: [`results/demos/e2_ablation_cases/case2_verifier_only.json`](../../results/demos/e2_ablation_cases/case2_verifier_only.json)",
        "",
        "### 3) Verifier + replan recovery",
        f"- mode `verifier_plus_replan`, episode `{vpr_row.get('episode_index')}`: success={vpr_row.get('success')}, replans={vpr_row.get('replan_count')}.",
        f"- Demo: [`results/demos/e2_ablation_cases/case3_plus_replan.json`](../../results/demos/e2_ablation_cases/case3_plus_replan.json)",
        "",
    ]
    cases_path.parent.mkdir(parents=True, exist_ok=True)
    cases_path.write_text("\n".join(cases_md) + calvin_tail, encoding="utf-8")

    for label, row, mode in (
        ("case1_none", none_row, "none"),
        ("case2_verifier_only", vo_row, "verifier_only"),
        ("case3_plus_replan", vpr_row, "verifier_plus_replan"),
    ):
        tr = run_v0_episode(
            row["instruction"],
            max_steps=12,
            forced_grasp_failures=row["forced_grasp_failures"],
            verifier_mode=mode,  # type: ignore[arg-type]
            experiment_id=payload["experiment_id"],
        )
        (demo / f"{label}.json").write_text(
            json.dumps(
                {
                    "backend": "mock",
                    "mode": mode,
                    "episode_meta": row,
                    "trace": {
                        "success": tr.success,
                        "replan_count": tr.replan_count,
                        "steps": tr.steps,
                    },
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def pick_calvin_cases(root: Path, payload: dict) -> None:
    """Write CALVIN fixture examples; merge markdown with mock section if present."""
    demo = root / "results" / "demos" / "e2_ablation_calvin_cases"
    demo.mkdir(parents=True, exist_ok=True)
    unified = root / "results" / "demos" / "e2_ablation_cases"
    unified.mkdir(parents=True, exist_ok=True)
    per = payload["per_episode_by_mode"]
    scenarios = list(calvin_fixture_scenario_grid())
    by_idx = {s["episode_index"]: s for s in scenarios}

    candidate_idx: int | None = None
    for r in sorted(per["verifier_only"], key=lambda x: x["episode_index"]):
        idx = r["episode_index"]
        vo = r
        vpr = next(x for x in per["verifier_plus_replan"] if x["episode_index"] == idx)
        if not vo["success"] and vpr["success"] and vpr.get("replan_count", 0) > 0:
            candidate_idx = idx
            break
    if candidate_idx is None:
        for idx in CALVIN_E2_SCENARIO_WHITELIST:
            if idx not in by_idx:
                continue
            vo = next(x for x in per["verifier_only"] if x["episode_index"] == idx)
            vpr = next(x for x in per["verifier_plus_replan"] if x["episode_index"] == idx)
            if not vo["success"] and vpr["success"]:
                candidate_idx = idx
                break
    if candidate_idx is None:
        candidate_idx = int(CALVIN_E2_SCENARIO_WHITELIST[0])

    repair_fail_idx = None
    for r in sorted(per["verifier_plus_replan"], key=lambda x: x["episode_index"]):
        if not r["success"] and r.get("replan_count", 0) > 0:
            repair_fail_idx = r["episode_index"]
            break
    if repair_fail_idx is None:
        repair_fail_idx = next(
            (r["episode_index"] for r in per["verifier_plus_replan"] if not r["success"]),
            int(CALVIN_E2_SCENARIO_WHITELIST[-1]),
        )

    cal_sel = {
        "selection_version": "e2_calvin_fixture_v1",
        "contrast_episode_index": candidate_idx,
        "repair_fail_episode_index": repair_fail_idx,
    }
    (unified / "calvin_selection_meta.json").write_text(
        json.dumps(cal_sel, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    s_fix = by_idx[candidate_idx]
    s_fail = by_idx[repair_fail_idx]

    tr_ok = run_calvin_minimal_episode(
        s_fix["instruction"],
        max_steps=12,
        initial_observation=s_fix["initial_observation"],
        verifier_mode="verifier_plus_replan",
        replanner_mode="rule",
        experiment_id=payload["experiment_id"],
    )
    tr_vo = run_calvin_minimal_episode(
        s_fix["instruction"],
        max_steps=12,
        initial_observation=s_fix["initial_observation"],
        verifier_mode="verifier_only",
        replanner_mode="rule",
        experiment_id=payload["experiment_id"],
    )
    tr_bad = run_calvin_minimal_episode(
        s_fail["instruction"],
        max_steps=12,
        initial_observation=s_fail["initial_observation"],
        verifier_mode="verifier_plus_replan",
        replanner_mode="rule",
        experiment_id=payload["experiment_id"],
    )

    fix_text = json.dumps(
        {
            "backend": "calvin_fixture",
            "episode_index": candidate_idx,
            "verifier_only_trace": {
                "success": tr_vo.success,
                "replan_count": tr_vo.replan_count,
                "steps": tr_vo.steps,
            },
            "verifier_plus_replan_trace": {
                "success": tr_ok.success,
                "replan_count": tr_ok.replan_count,
                "steps": tr_ok.steps,
            },
            "fixture_source": "tests/fixtures/calvin_mock_observation.json (variant copy)",
        },
        indent=2,
        ensure_ascii=False,
    )
    fail_text = json.dumps(
        {
            "backend": "calvin_fixture",
            "episode_index": repair_fail_idx,
            "verifier_plus_replan_trace": {
                "success": tr_bad.success,
                "replan_count": tr_bad.replan_count,
                "steps": tr_bad.steps,
            },
            "fixture_source": "tests/fixtures/calvin_mock_observation.json (variant copy)",
        },
        indent=2,
        ensure_ascii=False,
    )
    (demo / "calvin_case_replan_fixes_stuck_verifier_only.json").write_text(fix_text, encoding="utf-8")
    (demo / "calvin_case_repair_failed_after_failure_detected.json").write_text(fail_text, encoding="utf-8")
    (unified / "calvin_case_replan_fixes_stuck_verifier_only.json").write_text(fix_text, encoding="utf-8")
    (unified / "calvin_case_repair_failed_after_failure_detected.json").write_text(fail_text, encoding="utf-8")

    calvin_block = "\n".join(
        [
            "## CALVIN fixture batch (dev — not official benchmark)",
            "",
            f"_选例元数据：`results/demos/e2_ablation_cases/calvin_selection_meta.json`（与 mock 案例同目录便于引用）。_",
            "",
            "### 4) `verifier_only` 卡住；`verifier_plus_replan` 在同一 episode 设定下恢复",
            f"- episode_index `{candidate_idx}`；对比 trace：",
            "  - [`results/demos/e2_ablation_calvin_cases/calvin_case_replan_fixes_stuck_verifier_only.json`]"
            "(../../results/demos/e2_ablation_calvin_cases/calvin_case_replan_fixes_stuck_verifier_only.json)",
            "  - 同内容镜像：[`results/demos/e2_ablation_cases/calvin_case_replan_fixes_stuck_verifier_only.json`]"
            "(../../results/demos/e2_ablation_cases/calvin_case_replan_fixes_stuck_verifier_only.json)",
            "",
            "### 5) 检出 failure 但 repair / 后续仍失败",
            f"- episode_index `{repair_fail_idx}`：",
            "  - [`results/demos/e2_ablation_calvin_cases/calvin_case_repair_failed_after_failure_detected.json`]"
            "(../../results/demos/e2_ablation_calvin_cases/calvin_case_repair_failed_after_failure_detected.json)",
            "  - 镜像：[`results/demos/e2_ablation_cases/calvin_case_repair_failed_after_failure_detected.json`]"
            "(../../results/demos/e2_ablation_cases/calvin_case_repair_failed_after_failure_detected.json)",
            "",
        ]
    )
    path = root / "docs" / "failure_cases" / "e2_ablation_cases.md"
    marker = "## CALVIN fixture batch"
    if path.is_file():
        t = path.read_text(encoding="utf-8")
        if marker in t:
            head = t[: t.index(marker)].rstrip()
            path.write_text(head + "\n\n" + calvin_block + "\n", encoding="utf-8")
        else:
            path.write_text(t.rstrip() + "\n\n" + calvin_block + "\n", encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# E2 ablation — curated cases\n\n" + calvin_block + "\n", encoding="utf-8")


def lines_to_table_md(payload: dict) -> str:
    rows = [
        "| mode | task_completion | failure_detected_rate | replan_trigger | recovery_success | avg_steps |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode, s in payload["modes"].items():
        rows.append(
            f"| {mode} | {s['task_completion_rate']:.3f} | {s['failure_detected_rate']:.3f} | "
            f"{s['replan_trigger_rate']:.3f} | {s['recovery_success_rate']:.3f} | {s['average_steps']:.2f} |"
        )
    rows.append("")
    be = payload.get("backend", "mock")
    if be == "mock":
        tag = "_Symbolic mock v0_"
    elif be == "calvin_fixture":
        tag = "_CALVIN **fixture** minimal loop — not official CALVIN ablation._"
    else:
        tag = "_CALVIN **official debug npz** minimal loop — not official CALVIN ablation._"
    rows.append(tag)
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--backend",
        type=str,
        choices=["mock", "calvin_fixture", "calvin_debug_real"],
        default="mock",
    )
    parser.add_argument(
        "--calvin-debug-batch",
        type=str,
        choices=["pooled_manifest", "grouped_sequence", "same_task_subset"],
        default="grouped_sequence",
        help="CALVIN debug real-data episode construction (not official task labels).",
    )
    parser.add_argument(
        "--experiment-id",
        type=str,
        default="",
    )
    args, _ = parser.parse_known_args()
    root = args.root or repo_root()
    backend: Backend = args.backend  # type: ignore[assignment]
    if args.experiment_id:
        eid = args.experiment_id
    elif backend == "calvin_fixture":
        eid = datetime.now(timezone.utc).strftime("e2_calvin_fixture_%Y%m%dT%H%M%SZ")
    elif backend == "calvin_debug_real":
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        b = args.calvin_debug_batch
        if b == "grouped_sequence":
            eid = f"e2_calvin_debug_real_aligned_{ts}"
        elif b == "same_task_subset":
            eid = f"e2_calvin_debug_same_task_{ts}"
        else:
            eid = f"e2_calvin_debug_real_{ts}"
    else:
        eid = datetime.now(timezone.utc).strftime("e2_mock_%Y%m%dT%H%M%SZ")

    out_dir = root / "results" / "experiments" / "e2_ablation" / eid
    out_dir.mkdir(parents=True, exist_ok=True)

    cdb = args.calvin_debug_batch if backend == "calvin_debug_real" else None
    payload = run_all_modes(
        experiment_id=eid,
        replanner_mode="rule",
        backend=backend,
        calvin_debug_batch=cdb,  # type: ignore[arg-type]
    )
    payload["generated_utc"] = datetime.now(timezone.utc).isoformat()

    (out_dir / "metrics.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    per_path = out_dir / "per_episode.jsonl"
    with per_path.open("w", encoding="utf-8") as f:
        for mode, rows in payload["per_episode_by_mode"].items():
            for r in rows:
                f.write(json.dumps({"mode": mode, **r}, ensure_ascii=False) + "\n")

    if backend == "mock":
        label = "mock symbolic"
    elif backend == "calvin_fixture":
        label = "CALVIN fixture batch"
    else:
        label = "CALVIN debug real-data batch"
    lines = [
        f"# E2 ablation ({eid}) — {label}",
        "",
        "_Not official CALVIN benchmark._",
        "",
        "## Per-mode summary",
        "",
    ]
    for mode, stats in payload["modes"].items():
        lines.append(f"### `{mode}`")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(stats, indent=2))
        lines.append("```")
        lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    plots = out_dir / "plots"
    plots.mkdir(exist_ok=True)
    try:
        import matplotlib.pyplot as plt

        modes = list(payload["modes"].keys())
        tc = [payload["modes"][m]["task_completion_rate"] for m in modes]
        plt.figure(figsize=(6, 3))
        plt.bar(modes, tc)
        plt.ylabel("task_completion_rate")
        plt.title(f"E2 ablation ({backend})")
        plt.tight_layout()
        plt.savefig(plots / "task_completion_rate.png")
        plt.close()
    except Exception:  # noqa: BLE001
        (plots / "README.txt").write_text("matplotlib unavailable; skipped plot.\n", encoding="utf-8")

    table = root / "docs" / "tables" / "e2_ablation_summary.md"
    if backend == "mock":
        table.parent.mkdir(parents=True, exist_ok=True)
        table.write_text(lines_to_table_md(payload), encoding="utf-8")
        pick_cases(root, out_dir, payload)
    elif backend == "calvin_fixture":
        pick_calvin_cases(root, payload)
    else:
        pick_calvin_debug_real_cases(root, payload)

    mock_latest = find_latest_e2_dir(root, "mock")
    cal_latest = find_latest_e2_dir(root, "calvin_fixture")
    write_mock_vs_calvin_table(root, mock_latest, cal_latest)
    write_e2_three_backend_table(root)

    print(json.dumps({"wrote": str(out_dir), "backend": backend}, indent=2))


if __name__ == "__main__":
    main()
