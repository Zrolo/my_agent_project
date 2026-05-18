# Paper Citation Checklist / Bibliography Audit: Dialogue-State v3 20260518

## 使用边界

本文档把 Introduction / Related Work 中的 citation TODOs 转成可核对清单。它不新增实验、不修改数据、不接入线上系统。所有外部引用仍需在投稿前从论文 PDF / proceedings / BibTeX 再核对一次。

引用原则：

- 外部论文用于定位相关工作，不能用来支撑我们自己的实验结果。
- DBox、EDF/Copa、CodeHelp/CodeAid、Bridge、MRBench、MathDial 都只能按实际匹配范围引用。
- 不能声称完整复现任何相关工作，除非公开代码、数据、设置和评测协议都实际匹配。
- LLM-as-judge / rubric work 只能支撑“自动评审和 rubric-based evaluation 是相关方向”，不能支撑“LLM grader 可替代人类教练”。
- Anthropic agent eval 文章可作为工程方法论参考，不应替代同行评审学术引用。

## 1. Citation Placeholders To Resolve

| placeholder | candidate citations | use for | do not use for |
| --- | --- | --- | --- |
| `[TODO: MathDial / Socratic tutoring citations]` | MathDial; MRBench; optional Bridge novice-expert decision paper | LLM tutoring dialogue、pedagogical scaffolding、mistake remediation 和 tutor-response evaluation 背景。 | 不要说这些工作覆盖 CP missing bridge 或 critical bridge leakage。 |
| `[TODO: CodeHelp / CodeAid / programming-help citations]` | CodeHelp; CodeAid | no-direct-solution / no-direct-code guardrails 和 programming classroom assistant 背景。 | 不要说它们已经解决 critical bridge leakage。 |
| `[TODO: DBox citation]` | DBox arXiv / ACM CHI paper; local DBox official-materials review | step-tree / co-decomposition / decomposition tutoring 背景；支撑 DBox-inspired baseline。 | 不要写 we reproduce DBox；不要直接比较我们的单轮结果和 DBox learning-gain study。 |
| `[TODO: EDF/Copa citation]` | EDF/Copa arXiv paper; official supplementary materials repo | evidence-decision-feedback adaptive scaffolding 和 learner-state modeling 背景。 | 不要写 we reproduce Copa/EDF；不要把 Copa classroom results 当作我们的 CP tutoring result。 |
| `[TODO: LLM-as-judge / rubric evaluation citations]` | MT-Bench / Chatbot Arena LLM-as-judge; Prometheus; MRBench evaluator analysis; Rubrics as Rewards | LLM grader、rubric-based evaluation、custom scoring rubric 的相关工作。 | 不要说 LLM grader 是 gold；不要说我们做了 rubric-reward RL。 |
| `[TODO: agent eval citations]` | Anthropic “Demystifying evals for AI agents”; internal `agent_eval_methodology_v1` | harness-level eval、trace/outcome/grader 分层、deterministic + LLM + human grader 组合。 | 不要把工程博客当作唯一学术证据；不要把 runtime guard 当 offline grader。 |

## 2. Candidate External Sources

| short key suggestion | source | checked URL | paper-safe use | boundary |
| --- | --- | --- | --- | --- |
| `macina2023mathdial` | MathDial: A Dialogue Tutoring Dataset with Rich Pedagogical Properties Grounded in Math Reasoning Problems | https://arxiv.org/abs/2305.14536 | 引用 math tutoring dialogue dataset、human teacher + LLM-simulated student collection、pedagogical dialogue background。 | 不覆盖 programming / CP missing bridge；不要用来支撑我们的 CP 结果。 |
| `maurya2024mrbench` | Unifying AI Tutor Evaluation / MRBench | https://arxiv.org/abs/2412.09416 | 引用 AI tutor response evaluation taxonomy、human-annotated pedagogical dimensions、LLM evaluator reliability discussion。 | 主要是数学 mistake/confusion domain；不要说它评估 CP tutoring 或 critical bridge leakage。 |
| `wang2023bridge` | Bridging the Novice-Expert Gap via Models of Decision-Making | https://arxiv.org/abs/2310.10648 | 引用 expert decision modeling、student error / remediation strategy / intention before response generation。 | 它是 math mistake remediation；不要和本项目 Bridge Contract 混成同一个方法。 |
| `liffiton2023codehelp` | CodeHelp: Using Large Language Models with Guardrails for Scalable Support in Programming Classes | https://arxiv.org/abs/2308.06921 | 引用 programming class LLM assistant、guardrails、without directly revealing solutions。 | 不要说 CodeHelp 能防 critical bridge leakage；它是 no-direct-solution baseline anchor。 |
| `kazemitabaar2024codeaid` | CodeAid: Evaluating a Classroom Deployment of an LLM-based Programming Assistant that Balances Student and Educator Needs | https://arxiv.org/abs/2401.11314 | 引用 classroom deployment、avoid direct responses while encouraging learning、transparency/control。 | 不要说 CodeAid 与我们的 benchmark protocol 一致；不要称为 faithful reproduction。 |
| `ma2025dbox` | DBox: Scaffolding Algorithmic Programming Learning through Learner-LLM Co-Decomposition | https://arxiv.org/abs/2502.19133 | 引用 interactive step-tree、learner-LLM co-decomposition、algorithmic programming scaffolding。 | 我们只做 DBox-inspired single-turn baseline；不复现 UI、多轮、progressive reveal 或 learning-gain study。 |
| `cohn2026edf` | Evidence-Decision-Feedback: Theory-Driven Adaptive Scaffolding for LLM Agents | https://arxiv.org/abs/2602.01415 | 引用 evidence -> decision -> feedback adaptive scaffolding、Copa、learner-state-aware feedback。 | EDF/Copa 是 multi-turn STEM+C / classroom context；本项目不是 direct reproduction。 |
| `zheng2023llmjudge` | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | https://arxiv.org/abs/2306.05685 | 引用 LLM-as-judge as scalable evaluation direction and known bias/limitation concerns。 | 不要用它证明 DeepSeek grader 在本任务可靠；本项目 calibration 显示 critical recall 风险。 |
| `kim2023prometheus` | Prometheus: Inducing Fine-grained Evaluation Capability in Language Models | https://arxiv.org/abs/2310.08491 | 引用 custom rubric / reference material for fine-grained evaluator LMs。 | 不要说 Prometheus 或任何 LLM grader 可替代本项目人审。 |
| `gunjal2025rar` | Rubrics as Rewards: Reinforcement Learning Beyond Verifiable Domains | https://arxiv.org/abs/2507.17746 | 引用 instance-specific rubrics and multi-criteria judgments as related direction。 | 本项目不做 RL，不把 rubric 分数当 reward。 |
| `anthropic2026agentevals` | Demystifying evals for AI agents | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | 引用 harness-level eval、trace/outcome/grader 分层、deterministic/LLM/human grader 组合的工程方法论。 | 工程文章，不应作为唯一学术 citation；投稿时最好配合学术 eval references。 |

