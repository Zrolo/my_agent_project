# 50-case AI 预评高风险教练复核包

本文件记录 `heldout_50_ai_reference_dev_20260513_merged` 的高风险抽样复核包。该包来自 50 个 held-out draft cases × 8 个系统条件的 AI preliminary review，共 400 条回复。它只用于开发阶段质量控制和教练复核优先级排序，不是 coach gold label，也不作为论文 headline result。

## 目的

全量 400 条盲评对教练负担较重。为了先检查最可能影响论文结论和系统安全的失败样本，我们从 AI 预评结果中抽出两份小包：

1. `high_risk_rows`：只包含 AI 预评判为高风险的 25 条回复，用于最快确认是否真的存在 major / answer leakage。
2. `high_risk_case_pack`：包含上述高风险回复所在 11 个 case 的全部 8 条系统回复，共 88 条，用于同题内比较不同条件是否真的有质量/泄露差异。

## 输入与输出

- 来源 run：`evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged`
- 全量 AI 预评表：`coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx`
- 高风险行 CSV：`coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_rows.csv`
- 高风险行盲评表：`coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_rows.zh.xlsx`
- 高风险行 key：`coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_rows.key.csv`
- 高风险 case pack CSV：`coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_case_pack.csv`
- 高风险 case pack 盲评表：`coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_case_pack.zh.xlsx`
- 高风险 case pack key：`coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_case_pack.key.csv`

`*.key.csv` 只给研究者使用，不给盲评教练。教练只看 `.zh.xlsx` 文件。

## 抽样规则

一条回复满足任一条件即进入 `high_risk_rows`：

- AI 预评泄露标签为 `major_bridge_leakage` 或 `answer_leakage`；
- AI 预评 `would_show_to_student=no`；
- AI 预评 `needs_discussion=yes`；
- AI 预评总体质量为 1 或 2。

然后把这些高风险回复所在的 case 全部展开为 8 条系统回复，形成 `high_risk_case_pack`。

## 规模

| 包 | 行数 | case 数 | 用途 |
| --- | ---: | ---: | --- |
| `high_risk_rows` | 25 | 11 | 最快确认 AI 预评高风险是否真实 |
| `high_risk_case_pack` | 88 | 11 | 同题比较 8 个系统条件，判断问题是否集中在特定条件 |

高风险行中，AI 预评泄露标签分布：

| 标签 | 数量 |
| --- | ---: |
| `answer_leakage` | 16 |
| `major_bridge_leakage` | 9 |

高风险行所在 case 分布：

| case_id | 高风险行数 |
| --- | ---: |
| `heldout_cp_044` | 7 |
| `heldout_cp_017` | 5 |
| `heldout_cp_039` | 3 |
| `heldout_cp_014` | 2 |
| `heldout_cp_019` | 2 |
| `heldout_cp_003` | 1 |
| `heldout_cp_024` | 1 |
| `heldout_cp_035` | 1 |
| `heldout_cp_036` | 1 |
| `heldout_cp_045` | 1 |
| `heldout_cp_048` | 1 |

高风险行按真实条件分布如下。该表只供研究者看，不应交给盲评教练。

| 条件 | 高风险行数 |
| --- | ---: |
| `current_system` + `tutor_only_no_diagnosis` | 6 |
| `bridge_contract` + `tutor_plus_guard` | 6 |
| `codehelp_codeaid_no_direct_solution_tutor` + `tutor_only_no_diagnosis` | 4 |
| `enhanced_prompt_only` + `tutor_only_no_diagnosis` | 4 |
| `bridge_contract` + `tutor_plus_guard_plus_repair` | 2 |
| `bridge_inspired_expert_decision_tutor` + `tutor_only_no_diagnosis` | 1 |
| `dbox_inspired_decomposition_tutor` + `tutor_plus_guard` | 1 |
| `single_llm_structured` + `tutor_plus_guard` | 1 |

## 教练复核建议

建议先做两步，而不是直接要求教练评完整 400 条：

1. 先评 `high_risk_rows.zh.xlsx`。目标是确认 AI 预评标出的 25 条是否真的存在 `major_bridge_leakage` / `answer_leakage`，以及哪些是误报。
2. 如果 25 条中确有集中失败，再评 `high_risk_case_pack.zh.xlsx`。目标是在同一个 case 下比较 8 个匿名系统回复，判断是某个条件普遍更差，还是该 case 本身过难/标注边界不清。

复核时重点看：

- 是否真的替学生补完了当前关键桥；
- 是否只是给了合理背景，而不是泄露；
- 是否因为学生直接要完整代码/答案而应当安全拒答；
- micro-example 是否从“引导观察”变成了“完整演示答案”；
- 修复/Guard 条件是否只是更保守，还是实际保留了教学推进价值。

## 如何使用结论

如果教练确认 AI 预评误报很多：

- 不要直接修改 tutor prompt；
- 先校准 AI 预评规则、static lint 和 leakage rubric；
- 把误报样本加入 Judge calibration set。

如果教练确认高风险集中在某些条件：

- 把对应 case 加入 prompt regression；
- 检查该条件的 prompt 是否仍有 answer-slot、filled-trace 或 worked-example 泄露模式；
- 只在 dev set 上修 prompt，正式 held-out 前冻结。

如果教练确认高风险集中在某些 case：

- 检查 case 的 `missing_bridge`、`forbidden_content` 和 `success_criteria` 是否过严或不清；
- 必要时进入 adjudication，而不是直接判系统失败。

## 当前结论

这一步说明 50-case × 8-condition dev run 已经可以进入“目标教练复核”阶段。下一步不是继续加 baseline，而是让教练优先复核 25 条高风险回复，确认 AI 预评是否可靠；再决定是否需要 full 400 条盲评或只做分层抽样。
