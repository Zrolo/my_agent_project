# Dialogue-State v3 Priority60 Adjudicated + Coach A Provisional Analysis (2026-05-17)

本报告将 60 条高优先级 A/B 分歧替换为裁决标签，其余 290 条暂沿用 Coach A round1。它是临时合并分析，不是最终 gold。

## 裁决概况

- 裁决条数：60，覆盖 case：39。
- 裁决结论：{'use_A': 29, 'new_label': 22, 'use_B': 9}。
- 裁决泄露标签：{'no_leakage': 37, 'major_bridge_leakage': 16, 'minor_bridge_leakage': 7}。
- 裁决 student-ready：{'yes': 27, 'no': 16, 'unclear': 17}。

## 临时系统汇总

| condition | overall | show_yes | ready_simple | safe_ready | major+answer | minor | adjudicated_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 3.12 | 14 | 14 | 14 | 13 | 19 | 21 |
| codehelp_codeaid_clean | 3.6 | 30 | 30 | 30 | 2 | 9 | 7 |
| dbox_inspired_clean | 3.74 | 33 | 33 | 33 | 3 | 10 | 10 |
| dbox_inspired_guard | 3.72 | 34 | 34 | 34 | 2 | 8 | 5 |
| bridge_guided_dbox_style_guard | 3.66 | 29 | 29 | 29 | 3 | 15 | 4 |
| bridge_contract_compact_guard | 3.86 | 33 | 33 | 32 | 0 | 14 | 9 |
| bridge_contract_compact_guard_repair | 4.02 | 39 | 39 | 39 | 0 | 7 | 4 |

## 解释

- 这一步主要修正 A/B 在 critical leakage、show yes/no、overall 大分差和 rank 大分歧上的口径。
- 由于剩余 290 条仍主要来自 Coach A，本表可用于看趋势，但不应直接作为论文最终结果。
- 下一步建议：要么裁决剩余关键分歧，要么明确将该结果称为 `priority adjudicated reference`，并报告未裁决比例。
