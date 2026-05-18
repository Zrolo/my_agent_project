# Dialogue-State v3 External Review Handoff 20260518

本文档是给外部 AI / 人类 reviewer 的入口。它不新增实验、不修改线上系统、不改变主实验数据；目标是让 reviewer 能独立复核 dialogue-state v3 evidence package 是否可投稿、可追踪、不过度解释。

## 审核对象

- Repository: `https://github.com/Zrolo/my_agent_project`
- Branch: `codex/bridge-research-annotation`
- Primary review target: `33a5dd7 Add dialogue-state v3 evidence package gates`
- Branch-tip policy: 如果 branch tip 晚于 `33a5dd7`，请先审固定 evidence package，再单独说明后续 commit 是否改变 evidence、scripts 或 paper wording。
- Project path inside repo: `agent_learning/03_noi_agent`
- Paper working title:

```text
CP-MissingBridgeBench:
Turn-level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation
for LLM Tutors in Competitive Programming
```

当前状态是 `formal human-review evidence candidate`，不是 `final gold`。主 headline 只能使用 `main_scaffold_eval` slice；不要把 all 50 cases 混成一个 headline 平均。

## Reviewer Non-Goals

请不要做以下事情：

- 不要新增实验 condition。
- 不要改线上 AIChat 或 active mode。
- 不要修改 prompt、主实验数据或 held-out 数据。
- 不要把 Coach A、Coach B 或 priority60 adjudicated merge 称为 gold。
- 不要把 Guard-only 写成 rewrite / repair condition。
- 不要把 DBox+Repair 20-case add-on 写成完整主实验。
- 不要用 LLM grader 替代人类教练。
- 除非明确标为 future work，否则不要提出新增模块；本次任务是 evidence validation，不是 system expansion。
- 不要把 sensitivity analysis、stress test 或 calibration 写成 main result。

## 推荐阅读顺序

### 1. 总入口与 claim gate

先读：

- `docs/research/index.md`
- `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`
- `docs/research/dialogue_state_v3_paper_claims_final_gate_20260518.zh.md`
- `docs/research/project_status_after_taxonomy_revision_20260517.zh.md`

目标：确认当前项目状态、证据 manifest、允许/禁止论文表述。

### 2. 评测协议与 taxonomy

再读：

- `docs/research/evaluation_protocol_v3.zh.md`
- `docs/research/response_review_rubric_v3.zh.md`
- `docs/research/baseline_protocol_v1.zh.md`
- `docs/research/dialogue_state_v3_observed_error_taxonomy_20260517.zh.md`
- `docs/research/taxonomy_specificity_revision_summary_20260517.zh.md`

重点检查 taxonomy 是否稳定为：

```text
cognitive bridge family + leakage mechanism + surface anchor
```

其中 bridge bucket 是 operational cognitive bridge family，DP state / binary-search check / lazy propagation / tree difference / local code 是 surface anchor，不是 taxonomy 本体。

### 3. 主结果和解释边界

重点读：

- `docs/research/dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`
- `docs/research/dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md`
- `docs/research/human_review_reliability_section_draft_20260517.zh.md`
- `docs/research/paper_results_discussion_manuscript_dialogue_state_v3_20260518.zh.md`
- `docs/research/paper_results_discussion_section_dialogue_state_v3_20260518.zh.md`

重点判断：

- main scaffold headline 是否只使用 31-case `main_scaffold_eval`。
- paired uncertainty 是否阻止了“显著全面胜出”的强表述。
- Coach A/B disagreement 是否被正面报告，而不是隐藏。

### 4. Guard / Repair / DBox fairness / LLM grader

重点读：

- `docs/research/paper_results_interpretation_guardrails_20260517.zh.md`
- `docs/research/repair_same_candidate_stress_result_20260517.zh.md`
- `docs/research/dbox_guard_repair_fairness_report_20260517.zh.md`
- `docs/research/dbox_repair_fairness_extension_plan_20260518.zh.md`
- `docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md`

必须检查：

- Guard-only 是否只被解释为 guard-instrumented / runtime signal。
- Repair 因果证据是否只来自 same-candidate stress。
- DBox+Repair 是否只作为 targeted fairness sensitivity。
- DeepSeek LLM grader 是否只作为 auxiliary grader。

### 5. 实现与机器可读证据

复核脚本：

- `evals/aichat/reproduce_dialogue_state_v3_tables.py`
- `evals/aichat/verify_dialogue_state_v3_reports.py`
- `evals/aichat/run_bridge_offline_eval.py`
- `evals/aichat/prepare_llm_grader_calibration_pack.py`
- `evals/aichat/run_llm_grader_calibration.py`
- `evals/aichat/summarize_llm_grader_calibration.py`
- `evals/aichat/summarize_repair_same_candidate_stress.py`

机器可读结果入口：

- `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/`
- `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/`
- `docs/research/llm_grader_calibration_*deepseek_20260518.*`

## 建议复算命令

在 `agent_learning/03_noi_agent` 下运行：

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 -m json.tool docs/research/dialogue_state_v3_evidence_manifest_20260518.json >/tmp/dialogue_state_v3_evidence_manifest_check.json
```

如果脚本成功，请报告 command、exit status、key output files、reproduced numbers 是否与 reports 一致，以及是否有 mismatched claim IDs。如果脚本失败，请报告 exact failure stage，并说明该失败是否阻塞 evidence review。

可选双语检查：

```bash
python3 -m evals.aichat.validate_research_bilingual_docs --output-json /tmp/dialogue_state_v3_bilingual_check.json
```

已知限制：双语检查当前会因 4 个历史 `20260516 integrity` 文档缺中文配对和 23 个 legacy unpaired 文档失败。请重点确认本 handoff 及 20260518 新增 Markdown 是否成对。

## Reviewer Questions

请给出明确结论：

1. Evidence manifest 是否足够追踪每个 claim 的 report / input / script / output / checksum？
2. `verify_dialogue_state_v3_reports.py` 是否覆盖了论文核心数字？还缺哪些应 gate 的数字？
3. 主结果是否能支持 “trade-off / favorable trend in overall and critical-leakage control”，而不是 “absolute winner”？
4. Guard-only 是否仍存在被误写成 rewrite 的风险？
5. Repair same-candidate stress 是否足以支持因果解释？哪些 wording 仍过强？
6. DBox+Repair 20-case add-on 是否足以作为 fairness sensitivity？如果不足，是选 Option A、B 还是 C？
7. DeepSeek LLM grader calibration 是否正确写成 auxiliary grader，而非 replacement？
8. taxonomy 是否仍有被审稿人认为“具体算法特调”的风险？
9. 当前 Results / Discussion 草稿中最可能被严格审稿人攻击的 3 个点是什么？
10. 最低成本的修订建议是什么？

## Reviewer Output Format

建议输出：

```text
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
```

## Current Safe Interpretation

当前最稳论文解释是：

```text
CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
DBox-inspired decomposition is a strong baseline.
Bridge Contract compact + Guard/Repair shows favorable overall and critical-leakage-control trends under the primary human-review view, but most paired CIs support trend/trade-off wording rather than significant dominance.
Guard-only is instrumentation, not final-response rewrite.
Repair has same-candidate causal evidence for leakage reduction, with student-burden trade-off.
DBox+Repair is targeted fairness sensitivity, not a full main condition.
Human review and adjudication remain necessary; LLM graders are auxiliary only.
```
