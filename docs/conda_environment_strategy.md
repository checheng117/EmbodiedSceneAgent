# Conda 环境策略（唯一真源）

## 环境名

- **当前统一名称**：`embodied-scene-agent`（定义在仓库根目录 `environment.yml` 的 `name:` 字段）。
- **与 `pyproject.toml` 的 `name`（同为 `embodied-scene-agent`）**：后者为 **pip 分发包名**；conda 环境名与之一致，便于团队口头与文档统一。
- **命名理由**：与现有机器上已创建的开发环境同名，避免维护两套名称；所有脚本通过 `resolve_conda_env.sh` 读取 `name:`，不硬编码。

## 为何不在脚本里硬编码环境名？

- 环境名**只应**出现在 `environment.yml` 的 `name:`。
- Shell 通过 `scripts/resolve_conda_env.sh` 解析该字段，导出 `ESA_CONDA_ENV_NAME`。
- `scripts/conda_env.sh` 使用 `ESA_CONDA_ENV="${ESA_CONDA_ENV:-$ESA_CONDA_ENV_NAME}"`，允许单次会话覆盖。

## Python 版本

- **当前锁定**：`python=3.12.*`（conda-forge），与团队默认 `embodied-scene-agent` 环境一致。
- **下界**：本仓库 `requires-python >=3.10`（`pyproject.toml`）。
- **说明**：若个别依赖（如旧版仿真轮子）在 3.12 上受限，应在 issue/本文件中记录，并优先考虑上游修复或 pin；不再维护单独的 `esa-py310` 名称。

## 多环境扩展（若未来冲突）

若出现「EmbodiedSceneAgent 轻量开发」与「完整 CALVIN 仿真+训练」依赖冲突，建议：

1. **保留** `embodied-scene-agent` 用于本仓库核心开发与默认文档。
2. 另建独立环境（如 `esa-calvin-full`），在 `docs/calvin_env_factory_usage.md` 中说明仅在该环境下运行重依赖仿真。
3. 不在业务代码中写死环境名；通过 `ESA_CONDA_ENV` 或用户 shell profile 切换。

## 常用命令

```bash
bash scripts/setup_env.sh          # create/update env from environment.yml + pip install -e ".[dev]"
source scripts/conda_env.sh        # 在其它脚本中已使用；交互式可: conda activate embodied-scene-agent
```

（激活名以 `environment.yml` 为准；若改名，请只改 YAML。）
