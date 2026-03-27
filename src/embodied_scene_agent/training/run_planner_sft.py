"""Minimal LoRA SFT on planner JSONL (Qwen2.5-VL-3B-Instruct + dummy scene image)."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from embodied_scene_agent.utils.env import get_hf_token, load_project_dotenv
from embodied_scene_agent.utils.paths import repo_root


def main() -> None:
    parser = argparse.ArgumentParser(description="LoRA SFT for structured planner (Qwen2.5-VL).")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--train-jsonl", type=Path, required=True)
    parser.add_argument("--val-jsonl", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Default: results/checkpoints/planner_sft_3b_minimal/<timestamp>",
    )
    parser.add_argument("--max-steps", type=int, default=None, help="Override config train.max_steps.")
    parser.add_argument("--epochs", type=float, default=1.0)
    args = parser.parse_args()

    load_project_dotenv()
    get_hf_token(require=False)

    try:
        import torch
        from peft import LoraConfig, get_peft_model
        from torch.optim import AdamW
        from torch.utils.data import DataLoader
        from tqdm.auto import tqdm
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration, get_cosine_schedule_with_warmup
    except ImportError as e:
        raise SystemExit(
            "Missing training deps. Install with: pip install -e '.[train]'"
        ) from e

    from embodied_scene_agent.training.qwen_vl_sft_dataset import PlannerVLJsonlDataset, vl_collate_fn
    from embodied_scene_agent.utils.config import load_yaml_dict

    cfg_path = args.config
    cfg = load_yaml_dict(cfg_path)
    model_id = str(cfg["model_id"])
    lcfg = cfg.get("lora", {})
    tcfg = cfg.get("train", {})

    out_dir = args.output_dir
    if out_dir is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_dir = repo_root() / "results" / "checkpoints" / "planner_sft_3b_minimal" / ts
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(cfg_path, out_dir / "config.snapshot.yaml")

    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    dtype = torch.float32
    if torch.cuda.is_available():
        dtype = torch.bfloat16 if str(cfg.get("precision", "bf16")) == "bf16" else torch.float16
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=dtype,
        trust_remote_code=True,
        device_map=None,
    )

    target_modules = list(lcfg.get("target_modules", ["q_proj", "v_proj"]))
    peft_config = LoraConfig(
        r=int(lcfg.get("r", 16)),
        lora_alpha=int(lcfg.get("alpha", 32)),
        lora_dropout=float(lcfg.get("dropout", 0.05)),
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=target_modules,
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    train_ds = PlannerVLJsonlDataset(Path(args.train_jsonl), processor)
    val_ds = PlannerVLJsonlDataset(Path(args.val_jsonl), processor)
    if len(train_ds) == 0:
        raise SystemExit("train JSONL is empty")

    per_device_bs = int(tcfg.get("per_device_batch_size", 1))
    grad_accum = int(tcfg.get("gradient_accumulation_steps", 4))
    max_steps_cfg = int(tcfg.get("max_steps", 200))
    max_steps = int(args.max_steps) if args.max_steps is not None else max_steps_cfg
    lr = float(tcfg.get("learning_rate", 1e-4))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        model = model.to(device)
    else:
        model = model.to(device)

    train_loader = DataLoader(
        train_ds,
        batch_size=per_device_bs,
        shuffle=True,
        collate_fn=vl_collate_fn,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=per_device_bs,
        shuffle=False,
        collate_fn=vl_collate_fn,
    )

    no_decay = ["bias", "LayerNorm.weight"]
    opt_group = [
        {
            "params": [p for n, p in model.named_parameters() if p.requires_grad and not any(nd in n for nd in no_decay)],
            "weight_decay": 0.01,
        },
        {
            "params": [p for n, p in model.named_parameters() if p.requires_grad and any(nd in n for nd in no_decay)],
            "weight_decay": 0.0,
        },
    ]
    optimizer = AdamW(opt_group, lr=lr)
    steps_per_epoch = max(1, len(train_loader) // grad_accum)
    total_optimizer_steps = min(max_steps, int(steps_per_epoch * args.epochs))
    scheduler = get_cosine_schedule_with_warmup(
        optimizer, num_warmup_steps=max(1, total_optimizer_steps // 20), num_training_steps=total_optimizer_steps
    )

    log_lines: list[str] = []
    global_step = 0
    best_val = float("inf")
    model.train()
    pbar = tqdm(total=total_optimizer_steps, desc="train")
    micro = 0
    accum_loss = 0.0

    while global_step < total_optimizer_steps:
        for batch in train_loader:
            if global_step >= total_optimizer_steps:
                break
            batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
            out = model(**batch)
            loss = out.loss / grad_accum
            loss.backward()
            accum_loss += float(out.loss.detach())
            micro += 1
            if micro % grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1
                pbar.update(1)
                log_lines.append(f"step {global_step} train_loss {accum_loss / grad_accum:.4f}")
                accum_loss = 0.0
                pbar.set_postfix(loss=log_lines[-1].split()[-1])
                if global_step % max(1, total_optimizer_steps // 5) == 0 or global_step == total_optimizer_steps:
                    model.eval()
                    val_losses: list[float] = []
                    with torch.no_grad():
                        for vb in val_loader:
                            vb = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in vb.items()}
                            vo = model(**vb)
                            val_losses.append(float(vo.loss.detach()))
                    model.train()
                    vl = sum(val_losses) / max(1, len(val_losses))
                    log_lines.append(f"step {global_step} val_loss {vl:.4f}")
                    if vl < best_val:
                        best_val = vl
                        model.save_pretrained(out_dir / "best_lora")
                        processor.save_pretrained(out_dir / "best_lora")
        if global_step >= total_optimizer_steps:
            break

    model.save_pretrained(out_dir / "final_lora")
    processor.save_pretrained(out_dir / "final_lora")
    (out_dir / "training_log.txt").write_text("\n".join(log_lines), encoding="utf-8")
    meta = {
        "model_id": model_id,
        "train_jsonl": str(args.train_jsonl),
        "val_jsonl": str(args.val_jsonl),
        "output_dir": str(out_dir),
        "max_optimizer_steps": total_optimizer_steps,
        "best_val_loss": best_val if best_val < float("inf") else None,
        "device": str(device),
        "utc_iso": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[run_planner_sft] done → {out_dir}")


if __name__ == "__main__":
    main()
