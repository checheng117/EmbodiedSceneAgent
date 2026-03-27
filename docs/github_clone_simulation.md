# GitHub clone 模拟：「只有代码仓库」时会发生什么

_假设：在 A100 上全新 Linux，仅执行 `git clone` 得到本仓库（按当前 `.gitignore` 策略，**不含** data/raw、大 jsonl、checkpoints、experiments）。_

## 1. clone 后立刻可用的

- **全部 Python 包源码**与**契约测试**：`pip install -e ".[dev]"` 或 `pip install -e ".[train]"` 后，`pytest -q` 可在 **无 CALVIN 数据** 下通过绝大部分测试（与当前 CI 一致）。
- **Mock / 符号闭环**：`bash scripts/run_smoke_v0.sh`、`run_calvin_dev_smoke.sh`（fixture）、`run_calvin_minimal_loop_smoke.sh`（fixture）等，不依赖 `data/raw/calvin_official` 的 npz。
- **报告管线**：`python -m embodied_scene_agent.reporting.make_project_report` 可写 `results/reports/*`；若本地尚无 `results/experiments/`，JSON 中会如实反映 **not_run / missing**，路径为**相对仓库根**。
- **已随仓库的轻量快照**：`results/reports/`（若已提交）、`results/rlbench_*.json`（脱敏）、`docs/final_report_assets/`（若已提交）。

## 2. clone 后缺的（按类别）

| 缺失项 | 是否阻塞 | 说明 |
|--------|-----------|------|
| `data/raw/calvin_official` + debug 数据集 | **阻塞** debug 向量 E2 / hybrid / `build_calvin_debug_planner_data` | 需 `git clone --recurse-submodules` + `download_calvin_debug_data.sh` 或 rsync |
| `data/processed/**/*.jsonl` | **阻塞** 真实 planner SFT / `run_eval_base_vs_tuned`（除非改指向小 fixture） | 跑脚本重建或从 3090 scp/rsync |
| `results/checkpoints/.../best_lora` | **阻塞** base-vs-tuned **对比** | 需训练产出或拷贝 checkpoint |
| `results/experiments/*` | **不阻塞**代码；**影响**「最新 headline 数字」与 dashboard 中的强结果表 | 重跑 `run_ablation_e2*.sh`、`run_hybrid_*.sh` |
| `.env` 中 `HF_TOKEN` | **阻塞** 从 Hub 拉 Qwen | 在 A100 创建 `.env`（不提交） |
| `calvin_venv` | **不阻塞** pytest；**阻塞** **live** CALVIN probe（官方 Python 3.8 栈） | `bash scripts/setup_calvin_dev_env.sh` |

## 3. 哪些缺失只影响展示

- 缺少 `results/experiments/`：看板仍生成，但 E2/hybrid **strongest** 可能为「未运行」或沿用仓库内已提交的 JSON 快照叙述。
- 缺少 `results/demos/`：`make_demo_assets` 可再生成；`final_report_assets` 中部分 case 可能提示 missing（若依赖 demo JSON）。

## 4. README 是否足以补齐缺口

- **是（对主线）**：README 与 **`docs/github_a100_readiness_audit.md`** 已写明：官方仓库与 debug 下载、processed 数据重建或 rsync、HF token、7B 模板与 `train_planner_7b.sh` 的占位性质。
- **需人工再读**：`docs/calvin_official_setup_log.md`、`docs/calvin_env_factory_usage.md`（live 工厂）、`docs/training_run_log.md`（真实训练是否跑过以机器为准）。

## 5. 最小闭环 vs 全功能

- **最小**：clone → conda → `pip install -e ".[train]"` → `run_smoke_v0.sh` → `pytest -q`。
- **全功能（CALVIN debug 向量）**：在上述基础上 + official repo + debug zip + processed jsonl +（可选）checkpoint + HF token + 评测脚本链。
