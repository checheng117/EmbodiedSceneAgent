# 训练运行日志（仅记录真实执行）

## 2026-03-24

| 步骤 | 命令 / 脚本 | 结果 |
|------|----------------|------|
| CALVIN 语言子集 | `python -m embodied_scene_agent.data.prepare_calvin_real_subset` | **成功**：423 行 manifest → `data/processed/calvin_real_subset/manifest.jsonl` |
| Planner SFT 构建 | `python -m embodied_scene_agent.training.build_planner_data --source real_subset` | **成功**：train/val/test 共 **1166** 行 → `data/processed/planner_sft/*.jsonl`；统计 `docs/planner_data_stats.md` |
| 3B 模型缓存 | `python -m embodied_scene_agent.training.prepare_backbone`（`HF_HOME=./.hf_cache`） | **成功**：`Qwen/Qwen2.5-VL-3B-Instruct` snapshot；见 `results/logs/prepare_backbone_last.json` |
| 最小 LoRA SFT | `python -m embodied_scene_agent.training.run_planner_sft ...` / `scripts/run_planner_sft_3b_minimal.sh` | **2026-03-24 本会话**：`torch` 导入失败（见当时说明）。**2026-03-25**：环境验收通过并完成真实训练，见 **§2026-03-25**。 |
| Base vs tuned 评测 | `scripts/run_eval_base_vs_tuned.sh` | **2026-03-25**：在 **73** 条 `test.jsonl` 上跑通；产物见 **§2026-03-25**（指标为 JSONL 对齐 **proxy**，非 CALVIN 环境成功率）。 |

## 2026-03-25（环境、训练、评测 — 真实执行）

### PyTorch 环境

- **审计**：`embodied-scene-agent` 内 `torch` / `torchvision` 均为 **PyPI cu128 wheel**（`2.11.0+cu128` / `0.26.0+cu128`），与 `conda list` 中 `pypi_0` 一致，**无 conda 与 pip 双装 torch**。
- **防护**：训练/评测入口脚本增加 `PYTHONNOUSERSITE=1`，降低 `~/.local` 与 wheel 混载导致 `libtorch_nvshmem` / `libc10` 符号错误的风险。细节见 `docs/torch_env_repair_log.md`。
- **验收命令**（均成功）：
  - `python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"`
  - `python -c "import torchvision; print(torchvision.__version__)"`
  - `torch.randn(2,3).cuda()` 求和 smoke

### 最小 LoRA SFT

| 项 | 值 |
|----|-----|
| 命令 | `bash scripts/run_planner_sft_3b_minimal.sh`（仓库根目录，`HF_HOME` 默认 `.hf_cache`） |
| 配置快照 | `results/checkpoints/planner_sft_3b_minimal/run_latest/config.snapshot.yaml` |
| 数据 | `data/processed/planner_sft/train.jsonl`、`val.jsonl`（与 `docs/planner_data_stats.md` 一致） |
| 优化器步数 | **80**（`configs/planner/qwen25vl_3b_lora_minimal.yaml`） |
| 最佳验证 loss | **≈0.496**（`run_meta.json` 中 `best_val_loss`） |
| 末步验证 loss | **≈0.496**（`training_log.txt` 末条 `val_loss`） |
| Checkpoint | `best_lora/`、`final_lora/`（含 `adapter_model.safetensors`） |

**Checkpoint 加载 smoke**（同一条 `train.jsonl` 首行，`max_new_tokens=64`）：base 与 LoRA 均成功 `generate`，输出长度不同（定性可比较），命令见本机历史或可自行复现。

### Base vs tuned 评测

| 项 | 值 |
|----|-----|
| 命令 | `bash scripts/run_eval_base_vs_tuned.sh "$(pwd)/results/checkpoints/planner_sft_3b_minimal/run_latest/best_lora" 0`（`0` = 全量 `test.jsonl`） |
| `metrics.json` | `results/eval/planner_base_vs_tuned/metrics.json` |
| `summary.md` | `results/eval/planner_base_vs_tuned/summary.md` |
| `per_sample_results.jsonl` | `results/eval/planner_base_vs_tuned/per_sample_results.jsonl` |
| Case studies | `results/eval/base_vs_tuned_case_studies.md`（含 **normal / recovery / multi_step** 各至少一例） |

**metrics.json 摘要（n=73，均为 proxy）**：

- `format_compliance_rate_*`：base/tuned 均为 **1.0**
- `tool_use_accuracy_tuned` **>** `tool_use_accuracy_base`（约 **0.219** vs **0.082**）
- `target_match_rate_tuned` **>** `target_match_rate_base`（约 **0.479** vs **0.329**）
- `task_completion_rate_tuned` **>** `task_completion_rate_base`（约 **0.205** vs **0.068**）
- `error_recovery_rate_tuned`：**0.0**（`recovery_eval_rows`=8；`recovery_style_ok` 在该批上未命中，**不**表示 CALVIN 无恢复能力）

完整数值以 `metrics.json` 为准；`notes` 字段说明各指标含义。

## 3090 上恢复训练（建议顺序）

1. 在 conda 环境 **`embodied-scene-agent`** 内，用 **同一索引** 安装匹配的 `torch` 与 `torchvision`（例如 cu128：`pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128`）。  
2. `pip install -e '.[train]'`  
3. `bash scripts/run_planner_sft_3b_minimal.sh`  
4. `bash scripts/run_planner_inference_smoke.sh`  
5. `bash scripts/run_eval_base_vs_tuned.sh`（全量 test：第二个参数传 `0`，见 §2026-03-25）

## 代码层面事实

- 训练使用 **Qwen2.5-VL-3B-Instruct** + **PEFT LoRA**；数据为 **planner_sft/v1** JSONL（`user_prompt` / `target_text` + dummy 图）。  
- **Collate 仅支持 batch size 1**（见 `qwen_vl_sft_dataset.vl_collate_fn`）。
