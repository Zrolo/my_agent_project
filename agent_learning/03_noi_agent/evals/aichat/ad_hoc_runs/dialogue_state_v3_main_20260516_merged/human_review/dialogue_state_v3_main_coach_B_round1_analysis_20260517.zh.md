# Dialogue-State v3 Coach B Round1 Blind Review Analysis (2026-05-17)

本报告只分析 Coach B 的全量 350 行复评结果。它是第二位教练复评 evidence，不是最终裁决 gold。

| condition | overall | show_yes | ready_simple | safe_ready | major+answer | rank1 | rank7 | needs_discussion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 3.18 | 17 | 17 | 17 | 4 | 7 | 7 | 7 |
| codehelp_codeaid_clean | 3.1 | 10 | 10 | 10 | 1 | 4 | 10 | 5 |
| dbox_inspired_clean | 3.2 | 15 | 15 | 15 | 3 | 10 | 8 | 5 |
| dbox_inspired_guard | 3.22 | 16 | 16 | 16 | 1 | 10 | 3 | 5 |
| bridge_guided_dbox_style_guard | 3.14 | 12 | 12 | 12 | 2 | 7 | 5 | 5 |
| bridge_contract_compact_guard | 3.1 | 9 | 9 | 9 | 1 | 6 | 11 | 5 |
| bridge_contract_compact_guard_repair | 3.24 | 14 | 14 | 14 | 1 | 6 | 6 | 3 |


## 主要观察

- Coach B 口径下最高 overall 是 `bridge_contract_compact_guard_repair`，均分 3.24。
- Coach B 口径下 ready_simple 最多的是 `enhanced_prompt_only_clean`，17/50。
- Coach B 口径下 major/answer leakage 最少的是 `codehelp_codeaid_clean`，1/50。
- Coach B 整体评分比 Coach A 更严格，尤其 `overall=3`、`show=borderline`、`sufficiency=1/0` 更多；后续必须做 adjudication，而不能直接平均两位教练。
