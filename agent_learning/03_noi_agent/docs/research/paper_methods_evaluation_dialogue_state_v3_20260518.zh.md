# Paper Methods / Evaluation Draft: Dialogue-State v3 20260518

## 1. 研究对象与边界

CP-MissingBridgeBench 评估的是算法竞赛逐轮辅导中的一个具体问题：学生已经表达了部分思路或卡点，但还缺少从当前已知信息到下一步解题动作之间的关键推理桥。我们称这类缺口为 missing bridge。

本文的 dialogue-state v3 evidence package 聚焦 turn-level tutor response evaluation。每个样本包含题目上下文、近期对话、学生当前问题、case-specific rubric 和多个 tutor harness 的候选回复。该评测不声称覆盖所有算法竞赛辅导情景，也不验证线上 active-mode 系统；它是一个 formal human-review evidence candidate，用于比较不同离线 tutoring harness 的 quality-safety-burden trade-off。

主论文 headline 只使用 `main_scaffold_eval` slice。`main_eval_with_caution`、`clarification_safety_slice`、`policy_safety_slice` 和 all-50 aggregate 只作为 sensitivity / appendix。

## 2. 核心概念

### Missing Bridge

Missing bridge 是学生当前还没有跨过去、但完成下一步解题动作所必需的认知桥。它不是某个固定算法标签，而是当前学生状态下的局部推理缺口。例如，同一个 DP 题可能在不同学生轮次中对应状态语义、转移来源、边界初始化、正确性解释或代码调试等不同桥梁。

### Critical Bridge Leakage

Critical bridge leakage 指 tutor 没有直接给完整代码或完整题解，却提前替学生说穿了本应由学生自己推出的关键中间推理。它不同于普通信息量：合格辅导可以提供上下文、轻提示、检查问题或低负担下一步；泄露风险来自过早完成当前 missing bridge。

### Taxonomy Framing

本文使用三层 taxonomy：

```text
cognitive bridge family + leakage mechanism + surface anchor
```

`state_representation_semantics`、`transition_recurrence_source`、`predicate_check_semantics` 等是 operational cognitive bridge families。DP state、binary-search check、lazy propagation、tree difference、local code、greedy proof、debugging trace 等是 surface anchors，用来说明同一种认知桥和泄露机制在具体算法语境中的实例。论文不应把 benchmark 写成只评估 DP/check/lazy/差分/局部代码这些小场景。

## 3. Dataset And Slices

Dialogue-state v3 包含 50 个 reviewed candidate cases。每个 case 都保留学生当前轮次的对话状态，而不是只给孤立题目和问题。50 cases 按论文用途分为：

| slice | case_n | paper use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | 主脚手架质量、泄露和学生负担比较 |
| `main_eval_with_caution` | 5 | sensitivity / appendix |
| `clarification_safety_slice` | 10 | 澄清、不脑补和上下文不足时的安全询问 |
| `policy_safety_slice` | 4 | 学生直接要答案/代码时的安全重定向 |

这个分层是结果解释的一部分。主表不把四类 case 混成一个 headline 平均。

## 4. Case-Specific Rubric

每条 case 在评分前先固定 case-specific rubric，至少包含：

- `success_criteria`：本轮合格辅导应该帮助学生达成什么；
- `forbidden_content`：当前不应提前暴露的关键桥、答案或代码；
- `critical_bridge_boundary`：哪些内容属于当前 missing bridge 的边界；
- `acceptable_reveal`：哪些轻提示、澄清或背景解释是允许的；
- `expected_student_next_action`：学生看完后最合理的低负担下一步。

这个设计使评审不是按泛泛的“是否像好老师”打分，而是按当前学生状态、题目上下文和本轮教学目标评价回复。

## 5. Conditions

主 human review 比较 7 个匿名 condition，共 350 条回复。教练盲评时不看 condition 名称。论文可以在解盲后描述为：

| condition | role | interpretation boundary |
| --- | --- | --- |
| `enhanced_prompt_only_clean` | strong prompt-only baseline | 强教学提示词 baseline，不含 case-specific Bridge Contract。 |
| `codehelp_codeaid_clean` | no-direct-solution programming-help baseline | 检验“不直接给代码/题解”是否足以避免 critical bridge leakage。 |
| `dbox_inspired_clean` | literature-inspired decomposition baseline | DBox-inspired 单轮分解式脚手架，不声称复现 DBox。 |
| `dbox_inspired_guard` | DBox-inspired + guard-instrumented variant | Guard-only 在当前主实验中主要提供 runtime leakage signal，不改写最终回复。 |
| `bridge_guided_dbox_style_guard` | bridge-guided decomposition variant | 用 bridge signal 引导 DBox-style 回复；仍是 guard-instrumented 条件。 |
| `bridge_contract_compact_guard` | Bridge Contract compact + guard-instrumented method | 使用 compact bridge contract 和 guard signal；Guard-only 不是 rewrite condition。 |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard/Repair method | 学生可见回复可来自 Repair stage；主实验均值说明 condition-level trend，不单独证明 Repair 因果。 |

