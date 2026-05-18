# Dialogue-State v3 Paper-Ready Main Tables 20260517

## 范围

本文把现有 human review 结果整理成论文可用主表。它不新增实验、不修改主实验数据，只复用：

- `dialogue_state_v3_main_slice_analysis_20260517.csv/json`
- `dialogue_state_v3_main_scoring_sensitivity_20260517.csv/json`
- `dialogue_state_v3_main_priority60_adjudicated_plus_coachA_labels_20260517.jsonl`

主口径是 `main_scaffold_eval` slice + `priority60 adjudicated + Coach A`。`ready` / `safe-ready` 沿用现有 slice analysis 输出；`no leakage`、`scaffold avg` 和 `burden` 从同一 label JSONL 机械汇总。不要把 all 50 cases 混成 headline。

## 主表：main_scaffold_eval

| condition | n | overall | student-ready | safe-ready | no leakage | minor critical bridge leakage | major+answer leakage | scaffold avg | burden low/med/high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `enhanced_prompt_only_clean` | 31 | 3.032 | 7 | 7 | 10 | 12 | 9 | 1.13 | 2/12/17 |
| `codehelp_codeaid_clean` | 31 | 3.710 | 19 | 19 | 23 | 6 | 2 | 1.58 | 2/27/2 |
| `dbox_inspired_clean` | 31 | 3.774 | 21 | 21 | 23 | 6 | 2 | 1.65 | 6/22/3 |
| `dbox_inspired_guard` | 31 | 3.774 | 23 | 23 | 27 | 2 | 2 | 1.71 | 8/22/1 |
| `bridge_guided_dbox_style_guard` | 31 | 3.742 | 20 | 20 | 20 | 9 | 2 | 1.65 | 2/28/1 |
| `bridge_contract_compact_guard` | 31 | 4.000 | 23 | 23 | 26 | 5 | 0 | 1.74 | 3/28/0 |
| `bridge_contract_compact_guard_repair` | 31 | 4.065 | 22 | 22 | 25 | 6 | 0 | 1.68 | 3/28/0 |

主读法：`bridge_contract_compact_guard_repair` 的 overall 最高，`bridge_contract_compact_guard` 与 `bridge_contract_compact_guard_repair` 都把 major+answer leakage 控制到 0；但 DBox-inspired guard 在 student-ready 上仍是强 baseline。该表支持 trade-off / stable trend，不支持绝对胜利。

## 分层补充：main_eval_with_caution

| condition | n | overall | student-ready | safe-ready | no leakage | minor | major+answer | scaffold avg | burden low/med/high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `enhanced_prompt_only_clean` | 5 | 3.200 | 2 | 2 | 2 | 1 | 2 | 1.40 | 0/2/3 |
| `codehelp_codeaid_clean` | 5 | 3.400 | 3 | 3 | 5 | 0 | 0 | 1.40 | 0/5/0 |
| `dbox_inspired_clean` | 5 | 3.600 | 3 | 3 | 4 | 1 | 0 | 1.40 | 2/3/0 |
| `dbox_inspired_guard` | 5 | 3.200 | 2 | 2 | 4 | 1 | 0 | 1.40 | 2/2/1 |
| `bridge_guided_dbox_style_guard` | 5 | 3.600 | 3 | 3 | 4 | 1 | 0 | 1.60 | 0/5/0 |
| `bridge_contract_compact_guard` | 5 | 3.400 | 2 | 2 | 3 | 2 | 0 | 1.40 | 2/3/0 |
| `bridge_contract_compact_guard_repair` | 5 | 4.200 | 5 | 5 | 5 | 0 | 0 | 2.00 | 1/4/0 |

该 slice 只有 5 cases，应作为 sensitivity / appendix，不应进入 headline。

## 分层补充：clarification_safety_slice

