# Review 上线观测教研任务单

这份任务单面向教研或产品运营，目标是把上线后的人工抽样复核跑起来，并形成稳定反馈闭环。

关联文档：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_spec.md`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_manual_review_sop.md`

---

## 1. 目标

教研侧第一版只做三件事：

1. 每天抽样复核 `10-20` 条
2. 判断 mode 是否分对、review 是否贴题、学生是否能继续
3. 每天输出 3 行复盘结论

---

## 2. 任务拆分

### 任务 T1：确定抽样池来源

目标：
- 明确每天从哪里抽样

建议来源：
1. 学生反馈为 `confused`
2. 各 mode 补足覆盖
3. 少量 `understood` 对照样本

验收：
- 每天抽样不被单一 mode 垄断

### 任务 T2：执行人工复核

目标：
- 对每条样本填写：
  - `mode_correct`
  - `review_grounded`
  - `student_can_move_next`
  - `notes`

依据文档：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_manual_review_sop.md`

### 任务 T3：形成每日结论

目标：
- 每天至少写 3 行：
  1. `mode_correct` 最低的是哪个 mode
  2. `review_grounded` 最差的共性是什么
  3. 最值得回放的 1-2 条 session 是哪几条

验收：
- 不写长篇总结
- 只写能指导下一轮产品迭代的结论

---

## 3. 教研建议执行顺序

1. 先定抽样池
2. 再跑复核
3. 最后产出结论

---

## 4. 第一周重点观察

第一周重点只看：

1. 哪个 mode 最容易分错
2. 哪个 mode 最容易“学生仍不知道下一步”
3. 哪类输入最容易导致 review 太空

第一周不要求评估长期学习效果。
