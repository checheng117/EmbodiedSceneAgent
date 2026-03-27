# 本地 CALVIN `PlayTableSimEnv` 工厂（显式配置）

本仓库**不**猜测 Hydra 配置或 `PlayTableSimEnv(...)` 的具体参数。你必须在本地提供一个 **可 import 的工厂函数**，通过环境变量交给 probe / minimal loop。

## 1. 环境变量

```bash
export ESA_CALVIN_ENV_FACTORY='my_python_module.my_file:make_calvin_env'
export PYTHONPATH=/path/to/parent_of_module:$PYTHONPATH
```

- 格式：**`模块路径:可调用对象名`**（必须含冒号）。
- 可调用对象**无参数**，返回已配置好的 env 实例（通常即 `PlayTableSimEnv`）。

### 1.1 官方仓库路径与 conda（推荐与上游 CALVIN 一致时）

| 变量 | 含义 |
|------|------|
| **`ESA_CALVIN_OFFICIAL_ROOT`** | 克隆的 **mees/calvin** 根目录。未设置时，探针/最小闭环脚本默认 `<repo>/data/raw/calvin_official`。 |
| **`ESA_CALVIN_ENV_SRC`** | **可选**：显式指定 `calvin_env` **仓库根**（含 `calvin_env/` 包与 `conf/`），优先级 **高于** `ESA_CALVIN_OFFICIAL_ROOT/calvin_env`。 |
| **`ESA_CALVIN_CONDA_ENV`** | **可选**：运行 probe / minimal loop 前 **`conda activate`** 的环境名（如 **`calvin_venv`**，Python 3.8）。未设置时脚本仍 `source scripts/conda_env.sh`（主环境 **`embodied-scene-agent`**）。 |

**路径解析顺序**（`calvin_hydra_factory.py`）：`ESA_CALVIN_ENV_SRC` → `ESA_CALVIN_OFFICIAL_ROOT/calvin_env` → `<repo>/data/raw/calvin_official/calvin_env` → 已安装的 `calvin_env`。无匹配且未安装包时 import 失败；**无**静默回退到不透明旧路径。

**本仓库默认（已安装 `calvin_env` 时）**：`scripts/run_calvin_live_probe.sh` 与 `scripts/run_calvin_minimal_loop_smoke.sh` 在未设置该变量时会使用：

```text
embodied_scene_agent.envs.calvin_hydra_factory:make_calvin_env
```

实现见 `src/embodied_scene_agent/envs/calvin_hydra_factory.py`（基于包内 `conf/config_data_collection.yaml` + `hydra.compose`，非手写假参数）。若需自定义场景或 GUI，请自行 `export ESA_CALVIN_ENV_FACTORY=...` 覆盖。

## 2. 推荐做法

1. 复制 `examples/calvin_env_factory.py.example` 的思路，在本机任意目录创建 `calvin_env_local.py`（**勿提交含密钥/绝对路径的版本**）。
2. 在 `make_calvin_env()` 内使用**你**安装 CALVIN 时的官方方式实例化环境（Hydra、`hydra.initialize`、项目内 wrapper 等）。
3. 将父目录加入 `PYTHONPATH`，并设置 `ESA_CALVIN_ENV_FACTORY`。

## 3. 与 probe 配合

```bash
bash scripts/run_calvin_live_probe.sh
# 可选：reset 后再打一步零动作接口烟测
bash scripts/run_calvin_live_probe.sh --step-smoke
```

输出 JSON 中含 `factory_resolve`（解析状态）与 `calvin`（import / reset / summary）。**失败时**会带 `import_error` / `instantiate_error` / `reset_error` 等字段，**不会**伪装成功。

## 4. 与 minimal loop 配合

```bash
export ESA_CALVIN_ENV_FACTORY='...'
bash scripts/run_calvin_minimal_loop_smoke.sh --try-local-factory --live-action-strategy symbolic_fallback
```

- `symbolic_fallback`：使用 **live reset 后的观测** 建 SceneMemory，但技能仍为 **符号** teacher 更新（trace 标明，不冒充物理执行）。
- `live_zero_action_smoke`：每步调用 `env.step`（默认全零向量），仅验证接口与 teacher 刷新。

## 5. 加载实现位置

- `src/embodied_scene_agent/envs/calvin_factory_load.py`：`resolve_calvin_env_factory_from_env()`。
