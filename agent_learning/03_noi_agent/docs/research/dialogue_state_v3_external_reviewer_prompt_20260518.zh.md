# Dialogue-State v3 External Reviewer Prompt 20260518

下面这段可以直接复制给另一个 AI / reviewer。它的目标是让对方从 GitHub 项目真实文件出发，复核 CP-MissingBridgeBench 当前 dialogue-state v3 evidence package，而不是依赖聊天摘要。

```text
你现在作为 CP-MissingBridgeBench 项目的外部方法审稿人、统计复核人和论文结果解释审稿人工作。

请不要只根据我给你的描述判断。请先打开 GitHub 项目：

Repository: https://github.com/Zrolo/my_agent_project
Branch: codex/bridge-research-annotation
Project path: agent_learning/03_noi_agent
Primary review target:
Commit 33a5dd7 Add dialogue-state v3 evidence package gates.

If the branch tip is newer than 33a5dd7, first audit the fixed evidence package at 33a5dd7, then separately note whether newer commits change evidence files, reproduction scripts, or paper wording. Do not silently mix commits.

你的任务不是新增实验、不是改线上系统、不是修改 prompt、不是重跑 active mode。当前目标是复核 dialogue-state v3 证据包是否可投稿、可追踪、不过度解释。

Non-goals:

- 不要新增实验 condition。
- 不要修改线上 AIChat、active mode、prompt 或主实验数据。
- 除非明确标为 future work，否则不要提出新增模块；本次任务是 evidence validation，不是 system expansion。
- 不要把 sensitivity analysis、stress test 或 calibration 写成 main result。
- 如果 raw CSV/JSONL 或 reproduction scripts 与报告摘要冲突，不要根据摘要推断结论。

请优先阅读：

1. docs/research/dialogue_state_v3_external_review_handoff_20260518.zh.md
2. docs/research/index.md
3. docs/research/dialogue_state_v3_evidence_manifest_20260518.json
4. docs/research/dialogue_state_v3_paper_claims_final_gate_20260518.zh.md
5. docs/research/project_status_after_taxonomy_revision_20260517.zh.md
6. docs/research/evaluation_protocol_v3.zh.md
7. docs/research/response_review_rubric_v3.zh.md
8. docs/research/dialogue_state_v3_main_paper_ready_tables_20260517.zh.md
9. docs/research/dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md
10. docs/research/human_review_reliability_section_draft_20260517.zh.md
11. docs/research/paper_results_discussion_manuscript_dialogue_state_v3_20260518.zh.md
12. docs/research/repair_same_candidate_stress_result_20260517.zh.md
13. docs/research/dbox_guard_repair_fairness_report_20260517.zh.md
14. docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md

如果你可以运行代码，请在 agent_learning/03_noi_agent 下运行：

python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 -m json.tool docs/research/dialogue_state_v3_evidence_manifest_20260518.json >/tmp/dialogue_state_v3_evidence_manifest_check.json

如果脚本成功，请报告：

- command；
- exit status；
- key output files；
- reproduced numbers 是否与 reports 一致；
- 是否有 mismatched claim IDs。

如果脚本失败，请报告 exact failure stage，并说明该失败是否阻塞 evidence review。

请重点判断：

1. Evidence manifest 是否足够把论文 claim 追溯到 report / input / script / output / checksum？
2. 主 headline 是否只使用 main_scaffold_eval slice，而不是 all 50 cases 混合平均？
3. 当前结果是否只支持 trade-off / favorable trend，而不是 absolute winner / significant dominance？
4. Guard-only 是否被正确写成 guard-instrumented / runtime signal，而不是 rewrite / repair condition？
5. Repair 的因果证据是否只来自 same-candidate before/after stress，而不是主实验均值？
6. DBox+Repair 是否只是 targeted fairness sensitivity，而不是完整主实验 condition？
7. DeepSeek LLM grader 是否只作为 auxiliary grader，而不是替代人类教练？
8. taxonomy 是否稳定为 cognitive bridge family + leakage mechanism + surface anchor，避免被看成只针对 DP/check/lazy/tree/local-code 的特调？
9. Coach A / Coach B / priority60 adjudication 是否被正确写成 human-review evidence candidate，而不是 final gold？
10. 论文 Results / Discussion 最可能被严格审稿人攻击的 3 个点是什么？

请把每个 evidence item 分类为：

- main result；
- sensitivity analysis；
- stress test；
- calibration；
- future-work support。

请输出：

Verdict:
- ready / needs minor revision / needs major revision

Blocking issues:
- ...

Non-blocking issues:
- ...

Overclaim risks:
- ...

Evidence-chain risks:
- ...

Claim-by-claim audit table:

| Claim | Supported? yes/partial/no | Evidence files/scripts | Main/sensitivity/stress/calibration | Risk | Safer wording |
| --- | --- | --- | --- | --- | --- |

Recommended minimal fixes:
- ...

请特别注意以下禁止表述：

- 不要说 Bridge Contract 全面显著优于所有 baseline。
- 不要说 Guard-only 修复了最终输出。
- 不要说 Repair 的因果效果已由主实验 condition 均值证明。
- 不要说 Coach A、Coach B 或 priority60 adjudicated labels 是 final gold。
- 不要说 all 50 cases aggregate 是 headline。
- 不要说 DBox+Repair 已完成 full 50-case double-coach validation。
- 不要说 LLM grader 可以替代人类教练。

当前最安全论文口径是：

CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
DBox-inspired decomposition is a strong baseline.
Bridge Contract compact + Guard/Repair shows favorable overall and critical-leakage-control trends under the primary human-review view, but paired uncertainty supports trend/trade-off wording rather than broad significant dominance.
Guard-only is instrumentation, not final-response rewrite.
Repair has same-candidate causal evidence for leakage reduction, with student-burden trade-off.
DBox+Repair is targeted fairness sensitivity, not a full main condition.
Human review and adjudication remain necessary; LLM graders are auxiliary only.
```
