# Dialogue-State v3 Human Review Result Packet 20260517

English version: `dialogue_state_v3_human_review_result_packet_20260517.md`

## 结论摘要

本记录汇总 dialogue-state v3 50-case 主实验的 response blind review 阶段结果。当前状态是：

- 50 个 reviewed candidate cases 已生成 7-condition 主表回复，共 350 条匿名回复；
- Coach A 完成 350 条全量盲评；
- Coach B 完成 350 条全量复评；
- 已完成 60 条高优先级 A/B 分歧裁决；
- 已生成敏感性分析和按 case-use slice 的分层分析。

这批结果已经可以作为 **formal human-review evidence candidate**，但仍不应称为最终 gold。原因是：60 条高优先级分歧已裁决，剩余 290 条仍分别依赖 Coach A 或 Coach B 口径；论文中应报告 agreement、adjudication 和 sensitivity analysis，而不是只报单一分数表。

## 主实验条件

主实验包含 7 个匿名 condition：

| condition | 说明 |
| --- | --- |
| `enhanced_prompt_only_clean` | 强教学提示词 baseline，不使用 Guard / Repair |
| `codehelp_codeaid_clean` | CodeHelp / CodeAid 风格 no-direct-solution baseline |
| `dbox_inspired_clean` | DBox-inspired 分解式 baseline，不使用 Guard |
| `dbox_inspired_guard` | DBox-inspired 分解式 baseline + Guard |
| `bridge_guided_dbox_style_guard` | Bridge-guided DBox-style baseline + Guard |
| `bridge_contract_compact_guard` | Bridge Contract compact + Guard |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard + Repair |

## Coach A / Coach B 全量复评

Coach A 与 Coach B 都完成了 350 条全量评分。Coach B 比 Coach A 明显更严格，尤其在 `overall=3`、`show=borderline`、`scaffold_sufficiency=1/0` 上更集中。

A/B 一致性核心结果：

| metric | value |
| --- | ---: |
| overlap rows | 350 |
| overall exact | 0.2829 |
| overall within 1 | 0.8429 |
| leakage exact | 0.6714 |
| critical binary exact | 0.9029 |
| critical binary kappa | 0.2511 |
| critical recall B vs A | 0.2 |
| rank mean Spearman by case | 0.0264 |
| top-1 agreement cases | 10 / 50 |
| last-place agreement cases | 10 / 50 |
| flagged disagreement rows | 244 |

解释：总体质量分大多差在 1 分内，但 `student-ready`、rank 排序和 critical leakage 口径分歧较大。因此不能直接平均 A/B 分数，必须报告分歧与裁决。

## 高优先级裁决

从 244 条严重分歧中抽取 60 条高优先级样本进行裁决，覆盖 39 个 case。抽样优先级为：critical leakage disagreement、show yes/no flip、overall delta >= 2、rank delta >= 4、student-ready disagreement。

裁决结果：

| 裁决项 | 数量 |
| --- | ---: |
| `use_A` | 29 |
| `use_B` | 9 |
| `new_label` | 22 |
| adjudicated `no_leakage` | 37 |
| adjudicated `minor_bridge_leakage` | 7 |
| adjudicated `major_bridge_leakage` | 16 |
| adjudicated `answer_leakage` | 0 |
| adjudicated student-ready `yes` | 27 |
| adjudicated student-ready `unclear` | 17 |
| adjudicated student-ready `no` | 16 |

该裁决表明：分歧样本中并非单纯 Coach A 或 Coach B 更可靠，22 条需要新标签。论文中应把裁决作为 reliability control，而不是把任一教练当作绝对 gold。

## 敏感性分析

我们比较四种评分口径：Coach A only、Coach B only、priority60 adjudicated + Coach A、priority60 adjudicated + Coach B。

核心观察：

- `bridge_contract_compact_guard_repair` 在四种口径下 overall 都最高；
- Coach A 和 adjudicated+A 口径下，它也是 ready / safe-ready 最高；
- Coach B 和 adjudicated+B 口径下，ready / safe-ready 更偏向 `enhanced_prompt_only_clean` 或 `dbox_inspired_clean`；
- 说明 overall 结论较稳，但 student-ready 对评分者口径敏感。

| scenario | best overall | best ready | best safe-ready | lowest major+answer |
| --- | --- | --- | --- | --- |
| Coach A only | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` |
| Coach B only | `bridge_contract_compact_guard_repair` | `enhanced_prompt_only_clean` | `enhanced_prompt_only_clean` | `codehelp_codeaid_clean` |
| priority60 adjudicated + Coach A | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard` |
| priority60 adjudicated + Coach B | `bridge_contract_compact_guard_repair` | `dbox_inspired_clean` | `dbox_inspired_clean` | `bridge_contract_compact_guard` |

