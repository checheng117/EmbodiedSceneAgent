# GitHub-ready / A100-ready 审计

_日期：2026-03-27。范围：`.gitignore`、密钥与绝对路径、脚本可移植性、README 与 clone 后缺口。_

## A. Git 跟踪状态审计

### A.1 审计时工作区状态（说明）

执行本审计时，`git ls-files` 在部分环境中**仅**列出 `LICENSE`、`README.md`（历史提交极小），其余目录处于「待首次 `git add`」状态。**不代表**应忽略 `src/` / `docs/` 等；而是提醒：**push 前必须**将代码与文档纳入版本控制，并再次运行：

```bash
git status
git check-ignore -v <path>   # 对关键路径抽样
```

### A.2 意图：**应被跟踪**

| 类别 | 路径模式 |
|------|-----------|
| 代码与入口 | `src/**`、`pyproject.toml` |
| 脚本与配置 | `scripts/**`、`configs/**` |
| 测试 | `tests/**` |
| 环境与依赖声明 | `environment.yml`、`requirements/**` |
| 文档与展示 | `docs/**`（含 `final_report_assets`、`project_page`、`figures`、`tables` 等） |
| 示例 | `examples/**`、`demos/**`（体量小） |
| 轻量报告 | `results/reports/**`、`results/final_report_assets/**` |
| RLBench 快照（已脱敏） | `results/rlbench_dev_smoke.json`、`results/rlbench_stack_diagnosis.json` |
| 可选叙事指针 | `results/eval/planner_base_vs_tuned/metrics.json`、`summary.md` |
| 占位 | `data/raw/.gitkeep`、`data/processed/.gitkeep`、`results/.gitkeep` |

### A.3 意图：**必须忽略（勿提交）**

| 类别 | 路径模式 | 原因 |
|------|-----------|------|
| 密钥 | `.env`、`.env.*` | 含 `HF_TOKEN` 等 |
| 缓存 | `.hf_cache/`、`__pycache__/`、`.pytest_cache/` | 体积大、机器相关 |
| 权重 | `*.pt`、`*.bin`、`*.safetensors` | 体积极大 |
| 上游数据与仓库 | `data/raw/**` | 官方 CALVIN + debug 数据集；应 clone/下载 |
| 大型训练 JSONL | `data/processed/**/*.jsonl` | 可达数十 MB～百 MB+ |
| Checkpoints | `results/checkpoints/**` | 大、且应独立备份 |
| 实验与演示产物 | `results/experiments/**`、`results/demos/**` | 可复现生成 |
| 归档与日志 | `results/archive/**`、`results/logs/**` | 过程性 |
| 本地探针 JSON | `results/calvin_live_probe_summary.json`、`results/v0_mock_summary.json` | 机器相关 |
| eval 大文件 | `results/eval/planner_base_vs_tuned/per_sample_results.jsonl` 等 | 由父目录规则忽略 |

### A.4 误伤检查

- **`scripts/`、`configs/`、`docs/`、`tests/`、`src/`** 未被忽略。
- **`results/reports/**`** 通过 `!` 规则**显式取消忽略**（与 `results/**` 子目录白名单配合）。
- **`docs/final_report_assets/**`** 在 `docs/` 下，**正常跟踪**。

### A.5 已被跟踪但「不应存在」的内容

- 当前未发现已提交进 Git 的 `.env` 或 checkpoint（历史提交仅 LICENSE/README 快照）。
- 若曾误提交大文件，需用 `git rm --cached` + **Git LFS** 或从历史上清除（本审计未执行历史改写）。

---

## B. `.gitignore` 审计结论

- **合理**：密钥、HF 缓存、原始数据、`jsonl`、checkpoints、实验目录、archive、日志。
- **显式白名单**：`results/reports/**`、`results/final_report_assets/**`、根下两个 `rlbench_*.json`、`results/eval/planner_base_vs_tuned/metrics.json` 与 `summary.md`。
- **可选后续**：若希望 **完全不提交** `results/eval`，可删除对应 `!` 规则（当前为保留轻量 proxy 叙事）。

---

## C. Secret / 绝对路径审计

### C.1 扫描项

已检索：`HF_TOKEN`、`HUGGING_FACE_HUB_TOKEN`、`/home/`、`~/.cache`、`COPPELIASIM_ROOT` 等。

### C.2 修复摘要（本次）

| 区域 | 处理 |
|------|------|
| `make_project_report` / `build_report_payload` | 对外 JSON 中的路径改为**相对仓库根**（含 `run_meta` 内 `train_jsonl` 等） |
| `eval_planner_models.py` | `summary.md` 中 eval / LoRA 路径改为相对仓库根 |
| `rlbench_smoke.py` | fixture 路径写入 smoke JSON 时使用 `rel_repo_path` |
| `results/rlbench_dev_smoke.json` | 重新生成；`LD_LIBRARY_PATH_head` 在提交快照中脱敏 |
| `results/rlbench_stack_diagnosis.json` | 重新生成；`python_executable` / `conda_prefix` / `LD_LIBRARY_PATH_head` 脱敏 |
| 若干 `docs/*.md` | 去掉或泛化本机绝对路径（如 `calvin_live_validation_results.md`、`torch_env_repair_log.md`） |
| `build_final_report_assets.py` | `artifact_index` / `reproducibility` 不再写入绝对 `root` 字符串 |

### C.3 代码与脚本

- **`scripts/`**：未发现硬编码 `/home/...`；均通过 `ROOT="$(cd ...)"` 推导仓库根。
- **测试**：`tests/test_env_utils.py` 使用**临时目录**与占位 token，无真实密钥。

---

## D. A100 可迁移性审计

| 项 | 结论 |
|----|------|
| 子模块 | 本仓库**无** git submodule；官方 CALVIN 由文档约定 **clone 到 `data/raw/calvin_official`** |
| 缺数据时 smoke | `run_smoke_v0.sh`、多数 **pytest** 可不依赖 CALVIN |
| 训练脚本 | `scripts/train_planner_7b.sh` 为**模板**（默认 `exit 0`）；README 已说明需接真实 `run_planner_sft` |
| 报告 | `make_project_report` 在缺 `experiments/` 时仍可生成结构化「未运行」状态（路径已为相对路径） |

---

## E. 本次实施的修复清单

1. **重写 `.gitignore`**：显式忽略大数据/权重/实验目录，白名单轻量 `results/` 子集与部分 `eval` 文件。
2. **新增 `.gitattributes`**：`text=auto eol=lf`，`*.sh`/`*.json`/`*.svg` 统一 LF。
3. **`paths.rel_repo_path` + `make_project_report` / `eval_planner_models` / `rlbench_smoke`**：减少绝对路径泄漏。
4. **重新生成并脱敏** `results/rlbench_*.json`。
5. **文档去本地化路径** + **`build_final_report_assets`** 生成器去绝对路径。
6. **README**：增加 GitHub 边界、环境变量表、**Start here on A100**、指向本审计与 clone 模拟文档。
7. **运行** `make_project_report` + `build_final_report_assets.sh` 刷新报告与 `docs/final_report_assets`。

---

## F. push 前建议命令（维护者）

```bash
git add -A
git status
git diff --cached --stat
# 抽样：确保无 .env、无 *.safetensors、无 data/raw 大目录
pytest -q
```
