"""Probe live CALVIN: .env, optional ESA_CALVIN_ENV_FACTORY, reset, obs/info summary (not a benchmark)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from embodied_scene_agent.envs.calvin_factory_load import resolve_calvin_env_factory_from_env
from embodied_scene_agent.envs.calvin_probe import build_calvin_live_probe_report, probe_report_to_markdown
from embodied_scene_agent.utils.env import hf_token_status_message, load_project_dotenv
from embodied_scene_agent.utils.paths import repo_root


def main() -> None:
    p = argparse.ArgumentParser(
        description="Load .env, optional local CALVIN factory, reset, summarize obs/info. NOT a benchmark."
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Write full JSON report (default: results/calvin_live_probe_summary.json under repo root).",
    )
    p.add_argument(
        "--no-write-json",
        action="store_true",
        help="Do not write JSON file; only print to stdout.",
    )
    p.add_argument(
        "--md-out",
        type=Path,
        default=None,
        help="Optional markdown summary path (no secrets).",
    )
    p.add_argument(
        "--step-smoke",
        action="store_true",
        help="After reset, call env.step(zero action) once for interface smoke (not success claim).",
    )
    args = p.parse_args()

    dotenv_loaded = load_project_dotenv()
    hf_status = hf_token_status_message()
    fn, fac_meta = resolve_calvin_env_factory_from_env()

    report = build_calvin_live_probe_report(
        dotenv_file_loaded=dotenv_loaded,
        hf_token_status=hf_status,
        factory_resolve_meta=fac_meta,
        env_factory=fn,
        try_step_smoke=args.step_smoke,
    )
    text = json.dumps(report, indent=2, ensure_ascii=False)

    out_json = args.out_json
    if out_json is None and not args.no_write_json:
        out_json = repo_root() / "results" / "calvin_live_probe_summary.json"

    if out_json is not None and not args.no_write_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(text, encoding="utf-8")

    print(text)

    if args.md_out is not None:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(probe_report_to_markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
