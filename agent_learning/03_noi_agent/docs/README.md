# 教研与产品知识库

这套 `docs/` 不是会议纪要堆放区，而是给后续跨学科迁移复用的“方法资产库”。

记录重点：
- 通用教学原则
- 产品红线
- 决策理由
- 实验结果
- 学科桥梁地图
- 好坏案例

建议使用方式：
1. 新结论先写进 `common/decision_log.md`
2. 可复用原则再沉淀到 `common/teaching_principles.md` 或 `common/product_red_lines.md`
3. 学科特有内容写进 `subjects/<subject>/`
4. 每次试新方案，都在 `common/experiment_log.md` 留实验记录

目录说明：
- `common/`：跨学科可复用的通用资产
- `subjects/noi/`：当前 NOI 学科专用资产
- `harness/`：项目运行契约与上下文加载设计，用于降低后续多轮开发的上下文消耗
