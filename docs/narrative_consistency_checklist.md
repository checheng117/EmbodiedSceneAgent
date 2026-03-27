# 对外叙事一致性检查清单

在发 README / 博客 / 海报前自检：

- [ ] 是否始终强调 **3D object-centric scene memory** 作为 **high-level cognition layer**，而非端到端 VLA？
- [ ] 是否避免「训练了万能机器人」式表述？
- [ ] 是否说明 **teacher-state bootstrap** 是设计选择（可解释、可验证），而非偷懒？
- [ ] 是否解释 **verifier + replanner** 对长程任务必要？
- [ ] 是否区分 **CALVIN（主）**、**RLBench（泛化辅助）**、**VLABench（规划 stress，非主控）**？
- [ ] 是否区分 **真实跑出的指标** vs **模板/计划**（A100、RLBench 全量、VLABench）？
