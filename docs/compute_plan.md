# 计算资源规划

**原则**：主流程**不**针对 T4 优化；**不考虑 T4** 作为训练或正式评测设备。

## 1. 硬件分工

| 资源 | 用途 |
|------|------|
| **3090 24G** | 环境搭建、日常开发、单回合 debug、**Qwen2.5-VL-3B** 级快速实验与小批量 LoRA、日志/可视化、小规模消融 |
| **A100 80G** | **Qwen2.5-VL-7B** LoRA/QLoRA、批量 rollout、正式评测与核心消融、长上下文批量实验 |

## 2. 配置对应

- `configs/experiment/v0.yaml`：本地 smoke，无训练依赖。
- `configs/planner/qwen25vl_3b_lora.yaml`：3090 友好占位（batch、精度、LoRA）。
- `configs/planner/qwen25vl_7b_lora.yaml` + `configs/experiment/a100_final.yaml`：A100 终测入口。

## 3. 流程建议（与蓝图一致）

1. 在 3090 上固定 schema 与日志格式。  
2. 3B 上验证结构化输出与数据管线。  
3. schema 稳定后再上 A100 跑 7B 与正式实验。  
4. **对外报告的关键数字**：以 A100 正式配置与可复现 `experiment_id` 为准（未跑通前表格留空或 TODO）。
