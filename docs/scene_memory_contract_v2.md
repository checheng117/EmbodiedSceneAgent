# Scene memory contract v2（对象级 3D，与 blueprint 对齐）

本文件是 **逻辑契约**（`esa_sm_contract/v2`），**不破坏** 现有 JSONL / `esa_sm/v1` 序列化字段；代码真源见 `memory/schema.py`、`memory/cognitive_snapshot.py`。

## 1. 与 v1 的关系

- **v1（`SceneMemory`）**：`objects` 为 `dict[object_id, ObjectState]`，`relations` 为 `RelationEdge` 列表 — CALVIN / mock 主路径不变。
- **v2 契约**：在 v1 上**补字段与语义别名**，并引入 **认知帧信封** `CognitiveEpisodeFrame`（instruction / history / planner_output / failure_log 等与 planner 输入对齐）。

## 2. 对象字段（`ObjectState`）

| 契约名 | 代码字段 | 说明 |
|--------|----------|------|
| `object_id` | `object_id` | 实例主键 |
| `class_name` | `class_name` | 语义类 |
| `display_name` | `display_name` | 默认同 `name` 或 `object_id` |
| `position_3d` | `position` | 世界系 3D；JSON 可写 `position` 或 `position_3d`（builder 均支持） |
| `bbox_3d` | `bbox` | AABB 六元组；可写 `bbox` 或 `bbox_3d` |
| `state_tags` | `state_tags` | 离散状态 |
| `visibility` | `visibility` | [0,1] |
| `confidence` | `confidence` | [0,1] |
| `last_seen_step` | `last_seen_step` | 可选离散时刻 |

## 3. 关系

- 内部：`RelationEdge(subject_id, relation: RelationType, object_id)`。
- 报告 / 对外 tuple 视图：`(subject, relation, object)` — 见 `CognitiveEpisodeFrame.relations_tuple_view`。

## 4. 记忆来源

| 来源 | 枚举 | 说明 |
|------|------|------|
| Teacher-state | `MemorySource.TEACHER_STATE` | 当前 CALVIN / mock / RLBench stub 主路径 |
| Predicted | `MemorySource.PREDICTED` | 占位：`PredictedMemoryPlaceholder`（blueprint E3） |
| Hybrid | `MemorySource.HYBRID` | 预留 teacher + predicted 融合 |

## 5. 信封字段（单步认知上下文）

`CognitiveEpisodeFrame` 至少包含：`instruction`、`scene_memory`、`relations`（tuple 视图）、`history`、`failure_log`、可选 `planner_output`。

## 6. 真源与校验

- Pydantic：`SceneMemory`、`ObjectState`、`CognitiveEpisodeFrame`
- Builder：`SceneMemoryBuilder.from_teacher_payload`
- 单测：`tests/test_scene_memory.py`
