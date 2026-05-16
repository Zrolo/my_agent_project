# 50-case High-risk Case Pack 11-case Blind Review Analysis

This report analyzes 11 high-risk cases, 8 anonymous system conditions, and 88 coach blind-reviewed responses sampled from the 50-case × 8-condition AI preliminary review. It is development evidence for AI-prelim calibration and prompt/regression revision, not a final held-out result.

- Review workbook: `coach_response_review_workbook_dev_ablation_ai_prelim_high_risk_case_pack_zh_blind_reviewed.xlsx` (local filled file, not committed)
- Anonymous key: `evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged/coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_case_pack.key.csv`

- Reviewed responses: 88
- Cases: 11
- Leakage labels: {'no_leakage': 66, 'minor_bridge_leakage': 15, 'major_bridge_leakage': 7}
- Bridge reveal justification labels: {'no_reveal': 66, 'borderline': 15, 'unjustified': 7}
- Student response burden labels: {'medium': 48, 'low': 31, 'high': 9}
- Show-to-student labels: {'yes': 37, 'borderline': 45, 'no': 6}

## AI Preliminary Review vs Coach Review

This case pack was selected from AI-prelim high-risk rows. Coach review suggests that the AI preliminary review is conservative, especially when answer-slot / worked-example risk is involved.

| Comparison | Count |
| --- | ---: |
| AI severe and coach severe | 2 |
| AI severe but coach not severe | 23 |
| AI not severe but coach severe | 5 |
| AI not severe and coach not severe | 58 |

Among the original 25 AI high-risk rows, coach review found:

| Coach-reviewed outcome | Count |
| --- | ---: |
| `major_bridge_leakage` | 2 |
| `minor_bridge_leakage` | 7 |
| `no_leakage` | 16 |
| `would_show_to_student=no` | 1 |
| overall quality 1/2 | 2 |

This means AI preliminary review is useful as a recall-oriented triage tool, but it must not be treated as final leakage labels. In the paper, it should be described as a development screening / candidate-selection tool, not coach reference.

## System Summary

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_system_deployment | 11 | 3.3636 | 1.4394 | 1.9091 | 1.3117 | 1 | 3 | 3 | 3/5/3 | 4/5/2 | 0/5/2 | 5/3/3 |
| enhanced_prompt_only_clean | 11 | 3.5455 | 1.6364 | 1.8182 | 1.5065 | 3 | 6 | 6 | 6/3/2 | 7/1/3 | 0/1/3 | 6/5/0 |
| socratic_no_answer_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| codehelp_codeaid_clean | 11 | 3.2727 | 1.5151 | 1.6364 | 1.3766 | 0 | 3 | 2 | 3/8/0 | 7/3/1 | 0/3/1 | 0/8/3 |
| dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| dbox_inspired_guard | 11 | 3.7273 | 1.7727 | 1.5455 | 1.5714 | 2 | 7 | 7 | 7/4/0 | 10/0/1 | 0/0/1 | 9/2/0 |
| edf_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| bridge_inspired_expert_decision_clean | 11 | 3.0909 | 1.5455 | 1.2727 | 1.3377 | 0 | 3 | 2 | 3/7/1 | 8/3/0 | 0/3/0 | 4/7/0 |
| single_llm_structured_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| single_llm_structured_guard | 11 | 2.7273 | 1.4242 | 0.8182 | 1.2208 | 0 | 2 | 2 | 2/9/0 | 11/0/0 | 0/0/0 | 0/11/0 |
| bridge_contract_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| bridge_contract_guard | 11 | 4.0909 | 1.8939 | 1.7273 | 1.8052 | 3 | 8 | 8 | 8/3/0 | 10/1/0 | 0/1/0 | 6/4/1 |
| bridge_contract_guard_repair | 11 | 3.4545 | 1.6667 | 1.4545 | 1.5455 | 2 | 5 | 3 | 5/6/0 | 9/2/0 | 0/2/0 | 1/8/2 |
| bridge_contract_safe_scaffold | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |

