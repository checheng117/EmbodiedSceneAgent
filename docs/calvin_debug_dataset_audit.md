# CALVIN official `calvin_debug_dataset` 审计（EmbodiedSceneAgent）

**范围**：`data/raw/calvin_official/dataset/calvin_debug_dataset/`（gitignore，本机落盘）。  
**非**：官方 D/ABC/ABCD 全量、官方 leaderboard、带语言嵌入的完整训练 shard。

---

## 1. 顶层目录

| 路径 | 含义 |
|------|------|
| `training/` | 训练 split 的逐帧 `episode_*.npz` |
| `validation/` | 验证 split 的逐帧 `episode_*.npz` |
| `training/ep_start_end_ids.npy` | 连续帧的全局起止索引（本包内 **1 段** 大区间：`[[start, end]]`） |
| `validation/ep_start_end_ids.npy` | 同上 |
| `training/ep_lens.npy` / `scene_info.npy` | 上游元数据（本阶段未强制解析进认知闭环） |
| `training/.hydra/`、`statistics.yaml` | 归一化统计等（训练 policy 用；Planner SFT 本阶段可不读） |

**缺失（相对完整 CALVIN 数据说明）**：

- 本 debug zip **无** `lang_annotations/auto_lang_ann.npy`，因此 **npz 内不含与帧对齐的自然语言指令**。
- 语言需从 **外部池**（如本仓库 `calvin_real_subset` manifest 中的官方 YAML 指令）轮换绑定，并在 metadata 标明 **`instruction_lineage`**（见 `docs/calvin_debug_real_data_stats.md`）。

---

## 2. 单个 `*.npz` 内容（抽样一致）

| Key | 形状 / dtype | 含义（上游 README） |
|-----|----------------|---------------------|
| `actions` | `(7,)`, float | 绝对 tcp 位姿 + gripper |
| `rel_actions` | `(7,)`, float | 归一化相对动作 |
| `robot_obs` | `(15,)`, float | tcp pos/orn、夹爪开度、臂关节、gripper_action |
| `scene_obs` | `(24,)`, float | 关节/灯光 + 三色块位姿编码 |
| `rgb_static`, `depth_static`, … | 图像 | 真实传感器；**当前认知闭环默认不加载**（避免巨型 JSONL） |

---

## 3. 本项目直接复用字段

- **`robot_obs` + `scene_obs`** → `perception/calvin_debug_vector_teacher.py` 重构 `robot_info` / `scene_info` → `calvin_teacher_v0` → `SceneMemory`（契约与 live/fixture 一致）。
- **帧 ID**：文件名 `episode_XXXXXXX` 中的整数为全局帧索引（与 `ep_start_end_ids` 一致）。
- **多步语义**：可对 `ep_start_end_ids` 内连续帧做多步窗口；当前最小管线以 **单帧初始化 + 符号执行闭环** 为主（metadata 标明）。

---

## 4. 仍缺映射 / 诚实边界

- **指令–帧对齐**：无 `auto_lang_ann` 时 **不能** 声称「该句即该帧官方标注」。
- **held / in_drawer**：向量布局未提供与 teacher 一致的抓取语义；`held_object_uid` 等保持 **未推断**（与 live 映射一致）。
- **物理 rollout**：debug 接入默认 **不** 调用 `env.step`；执行仍为 **CalvinEnvAdapter + 符号技能**（与 `symbolic_fallback` 叙事一致）。

---

## 5. 相关实现入口

- 枚举/加载：`embodied_scene_agent.data.calvin_debug_dataset`
- 向量→teacher：`embodied_scene_agent.perception.calvin_debug_vector_teacher`
- 构建 Planner 数据：`python -m embodied_scene_agent.training.build_planner_data --source calvin_debug_real …`
