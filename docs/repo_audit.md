# 仓库审计报告（EmbodiedSceneAgent）

**日期**：2025-03-22  
**依据**：《EmbodiedSceneAgent_Project_Blueprint_CheCheng.docx》  
**审计范围**：本仓库根目录（含 `pyproject.toml`）当前快照

## 1. 当前已有目录与文件

| 路径 | 说明 |
|------|------|
| `README.md` | 仅一行标题，无工程说明 |
| `LICENSE` | 许可证文件 |
| `docs/EmbodiedSceneAgent_Project_Blueprint_CheCheng.docx` | 项目蓝图（设计权威来源） |
| `.git/` | Git 元数据 |

**结论**：仓库处于**近乎空白**状态，无 `pyproject.toml`、`src/`、`configs/`、`tests/`、`scripts/` 等研究工程结构。

## 2. 可复用内容

- **蓝图文档**：完整定义六段式流水线、benchmark 策略（CALVIN 主、RLBench/VLABench 辅助）、算力分工（3090 开发 / A100 7B 终测）、模块职责与数据策略——作为后续目录与接口设计的最高优先级依据。
- **LICENSE**：保留，无需替换除非项目方另有要求。

## 3. 与 blueprint 的冲突

- **无代码冲突**：当前无实现，不存在逻辑冲突。
- **README 占位**：与蓝图要求的「旗舰级对外叙事」不一致，需重写。

## 4. 缺失模块（相对 blueprint 附录结构）

- `pyproject.toml`、依赖管理（`requirements/` 或可选 lock）
- `configs/{planner,verifier,experiment,dataset}`
- `data/{raw,processed,scene_memory,planner_sft,verifier_labels}` 及占位说明
- `src/` 下 `memory`, `perception`, `planner`, `skills`, `verifier`, `envs`, `training`, `evaluation`, `visualization`, `utils`
- `scripts/`（setup、smoke、数据构造、训练、评测入口）
- `tests/`（schema、闭环 smoke）
- `docs/` 除 blueprint 外的系统设计、契约、路线图等
- `results/`、`demos/`（目录与最小示例）

## 5. 需要新增的内容

1. **可安装 Python 包**（建议包名 `embodied_scene_agent`，源码置于 `src/embodied_scene_agent/`，与 blueprint 中 `src/memory/` 等**一一对应**为子包，避免顶层包名 `memory` 与 PyPI 冲突）。
2. **v0 最小闭环**：teacher-state → scene memory → rule planner → skill executor → verifier → replanner → episode trace（Mock 环境可跑通）。
3. **配置系统**：YAML + Pydantic/dataclass 加载与校验。
4. **脚本**：至少 `run_smoke_v0.sh` 可真实执行。
5. **测试**：核心 schema、memory、verifier、smoke v0。

## 6. 需要重构的内容

- **不适用**：无历史代码需重构。后续若在单文件脚本中堆积逻辑，应逐步迁入 `src/` 模块。

## 7. 建议保留的内容

- `docs/*.docx` 蓝图原文。
- `LICENSE`。
- Git 历史（不强制重写）。

## 8. 目标仓库结构（落地版）

在 blueprint 附录基础上，将 Python 包集中为 `src/embodied_scene_agent/`，其余顶层目录与 blueprint 一致：

```
EmbodiedSceneAgent/
├── README.md
├── pyproject.toml
├── requirements/
│   ├── base.txt
│   └── dev.txt
├── configs/
│   ├── planner/
│   ├── verifier/
│   └── experiment/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── scene_memory/
│   ├── planner_sft/
│   └── verifier_labels/
├── src/
│   └── embodied_scene_agent/
│       ├── memory/
│       ├── perception/
│       ├── planner/
│       ├── skills/
│       ├── verifier/
│       ├── envs/
│       ├── training/
│       ├── evaluation/
│       ├── visualization/
│       ├── utils/
│       └── cli/
├── scripts/
├── docs/
├── demos/
├── results/
└── tests/
```

## 9. 下一步行动（与本轮交付对齐）

1. 补齐 `docs/system_overview.md`、`module_contracts.md`、`development_roadmap.md` 等设计文档。
2. 实现对象级 scene memory、teacher-state adapter、planner/skills/verifier/replanner 与 Mock 环境闭环。
3. 添加配置、脚本、测试与旗舰风格 `README.md`。

---

*本文件为 Phase 1 审计产物；后续架构变更应在此或 `docs/system_overview.md` 中同步说明。*
