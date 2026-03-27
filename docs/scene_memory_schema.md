# Scene Memory 规范（canonical）

**版本字符串**：`esa_sm/v1`（常量 `ESA_SCENE_MEMORY_SCHEMA_VERSION`）。

**契约 v2（对象字段别名 + 认知帧）**：见 [`docs/scene_memory_contract_v2.md`](scene_memory_contract_v2.md)（`ESA_SCENE_MEMORY_CONTRACT_V2`）。

## 1. 设计原则

- **对象级**：每个 `ObjectState` 对应一个实例；**canonical `object_id`** 在单帧内唯一，供 planner / verifier 引用。
- **类别与实例**：`class_name` / `category` 表示语义类别；`name` 为可读实例名；`aliases` 保存 benchmark 原始 id（如 CALVIN `uid`）。
- **状态**：`state_tags` 为 **小写 snake_case** 字符串列表（如 `open`, `closed`, `held`, `in_drawer`, `on_table`）。
- **来源**：`SceneMemory.source` 标明构建来源（如 `calvin_teacher`, `mock_teacher`）。

## 2. 核心类型

| 类型 | 说明 |
|------|------|
| `ObjectState` | `object_id`, `name`, `class_name`, `category`, `aliases`, `position`, `bbox`, `state_tags`, `visibility`, `confidence`, `metadata` |
| `RelationEdge` | `subject_id`, `object_id`, `RelationType`, `confidence` |
| `SceneMemory` | `objects`, `relations`, `frame_id`, `schema_version`, `timestamp_s`, `source`, `extra` |

## 3. JSON 与 JSON Schema

- **实例 JSON**：`SceneMemory.to_json_dict()`（Pydantic `model_dump(mode="json")`）。
- **JSON Schema（机器可读）**：`embodied_scene_agent.memory.schema.scene_memory_json_schema()` 返回 Pydantic 生成的 schema 字典。

## 4. 示例快照（节选）

见 `docs/examples/scene_memory.example.json`。

## 5. 兼容性

- 破坏性变更时需递增 `ESA_SCENE_MEMORY_SCHEMA_VERSION`（例如 `esa_sm/v2`），并在 `docs/` 与 `CHANGELOG`（若启用）中说明。
