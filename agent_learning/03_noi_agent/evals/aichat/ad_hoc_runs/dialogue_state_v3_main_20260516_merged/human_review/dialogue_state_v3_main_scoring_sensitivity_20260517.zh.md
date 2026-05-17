# Dialogue-State v3 Scoring Sensitivity Analysis (2026-05-17)

本报告比较四种评分口径：Coach A only、Coach B only、priority60 裁决 + Coach A、priority60 裁决 + Coach B。目的不是增加人工负担，而是检查系统结论对评分口径是否稳定。

## 跨口径主指标表

| condition | overall A | overall B | overall adj+A | overall adj+B | ready A | ready B | ready adj+A | ready adj+B | major+answer A | major+answer B | major+answer adj+A | major+answer adj+B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 3.16 | 3.18 | 3.12 | 3.02 | 14 | 17 | 14 | 13 | 18 | 4 | 13 | 13 |
| codehelp_codeaid_clean | 3.64 | 3.1 | 3.6 | 3.14 | 31 | 10 | 30 | 11 | 3 | 1 | 2 | 2 |
| dbox_inspired_clean | 3.68 | 3.2 | 3.74 | 3.32 | 31 | 15 | 33 | 18 | 4 | 3 | 3 | 3 |
| dbox_inspired_guard | 3.7 | 3.22 | 3.72 | 3.3 | 33 | 16 | 34 | 17 | 2 | 1 | 2 | 2 |
| bridge_guided_dbox_style_guard | 3.68 | 3.14 | 3.66 | 3.22 | 29 | 12 | 29 | 15 | 3 | 2 | 3 | 3 |
| bridge_contract_compact_guard | 3.9 | 3.1 | 3.86 | 3.28 | 33 | 9 | 33 | 14 | 4 | 1 | 0 | 0 |
| bridge_contract_compact_guard_repair | 3.96 | 3.24 | 4.02 | 3.34 | 37 | 14 | 39 | 17 | 1 | 1 | 0 | 0 |

## 各口径领先项

| scenario | best overall | best ready | best safe-ready | lowest major+answer |
| --- | --- | --- | --- | --- |
| coach_A_only | bridge_contract_compact_guard_repair (3.96) | bridge_contract_compact_guard_repair (37) | bridge_contract_compact_guard_repair (37) | bridge_contract_compact_guard_repair (1) |
| coach_B_only | bridge_contract_compact_guard_repair (3.24) | enhanced_prompt_only_clean (17) | enhanced_prompt_only_clean (17) | codehelp_codeaid_clean (1) |
| priority60_adjudicated_plus_coachA | bridge_contract_compact_guard_repair (4.02) | bridge_contract_compact_guard_repair (39) | bridge_contract_compact_guard_repair (39) | bridge_contract_compact_guard (0) |
| priority60_adjudicated_plus_coachB | bridge_contract_compact_guard_repair (3.34) | dbox_inspired_clean (18) | dbox_inspired_clean (18) | bridge_contract_compact_guard (0) |

## 解释

- Coach B 明显比 Coach A 严格，因此 B-only 结果不适合直接和 A-only 平均。
- `priority60_adjudicated_plus_coachA/B` 用同一批 60 条高风险裁决修正两种口径，可用于观察趋势是否稳健。
- 如果某个 condition 在 adj+A 与 adj+B 下仍保持领先或接近领先，说明结果较稳；如果只在某一位教练口径下领先，则应谨慎写成探索性发现。
- 本报告仍不是最终 gold：60 条已裁决，剩余 290 条仍分别沿用 A 或 B。
