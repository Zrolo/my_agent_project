# Dialogue-State v3 A/B 高优先级裁决包（2026-05-17）

本裁决包从 244 条 A/B 严重分歧中抽取 60 条高优先级样本，覆盖 39 个 case。condition 已隐藏。

| 分歧类型 | 数量 |
| --- | --- |
| student-ready 判断分歧 | 38 |
| 总体质量差至少 2 分 | 34 |
| 关键/答案级泄露分歧 | 34 |
| 同题排序差至少 4 位 | 33 |
| 是否可给学生看 yes/no 翻转 | 26 |


## 使用建议

- 优先裁决 `关键/答案级泄露分歧`，因为它直接影响 safe-ready 和论文安全结论。
- `是否可给学生看 yes/no 翻转` 和 `总体质量差至少 2 分` 用于统一教练对教学质量的阈值。
- 裁决时不要看揭盲 condition；只根据题面、当前学生问题、case-specific rubric 和 AI 回复判断。
- 裁决后再生成 adjudicated label，不建议直接平均 Coach A / Coach B。