这些 condition 都是离线 evaluation harness，不等于线上默认 AIChat。

## 6. Human Review Protocol

Coach A 和 Coach B 都完成了 350 条全量盲评。评分流程是：

1. 阅读题目上下文和必要题面。
2. 阅读 case-specific rubric。
3. 阅读近期对话和学生当前问题。
4. 只评价待评分 AI 回复。
5. 填写主指标、诊断指标和可靠性字段。
6. 对高风险情况写强制备注。

强制备注包括 major / answer leakage、`show=no`、`overall_quality<=2`、同题排序第一或最后、低置信度和需要讨论的样本。

Coach A、Coach B 和 priority60 adjudication 都是 expert reference / adjudicated sensitivity view，不能称为 gold。A/B disagreement 被视为 pedagogical judgment 的真实敏感性，而不是评测失败；论文通过双评、priority adjudication、slice analysis 和 sensitivity analysis 报告这种不确定性。

## 7. Metrics

主指标包括：

| metric | role |
| --- | --- |
| `overall_quality` | 1-5 总体辅导质量判断 |
| `student_ready_pass` | 综合判断是否愿意给学生看 |
| `safe_ready_pass` | 安全与可用性门槛 |
| `critical_leakage_label` | `no_leakage` / `minor_bridge_leakage` / `major_bridge_leakage` / `answer_leakage` |
| `scaffold_sufficiency` | 防止“安全但没帮助” |
| `student_response_burden` | 学生下一轮需要付出的输入和推理负担 |

诊断指标用于解释错误和校准 LLM grader，不作为唯一胜负依据。它们包括是否抓住卡点、是否贴合题目/对话、帮助强度是否合适、下一步是否清楚、是否保持单一焦点和桥梁导向微型例子。

## 8. Analysis Plan

论文结果按证据类别组织：

| evidence class | use |
| --- | --- |
| main result | `main_scaffold_eval` + priority60 adjudicated + Coach A 主口径 |
| sensitivity | Coach A only、Coach B only、priority60 + Coach A、priority60 + Coach B、all-case appendix |
| slice analysis | main scaffold、caution、clarification safety、policy safety 分开报告 |
| paired uncertainty | 同 case 条件比较的 W/T/L、mean delta、bootstrap CI 和 permutation test |
| stress test | Repair same-candidate before/after 因果压力测试 |
| fairness sensitivity | DBox+Repair 20-case targeted add-on |
| calibration | DeepSeek LLM grader calibration，作为 auxiliary grader 评估 |

配对比较至少报告 win/tie/loss、mean delta、safe-ready delta、major+answer leakage delta 和 uncertainty。若 CI 跨 0，应写成 favorable trend / trade-off，而不是 significant dominance。

## 9. Repair And Guard Interpretation

Guard-only 条件在当前主实验中主要是 guard-instrumented / guard-checked condition：它提供 leakage risk signal；除非触发 block fallback，否则不会改写最终学生可见回复。因此不能写成 Guard-only 修复了最终输出。

Repair 的因果证据来自 same-candidate before/after stress test。该测试固定同一个原始 candidate，并盲化比较 before_repair 与 after_repair。主实验中的 `bridge_contract_compact_guard_repair` 只能说明 repair-enabled condition 的 condition-level trend；不能单独证明 Repair 因果有效。

## 10. Reproducibility

主证据链由 evidence manifest 和复算脚本固定：

- `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`
- `evals/aichat/verify_dialogue_state_v3_reports.py`

投稿前应运行：

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_final.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
```

## 11. Paper-Safe Wording

可以写：

- CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
- DBox-inspired decomposition is a strong baseline.
- Bridge Contract compact + Guard/Repair shows favorable overall and critical-leakage-control trends under the primary human-review view.
- No-direct-solution prompting does not eliminate critical bridge leakage.
- Human review remains necessary; LLM graders are auxiliary only.

不能写：

- Bridge Contract 显著全面优于所有 baseline。
- Guard-only 修复了最终输出。
- Repair 的因果作用已由主实验均值单独证明。
- priority60 或任一教练标签是 gold。
- all-50 aggregate 是主 headline。
- 当前 50-case set 覆盖所有 CP tutoring 情景。
