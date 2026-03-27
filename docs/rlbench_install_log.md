# RLBench / PyRep / CoppeliaSim 安装与分层诊断（事实记录）

## 环境快照（自动探测，可随机器变化）

- **日期**: 2026-03-25（本轮更新）
- **结构化诊断落盘（real）**：`results/rlbench_stack_diagnosis.json`  
  - 生成：`bash scripts/diagnose_rlbench_stack.sh`（默认含 sim probe；仅 import/路径：`ESA_RLBench_DIAGNOSE_NO_SIM=1 bash scripts/diagnose_rlbench_stack.sh`）  
  - 或：`python -m embodied_scene_agent.evaluation.rlbench_smoke --diagnose` / `--diagnose --diagnose-no-sim`
- **字段摘要**：`python_executable`、`conda_prefix`、`pip_distribution_probe`（rlbench/pyrep）、`COPPELIASIM_ROOT`、`LD_LIBRARY_PATH_head`、`import_status`、`env_create_probe`、`reset_probe`、`deepest_reached_stage`、`blocker_summary`。
- **Python 探测**（仓库根目录 `PYTHONPATH=src`）:
  - `import rlbench` → **失败**（示例：`ModuleNotFoundError: No module named 'rlbench'`）
  - `import pyrep` → **失败**（`No module named 'pyrep'`）
- **环境变量**:
  - `COPPELIASIM_ROOT`：**未设置**（本轮）
  - `LD_LIBRARY_PATH`：**已设置**（含 CUDA / ROS 等路径；**不**等同于 CoppeliaSim 库已就绪）

## 本轮安装尝试（压缩阻塞层级）

| 步骤 | 结果 | 阻塞类型 |
|------|------|----------|
| `pip install 'rlbench>=1.2.0'` | **失败** | PyPI **无匹配发行版**（非编译错误） |
| `pip install git+https://github.com/stepjam/PyRep.git` | **失败** | **构建期** `RuntimeError: COPPELIASIM_ROOT not defined`（未进入动态库加载或 sim 启动） |

**结论（诚实）**：当前机器停在 **第 1 层（import / 包未安装）**；PyRep 的 **wheel 构建** 在缺少 `COPPELIASIM_ROOT` 时即失败，尚未到达「动态库找不到」或「simulator 启动」层级。

## 分层状态（与 `results/rlbench_dev_smoke.json` 对齐）

| 层 | 含义 | 本轮本机结果 |
|----|------|----------------|
| 1 | package import（`rlbench` / `pyrep`） | **blocked**（包未安装） |
| 2 | simulator locate（`COPPELIASIM_ROOT`、可执行文件） | **blocked**（根路径未设置）；`layer_status.simulator_locate=false` |
| 3 | env construct（`Environment` + `launch`） | **未尝试**（import 失败时跳过）；见 smoke `stages.sim_env_create` |
| 4 | task reset | **未尝试**；见 `stages.sim_reset` |
| 5 | observation capture（低维 dict） | **未达成**（依赖层 4） |
| 6 | scene memory mapping | **可用**（`observation_like` / fixture → `SceneMemory` + planner smoke） |

**结论（诚实）**：在 **fixture_file** 下 cognition 链（memory_bridge + planner_smoke）仍可跑通并落盘，**不是** RLBench 官方 benchmark 分数。

## 历史 pip / 构建尝试（摘要）

1. **`pip install rlbench>=1.2.0`** — PyPI 无匹配发行版（历史 + 本轮复现）。
2. **`pip install git+https://github.com/stepjam/PyRep.git`** — 构建需 `COPPELIASIM_ROOT` 指向本机 CoppeliaSim 安装树（本轮：构建脚本在 `get_requires` 阶段即报错）。

## 有 CoppeliaSim 时的最小步骤（用户侧）

1. 安装与 RLBench 文档匹配的 **CoppeliaSim EDU**。  
2. `export COPPELIASIM_ROOT=/path/to/CoppeliaSim`（并按官方说明配置 `LD_LIBRARY_PATH`）。  
3. `pip install git+https://github.com/stepjam/PyRep.git`  
4. `pip install git+https://github.com/stepjam/RLBench.git`  
5. `python -c "import rlbench; print('ok')"`  
6. `bash scripts/diagnose_rlbench_stack.sh` → 核对 `results/rlbench_stack_diagnosis.json`  
7. `bash scripts/run_rlbench_dev_smoke.sh`（默认 `--mode all` 可分层写 JSON）

## 代码与日志入口

- 分层 smoke：`src/embodied_scene_agent/evaluation/rlbench_smoke.py`（`--mode fixture_file|sim_import_only|sim_env_create|sim_reset|all`；`--diagnose`）
- 桥接实现：`src/embodied_scene_agent/envs/rlbench_adapter.py`（`build_rlbench_stack_diagnosis`, `diagnose_rlbench_stack`, `try_rlbench_env_launch_only`, `try_rlbench_reset_observation`）
- 输出：`results/rlbench_stack_diagnosis.json`、`results/rlbench_dev_smoke.json`，`results/episode_logs/rlbench_layered_smoke.json`，`results/demos/rlbench_*`
