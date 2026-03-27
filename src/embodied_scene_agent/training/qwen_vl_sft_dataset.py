"""Multimodal JSONL → Qwen2.5-VL processor tensors (dummy image + text supervision)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torch.utils.data import Dataset

_DUMMY_IMG: Image.Image | None = None


def dummy_planner_image() -> Image.Image:
    global _DUMMY_IMG
    if _DUMMY_IMG is None:
        _DUMMY_IMG = Image.new("RGB", (224, 224), color=(24, 24, 24))
    return _DUMMY_IMG


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


class PlannerVLJsonlDataset(Dataset):
    """One row = user image+text prompt + assistant target (SFT labels masked on user)."""

    def __init__(self, jsonl_path: Path, processor: Any) -> None:
        self.rows = load_jsonl_rows(Path(jsonl_path))
        self.processor = processor

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        from qwen_vl_utils import process_vision_info

        row = self.rows[idx]
        user_text = str(row["user_prompt"])
        assistant_text = str(row["target_text"])
        img = dummy_planner_image()

        user_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": user_text},
                ],
            }
        ]
        full_messages = [
            *user_messages,
            {"role": "assistant", "content": assistant_text},
        ]

        user_text_templated = self.processor.apply_chat_template(
            user_messages, tokenize=False, add_generation_prompt=True
        )
        full_text = self.processor.apply_chat_template(
            full_messages, tokenize=False, add_generation_prompt=False
        )

        image_inputs, video_inputs = process_vision_info(user_messages)
        user_enc = self.processor(
            text=[user_text_templated],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        user_prefix = user_enc["input_ids"][0]

        image_inputs_f, video_inputs_f = process_vision_info(full_messages)
        full_enc = self.processor(
            text=[full_text],
            images=image_inputs_f,
            videos=video_inputs_f,
            padding=True,
            return_tensors="pt",
        )

        input_ids = full_enc["input_ids"][0]
        attention_mask = full_enc["attention_mask"][0]
        up_len = int(user_prefix.shape[0])
        full_prefix = input_ids[:up_len]
        if not torch.equal(full_prefix, user_prefix):
            raise RuntimeError(
                "Qwen VL tokenization prefix mismatch: user-only vs full chat template length alignment failed."
            )
        user_len = up_len
        labels = input_ids.clone()
        labels[:user_len] = -100
        # Mask padding tokens
        pad_id = getattr(self.processor.tokenizer, "pad_token_id", None)
        if pad_id is not None:
            labels = labels.masked_fill(labels == pad_id, -100)

        pixel_values = full_enc.get("pixel_values")
        image_grid_thw = full_enc.get("image_grid_thw")
        out: dict[str, Any] = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }
        # Keep processor layout (do not drop the leading batch dim) — vision tensors are not simple stack.
        if pixel_values is not None:
            out["pixel_values"] = pixel_values
        if image_grid_thw is not None:
            out["image_grid_thw"] = image_grid_thw
        return out


def vl_collate_fn(batch: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Pad text fields; keep Qwen2.5-VL ``pixel_values`` / ``image_grid_thw`` as returned by the processor.

    **Batch size > 1** is not supported (variable vision token counts); use ``per_device_batch_size=1``.
    """
    if len(batch) != 1:
        raise ValueError("vl_collate_fn only supports batch_size=1 for Qwen2.5-VL planner SFT.")
    b = batch[0]
    out: dict[str, Any] = {
        "input_ids": b["input_ids"].unsqueeze(0),
        "attention_mask": b["attention_mask"].unsqueeze(0),
        "labels": b["labels"].unsqueeze(0),
    }
    if "pixel_values" in b:
        out["pixel_values"] = b["pixel_values"]
    if "image_grid_thw" in b:
        out["image_grid_thw"] = b["image_grid_thw"]
    return out
