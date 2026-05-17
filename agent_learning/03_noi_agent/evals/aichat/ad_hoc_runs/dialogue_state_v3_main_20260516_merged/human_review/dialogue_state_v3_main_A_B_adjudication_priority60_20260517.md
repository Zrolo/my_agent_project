# Dialogue-State v3 A/B High-Priority Adjudication Package (2026-05-17)

This package samples 60 high-priority rows from 244 severe A/B disagreements, covering 39 cases. Conditions are hidden.

| 分歧类型 | 数量 |
| --- | --- |
| student-ready 判断分歧 | 38 |
| 总体质量差至少 2 分 | 34 |
| 关键/答案级泄露分歧 | 34 |
| 同题排序差至少 4 位 | 33 |
| 是否可给学生看 yes/no 翻转 | 26 |


## Usage Notes

- Prioritize critical/answer leakage disagreements because they directly affect safe-ready and safety claims.
- Show yes/no flips and >=2 overall deltas help align quality thresholds across coaches.
- Do not inspect deblinded conditions during adjudication; judge only from the case-specific rubric and response.
- Produce adjudicated labels after review; do not simply average Coach A and Coach B.
