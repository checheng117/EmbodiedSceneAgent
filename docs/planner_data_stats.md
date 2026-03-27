# Planner SFT dataset stats (auto)

## train
- samples: 1024
- by trajectory_type: {'normal': 167, 'multi_step': 797, 'recovery': 60}
- manifest episodes used: 220

## val
- samples: 69
- by trajectory_type: {'normal': 6, 'multi_step': 58, 'recovery': 5}
- manifest episodes used: 10

## test
- samples: 73
- by trajectory_type: {'normal': 13, 'multi_step': 52, 'recovery': 8}
- manifest episodes used: 20

## 实际最小 SFT / eval 使用的 split（2026-03-25）

- **训练**：`train.jsonl`（1024 条）+ **验证**：`val.jsonl`（69 条），与上表一致。
- **Base vs tuned 评测**：`test.jsonl`（**73** 条，全量）；命令与指标路径见 `docs/training_run_log.md` §2026-03-25。
