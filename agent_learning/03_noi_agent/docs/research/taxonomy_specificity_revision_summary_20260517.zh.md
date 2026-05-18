# Taxonomy Specificity Revision Summary 20260517

## 目标

本轮只完成 P0/P1 文档与 reviewer-facing wording 修改，不新增实验、不修改线上系统、不改主实验数据、不扩 annotation dropdown。

核心口径调整为：

```text
cognitive bridge family + leakage mechanism + surface anchor
```

其中 `state_representation_semantics`、`transition_recurrence_source`、`predicate_check_semantics` 等 bridge bucket 是 Research v1 的 operational cognitive bridge families；DP state、binary-search check、lazy propagation、tree difference、local code 等具体算法实例才是 surface anchors。

## 修改文件

| 文件 | 修改内容 |
| --- | --- |
| `docs/research/evaluation_protocol_v3.zh.md` | 将 Case memo 从“micro-example / 状态转移 check 边界 / 局部代码”等具体场景，上提为 direct bridge completion、answer-slot compression、worked-trace completion、local implementation completion、proof/invariant completion、decision-rule completion、debugging diagnosis completion、modeling-plan completion、over-constrained scaffold 等 leakage mechanisms；补充 bridge bucket 与 surface anchor 的区别。 |
| `docs/research/evaluation_protocol_v3.md` | 同步英文版 Case Memo wording。 |
| `docs/research/response_review_rubric_v3.zh.md` | 新增“泄露机制不是算法类别”小节，明确 leakage label 判断的是是否替学生完成 current missing bridge，而不是题目属于哪种算法；列出抽象 leakage mechanisms。 |
| `docs/research/response_review_rubric_v3.md` | 同步英文版 rubric wording。 |
| `docs/research/dialogue_state_v3_human_review_result_packet_20260517.zh.md` | 新增 “Taxonomy Scope” 小节，说明 dialogue-state v3 50-case 是按 operational cognitive bridge families 采样，不是算法题型清单；明确 surface anchors 与 coverage limitations。 |
| `docs/research/dialogue_state_v3_human_review_result_packet_20260517.md` | 同步英文版 Taxonomy Scope。 |
| `docs/research/paper_results_interpretation_guardrails_20260517.zh.md` | 新增 “Taxonomy / Coverage Guardrail”，规定论文不能写成只评估 DP/check/lazy/差分/局部代码；应写为 operational cognitive bridge families + leakage mechanisms，并报告 coverage limitations。 |
| `docs/research/paper_results_interpretation_guardrails_20260517.md` | 同步英文版 guardrail。 |
| `docs/research/coach_blind_review_instructions_v1.zh.md` | 在常见边界情况前新增说明：后续例子是 surface anchors，不是穷尽 taxonomy；补充 proof/invariant、debugging diagnosis、modeling relation、complexity bottleneck 也可能泄露的边界例。 |
| `docs/research/coach_blind_review_instructions_v1.md` | 同步英文版 reviewer instruction wording。 |
| `evals/aichat/export_coach_response_review_workbook_xlsx.py` | 修改人审工作簿 instruction 文案：新增 taxonomy 分层说明；把 DP/lazy/check 等例子改写为“抽象类别 + concrete surface anchor example”；补充 proof/debug/modeling/complexity 的泄露风险例。 |
| `evals/aichat/coach_labeling_schema_v2.py` | 仅修改 `critical_bridge_completion_risk` 描述，把“状态、转移、check 或公式”扩展为“表示语义、关系建模、转移/动作映射、判定语义、更新顺序、贡献汇总、正确性理由、调试定位或局部实现”。未新增 dropdown 项。 |

## 未改历史报告

以下历史结果/运行产物没有批量修改：

- `evals/aichat/ad_hoc_runs/*/*analysis*.md`
- `docs/research/dev_ablation_bridge_contract_cases_20260511.zh.md`
- `docs/research/repair_stress_v1_all20_report_20260511.zh.md`
- `docs/research/repair_stress_v1_all20_report_20260511.md`

原因：

1. 它们是 historical memo / dev seed / stress report，不是当前论文主 taxonomy 定义。
2. 批量改历史报告会模糊当时实验记录，不利于追溯。
3. 新增的 result packet、evaluation protocol、rubric 和 paper guardrails 已明确说明：历史 error memo 中的 DP/check/lazy/code 说法是 surface-anchor 快速诊断标签，不是完整 taxonomy。

## 当前论文应如何描述 taxonomy

建议论文这样写：

```text
CP-MissingBridgeBench evaluates open-ended tutor responses through operational cognitive bridge families and leakage mechanisms. Bridge families such as representation semantics, transition/action mapping, predicate/decision semantics, ordering/dependency, modeling relations, aggregation/contribution accounting, data-structure operation mapping, correctness/invariant reasoning, implementation/debugging evidence, and policy-request handling describe the student’s local learning bottleneck. Concrete algorithm patterns such as DP states, binary-search checks, lazy propagation, tree-difference marking, greedy proofs, debugging traces, or local code snippets are surface anchors that instantiate these families.
```

中文写法：

```text
CP-MissingBridgeBench 的 taxonomy 不是算法清单，而是围绕学生当前学习瓶颈建立的 operational cognitive bridge families 与 tutor leakage mechanisms。DP 状态、二分 check、lazy propagation、树上差分、贪心证明、调试 trace 或局部代码只是具体算法语境中的 surface anchors。
```

论文中可以保留 concrete examples，但必须把它们放在 “surface anchor examples” 层，不要把它们写成 benchmark 的完整覆盖边界。

## 当前 Coverage Limitations

当前 dialogue-state v3 50-case set 覆盖较充分的 family 包括：

- representation semantics；
- transition / action mapping；
- predicate / decision semantics；
- ordering / dependency control；
- modeling relation；
- aggregation / contribution accounting；
- data-structure operation mapping；
- correctness / invariant reasoning；
- implementation boundary；
- debugging evidence；
- policy-request handling。

仍需正面报告的 coverage limitations：

- math property / modular invariant；
- counting / inclusion-exclusion；
- geometry predicate relation；
- search pruning / deduplication；
- reflection / transfer；
- richer multi-turn debugging diagnosis；
- broader non-DP/non-data-structure mathematical reasoning cases。

这些 limitation 不推翻当前结果，但会限制论文主张范围。当前最稳写法是：Research v1 覆盖了一组高风险 CP tutoring cognitive bridge families，并证明 CP-MissingBridgeBench 能揭示质量、安全和学生负担 trade-off；更完整的 algorithm-domain coverage 是后续扩展。
