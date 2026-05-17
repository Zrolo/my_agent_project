# Dialogue-State v3 Slice Analysis (2026-05-17)

本报告按 context readiness audit 的 `recommended_use` 对 50 cases 分层，避免把主脚手架样本、澄清安全样本和策略安全样本混成一个总分。

case slice 分布：{'clarification_safety_slice': 10, 'main_scaffold_eval': 31, 'main_eval_with_caution': 5, 'policy_safety_slice': 4}。

## priority60 裁决 + Coach A：分层主表

| slice | condition | case_n | overall | ready | safe_ready | major+answer | minor | adjudicated_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| main_scaffold_eval | enhanced_prompt_only_clean | 31 | 3.0323 | 7 | 7 | 9 | 12 | 13 |
| main_scaffold_eval | codehelp_codeaid_clean | 31 | 3.7097 | 19 | 19 | 2 | 6 | 4 |
| main_scaffold_eval | dbox_inspired_clean | 31 | 3.7742 | 21 | 21 | 2 | 6 | 5 |
| main_scaffold_eval | dbox_inspired_guard | 31 | 3.7742 | 23 | 23 | 2 | 2 | 4 |
| main_scaffold_eval | bridge_guided_dbox_style_guard | 31 | 3.7419 | 20 | 20 | 2 | 9 | 3 |
| main_scaffold_eval | bridge_contract_compact_guard | 31 | 4.0 | 23 | 23 | 0 | 5 | 6 |
| main_scaffold_eval | bridge_contract_compact_guard_repair | 31 | 4.0645 | 22 | 22 | 0 | 6 | 2 |
| main_eval_with_caution | enhanced_prompt_only_clean | 5 | 3.2 | 2 | 2 | 2 | 1 | 2 |
| main_eval_with_caution | codehelp_codeaid_clean | 5 | 3.4 | 3 | 3 | 0 | 0 | 0 |
| main_eval_with_caution | dbox_inspired_clean | 5 | 3.6 | 3 | 3 | 0 | 1 | 2 |
| main_eval_with_caution | dbox_inspired_guard | 5 | 3.2 | 2 | 2 | 0 | 1 | 0 |
| main_eval_with_caution | bridge_guided_dbox_style_guard | 5 | 3.6 | 3 | 3 | 0 | 1 | 0 |
| main_eval_with_caution | bridge_contract_compact_guard | 5 | 3.4 | 2 | 2 | 0 | 2 | 0 |
| main_eval_with_caution | bridge_contract_compact_guard_repair | 5 | 4.2 | 5 | 5 | 0 | 0 | 1 |
| clarification_safety_slice | enhanced_prompt_only_clean | 10 | 3.2 | 3 | 3 | 2 | 4 | 4 |
| clarification_safety_slice | codehelp_codeaid_clean | 10 | 3.3 | 5 | 5 | 0 | 2 | 3 |
| clarification_safety_slice | dbox_inspired_clean | 10 | 3.7 | 6 | 6 | 0 | 3 | 1 |
| clarification_safety_slice | dbox_inspired_guard | 10 | 3.8 | 6 | 6 | 0 | 4 | 0 |
| clarification_safety_slice | bridge_guided_dbox_style_guard | 10 | 3.4 | 4 | 4 | 0 | 4 | 1 |
| clarification_safety_slice | bridge_contract_compact_guard | 10 | 3.6 | 5 | 4 | 0 | 6 | 2 |
| clarification_safety_slice | bridge_contract_compact_guard_repair | 10 | 3.7 | 8 | 8 | 0 | 1 | 1 |
| policy_safety_slice | enhanced_prompt_only_clean | 4 | 3.5 | 2 | 2 | 0 | 2 | 2 |
| policy_safety_slice | codehelp_codeaid_clean | 4 | 3.75 | 3 | 3 | 0 | 1 | 0 |
| policy_safety_slice | dbox_inspired_clean | 4 | 3.75 | 3 | 3 | 1 | 0 | 2 |
| policy_safety_slice | dbox_inspired_guard | 4 | 3.75 | 3 | 3 | 0 | 1 | 1 |
| policy_safety_slice | bridge_guided_dbox_style_guard | 4 | 3.75 | 2 | 2 | 1 | 1 | 0 |
| policy_safety_slice | bridge_contract_compact_guard | 4 | 4.0 | 3 | 3 | 0 | 1 | 1 |
| policy_safety_slice | bridge_contract_compact_guard_repair | 4 | 4.25 | 4 | 4 | 0 | 0 | 0 |

## 四种评分口径下各 slice 领先项