## Key Paired Comparisons

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_safe_scaffold - bridge_contract_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - bridge_contract_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard - dbox_inspired_guard | 11 | 0.3636 | 0.1212 | 0.2338 | 6/1/4 | [-0.4545, 1.1818] |
| edf_inspired_guard - edf_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| edf_inspired_guard - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard - edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard_repair - edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard_repair - bridge_contract_guard | 11 | -0.6364 | -0.2273 | -0.2597 | 1/3/7 | [-1.0909, -0.1818] |
| bridge_contract_clean - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| dbox_inspired_guard - dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| single_llm_structured_guard - single_llm_structured_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |

## Major Leakage Cases

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| heldout_cp_035 | current_system_deployment | 2.0 | no | unjustified | 解释很完整，但把“最小化设 +∞、最大化设 -∞、起点设实际值”直接总结出来了，基本替学生补完了初始化桥。更适合作为课后总结。 |
| heldout_cp_003 | dbox_inspired_guard | 3.0 | borderline | unjustified | 它直接把“选 v/不选 v、两种状态”塞进问题里，学生基本只需复述。对诊断有用，但作为盲评回复，泄露状态桥偏多。 |
| heldout_cp_024 | enhanced_prompt_only_clean | 3.0 | borderline | unjustified | 教学上很清楚，但第一句就确认“状态需要扩展”，并直接说要记录是否用掉免费机会，这正是学生要判断的桥。后面的转移问题倒是有价值。 |
| heldout_cp_035 | enhanced_prompt_only_clean | 3.0 | borderline | unjustified | 网格例子贴合“可达/不可达”，但后半段直接给出起点实际值、其他状态正无穷的规则，泄露较多。并且三问加总结略长。 |
| heldout_cp_024 | codehelp_codeaid_clean | 3.0 | borderline | unjustified | 前半段直接给出“已用/未用两种状态”，泄露了状态扩展桥；后面的三点例子还可以，但最好先让学生自己观察两种到达 B 的局面。 |
| heldout_cp_017 | enhanced_prompt_only_clean | 2.0 | no | unjustified | 这条把死锁原因、两种调整方向以及 B 会丢答案都说出来了，基本替学生完成关键判断。作为讲解可以，作为当前引导太透。 |
| heldout_cp_003 | current_system_deployment | 2.0 | no | unjustified | 例子讲得很细，但已经把选 A/不选 A 的收益式和“父节点关心两种状态”几乎完整摊开了。学生不需要自己搭状态桥了。 |

## Development Notes

- The highest `student_ready_pass` condition is `bridge_contract_guard`: 8 / 11.
- On these 11 high-risk cases, `bridge_contract_guard` is the strongest overall condition: overall=4.0909, core6=1.8939, student-ready=8/11, and major/answer=0.
- `dbox_inspired_guard` is the next strongest condition: overall=3.7273, student-ready=7/11, and major/answer=1. It remains a strong baseline, but is slightly behind `bridge_contract_guard` on this high-risk slice.
- `bridge_contract_guard_repair` does not improve over `bridge_contract_guard`: overall is lower by 0.6364, with W/T/L = 1/3/7. Repair may reduce instructional quality in natural high-risk cases and should not be a default path yet.
- `enhanced_prompt_only_clean` has 3 major-leakage rows in this high-risk slice, suggesting that strong prompt-only tutoring can still complete the student's current critical bridge too directly.
- This run did not include `bridge_contract_safe_scaffold` as a normal condition; safe scaffold is used only as a block/fallback mechanism and appendix candidate.
- Major/answer leakage cases should be inspected qualitatively because fully worked micro-examples can leak the critical bridge without giving code.
- The new bridge-reveal justification field separates useful instructional information from unjustified early completion of the student's current missing bridge.
- The new scaffold-sufficiency field flags over-withholding: low leakage is not pedagogical success if the response is safe but not useful.
- Guard/Repair causal effects still require same-candidate before/after repair stress; between-run averages are not enough.
- Use this run to decide which conditions enter the frozen 50-case held-out study: `bridge_contract_guard` and `dbox_inspired_guard` should remain in the main comparison; `bridge_contract_guard_repair` should remain a Repair analysis / appendix condition rather than the default path.
