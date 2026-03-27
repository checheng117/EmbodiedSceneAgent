# CALVIN debug real：指令–观测对齐审计（本地收口）

_范围：官方 `calvin_debug_dataset` 的 `robot_obs` / `scene_obs` 向量 → `calvin_teacher_v0` → `SceneMemory` → `build_planner_data` / E2 / hybrid。**非**官方 CALVIN 排行榜或全量 D 划分。_

## 1. 当前 instruction 来源

- **主来源**：`data/processed/calvin_real_subset/manifest.jsonl`（由官方 CALVIN 语言 YAML 派生）。
- **函数**：`instruction_pool_from_manifest()`（`calvin_debug_dataset.py`）去重抽取 `instruction` 字段，最多 500 条；缺文件时回退单句。
- **重要事实**：官方 **debug zip 不含** 可与每帧严格对齐的 `lang_annotations`，因此 **npz 内不带可信自然语言任务句**。

## 2. 帧 / episode / split 与 instruction 的绑定（历史 vs 本轮）

### 2.1 `pooled_manifest`（弱对齐）

- **采样**：训练 / 验证目录各自随机 `*.npz` 子样本；验证集路径再哈希拆成 val / test。
- **绑定**：在同一 split 内按 **样本枚举下标** `i` 做 `pool[i % len(pool)]`。
- **后果**：帧观测与指令 **无时空一致性保证**；`task_completion` 低可能仅反映 **语言–布局错配**，而非规划器实现无效。

### 2.2 `grouped_sequence`（较强对齐，推荐解释性小批）

- **分组**：对同一 split 下按文件名索引排序的帧索引做 **连续段**，再在段内用窗口 `alignment_window` + 步长 `alignment_stride` 切 `temporal_group_id`。
- **绑定**：每个窗口生成稳定 `group_key`，指令为 `SHA256(group_key)` 映射到 pool 下标 → **同窗口内所有帧共享同一句指令**。
- **局限**：仍是 **YAML 池句子**，不是数据集标注的 ground-truth task；只是 **同一段视觉上下文 + 固定句**。

### 2.3 `same_task_subset`（最小、同任务**风格**子集）

- **规则**：在 train / validation 上取 **前 N 个时间窗口组**（实现见 `calvin_debug_alignment.same_task_subset_splits`），写出 `data/processed/calvin_debug_same_task_subset/*_manifest.jsonl`。
- **用途**：E2 / hybrid 的 `--calvin-debug-batch same_task_subset` 从 manifest 按组抽场景，**batch 内上下文更同质**。

## 3. 强 / 弱对齐小结

| 模式 | 对齐强度 | 说明 |
|------|----------|------|
| `pooled_manifest` | 弱 | 轮换池 + 随机帧 |
| `grouped_sequence` | 中强 | 连续帧窗口 + 每窗口一指令 |
| `same_task_subset` | 中强（更小） | 前 N 组窗口 + manifest 可追溯 |

## 4. 对 E2 / hybrid 指标的影响

- **E2**：弱对齐下 `task_completion_rate` 与 `failure_detected_rate` **混入了错配噪声**；`grouped_sequence` / `same_task_subset` 下指标更适合解释 **verifier / replan 机制**，仍不可外推官方 benchmark。
- **Hybrid**：若 LLM 输出非法 `skill`，在旧路径下与 **错配指令** 叠加，难以区分 **schema 失败** vs **语义失败**；本轮在 `planner_output_contract` 与 `skills/vocabulary.py` 收紧后，parse 阶段单独统计 `invalid_skill` / alias 归一化。

## 5. 本轮改进（已实现）

- JSONL `metadata` 扩展：`alignment_mode`、`instruction_source`、`instruction_assignment_strategy`、`episode_key`、`clip_key`、`npz_group_key`、`temporal_group_id`、`whether_same_task_subset`、`lineage_note` 等（见 `build_planner_data._alignment_extra_metadata`）。
- CLI：`build_planner_data --alignment-mode {pooled_manifest,grouped_sequence,same_task_subset}`。
- 产物命名：`calvin_debug_real_{train,val,test}.jsonl`（pooled）、`calvin_debug_real_aligned_*.jsonl`、`calvin_debug_real_same_task_*.jsonl`。
- 统计：`scripts/write_calvin_debug_alignment_stats.md.py` → `docs/calvin_debug_alignment_stats.md`；一键 `scripts/refresh_calvin_debug_alignment_bundle.sh`。

## 6. 相关代码路径

- `src/embodied_scene_agent/data/calvin_debug_dataset.py` — 路径、npz 加载、manifest pool。
- `src/embodied_scene_agent/data/calvin_debug_alignment.py` — 时间分组、same-task manifest。
- `src/embodied_scene_agent/perception/calvin_debug_vector_teacher.py` — 向量 → teacher bundle（本轮未改语义，仅消费侧对齐策略变化）。
- `src/embodied_scene_agent/training/build_planner_data.py` — 导出与 metadata。
