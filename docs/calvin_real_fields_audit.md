# CALVIN 真实字段审计（源码级）

**范围**：基于公开仓库 **mees/calvin_env**（仿真）与 **mees/calvin**（评测脚本）的 **在线源码阅读**（未在本机 import `calvin_env` 运行验证）。  
**原则**：区分 **已验证（有源码行号/函数可指）**、**推测（由结构推断）**、**未确认（本仓库尚未接真 env）**。

---

## 1. 已验证字段（来自 `PlayTableSimEnv`）

**来源**：`calvin_env/envs/play_table_env.py`（`mees/calvin_env`，`main` 分支，2025-03 左右快照）。

### 1.1 `get_obs()` 返回的 observation 顶层键

| 键 | 类型（文档描述） | 来源 |
|----|------------------|------|
| `rgb_obs` | `dict`，键为 `rgb_{camera_name}` | `get_camera_obs()` |
| `depth_obs` | `dict`，键为 `depth_{camera_name}` | `get_camera_obs()` |
| `robot_obs` | `numpy` 向量 | `robot.get_observation()` 第一个返回值 |
| `scene_obs` | `numpy` 向量 | `scene.get_obs()` |

`get_obs()` 实现：`obs = {rgb_obs, depth_obs}; obs.update(get_state_obs())`，`get_state_obs` 写入 `robot_obs` 与 `scene_obs`。

### 1.2 `get_state_obs()` / `robot` 侧（`Robot.get_observation()`）

**来源**：`calvin_env/robot/robot.py` — `get_observation()`。

- **返回值 1**：`robot_state` 一维 `ndarray`，由以下按顺序拼接：
  - TCP 位置 3 维
  - TCP 朝向：四元数 **4** 维或欧拉 **3** 维（由 `euler_obs` 配置决定）
  - `gripper_opening_width` 标量（两指关节位置之和）
  - 臂关节角（`arm_joint_ids` 长度，典型 7）
  - `gripper_action` 标量（-1 / 1）
- **返回值 2**：`robot_info` **dict**，至少包含键：
  - `tcp_pos`, `tcp_orn`, `gripper_opening_width`, `arm_joint_states`, `gripper_action`, `uid`, `contacts`（PyBullet `getContactPoints`）

`get_observation_labels()` 给出 `robot_obs` 各维语义标签（如 `tcp_pos_x`…、`gripper_opening_width`、`robot_joint_*`、`gripper_action`）。

### 1.3 `scene_obs` 向量结构

**来源**：`calvin_env/scene/play_table_scene.py` — `get_obs()`。

`scene_obs` 为 **一维 `np.concatenate`**，顺序为：

1. 各 `door.get_state()`（标量浮点）
2. 各 `button.get_state()`
3. 各 `switch.get_state()`
4. 各 `light.get_state()`
5. 各 `movable_object.get_state()`（位置+朝向拼接）

**注意**：具体 **长度与顺序依赖场景 Hydra 配置**（门/按钮/可动物体数量）。本仓库 **未** 在运行时对齐某一固定 `scene.yaml` 的索引 → 对「第 i 维对应哪个物体」标记为 **未确认（依赖配置）**。

### 1.4 `get_info()`（`use_scene_info=True` 时）

**来源**：`play_table_env.py` — `get_info()`；`play_table_scene.py` — `get_info()`。

- 始终包含：`robot_info`（同上）。
- 若 `use_scene_info`：`scene_info` = `scene.get_info()`，结构为嵌套 dict：
  - `fixed_objects`, `movable_objects`, `doors`, `buttons`, `switches`, `lights`
  - 各子键为 **对象名** → 该对象的 `get_info()` 结果。

**可移动物体 `MovableObject.get_info()`（已验证键）**：

- `current_pos`, `current_orn`, `current_lin_vel`, `current_ang_vel`, `contacts`, `uid`

**门/抽屉关节 `Door.get_info()`（已验证）**：

- `{"current_state": float}`（关节位置标量）

### 1.5 `reset(robot_obs=None, scene_obs=None)`

**来源**：`play_table_env.py`。

- 调用 `scene.reset(scene_obs)`、`robot.reset(robot_obs)`，再 `stepSimulation`，**返回 `get_obs()`**（与 `step` 后 observation 同形）。

---

## 2. 语言指令 / subtask（评测侧，非 env.get_obs）

**来源**：`mees/calvin` — `calvin_models/calvin_agent/evaluation/evaluate_policy.py` — `rollout()`。

- 每个子任务关键字 `subtask` 来自 **预定义序列**；**自然语言** 来自 `val_annotations[subtask][0]`，配置文件如 `conf/annotations/new_playtable_validation.yaml`。
- **结论（已验证）**：**instruction 字符串不来自 `PlayTableSimEnv.get_obs()`**；须由 **数据集/评测配置或上层 wrapper** 与 observation **并排**传入认知层。

---

## 3. 推测字段（结构合理，但未在本仓库用真 env 跑通）

| 主题 | 说明 |
|------|------|
| `gripper_open` 布尔 | 可由 `gripper_opening_width` 与阈值比较推导；**阈值依赖机器人与标定** → 推测。 |
| `drawer_open` | `Door.get_info()["current_state"]` 相对 `initial_state`（在 Door 对象内，**不在** `get_info()` 返回中）或固定阈值；**未在审计源码中见 `initial_state` 导出** → 推测/需读 scene yaml。 |
| `held_object_uid` / `in_drawer` | 无官方布尔字段；可能由 `contacts` + 几何推理或任务 oracle 得到 → 推测，**本仓库 mapper 默认不填或占位**。 |

---

## 4. 未确认 / 本阶段不承诺

- 具体 **场景配置** 下 `scene_obs` 各切片与物体名的 **索引映射表**。
- 多环境（A/B/C/D）下 **物体命名** 与 **CALVIN 任务定义** 的一一对应（需结合 `mees/calvin` task yaml）。
- 在本机 **import calvin_env 并成功渲染** 的观测字典 **与文档逐字段对照**（运行级验证）。

---

## 5. 对 `CalvinEnvAdapter` / `calvin_teacher_v0` 的含义

- **真实路径**：应使用 `get_obs()` + `get_info()`（建议 `use_scene_info=True`），经 **`calvin_field_mapper`** 集中转为 `calvin_teacher_v0`，再交给 `CalvinTeacherStateAdapter` → `SceneMemory`。
- **Fixture 路径**：继续用于无仿真时的 **结构回归** 与 **符号执行** 最小闭环。

---

## 6. 参考链接（源码）

- `https://github.com/mees/calvin_env/blob/main/calvin_env/envs/play_table_env.py`
- `https://github.com/mees/calvin_env/blob/main/calvin_env/robot/robot.py`
- `https://github.com/mees/calvin_env/blob/main/calvin_env/scene/play_table_scene.py`
- `https://github.com/mees/calvin_env/blob/main/calvin_env/scene/objects/movable_object.py`
- `https://github.com/mees/calvin_env/blob/main/calvin_env/scene/objects/door.py`
- `https://github.com/mees/calvin/blob/main/calvin_models/calvin_agent/evaluation/evaluate_policy.py`
