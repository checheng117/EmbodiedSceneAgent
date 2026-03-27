"""Compare base Qwen2.5-VL vs LoRA-tuned planner on a JSONL eval split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from embodied_scene_agent.evaluation.planner_eval_utils import score_row
from embodied_scene_agent.training.qwen_vl_sft_dataset import dummy_planner_image, load_jsonl_rows
from embodied_scene_agent.utils.env import get_hf_token, load_project_dotenv
from embodied_scene_agent.utils.paths import rel_repo_path, repo_root


def _build_generate_kwargs(processor: object, user_prompt: str, model: object, device: str) -> dict:
    from qwen_vl_utils import process_vision_info

    img = dummy_planner_image()
    user_messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": img},
                {"type": "text", "text": user_prompt},
            ],
        }
    ]
    text = processor.apply_chat_template(user_messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(user_messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    import torch

    inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
    return inputs


def _generate_text(
    model: object,
    processor: object,
    user_prompt: str,
    *,
    device: str,
    max_new_tokens: int = 384,
) -> str:
    import torch

    inputs = _build_generate_kwargs(processor, user_prompt, model, device)
    with torch.no_grad():
        out_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )
    trimmed = out_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(trimmed, skip_special_tokens=True)[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Eval base vs LoRA planner.")
    parser.add_argument("--eval-jsonl", type=Path, required=True)
    parser.add_argument("--base-model-id", type=str, default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--lora-dir", type=Path, required=True, help="PEFT adapter directory (best_lora or final_lora).")
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--max-samples", type=int, default=0, help="0 = all rows in eval JSONL.")
    args = parser.parse_args()

    load_project_dotenv()
    get_hf_token(require=False)

    import torch
    from peft import PeftModel
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    rows = load_jsonl_rows(Path(args.eval_jsonl))
    if args.max_samples > 0:
        rows = rows[: args.max_samples]

    out_dir = args.out_dir or Path("results/eval/planner_base_vs_tuned")
    out_dir.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    processor = AutoProcessor.from_pretrained(args.base_model_id, trust_remote_code=True)
    base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.base_model_id, torch_dtype=dtype, trust_remote_code=True, device_map=None
    ).to(device)
    base_model.eval()

    base_texts: list[str] = []
    for row in rows:
        up = str(row["user_prompt"])
        base_texts.append(_generate_text(base_model, processor, up, device=device))

    tuned = PeftModel.from_pretrained(base_model, str(args.lora_dir))
    tuned.eval()

    per_sample: list[dict] = []
    agg = {
        "n": 0,
        "base_format": 0,
        "tuned_format": 0,
        "base_tool": 0,
        "tuned_tool": 0,
        "base_target": 0,
        "tuned_target": 0,
        "base_task_complete": 0,
        "tuned_task_complete": 0,
        "tuned_recovery_style": 0,
        "recovery_rows": 0,
    }

    for row, btext in zip(rows, base_texts, strict=True):
        up = str(row["user_prompt"])
        ref = str(row["target_text"])
        tt = str(row.get("trajectory_type", "normal"))
        if tt == "recovery":
            agg["recovery_rows"] += 1

        ttext = _generate_text(tuned, processor, up, device=device)

        sb = score_row(reference_target=ref, generated=btext, trajectory_type=tt)
        st = score_row(reference_target=ref, generated=ttext, trajectory_type=tt)
        agg["n"] += 1
        agg["base_format"] += int(sb["format_compliance"])
        agg["tuned_format"] += int(st["format_compliance"])
        agg["base_tool"] += int(sb["tool_skill_match"])
        agg["tuned_tool"] += int(st["tool_skill_match"])
        agg["base_target"] += int(sb["target_match"])
        agg["tuned_target"] += int(st["target_match"])
        agg["base_task_complete"] += int(
            sb["format_compliance"] and sb["tool_skill_match"] and sb["target_match"]
        )
        agg["tuned_task_complete"] += int(
            st["format_compliance"] and st["tool_skill_match"] and st["target_match"]
        )
        if tt == "recovery":
            agg["tuned_recovery_style"] += int(st["recovery_style_ok"])

        per_sample.append(
            {
                "sample_id": row.get("sample_id"),
                "trajectory_type": tt,
                "reference_head": ref[:500],
                "base_output_head": btext[:800],
                "tuned_output_head": ttext[:800],
                "base_scores": sb,
                "tuned_scores": st,
            }
        )

    n = max(1, agg["n"])
    metrics = {
        "n": agg["n"],
        "format_compliance_rate_base": agg["base_format"] / n,
        "format_compliance_rate_tuned": agg["tuned_format"] / n,
        "tool_use_accuracy_base": agg["base_tool"] / n,
        "tool_use_accuracy_tuned": agg["tuned_tool"] / n,
        "target_match_rate_base": agg["base_target"] / n,
        "target_match_rate_tuned": agg["tuned_target"] / n,
        "task_completion_rate_base": agg["base_task_complete"] / n,
        "task_completion_rate_tuned": agg["tuned_task_complete"] / n,
        "error_recovery_rate_tuned": agg["tuned_recovery_style"] / max(1, agg["recovery_rows"]),
        "recovery_eval_rows": agg["recovery_rows"],
        "notes": (
            "tool_use_accuracy compares final Skill: line to reference JSONL target_text; "
            "target_match_rate is an action-target string proxy (last Target: line). "
            "task_completion_rate is a strict proxy: format_compliance AND tool_skill_match AND target_match. "
            "error_recovery_rate_tuned is recovery_style_ok rate on rows with trajectory_type==recovery only; "
            "not CALVIN env success."
        ),
    }

    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    with (out_dir / "per_sample_results.jsonl").open("w", encoding="utf-8") as f:
        for p in per_sample:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    root = repo_root()
    eval_disp = rel_repo_path(root, Path(args.eval_jsonl))
    lora_disp = rel_repo_path(root, Path(args.lora_dir))
    summary_md = [
        "# Base vs tuned planner eval",
        "",
        f"- eval file: `{eval_disp}`",
        f"- base model: `{args.base_model_id}`",
        f"- LoRA dir: `{lora_disp}`",
        "",
        "## Metrics",
        "",
        "```json",
        json.dumps(metrics, indent=2),
        "```",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_md), encoding="utf-8")
    print(f"[eval_planner_models] wrote {out_dir}")


if __name__ == "__main__":
    main()