论文中较稳的说法是：

> Bridge Contract compact + Guard/Repair shows a stable advantage in overall quality and critical-leakage control across rater views, while student-ready preference is sensitive to rater strictness and should be reported with sensitivity analysis.

中文表述：

> Bridge Contract compact + Guard/Repair 在总体质量和 critical leakage 控制上表现出稳定优势；但 student-ready 偏好对评分者严格程度敏感，因此必须配合敏感性分析报告。

## 分层分析

根据 context-readiness audit，50 cases 被分成：

| slice | case 数 | 用途 |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | 主脚手架质量比较 |
| `main_eval_with_caution` | 5 | 可谨慎纳入敏感性分析 |
| `clarification_safety_slice` | 10 | 澄清、不脑补、安全询问能力 |
| `policy_safety_slice` | 4 | 直接要答案/代码时的安全重定向 |

在当前主参考口径 `priority60 adjudicated + Coach A` 下，`main_scaffold_eval` 的主表为：

| condition | overall | ready | safe-ready | major+answer |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.0323 | 7 | 7 | 9 |
| `codehelp_codeaid_clean` | 3.7097 | 19 | 19 | 2 |
| `dbox_inspired_clean` | 3.7742 | 21 | 21 | 2 |
| `dbox_inspired_guard` | 3.7742 | 23 | 23 | 2 |
| `bridge_guided_dbox_style_guard` | 3.7419 | 20 | 20 | 2 |
| `bridge_contract_compact_guard` | 4.0000 | 23 | 23 | 0 |
| `bridge_contract_compact_guard_repair` | 4.0645 | 22 | 22 | 0 |

这说明：在主脚手架样本上，Bridge Contract compact + Guard/Repair 在 overall 与 major/answer leakage 上最稳；DBox-inspired + Guard 在 ready 上仍是强 baseline。

## 论文可用主张

可以作为论文候选主张：

1. `critical bridge leakage` 比 answer/code leakage 更细，能够暴露 no-direct-code baseline 仍可能存在的过度提示问题。
2. DBox-inspired decomposition 是强 baseline，不能被当作弱对照。
3. Bridge Contract compact + Guard/Repair 在 overall 与 critical-leakage control 上表现稳定。
4. student-ready 与 rank 偏好对教练口径敏感，因此需要双评审、裁决和 sensitivity analysis。
5. 论文应报告 quality-safety-burden trade-off，而不是只宣布某个系统绝对胜出。

不应声称：

1. Bridge Contract 全面显著优于所有 baseline。
2. Guard/Repair 已经完全解决泄露。
3. Coach A 或 Coach B 单独评分就是 gold。
4. 60 条裁决后的临时合并表就是 final adjudicated reference。
5. 所有 50 cases 可以混成一个无分层 headline 平均。

## 关键产物

- Coach A analysis：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_coach_A_round1_analysis_20260517.zh.md`
- Coach B analysis：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_coach_B_round1_analysis_20260517.zh.md`
- A/B agreement：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_coach_A_B_agreement_20260517.zh.md`
- A/B high-priority adjudication package：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_A_B_adjudication_priority60_20260517.zh.xlsx`
- Completed adjudication workbook：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_A_B_adjudication_priority60_20260517_zh1_adjudicated.xlsx`
- Priority60 adjudicated labels：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_adjudication_priority60_labels_20260517.jsonl`
- Priority60 adjudicated + Coach A labels：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_priority60_adjudicated_plus_coachA_labels_20260517.jsonl`
- Priority60 adjudicated + Coach B labels：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_priority60_adjudicated_plus_coachB_labels_20260517.jsonl`
- Sensitivity analysis：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_scoring_sensitivity_20260517.zh.md`
- Slice analysis：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_slice_analysis_20260517.zh.md`

## 下一步

建议下一阶段做三件事：

1. 把本结果包交给外部 reviewer / AI 审查，重点检查是否存在评分口径或统计解释问题。
2. 对 `main_scaffold_eval` slice 写正式论文结果草稿，clarification / policy slice 放补充分析。
3. 继续做 LLM grader calibration：比较 `likert_only_judge`、`generic_rubric_judge`、`case_specific_bridge_rubric_judge` 对 Coach adjudicated labels 的一致性。
