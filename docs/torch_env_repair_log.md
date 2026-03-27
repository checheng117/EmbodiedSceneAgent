# PyTorch / CUDA 环境修复记录（仅事实）

## 2026-03-25

### 审计命令（在 conda 环境 `embodied-scene-agent` 内）

- `python -c "import sys; print(sys.executable)"` → 应为 conda 环境 **`embodied-scene-agent`** 下的解释器（路径因机器而异）
- `conda list | grep -iE 'torch|vision|cuda|nvidia'`：见下表（与 `pip list` 一致，**无 conda-forge 的 pytorch 与 pip torch 双装**）。
- `pip list | grep -iE 'torch|vision|cuda|nvidia'`：同上。

### 结论

| 包 | 版本 | 来源 |
|----|------|------|
| torch | 2.11.0+cu128 | PyPI（PyTorch cu128 wheel） |
| torchvision | 0.26.0+cu128 | PyPI |
| nvidia-*-cu12 / cuda-toolkit 等 | 12.8 线 | PyPI 依赖 |

- **未发现**「conda 装一套 torch + pip 再装一套」的重复：`conda list` 中 torch/torchvision 均标记为 `pypi_0`。
- 先前日志中的 `libtorch_nvshmem.so` / `c10::MessageLogger` 类错误，典型原因是 **用户 site-packages（`~/.local`）或 `PYTHONPATH` 混入另一套 libtorch**。本环境 Python 3.12 下 `sys.path` 曾出现 `/opt/ros/foxy/...`（若该路径下存在旧扩展模块可能干扰）；训练/评测脚本已设置 **`PYTHONNOUSERSITE=1`**，避免加载 `~/.local` 中与 conda 不一致的二进制扩展。

### 验收（本机当日执行）

```text
torch 2.11.0+cu128
torch.cuda.is_available() == True
torchvision 0.26.0+cu128
cuda:0 上 torch.randn(2,3).cuda() 前向可执行
```

### 可复现策略（保持单一来源）

- 继续在 **`embodied-scene-agent`** 内仅通过 **PyTorch 官方 cu128 wheel** 维护 `torch` + `torchvision`（例如 `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128`），其余训练依赖仍走 `pip install -e ".[train]"`。
- 运行训练/评测时使用仓库脚本（已 export `PYTHONNOUSERSITE=1`）。
