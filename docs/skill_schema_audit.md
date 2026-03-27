# Skill schema / alias 审计（planner + executor + hybrid LLM）

## 1. Canonical skills（执行器注册）

与 `SkillRegistry.register_defaults` 一致的可执行技能：

- `reach`, `grasp`, `place`, `open`, `close`, `move_to`
- `diagnostic_verifier_unknown`（仅 hybrid smoke / 诊断，**不**应对 LLM 开放）

**真源模块**：`src/embodied_scene_agent/skills/vocabulary.py` 中 `CANONICAL_SKILLS`、`LLM_ALLOWED_SKILLS`。

## 2. Alias 列表（归一化到 canonical）

定义于 `SKILL_ALIASES`，示例：

- `open_gripper`, `gripper_open` → `open`
- `close_gripper`, `gripper_close` → `close`
- `pick`, `pick_up` → `grasp`
- `put`, `put_down` → `place`

## 3. `unknown_skill` 的主要来源（历史）

1. **LLM 输出**不在 vocabulary（拼写变体、多余下划线、自造动词）。
2. **Prompt 与校验器不一致**（例如提示写 `open_gripper` 而校验只接受部分拼写）。
3. **Executor** 在 alias 未覆盖时直接 `KeyError` → `unknown_skill:*`。

## 4. LLM 自由生成导致的失败

- Hybrid replan 若输出 JSON 合法但 `skill` 非 canonical 且非 alias → `PlannerParseErrorCode.INVALID_SKILL` → `replanner_parse_error_kind=invalid_skill`。
- 此类失败 **不代表**「物理执行失败」，而是 **schema 层** 可修复问题。

## 5. 本轮收紧措施

- **单一 vocabulary**：`registry`、`validate_planner_output_dict`、`llm_replan` 的 allowed list 均来自 `vocabulary.py`。
- **校验**：`validate_planner_output_dict` 先 alias 归一化，再拒绝未知 skill（`INVALID_SKILL`）。
- **审计**：`ReplannerAuditLog.skill_alias_normalized_from`；hybrid `fallback_stats.json` / `metrics.json` 增加 `alias_normalization_count`、`invalid_skill_count`、`unknown_skill_rate`。

## 6. `planner_output_contract` 相关字段

- Pydantic 模型仍为 `PlannerOutput.skill: str`；**枚举约束在 validate 层**完成，避免破坏既有 JSON schema 文档的宽松 `string` 类型。
