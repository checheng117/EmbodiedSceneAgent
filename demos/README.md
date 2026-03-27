# Demos

- **v0**：直接运行 `bash scripts/run_smoke_v0.sh`，在 mock 桌面场景中完成「开抽屉 → 抓取积木 → 放入抽屉」的长程指令。
- **可视化**：`python -c "from embodied_scene_agent.memory.builder import SceneMemoryBuilder; from embodied_scene_agent.visualization.render_scene_graph import render_scene_graph; ..."`（可将 `SceneMemory` 导出为 graphviz 文本）。

后续将补充：CALVIN 单回合录屏脚本、scene graph 渲染图、失败恢复案例对拍。