| scenario | slice | best overall | best ready | best safe-ready | lowest major+answer |
| --- | --- | --- | --- | --- | --- |
| coach_A_only | main_scaffold_eval | bridge_contract_compact_guard (4.0645) | bridge_contract_compact_guard (23) | bridge_contract_compact_guard (23) | bridge_contract_compact_guard_repair (0) |
| coach_A_only | main_eval_with_caution | bridge_contract_compact_guard_repair (4.0) | bridge_contract_compact_guard_repair (4) | bridge_contract_compact_guard_repair (4) | codehelp_codeaid_clean (0) |
| coach_A_only | clarification_safety_slice | dbox_inspired_guard (3.8) | bridge_contract_compact_guard_repair (8) | bridge_contract_compact_guard_repair (8) | codehelp_codeaid_clean (0) |
| coach_A_only | policy_safety_slice | bridge_contract_compact_guard_repair (4.25) | bridge_contract_compact_guard_repair (4) | bridge_contract_compact_guard_repair (4) | codehelp_codeaid_clean (0) |
| coach_B_only | main_scaffold_eval | codehelp_codeaid_clean (3.1935) | enhanced_prompt_only_clean (11) | enhanced_prompt_only_clean (11) | bridge_contract_compact_guard (0) |
| coach_B_only | main_eval_with_caution | bridge_contract_compact_guard (3.4) | dbox_inspired_clean (2) | dbox_inspired_clean (2) | enhanced_prompt_only_clean (0) |
| coach_B_only | clarification_safety_slice | dbox_inspired_clean (3.5) | dbox_inspired_clean (5) | dbox_inspired_clean (5) | codehelp_codeaid_clean (0) |
| coach_B_only | policy_safety_slice | bridge_contract_compact_guard_repair (4.0) | bridge_contract_compact_guard_repair (4) | bridge_contract_compact_guard_repair (4) | enhanced_prompt_only_clean (0) |
| priority60_adjudicated_plus_coachA | main_scaffold_eval | bridge_contract_compact_guard_repair (4.0645) | dbox_inspired_guard (23) | dbox_inspired_guard (23) | bridge_contract_compact_guard (0) |
| priority60_adjudicated_plus_coachA | main_eval_with_caution | bridge_contract_compact_guard_repair (4.2) | bridge_contract_compact_guard_repair (5) | bridge_contract_compact_guard_repair (5) | codehelp_codeaid_clean (0) |
| priority60_adjudicated_plus_coachA | clarification_safety_slice | dbox_inspired_guard (3.8) | bridge_contract_compact_guard_repair (8) | bridge_contract_compact_guard_repair (8) | codehelp_codeaid_clean (0) |
| priority60_adjudicated_plus_coachA | policy_safety_slice | bridge_contract_compact_guard_repair (4.25) | bridge_contract_compact_guard_repair (4) | bridge_contract_compact_guard_repair (4) | enhanced_prompt_only_clean (0) |
| priority60_adjudicated_plus_coachB | main_scaffold_eval | bridge_contract_compact_guard_repair (3.2581) | bridge_guided_dbox_style_guard (9) | bridge_guided_dbox_style_guard (9) | bridge_contract_compact_guard (0) |
| priority60_adjudicated_plus_coachB | main_eval_with_caution | bridge_contract_compact_guard_repair (3.6) | bridge_contract_compact_guard_repair (3) | bridge_contract_compact_guard_repair (3) | codehelp_codeaid_clean (0) |
| priority60_adjudicated_plus_coachB | clarification_safety_slice | dbox_inspired_clean (3.7) | dbox_inspired_clean (6) | dbox_inspired_clean (6) | codehelp_codeaid_clean (0) |
| priority60_adjudicated_plus_coachB | policy_safety_slice | enhanced_prompt_only_clean (4.0) | enhanced_prompt_only_clean (4) | enhanced_prompt_only_clean (4) | enhanced_prompt_only_clean (0) |

## 论文使用建议

- 主论文质量比较应优先报告 `main_scaffold_eval`，不要把 clarification/policy slice 混入一个 headline 平均。
- `clarification_safety_slice` 应报告系统是否会澄清、不脑补；它不是普通教学质量样本。
- `policy_safety_slice` 应报告安全重定向和拒绝直接答案/代码的表现。
- `main_eval_with_caution` 可以放进 sensitivity 或 appendix，不宜作为主 headline。
- 若同一 condition 在 `main_scaffold_eval` 与 all-slice 趋势一致，结论更稳；若不一致，应按 slice 分开讨论。
