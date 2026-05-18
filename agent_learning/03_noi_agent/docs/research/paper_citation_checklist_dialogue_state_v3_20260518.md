# Paper Citation Checklist / Bibliography Audit: Dialogue-State v3 20260518

## Scope

This document turns the Introduction / Related Work citation TODOs into an auditable checklist. It adds no experiments, changes no data, and connects no online system. All external citations still need to be rechecked against the paper PDF / proceedings / BibTeX before submission.

Citation principles:

- External papers position related work; they do not support our experimental results.
- DBox, EDF/Copa, CodeHelp/CodeAid, Bridge, MRBench, and MathDial should be cited only within their actual matching scope.
- Do not claim faithful reproduction of any related system unless public code, data, settings, and evaluation protocol are actually matched.
- LLM-as-judge / rubric work can motivate automatic grading and rubric-based evaluation, but cannot justify replacing human coaches.
- The Anthropic agent-eval article can support engineering-methodology framing, but should not replace peer-reviewed academic citations.

## 1. Citation Placeholders To Resolve

| placeholder | candidate citations | use for | do not use for |
| --- | --- | --- | --- |
| `[TODO: MathDial / Socratic tutoring citations]` | MathDial; MRBench; optional Bridge novice-expert decision paper | LLM tutoring dialogue, pedagogical scaffolding, mistake remediation, and tutor-response evaluation background. | Do not claim these works cover CP missing bridges or critical bridge leakage. |
| `[TODO: CodeHelp / CodeAid / programming-help citations]` | CodeHelp; CodeAid | No-direct-solution / no-direct-code guardrails and programming classroom assistant background. | Do not claim they solve critical bridge leakage. |
| `[TODO: DBox citation]` | DBox arXiv / ACM CHI paper; local DBox official-materials review | Step-tree / co-decomposition / decomposition tutoring background; support for the DBox-inspired baseline. | Do not write that we reproduce DBox; do not directly compare our single-turn results with DBox learning-gain results. |
| `[TODO: EDF/Copa citation]` | EDF/Copa arXiv paper; official supplementary materials repo | Evidence-decision-feedback adaptive scaffolding and learner-state modeling background. | Do not write that we reproduce Copa/EDF; do not transfer Copa classroom results to our CP tutoring result. |
| `[TODO: LLM-as-judge / rubric evaluation citations]` | MT-Bench / Chatbot Arena LLM-as-judge; Prometheus; MRBench evaluator analysis; Rubrics as Rewards | LLM grader, rubric-based evaluation, and custom scoring rubric related work. | Do not claim LLM grader is gold; do not claim we do rubric-reward RL. |
| `[TODO: agent eval citations]` | Anthropic "Demystifying evals for AI agents"; internal `agent_eval_methodology_v1` | Harness-level eval, trace/outcome/grader separation, and deterministic + LLM + human grader combinations. | Do not use an engineering blog as the only academic evidence; do not treat runtime guard as offline grader. |

## 2. Candidate External Sources

| short key suggestion | source | checked URL | paper-safe use | boundary |
| --- | --- | --- | --- | --- |
| `macina2023mathdial` | MathDial: A Dialogue Tutoring Dataset with Rich Pedagogical Properties Grounded in Math Reasoning Problems | https://arxiv.org/abs/2305.14536 | Cite math tutoring dialogue data, human teacher + LLM-simulated student collection, and pedagogical dialogue background. | Does not cover programming / CP missing bridge; do not use for our CP results. |
| `maurya2024mrbench` | Unifying AI Tutor Evaluation / MRBench | https://arxiv.org/abs/2412.09416 | Cite AI tutor response evaluation taxonomy, human-annotated pedagogical dimensions, and LLM evaluator reliability discussion. | Mainly math mistake/confusion domain; do not claim it evaluates CP tutoring or critical bridge leakage. |
| `wang2023bridge` | Bridging the Novice-Expert Gap via Models of Decision-Making | https://arxiv.org/abs/2310.10648 | Cite expert decision modeling, student error / remediation strategy / intention before response generation. | It is math mistake remediation; do not merge it with our Bridge Contract method. |
| `liffiton2023codehelp` | CodeHelp: Using Large Language Models with Guardrails for Scalable Support in Programming Classes | https://arxiv.org/abs/2308.06921 | Cite programming class LLM assistant, guardrails, and support without directly revealing solutions. | Do not claim CodeHelp prevents critical bridge leakage; it anchors a no-direct-solution baseline. |
| `kazemitabaar2024codeaid` | CodeAid: Evaluating a Classroom Deployment of an LLM-based Programming Assistant that Balances Student and Educator Needs | https://arxiv.org/abs/2401.11314 | Cite classroom deployment, avoiding direct responses while encouraging learning, transparency, and control. | Do not claim CodeAid matches our benchmark protocol; do not call it faithful reproduction. |
| `ma2025dbox` | DBox: Scaffolding Algorithmic Programming Learning through Learner-LLM Co-Decomposition | https://arxiv.org/abs/2502.19133 | Cite interactive step-tree, learner-LLM co-decomposition, and algorithmic programming scaffolding. | We only build a DBox-inspired single-turn baseline; no UI, multi-turn, progressive reveal, or learning-gain reproduction. |
| `cohn2026edf` | Evidence-Decision-Feedback: Theory-Driven Adaptive Scaffolding for LLM Agents | https://arxiv.org/abs/2602.01415 | Cite evidence -> decision -> feedback adaptive scaffolding, Copa, and learner-state-aware feedback. | EDF/Copa is multi-turn STEM+C / classroom context; this project is not a direct reproduction. |
| `zheng2023llmjudge` | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | https://arxiv.org/abs/2306.05685 | Cite LLM-as-judge as a scalable evaluation direction and known bias/limitation concerns. | Do not use it to prove DeepSeek grader reliability on this task; our calibration shows critical recall risk. |
| `kim2023prometheus` | Prometheus: Inducing Fine-grained Evaluation Capability in Language Models | https://arxiv.org/abs/2310.08491 | Cite custom rubric / reference material for fine-grained evaluator LMs. | Do not claim Prometheus or any LLM grader can replace our human review. |
| `gunjal2025rar` | Rubrics as Rewards: Reinforcement Learning Beyond Verifiable Domains | https://arxiv.org/abs/2507.17746 | Cite instance-specific rubrics and multi-criteria judgments as a related direction. | This project does not do RL and does not use rubric scores as rewards. |
| `anthropic2026agentevals` | Demystifying evals for AI agents | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | Cite harness-level eval, trace/outcome/grader separation, and deterministic/LLM/human grader combinations as engineering methodology. | Engineering article; should not be the only academic citation for evaluation methodology. |

