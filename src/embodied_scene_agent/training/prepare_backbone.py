"""Download / cache Hugging Face backbone (Qwen2.5-VL-3B-Instruct) using HF_TOKEN from env / .env."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from embodied_scene_agent.utils.env import get_hf_token, load_project_dotenv
from embodied_scene_agent.utils.paths import repo_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Snapshot-download planner backbone to local HF cache.")
    parser.add_argument(
        "--model-id",
        type=str,
        default="Qwen/Qwen2.5-VL-3B-Instruct",
        help="Hugging Face model id (default matches configs/planner/qwen25vl_3b_lora.yaml).",
    )
    parser.add_argument(
        "--log-json",
        type=Path,
        default=None,
        help="Write a token-free status JSON (default: results/logs/prepare_backbone_last.json).",
    )
    args = parser.parse_args()

    load_project_dotenv()
    token = get_hf_token(require=False)

    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:
        raise SystemExit(
            "huggingface_hub is required: pip install huggingface_hub (or conda env train extras)."
        ) from e

    log_path = args.log_json or (repo_root() / "results" / "logs" / "prepare_backbone_last.json")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    status: dict = {
        "model_id": args.model_id,
        "utc_iso": datetime.now(timezone.utc).isoformat(),
        "hf_token_configured": bool(token),
        "status": "started",
    }

    try:
        cache_dir = snapshot_download(
            repo_id=args.model_id,
            token=token,
            local_files_only=False,
        )
        status["status"] = "ok"
        status["cache_dir"] = cache_dir
    except Exception as e:  # noqa: BLE001
        status["status"] = "error"
        status["error_type"] = type(e).__name__
        status["error_message"] = str(e)[:2000]

    log_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(f"[prepare_backbone] {status['status']} — log: {log_path}")
    if status["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
