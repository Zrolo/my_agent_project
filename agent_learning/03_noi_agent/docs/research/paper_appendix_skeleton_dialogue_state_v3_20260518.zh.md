# Paper Appendix Skeleton: Dialogue-State v3 20260518

## 使用边界

本文档是 dialogue-state v3 manuscript 的 supplementary-material skeleton。它不新增实验、不修改数据、不接入线上 active mode。它的作用是按 evidence class 组织附录证据，避免把 sensitivity、stress-test、fairness、calibration 和 artifact evidence 误写成 main results。

请和以下文件一起使用：

- `paper_submission_manuscript_dialogue_state_v3_20260518.zh.md`
- `paper_manuscript_assembly_map_dialogue_state_v3_20260518.zh.md`
- `paper_figure_table_plan_dialogue_state_v3_20260518.zh.md`
- `dialogue_state_v3_evidence_manifest_20260518.json`
- `dialogue_state_v3_paper_claims_final_gate_20260518.zh.md`

## Appendix A. Evidence Package Overview

目的：说明 dialogue-state v3 package 包含什么、不包含什么。

应包含：

- Branch 和 checkpoint 说明：
  - evidence-content base 可能显示为 `dbbbd5c`；
  - evidence-package gates checkpoint 是 `33a5dd7`；
  - 后续 branch-tip commits 主要收紧论文表述和 handoff docs，除非明确说明改变证据。
- Evidence package status：
  - `formal human-review evidence candidate`；
  - 不是 final gold；
  - 不是 online active-mode validation。
- Main headline rule：
  - 只用 `main_scaffold_eval`；
  - all-50 aggregate 只作为 sensitivity / robustness。

主要来源：

- `docs/research/index.md`
- `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`
- `docs/research/dialogue_state_v3_paper_claims_final_gate_20260518.zh.md`

## Appendix B. Dataset Slices and Case Use

目的：防止读者把 50 cases 理解成一个无分层 headline set。

推荐表格：

| slice | case_n | appendix use | headline use |
| --- | ---: | --- | --- |
| `main_scaffold_eval` | 31 | 完整指标和 paired comparisons。 | 是。 |
| `main_eval_with_caution` | 5 | 仅 sensitivity。 | 否。 |
| `clarification_safety_slice` | 10 | Clarification 和 context-insufficient safety 分析。 | 否。 |
| `policy_safety_slice` | 4 | Direct-answer / policy redirection 分析。 | 否。 |

主要来源：

- `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md`
- `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`
- `dialogue_state_v3_50_context_readiness_audit_20260515.jsonl`

## Appendix C. Human Review Reliability

目的：正面报告 rater sensitivity，而不是把它藏在单一分数表后面。

应包含：

- Coach A 和 Coach B 都完成 350 条 AI responses 评分。
- Overall-quality exact agreement: 0.2829。
- Overall-quality within-1 agreement: 0.8429。
- Leakage-label exact agreement: 0.6714。
- Critical-binary exact agreement: 0.9029。
- Critical-binary kappa: 0.2511。
- Rank top-1 agreement: 10/50。
- Rank last-place agreement: 10/50。
- priority60 adjudication outcomes:
  - `use_A=29`;
  - `use_B=9`;
  - `new_label=22`.

必要解释：

- Coach A、Coach B 和 priority60 adjudication 是 expert reference / adjudicated sensitivity views，不是 gold。
- Student-ready、safe-ready 和 rank 应作为 rater-sensitive outcomes 报告。

主要来源：

- `human_review_reliability_section_draft_20260517.zh.md`
- `dialogue_state_v3_main_coach_A_B_agreement_20260517.zh.md`
- `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/` 下的 priority60 adjudication JSONL files

## Appendix D. Full Slice and Rater-View Sensitivity

目的：说明主张不是建立在隐藏的 all-50 平均上。

应包含这些表：

- `main_scaffold_eval` 在以下口径下的结果：
  - Coach A only；
  - Coach B only；
  - priority60 adjudicated + Coach A；
  - priority60 adjudicated + Coach B。
- `main_eval_with_caution`。
- `clarification_safety_slice`。
- `policy_safety_slice`。
- all-50 aggregate 仅作为 sensitivity。

必要解释：

- 主文可以使用 `main_scaffold_eval + priority60 adjudicated + Coach A` 作为 primary view。
- all-50 aggregate 混合了不同 paper use 的 slices，只能作为 appendix robustness。

主要来源：

- `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`
- `dialogue_state_v3_main_scoring_sensitivity_20260517.zh.md`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`

## Appendix E. Paired Comparisons and Uncertainty

目的：展示 same-case uncertainty，防止过强结论。

最少包含这些 comparisons：

1. `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard`
2. `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard`
3. `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean`
4. `dbox_inspired_guard` vs `dbox_inspired_clean`
5. `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean`
6. `bridge_contract_compact_guard` vs `dbox_inspired_guard`

必要字段：

- `n`
- W/T/L
- mean overall delta
- bootstrap CI
- paired permutation p
- safe-ready delta
- major+answer leakage delta
- paper interpretation

关键边界：

- 如果 CI 跨 0，只能写 favorable trend / trade-off，不能写 significant dominance。

主要来源：

- `dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md`
- `dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.zh.md`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`

## Appendix F. Observed Error Taxonomy

目的：说明 taxonomy 不是为 DP/check/lazy/tree/local-code 这些例子特调。