## 3. Internal Evidence Citations

| paper claim | cite internal docs | note |
| --- | --- | --- |
| CP-MissingBridgeBench 的 scope 和 claim boundary | `paper_scope_v2.zh.md`; `dialogue_state_v3_paper_claims_final_gate_20260518.zh.md` | 这些是项目内部 claim gate，不是外部 citation。 |
| Methods / Evaluation | `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md`; `evaluation_protocol_v3.zh.md`; `response_review_rubric_v3.zh.md` | 支撑 missing bridge、critical bridge leakage、case-specific rubric 和 metrics。 |
| Results / Discussion | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.zh.md` | 论文正文压缩结果草稿。 |
| Main tables and pairwise uncertainty | `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`; `dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md` | 只用 `main_scaffold_eval` 做 headline。 |
| Human review reliability | `human_review_reliability_section_draft_20260517.zh.md`; A/B agreement JSON | Coach A/B/priority60 不是 gold。 |
| Repair causality | `repair_same_candidate_stress_result_20260517.zh.md` | 因果措辞只来自 same-candidate stress。 |
| DBox+Repair fairness | `dbox_guard_repair_fairness_report_20260517.zh.md` | targeted 20-case sensitivity，不是 full main condition。 |
| LLM grader limitation | `llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md` | DeepSeek priority60 critical recall = 0。 |
| Reproducibility | `dialogue_state_v3_evidence_manifest_20260518.json`; `reproduce_dialogue_state_v3_tables.py`; `verify_dialogue_state_v3_reports.py` | 用于 artifact / appendix。 |

## 4. BibTeX Work Items

投稿前需要完成：

1. 从 arXiv / ACL Anthology / ACM DL / DOI 页面导出 BibTeX。
2. 统一 citation keys，例如 `macina2023mathdial`、`liffiton2023codehelp`、`kazemitabaar2024codeaid`。
3. 检查 DBox 的最终 venue 是否使用 CHI 2025 ACM DL citation，而不是只引用 arXiv。
4. 检查 MRBench 是否已进入 NAACL 2025 Anthology；若是，优先使用 anthology citation。
5. 检查 CodeAid 是否使用 CHI 2024 DOI / ACM citation，而不是只用 arXiv。
6. 检查 EDF/Copa 是否仍为 arXiv preprint；如已被会议接收，更新 venue。
7. 在 Introduction / Related Work 中将 TODO placeholders 替换为 BibTeX keys。
8. 保留 local docs 中的 wording boundary，不因外部 citation 改强论文主张。

## 5. Unsafe Citation Patterns

不要写：

- “DBox was reproduced as our baseline.”
- “CodeHelp/CodeAid show no-direct-solution is sufficient for tutoring safety.”
- “LLM-as-judge prior work validates our DeepSeek grader.”
- “Rubrics as Rewards means our rubric scores can be used as reward.”
- “EDF/Copa results transfer to our single-turn CP tutoring setting.”
- “Bridge Contract is proven superior because Bridge prior work uses expert decision models.”

安全写法：

- “We derive literature-inspired baselines from prior tutoring and programming-education systems.”
- “We do not claim direct reproduction unless code, data, and settings are matched.”
- “Prior LLM-as-judge work motivates scalable auxiliary grading, but our calibration shows human review remains necessary for critical bridge leakage.”
- “Rubric-based evaluation motivates case-specific criteria; this work does not perform rubric-reward RL.”