## 3. Internal Evidence Citations

| paper claim | cite internal docs | note |
| --- | --- | --- |
| CP-MissingBridgeBench scope and claim boundary | `paper_scope_v2.md`; `dialogue_state_v3_paper_claims_final_gate_20260518.md` | Internal claim gate, not external citation. |
| Methods / Evaluation | `paper_methods_evaluation_dialogue_state_v3_20260518.md`; `evaluation_protocol_v3.md`; `response_review_rubric_v3.md` | Supports missing bridge, critical bridge leakage, case-specific rubric, and metrics. |
| Results / Discussion | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.md` | Compact manuscript results draft. |
| Main tables and paired uncertainty | `dialogue_state_v3_main_paper_ready_tables_20260517.md`; `dialogue_state_v3_pairwise_win_tie_loss_20260517.md` | Headline uses only `main_scaffold_eval`. |
| Human review reliability | `human_review_reliability_section_draft_20260517.md`; A/B agreement JSON | Coach A/B/priority60 are not gold. |
| Repair causality | `repair_same_candidate_stress_result_20260517.md` | Causal wording only comes from same-candidate stress. |
| DBox+Repair fairness | `dbox_guard_repair_fairness_report_20260517.md` | Targeted 20-case sensitivity, not a full main condition. |
| LLM grader limitation | `llm_grader_calibration_deepseek_sensitivity_report_20260518.md` | DeepSeek priority60 critical recall = 0. |
| Reproducibility | `dialogue_state_v3_evidence_manifest_20260518.json`; `reproduce_dialogue_state_v3_tables.py`; `verify_dialogue_state_v3_reports.py` | For artifact / appendix. |

## 4. BibTeX Work Items

Before submission:

1. Export BibTeX from arXiv / ACL Anthology / ACM DL / DOI pages.
2. Normalize citation keys, for example `macina2023mathdial`, `liffiton2023codehelp`, and `kazemitabaar2024codeaid`.
3. Check whether DBox should use the CHI 2025 ACM DL citation rather than arXiv only.
4. Check whether MRBench has a NAACL 2025 Anthology citation; if yes, prefer the anthology citation.
5. Check whether CodeAid should use a CHI 2024 DOI / ACM citation rather than arXiv only.
6. Check whether EDF/Copa is still an arXiv preprint; update venue if accepted.
7. Replace Introduction / Related Work TODO placeholders with BibTeX keys.
8. Keep local wording boundaries; do not strengthen paper claims because a related-work citation exists.

## 5. Unsafe Citation Patterns

Do not write:

- "DBox was reproduced as our baseline."
- "CodeHelp/CodeAid show no-direct-solution is sufficient for tutoring safety."
- "LLM-as-judge prior work validates our DeepSeek grader."
- "Rubrics as Rewards means our rubric scores can be used as reward."
- "EDF/Copa results transfer to our single-turn CP tutoring setting."
- "Bridge Contract is proven superior because Bridge prior work uses expert decision models."

Safe wording:

- "We derive literature-inspired baselines from prior tutoring and programming-education systems."
- "We do not claim direct reproduction unless code, data, and settings are matched."
- "Prior LLM-as-judge work motivates scalable auxiliary grading, but our calibration shows human review remains necessary for critical bridge leakage."
- "Rubric-based evaluation motivates case-specific criteria; this work does not perform rubric-reward RL."
