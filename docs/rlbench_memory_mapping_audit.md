# RLBench observation → SceneMemory 映射审计

_状态：cognition 层桥接；**非**官方 RLBench benchmark。_

## 直接来自（或等价于）观测的字段

| 目标 | 来源 | 说明 |
|------|------|------|
| `gripper.position` | `Observation.gripper_pose[:3]` | 经 `numpy_observation_to_dict` 序列化 |
| `gripper` bbox | 由 position 派生 ± 固定边长 | 几何包络，**非** RLBench 原始 bbox |
| `gripper` `state_tags` | `gripper_open` 阈值 0.5 | 启发式 open/closed |
| `task_low_dim_state` 向量 | `Observation.task_low_dim_state` | 原样进入 dict；维度假设由任务决定 |

## Adapter 推断 / 合成（非观测直接字段）

| 目标 | 推断规则 | 风险 |
|------|-----------|------|
| `rlbench_target.position` | `task_low_dim_state[:3]` | **Reach 类**任务常见；OpenDrawer 等语义可能**不匹配** |
| `rlbench_target` 类别名 `target` | 固定 | 仅为 planner 占位 |
| `workspace` 桌台 | 固定原点大平面 bbox | 占位锚点，非仿真桌台 mesh |
| 关系 `gripper --near--> rlbench_target` | 总是写入 | **未**基于真实距离阈值 |
| 关系 `rlbench_target --on--> workspace` | 总是写入 | 拓扑简化 |

## 当前无真实来源的关系 / 对象

- 多物体、关节抽屉、门、杯具几何：**未**从 `misc` 或高维观测解析（本轮 smoke 关高维）。
- `misc` 字典：进入 `SceneMemory` metadata 路径有限（见 `observation_like_dict_to_scene_memory` 内 `metadata.misc`）。

## `predicted_memory` / 感知预测如何接 RLBench

- 未来可在 `build_cognitive_frame_from_observation_like` 之后插入 **perception 模块输出**，与 `MemorySource` 枚举对齐，将 `predicted_memory` 与 `teacher_state` 并列写入 episode log。
- 需单独约定：低维 `task_low_dim_state` 与各任务物体 grounding 的校准协议（否则保持 **fixture / qualitative** 声明）。

## 参考实现

- `src/embodied_scene_agent/envs/rlbench_adapter.py`：`numpy_observation_to_dict`, `observation_like_dict_to_scene_memory`
- Fixture：`tests/fixtures/rlbench_observation_like.json`
