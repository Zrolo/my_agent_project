# Fair 20-case Paired Analysis（2026-05-11）

本报告把 20 个 case 当作配对样本分析，而不是把 140 行回复当作独立样本。它是 development / pilot evidence，不是最终 held-out test。

## 系统汇总

| 系统 | 总体质量均分 | student_ready_pass | student_ready_safe_pass | rank=1 | major/answer 泄露 | repair_applied |
| --- | --- | --- | --- | --- | --- | --- |
| current_system | 3.35 | 9 | 9 | 0 | 7 | 0 |
| single_llm | 3.35 | 6 | 6 | 0 | 1 | 0 |
| single_llm+guard | 3.95 | 11 | 11 | 1 | 1 | 0 |
| single_llm+guard+repair | 3.75 | 10 | 10 | 2 | 0 | 3 |
| bridge_contract | 4.2 | 12 | 12 | 5 | 2 | 0 |
| bridge_contract+guard | 4.2 | 12 | 12 | 6 | 2 | 0 |
| bridge_contract+guard+repair | 4.4 | 13 | 13 | 6 | 1 | 1 |

## 关键配对比较（总体质量）

| 比较 | 均值差 | bootstrap 95% CI | win/tie/loss | 配对 case |
| --- | --- | --- | --- | --- |
| bridge_contract+guard+repair - single_llm+guard | 0.45 | [-0.05, 0.95] | 8/9/3 | 20 |
| bridge_contract+guard+repair - single_llm+guard+repair | 0.65 | [0.25, 1.05] | 12/5/3 | 20 |
| bridge_contract - single_llm | 0.85 | [0.2, 1.4] | 13/4/3 | 20 |
| bridge_contract+guard+repair - current_system | 1.05 | [0.65, 1.45] | 14/6/0 | 20 |

## 解释边界

- `single_llm+guard` 的质量高于 `single_llm` 不能归因于 Guard 本身；当前 guard-only 条件没有修改 final response，差异更可能来自 LLM 多次生成的 run-to-run variance。
- Guard/Repair 的因果作用需要复用同一个 candidate 做 paired before/after ablation，不能只比较分别生成的系统输出。
- 当前最稳定的 pilot 信号是：Bridge Contract variants 在 case-level preference 和 student-ready 指标上更强；critical bridge leakage 仍未完全解决。
