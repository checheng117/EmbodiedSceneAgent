# 3B backbone 选择与拉取记录（事实）

## 仓库配置

- `configs/planner/qwen25vl_3b_lora.yaml` 与 `configs/planner/qwen25vl_3b_lora_minimal.yaml` 均使用 **`Qwen/Qwen2.5-VL-3B-Instruct`**。
- 理由：与 README / 算力规划一致；支持 LoRA；可通过 Hugging Face Hub 公开拉取；planner 监督为文本 + 占位图像（训练脚本使用统一 dummy 图像，而非 CALVIN 真实帧）。

## 本仓库执行记录

| 时间 (UTC) | 动作 | 结果 |
|------------|------|------|
| 2026-03-24 | `python -m embodied_scene_agent.training.prepare_backbone`（`HF_HOME` 指向仓库内 `.hf_cache`） | **成功**：`snapshot_download` 完成；状态见 `results/logs/prepare_backbone_last.json`（**勿**提交 token；目录可能被 `.gitignore` 忽略）。 |

封装脚本：`scripts/pull_3b_backbone.sh`（内部 `source scripts/conda_env.sh`，并默认 `HF_HOME=$ROOT/.hf_cache`）。

## 依赖说明（训练）

- `transformers` 加载 Qwen2.5-VL 处理器时，**需要 `torchvision`**（`Qwen2VLVideoProcessor` 依赖）。若使用 **Python 3.13 + CUDA 12.8**，本机验证可用的安装方式为：  
  `pip install torchvision==0.25.0 --index-url https://download.pytorch.org/whl/cu128`（需与已安装的 `torch` cu 版本一致）。
- 训练 collate 当前 **仅支持 `per_device_batch_size=1`**（Qwen2.5-VL 视觉 token 长度随样本变化，未实现多图 batch 拼接）。

## 未完成（勿写进简历为「已训练」）

- 若本机 `torch` 出现 `libtorch_nvshmem.so: undefined symbol` 等动态库错误，需在同一虚拟环境/conda 环境中 **对齐重装 torch 与 torchvision** 后再跑 `scripts/run_planner_sft_3b_minimal.sh`。**修复前的训练 loss / checkpoint 不得伪造。**
