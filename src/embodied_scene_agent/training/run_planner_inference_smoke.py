"""Qualitative base vs LoRA on a few val rows (markdown report)."""

from __future__ import annotations

import argparse
from pathlib import Path

from embodied_scene_agent.evaluation.eval_planner_models import _generate_text
from embodied_scene_agent.training.qwen_vl_sft_dataset import load_jsonl_rows
from embodied_scene_agent.utils.env import get_hf_token, load_project_dotenv


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke inference: base vs LoRA planner.")
    parser.add_argument("--val-jsonl", type=Path, required=True)
    parser.add_argument("--base-model-id", type=str, default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--lora-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-samples", type=int, default=3)
    args = parser.parse_args()

    load_project_dotenv()
    get_hf_token(require=False)

    import torch
    from peft import PeftModel
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    rows = load_jsonl_rows(Path(args.val_jsonl))[: max(1, args.max_samples)]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    processor = AutoProcessor.from_pretrained(args.base_model_id, trust_remote_code=True)
    base = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.base_model_id, torch_dtype=dtype, trust_remote_code=True, device_map=None
    ).to(device)
    base.eval()

    lines = ["# Planner inference smoke (base vs LoRA)", "", f"- device: `{device}`", ""]
    base_out: list[str] = []
    for row in rows:
        up = str(row["user_prompt"])
        base_out.append(_generate_text(base, processor, up, device=device))

    tuned = PeftModel.from_pretrained(base, str(args.lora_dir))
    tuned.eval()

    for row, bo in zip(rows, base_out, strict=True):
        up = str(row["user_prompt"])
        to = _generate_text(tuned, processor, up, device=device)
        lines.append(f"## {row.get('sample_id')}")
        lines.append("")
        lines.append("### Reference (target head)")
        lines.append("")
        lines.append("```")
        lines.append(str(row.get("target_text", ""))[:1200])
        lines.append("```")
        lines.append("")
        lines.append("### Base")
        lines.append("")
        lines.append("```")
        lines.append(bo[:1200])
        lines.append("```")
        lines.append("")
        lines.append("### LoRA")
        lines.append("")
        lines.append("```")
        lines.append(to[:1200])
        lines.append("```")
        lines.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[run_planner_inference_smoke] wrote {args.out}")


if __name__ == "__main__":
    main()
