# CALVIN 接入方案（最小 teacher-state ingestion）

**范围**：本文档描述 **EmbodiedSceneAgent** 如何将 CALVIN **风格**的仿真/teacher 信息接入到 canonical `SceneMemory`，**不**假设已接入官方评测协议或完整 observation 定义。

**非目标**：不在此阶段承诺官方 benchmark 可复现分数、不覆盖 RLBench/VLABench。

---

## 1. 当前阶段目标

- **最小 teacher-state ingestion**：从结构化 dict（或本仓库提供的 **mock JSON**，明确标注为结构模拟）构造 `SceneMemory`。
- **与现有 v0 规则规划器对齐**：canonical 物体 id（`drawer`, `red_block`, `table`, `gripper`）与 `state_tags`（`open`/`closed`, `held`, `in_drawer`, `on_table`）与 mock 闭环一致，便于同一套 `RuleBasedPlanner` / `StateDiffVerifier` 逐步复用。

---

## 2. 计划使用的 observation / state 字段（分层）

### 2.1 真实 CALVIN 接入时（未来）

| 来源（预期） | 用途 |
|--------------|------|
| 多相机 RGB（及可选深度） | **v1+** 感知；**不在本阶段** 写入 SceneMemory（无 RGB-D predictor）。 |
| `robot_obs` / 末端位姿 / 夹爪 | 推断 **held**、可达性（后续）。 |
| 仿真器 **scene / object pose** 或 **info** 中的 teacher 字段 | **teacher-state** 主来源，映射到对象位置与关节/抽屉状态。 |

### 2.2 本仓库 v0 开发路径（当前）

使用 **`calvin_teacher_v0`** 嵌套字典（或等价的 `scene_objects` + `robot` 顶层），字段包括：

| 字段 | 说明 |
|------|------|
| `frame_id` | 可选，字符串帧 id |
| `timestamp_s` | 可选，仿真/时间戳 |
| `robot.held_object_uid` | 可选，被抓取物体的 uid（与 `scene_objects` 对齐） |
| `robot.gripper_open` | 可选，布尔 |
| `scene_objects[]` | 列表；每项含 `uid`, `category`, `position` [x,y,z]，以及 `drawer_open` / `in_drawer` / `held` 等布尔 |

**明确不做**：不从不含 teacher 的纯 `rgb_obs` 推断场景结构；若仅传入 `rgb_obs`，`CalvinTeacherStateAdapter` 会 **显式报错** 并提示注入 teacher bundle。

---

## 3. 到 canonical SceneMemory 的映射

- **实例 id**：经 `_canonical_id` 将 CALVIN uid / category 映射到 **drawer / red_block / table / gripper**（可扩展表见 `perception/calvin_teacher.py`）。
- **ObjectState**：`object_id` 为 canonical id；`aliases` 保留原始 `uid`；`class_name` / `category` 来自 teacher。
- **state_tags**：
  - 抽屉：`open` 或 `closed`
  - 块：`on_table` / `held` / `in_drawer`（与 robot 的 `held_object_uid` 对齐后做互斥修正）
- **RelationEdge**：
  - 块在桌上：`red_block` → `on` → `table`
  - 块在抽屉内：`red_block` → `in` → `drawer`
  - 块被抓：`red_block` → `on` → `gripper`，并增加 `gripper` 物体节点

---

## 4. v0 必须支持的对象与关系

| 对象 | 必须 state_tags / 语义 |
|------|------------------------|
| `table` | `static` |
| `drawer` | `open` 或 `closed` |
| `red_block` | `on_table` / `held` / `in_drawer`（互斥） |
| `gripper` | 仅在被抓取时出现；`end_effector` |

| 关系 | 条件 |
|------|------|
| `on` | 块在桌上或附着在 gripper |
| `in` | 块在抽屉内 |

---

## 5. 暂不支持 / TODO

- 官方 `calvin_env` 逐步 `reset/step/get_obs` 全链路。
- 与 CALVIN 数据集 HDF5 字段 1:1 对齐。
- 开放词表物体与细粒度部件分割。
- 从 RGB-D 预测 SceneMemory。

---

## 6. Mock 样本位置

- `tests/fixtures/calvin_mock_observation.json`：**结构模拟**，非官方完整格式（见文件内 `_meta.disclaimer`）。