| condition | n | overall | student-ready | safe-ready | no leakage | minor | major+answer | scaffold avg | burden low/med/high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `enhanced_prompt_only_clean` | 10 | 3.200 | 3 | 3 | 4 | 4 | 2 | 1.30 | 1/5/4 |
| `codehelp_codeaid_clean` | 10 | 3.300 | 5 | 5 | 8 | 2 | 0 | 1.30 | 3/7/0 |
| `dbox_inspired_clean` | 10 | 3.700 | 6 | 6 | 7 | 3 | 0 | 1.60 | 0/9/1 |
| `dbox_inspired_guard` | 10 | 3.800 | 6 | 6 | 6 | 4 | 0 | 1.60 | 2/8/0 |
| `bridge_guided_dbox_style_guard` | 10 | 3.400 | 4 | 4 | 6 | 4 | 0 | 1.40 | 1/9/0 |
| `bridge_contract_compact_guard` | 10 | 3.600 | 5 | 4 | 4 | 6 | 0 | 1.50 | 3/6/1 |
| `bridge_contract_compact_guard_repair` | 10 | 3.700 | 8 | 8 | 9 | 1 | 0 | 1.70 | 1/9/0 |

该 slice 评估澄清、不脑补和安全询问能力，不是普通脚手架质量 headline。

## 分层补充：policy_safety_slice

| condition | n | overall | student-ready | safe-ready | no leakage | minor | major+answer | scaffold avg | burden low/med/high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `enhanced_prompt_only_clean` | 4 | 3.500 | 2 | 2 | 2 | 2 | 0 | 1.50 | 1/2/1 |
| `codehelp_codeaid_clean` | 4 | 3.750 | 3 | 3 | 3 | 1 | 0 | 1.75 | 0/3/1 |
| `dbox_inspired_clean` | 4 | 3.750 | 3 | 3 | 3 | 0 | 1 | 1.75 | 1/2/1 |
| `dbox_inspired_guard` | 4 | 3.750 | 3 | 3 | 3 | 1 | 0 | 1.50 | 0/4/0 |
| `bridge_guided_dbox_style_guard` | 4 | 3.750 | 2 | 2 | 2 | 1 | 1 | 1.50 | 0/3/1 |
| `bridge_contract_compact_guard` | 4 | 4.000 | 3 | 3 | 3 | 1 | 0 | 1.75 | 1/3/0 |
| `bridge_contract_compact_guard_repair` | 4 | 4.250 | 4 | 4 | 4 | 0 | 0 | 2.00 | 0/4/0 |

该 slice 评估直接索要答案/代码时的安全重定向，N=4，只能作为补充分析。

## main_scaffold_eval 敏感性

| scenario | condition | overall | ready | safe-ready | major+answer | minor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Coach A only | `bridge_contract_compact_guard` | 4.064 | 23 | 23 | 3 | 4 |
| Coach A only | `bridge_contract_compact_guard_repair` | 4.000 | 21 | 21 | 0 | 6 |
| Coach A only | `dbox_inspired_guard` | 3.742 | 22 | 22 | 2 | 4 |
| Coach B only | `bridge_contract_compact_guard_repair` | 3.193 | 7 | 7 | 0 | 1 |
| Coach B only | `enhanced_prompt_only_clean` | 3.161 | 11 | 11 | 3 | 0 |
| Coach B only | `codehelp_codeaid_clean` | 3.193 | 8 | 8 | 1 | 0 |
| priority60 adjudicated + Coach A | `bridge_contract_compact_guard_repair` | 4.064 | 22 | 22 | 0 | 6 |
| priority60 adjudicated + Coach A | `bridge_contract_compact_guard` | 4.000 | 23 | 23 | 0 | 5 |
| priority60 adjudicated + Coach A | `dbox_inspired_guard` | 3.774 | 23 | 23 | 2 | 2 |
| priority60 adjudicated + Coach B | `bridge_contract_compact_guard_repair` | 3.258 | 8 | 8 | 0 | 1 |
| priority60 adjudicated + Coach B | `bridge_guided_dbox_style_guard` | 3.226 | 9 | 9 | 2 | 0 |
| priority60 adjudicated + Coach B | `bridge_contract_compact_guard` | 3.226 | 8 | 8 | 0 | 1 |

敏感性读法：overall 领先趋势在 repair-enabled Bridge condition 上较稳；student-ready 排名对 rater strictness 敏感，不能写成单一结论。

## all-case sensitivity 仅作补充

全 50 cases 的 `dialogue_state_v3_main_scoring_sensitivity_20260517.csv` 显示 `bridge_contract_compact_guard_repair` 在四种口径下 overall 都最高；但 all-case 平均混入 clarification / policy slice，不能作为主 headline。论文可以在 appendix 报告这个趋势，用来说明 slice 分析之外的 robustness，而不是替代主 slice。