Taxonomy 写作格式：

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

应包含：

- Level 1 failure type definitions。
- Level 2 cognitive bridge family coverage。
- Level 3 surface-anchor examples。
- Condition-level error distribution。
- Level 1 x Level 2 coverage table。

必要解释：

- 这是 observed operational taxonomy，不是 universal taxonomy。
- DP state、binary-search check、lazy propagation、tree difference、local code、greedy proof 和 debugging trace 是 surface anchors，不是 taxonomy 本体。

主要来源：

- `dialogue_state_v3_observed_error_taxonomy_20260517.zh.md`
- `taxonomy_specificity_revision_summary_20260517.zh.md`
- `response_review_rubric_v3.zh.md`

## Appendix G. Repair Same-Candidate Stress Test

目的：把 Repair 因果证据和主实验 condition means 分开。

应报告：

- 30 before/after pairs。
- Leakage severity improved / same / worsened: 16/14/0。
- Major leakage: 7/30 before -> 0/30 after。
- Mean overall: 3.367 before -> 3.633 after。
- Burden improved / same / worsened: 2/16/12。

必要解释：

- Repair 在 fixed-candidate stress testing 中降低 leakage。
- Repair 可能增加 student burden。
- 主实验 condition means 本身不能证明 Repair causality。

主要来源：

- `repair_same_candidate_stress_protocol_20260517.zh.md`
- `repair_same_candidate_stress_result_20260517.zh.md`
- evidence manifest 中列出的 repair stress summary files

## Appendix H. DBox+Repair Fairness Sensitivity

目的：回应“为什么主表只有 Bridge Contract 有 Repair”的公平性质疑。

应报告：

- 20 headline-sensitive cases。
- DBox+Repair overall: 3.55。
- DBox+Repair safe-ready: 11/20。
- DBox+Repair no/minor/major+answer leakage: 14/6/0。
- Same-case DBox Guard comparison:
  - overall +0.15；
  - major+answer leakage 2 -> 0。
- Same-case Bridge+Repair comparison:
  - Bridge+Repair 仍高 +0.50 overall；
  - W/T/L 12/5/3；
  - +4 safe-ready。

必要解释：

- DBox+Repair 是 targeted fairness sensitivity，不是 full 50-case double-coach main condition。
- 结果应公平报告，但不替代主实验设计。

主要来源：

- `dbox_guard_repair_fairness_report_20260517.zh.md`
- `dbox_repair_fairness_extension_plan_20260518.zh.md`
- evidence manifest 中列出的 DBox+Repair review workbook / summary files

## Appendix I. DeepSeek LLM Grader Calibration

目的：说明 automatic graders 只是 auxiliary，不能替代 human review。

应报告：

- Backend: DeepSeek `deepseek-v4-flash`，thinking disabled。
- Judge variants:
  - likert-only；
  - generic rubric；
  - case-specific bridge rubric。
- Priority60 key metrics:
  - case-specific leakage-label accuracy 0.617 vs generic 0.583；
  - case-specific student-ready agreement 0.467 vs generic 0.433；
  - case-specific safe-ready agreement 0.533 vs generic 0.400；
  - critical recall 0；
  - major leakage false-negative rate 1.000。

必要解释：

- LLM graders 可以是 scalable auxiliary signals。
- 它们不是 gold，不能替代 human coaches 做 critical bridge leakage 评审。
- Kimi-backed calibration records 只是 exploratory/tooling evidence。

主要来源：

- `llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md`
- `llm_grader_calibration_plan_or_report_20260517.zh.md`
- `evals/aichat/run_llm_grader_calibration.py`
- `evals/aichat/summarize_llm_grader_calibration.py`

## Appendix J. Evidence Manifest and Reproduction

目的：让 evidence package 可审计。

应包含：

- Manifest entry table:
  - claim_id；
  - report_file；
  - input_files；
  - script_used；
  - output_files；
  - checksum；
  - interpretation_boundary；
  - forbidden_wording。
- Reproduction commands:

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_submission.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 evals/aichat/validate_research_bilingual_docs.py --output-json /tmp/bilingual_docs_validation_submission.json
```

Known validator note:

- Bilingual docs validator 可能因 historical / legacy unpaired docs 失败。
- 新增 dialogue-state v3 paper-facing docs 应保持中英文成对。
- historical pairing debt 不改变主 evidence package 数字。

主要来源：

- `dialogue_state_v3_evidence_manifest_20260518.json`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`
- `evals/aichat/verify_dialogue_state_v3_reports.py`
- `evals/aichat/validate_research_bilingual_docs.py`

## Appendix K. Claim Gate

目的：防止 reviewer、collaborator 和 external AI 过度解读附录。

禁止的 appendix interpretations：

- 50-case set 是 final gold。
- all-50 aggregate 是 main headline。
- Guard-only rewrites 或 repairs final student-visible responses。
- Repair causality 由 main-condition means 单独证明。
- DBox+Repair 是 full main condition。
- DeepSeek 或任何 LLM grader 替代 human review。
- Taxonomy 只是 DP/check/lazy/tree/local-code。

附录末尾推荐句：

```text
The appendix provides sensitivity, stress-test, calibration, and artifact evidence for the dialogue-state v3 human-review package; it does not change the main headline slice, gold-label boundary, Guard/Repair interpretation, or LLM-grader limitation stated in the main paper.
```
