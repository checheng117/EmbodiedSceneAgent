# CALVIN debug：连续同任务风格子批次（same-task-like）

这不是官方标注的同一 CALVIN task ID 子集；debug 包无 per-frame 语言标签。

## 1. 子批次如何构造（可复现）

1. 在 training 与 validation split 上，将存在的 episode_XXXXXXX.npz 按帧索引排序并划为连续索引段。
2. 在每段内用 alignment_window（默认 40）与 alignment_stride（默认 20）生成时间窗口；每个窗口一个 temporal_group_id。
3. 指令：temporal_group_id 经 SHA256 稳定映射到 YAML manifest instruction pool 中的下标，窗口内所有帧同指令。
4. 子集：same_task_subset_splits 取训练侧前 max_groups_train 个窗口、验证侧前 max_groups_val / max_groups_test 组的全部帧，写入 data/processed/calvin_debug_same_task_subset/train_manifest.jsonl 等同目录文件。

构建：python -m embodied_scene_agent.training.build_planner_data --source calvin_debug_real --alignment-mode same_task_subset，或 scripts/refresh_calvin_debug_alignment_bundle.sh。

## 2. 为何比 pooled manifest 更可解释

同一 batch 内帧来自少数连续窗口，共享指令与相近视觉上下文；E2 与 hybrid 使用 --calvin-debug-batch same_task_subset 时跨 episode 的指令轮换噪声更小。

## 3. 局限

指令仍来自外部 YAML 池；窗口超参为工程选择；子集更小、方差更大，不得与 leaderboard 对比作排名结论。

## 4. 可读与不可读结论

可读：控制对齐后 verifier、replan、hybrid 管线稳定性；schema 指标如 unknown_skill_rate。不可读：官方任务成功率与「模型已理解任务语义」的声明。
