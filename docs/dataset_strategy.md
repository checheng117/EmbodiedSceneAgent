# 数据策略

## 1. 目录约定

| 路径 | 用途 |
|------|------|
| `data/raw/` | 原始 benchmark 导出、原始日志 |
| `data/processed/` | 清洗后中间表 |
| `data/scene_memory/` | teacher-state 或预测得到的 memory 快照（JSON） |
| `data/planner_sft/` | Planner SFT 样本（JSONL/JSON） |
| `data/verifier_labels/` | Verifier 监督或规则打标 |

## 2. Planner SFT 样本（统一格式）

单条样本建议字段：

```json
{
  "id": "optional",
  "instruction": "自然语言任务",
  "scene_memory": { },
  "history": ["子目标或步骤摘要"],
  "failure_log": [],
  "output": {
    "task": "normalized_task_id",
    "subgoal": "...",
    "target_object": "object_id_or_name",
    "skill": "grasp",
    "success_check": "条件描述或表达式占位",
    "fallback": "...",
    "reasoning": null,
    "confidence": null
  }
}
```

构造方式（蓝图）：从演示或 rollout **切分**为「当前状态 → 下一步子任务」，提高样本密度。

## 3. Verifier 样本格式

```json
{
  "before_state": { },
  "subgoal": "...",
  "after_state": { },
  "label": "success | fail",
  "fail_type": "precondition_unsatisfied | ... | null"
}
```

## 4. 阶段策略

- **阶段一**：teacher-state bootstrapping，强调 schema 稳定与可复用。
- **阶段二**：混入 predicted memory，对齐同一 schema。
