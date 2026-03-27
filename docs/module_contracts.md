# 模块契约（Module Contracts）

本文档定义核心模块的输入/输出、数据格式、依赖与不变量；实现以 `embodied_scene_agent` 包内类型为准。

## 1. Scene Memory（`memory`）

### 1.1 类型

- **`ObjectState`**：单物体；字段包括 `object_id`（canonical 实例 id）、`name`、`class_name`、`category`（语义类）、`aliases`（benchmark 原始 id）、位置、`bbox`、`state_tags`（小写 snake_case）、`visibility`、`confidence`、`metadata` 等。
- **`RelationEdge`**：有向关系边；`subject_id`、`object_id`、`relation`（枚举）、可选 `confidence`。
- **`SceneMemory`**：容器；`objects`、`relations`、`frame_id`、`schema_version`（默认 `esa_sm/v1`）、`timestamp_s`、`source`、`extra`。

规范说明与 JSON 示例见 `docs/scene_memory_schema.md`、`docs/examples/scene_memory.example.json`；JSON Schema 可通过 `scene_memory_json_schema()` 导出。

### 1.2 输入 / 输出

| 组件 | 输入 | 输出 |
|------|------|------|
| `SceneMemoryBuilder` | teacher-state 字典或已解析物体列表 | `SceneMemory` |

### 1.3 不变量

- `object_id` 在单帧 memory 内唯一。
- 关系边引用的 `subject_id` / `object_id` 必须存在于 `objects`（或显式标记为外键占位，见实现注释）。

### 1.4 错误处理

- 未知字段：perception 层应记录于 `metadata`，不静默丢弃关键安全信息。
- 解析失败：抛出 `ValueError` 并附带原始 payload 摘要（避免日志泄露过大二进制）。

---

## 2. Perception / Teacher-state（`perception`）

### 2.1 `BaseTeacherStateAdapter`

- **输入**：`instruction: str`，`state: dict[str, Any]`（仿真器/benchmark 原始状态）
- **输出**：`SceneMemory`
- **依赖**：`SceneMemoryBuilder`

### 2.2 `CalvinTeacherStateAdapter`

- **输入**：含 `calvin_teacher_v0`（推荐）或等价 `scene_objects` + `robot` 的 teacher bundle；**不接受**仅含 `rgb_obs` 而无 teacher 的观测（显式报错）。
- **输出**：`SceneMemory`（`source` 为 `calvin_teacher`）
- **字段契约**：见 `docs/calvin_adapter_plan.md`。

### 2.3 错误处理

- 缺少必需键：抛出 `ValueError` 或返回带 `confidence=0` 的空物体并记录（由具体适配器策略决定；Mock 适配器采用严格模式便于测试）。

---

## 3. Planner（`planner`）

### 3.1 `PlannerInput`

- `instruction: str`
- `scene_memory: SceneMemory`（可序列化为 JSON）
- `history: list[str]`（已完成子目标或步骤摘要）
- `failure_log: list[str]`（可选）

### 3.2 `PlannerOutput`（结构化）

| 字段 | 说明 |
|------|------|
| `task` | 任务名或规范化 id |
| `subgoal` | 当前子目标描述 |
| `target_object` | 目标物体 id 或名称 |
| `skill` | 技能名（与 `SkillRegistry` 对齐） |
| `success_check` | 可解析的成功条件描述（v0 为字符串；后续可收紧为表达式） |
| `fallback` | 失败时建议 |
| `reasoning` | 可选 |
| `confidence` | 可选 |

### 3.3 依赖

- 仅依赖 `memory` 与工具；**不**直接依赖仿真器。

### 3.4 错误处理

- JSON 解析失败：由 `serialization` 层捕获并包装为 `ValueError`；LLM planner 应支持重试/回退模板（TODO）。

---

## 4. Skills（`skills`）

### 4.1 `SkillContext`

- 环境句柄、`target_object_id`、`planner_output` 引用、`params` 等。

### 4.2 `SkillResult`

- `success: bool`、`message: str`、`delta: dict`（环境相关增量）

### 4.3 `SkillExecutor`

- **输入**：`skill_name`, `context`
- **输出**：`SkillResult`
- **不变量**：技能名必须注册；未注册抛 `KeyError`。

---

## 5. Verifier（`verifier`）

### 5.1 `VerificationResult`

- `success: bool`
- `failure_type: FailureType | None`
- `should_replan: bool`
- `details: str`

### 5.2 `FailureType`（taxonomy）

包含但不限于：`target_not_found`、`wrong_object_grounded`、`precondition_unsatisfied`、`action_no_effect`、`blocked_or_collision`、`occlusion_or_low_confidence`、`unknown_failure`。

### 5.3 `BaseVerifier`

- **输入**：前状态 memory、后状态 memory、当前 `PlannerOutput`（至少 subgoal/skill/target）
- **输出**：`VerificationResult`

---

## 6. Replanner（`replanner`）

### 6.1 输入

- `instruction: str`
- `history: list[str]`
- `scene_memory: SceneMemory`
- `verification: VerificationResult`
- 可选：`previous_plan: PlannerOutput`

### 6.2 输出

- 新的 `PlannerOutput`（或等价结构化对象），字段与 planner 输出 schema 一致。

### 6.3 不变量

- 不应默认清空 `history`；应追加本轮尝试摘要。

---

## 7. Environments（`envs`）

### 7.1 `BaseEmbodiedEnv`

- `reset(instruction) -> dict`：返回初始观测/teacher-state
- `step(action) -> dict`：底层步进（可选）
- `get_teacher_state() -> dict`：用于 memory 构建

### 7.2 CALVIN / RLBench / VLABench

- 当前阶段：**接口 + 占位实现**；真实数据集/仿真连接在后续 milestone 接入。

---

## 8. 训练与数据（占位契约）

- **Planner SFT 样本**：`instruction`、`scene_memory`、`history`、`output`（subgoal/target/skill/check/fallback）
- **Verifier 样本**：`before_state`、`subgoal`、`after_state`、`label`、`fail_type`

详见 `docs/dataset_strategy.md`。
