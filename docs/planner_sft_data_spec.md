# Planner SFT 数据规格（CALVIN-grounded 最小 loop 出口）

**状态**：与 `src/embodied_scene_agent/training/build_planner_data.py` 对齐；**非**正式训练跑数说明。

---

## JSONL 行结构（`planner_sft/v1` — 可训练 agent 轨迹）

由 `--source real_subset` 生成，见 `data/processed/planner_sft/train.jsonl` 等。

| 字段 | 含义 |
|------|------|
| `sample_id` | 全局唯一步样本 id |
| `schema_version` | `planner_sft/v1` |
| `source_type` | 如 `real_subset_mock_rollout` |
| `trajectory_type` | `normal` / `recovery` / `multi_step`（逐步标注） |
| `split` | `train` / `val` / `test` |
| `instruction` | CALVIN 官方 YAML 中的自然语言 |
| `user_prompt` | 与评测一致的完整 user 文本（含 tools + scene JSON） |
| `target_text` | assistant 监督（单步 `Plan:` 或 恢复链） |
| `messages` | `[{role,user},{role,assistant}]` 简化对话（内容同文本） |
| `metadata` | episode_id、step_index、manifest 来源 URL、`rollout_backend` 等 |

生成命令：

```bash
python -m embodied_scene_agent.data.prepare_calvin_real_subset
python -m embodied_scene_agent.training.build_planner_data --source real_subset \
  --manifest data/processed/calvin_real_subset/manifest.jsonl \
  --out-dir data/processed/planner_sft
```

提示模板与解析：`docs/agent_prompt_template.md`。

---

## JSONL 行结构（`planner_sft/v0`）

| 字段 | 含义 |
|------|------|
| `instruction` | 语言指令字符串 |
| `scene_memory` | 该步规划前的 `SceneMemory` JSON |
| `history` / `failure_log` | 与 `PlannerInput` 一致 |
| `planner_output` / `target_subgoal` | 规则 planner 输出 |
| `verification` | `StateDiffVerifier` 结果 |
| `skill_execution` | `SkillResult` |
| `metadata` | 见下 |

### `metadata` 必填字段（本轮）

| 键 | 含义 |
|----|------|
| `source` | 默认 `calvin` |
| `schema_version` | 如 `planner_sft/v0` |
| `env_mode` | `fixture` / `live_env` |
| `teacher_source` | `fixture_json` / `live_mapper` |
| `action_mode` | `fixture_symbolic` / `live_observation_symbolic_fallback` / `live_zero_action_smoke` |
| `data_lineage` | 见下表（**区分是否真实 live step**） |
| `live_probe_status` | episode 级 factory 解析等摘要（dict，来自 `EpisodeTrace`） |
| `live_reset_succeeded` | 是否 live `reset` 成功 |
| `live_step_attempted_episode` | 本 episode 是否尝试过 `env.step` |
| `loop_fallback_reason` | 回退 fixture 时的原因；无则 `null` |
| `trace_id` | UUID |
| `experiment_id` | 可选；无则 `null` |
| `episode_whether_live_step_executed` | 是否至少一步执行了 live `step` |
| `step_live_step_executed` | 当前行对应步是否 `env.step` |
| `executor_mode` | 与 trace step 一致 |
| `episode_success` / `episode_final_message` | episode 摘要 |

### `data_lineage` 取值（一眼识别数据来源）

| 值 | 含义 |
|----|------|
| `fixture` | 纯 fixture，无 live |
| `live_observation_symbolic_action` | **live 观测** grounding，但动作为 **符号** teacher 更新（非 `env.step`） |
| `live_observation_live_step` | 调用了 **`env.step`**（含零向量 smoke） |
| `symbolic` | 预留；当前以 `fixture` / 上两者为主 |

**禁止**将 `live_observation_symbolic_action` 与 `live_observation_live_step` 混用标签。

## 生成命令（v0 fixture）

```bash
python -m embodied_scene_agent.training.build_planner_data --out data/processed/planner_sft/calvin_minimal_dev.jsonl
python -m embodied_scene_agent.training.build_planner_data --experiment-id my_run_001 --out data/processed/planner_sft/calvin_minimal_dev.jsonl
```

（需已配置 `PYTHONPATH=src` 或已 `pip install -e .`。）
