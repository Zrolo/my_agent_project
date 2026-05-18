# Paper Introduction / Related Work Draft: Dialogue-State v3 20260518

## Scope

This document is a submission-safe Introduction / Related Work draft. It adds no experiments, changes no data, and connects no online system. Bracketed citation keys are candidate BibTeX keys from `paper_citation_checklist_dialogue_state_v3_20260518.md`; before submission, verify each venue, BibTeX entry, and cited claim against the source text.

Core boundaries:

- This is an evaluation framework paper, not a full online-system paper.
- The main contributions are missing bridge, critical bridge leakage, case-specific rubric, and the human-review evidence package.
- Bridge Contract / Guard / Repair are tutoring harness conditions being evaluated, not the sole contribution.
- We do not claim faithful reproduction of DBox, EDF/Copa, CodeHelp/CodeAid, MathDial, MRBench, or Bridge.
- We do not claim that LLM graders can replace human coaches.

## 1 Introduction Draft

Large language models are increasingly used as programming tutors, but evaluating their help remains difficult. A response can be polite, concise, and compliant with a "do not give the answer" instruction while still removing the central reasoning work the student should perform. This problem is especially sharp in competitive programming, where learning often depends on crossing a small but decisive reasoning gap: understanding what a state represents, why a transition is valid, what a feasibility check means, which boundary should move, or what evidence would isolate a bug.

We call this gap a missing bridge: the local reasoning bridge between what the student currently knows and the next useful solving action. We define critical bridge leakage as a tutoring failure in which the model does not necessarily reveal the full solution or code, but prematurely completes that missing bridge for the student. This makes critical bridge leakage different from ordinary answer leakage. A tutor may avoid final code and still say too much; conversely, a tutor may reveal limited context or ask a focused question without leaking the bridge.

Existing programming-help safeguards often focus on direct answer or code avoidance. This is necessary but insufficient for turn-level tutoring. In competitive programming, a short hint can be overly complete if it gives away the current invariant, predicate meaning, update rule, or proof step. At the same time, overly cautious refusal can be pedagogically empty. The relevant evaluation target is therefore not only "did the model give the answer?", but whether the response preserves an appropriate amount of student reasoning while still providing useful, grounded scaffolding.

We introduce CP-MissingBridgeBench, a turn-level evaluation framework for LLM tutors in competitive programming. Each case includes the problem context, recent dialogue, the student's current message, and a case-specific rubric specifying success criteria, forbidden content, acceptable reveal, and the expected next student action. The benchmark evaluates tutor responses along quality, safety, and student-burden dimensions rather than reducing tutoring to a single scalar score.

Our dialogue-state v3 evidence package contains 50 reviewed candidate cases, 7 anonymized tutoring harness conditions, and 350 AI responses reviewed by two coaches. We report double review, priority adjudication, paired uncertainty, slice analysis, same-candidate Repair stress testing, targeted DBox+Repair fairness sensitivity, and DeepSeek-backed LLM grader calibration. The primary headline uses only the `main_scaffold_eval` slice; all-50 aggregate results are reported as sensitivity / appendix evidence.

The current evidence supports a bounded conclusion. CP-MissingBridgeBench reveals quality-safety-burden trade-offs across tutoring harnesses. DBox-inspired decomposition is a strong baseline. Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity critical-leakage-control trends under the primary human-review view, but paired uncertainty, rater sensitivity, Guard-only instrumentation, Repair stress-test boundaries, DBox+Repair fairness sensitivity, and LLM grader limitations must be reported explicitly.

### Contributions

This paper makes four contributions:

1. We define missing bridge as a turn-level representation of the student's current reasoning gap in competitive-programming tutoring.
2. We define critical bridge leakage, a safety-and-pedagogy failure mode beyond direct answer or code leakage.
3. We construct a case-specific human-review protocol with success criteria, forbidden content, acceptable reveal, expected next action, double review, priority adjudication, and sensitivity reporting.
4. We evaluate strong prompt-only, no-direct-solution, DBox-inspired, Bridge-guided, Bridge Contract, Guard, and Repair harnesses under a common dialogue-state v3 evidence package, emphasizing quality-safety-burden trade-offs rather than absolute system victory.

## 2 Related Work Draft

### 2.1 LLM Tutors And Socratic Scaffolding

Prior work on dialogue tutoring and Socratic guidance studies how models can ask questions, elicit explanations, and scaffold student reasoning rather than directly provide final answers [macina2023mathdial; maurya2024mrbench; wang2023bridge]. CP-MissingBridgeBench shares this emphasis on preserving learner reasoning, but focuses on competitive-programming turns where the critical unit is often a localized bridge: a state meaning, transition source, check predicate, invariant, or debugging evidence target.

Our contribution is not a new Socratic style prompt. Instead, we make the boundary between helpful scaffolding and premature bridge completion explicit through case-specific rubrics and human review. This allows the evaluation to distinguish an open, low-burden prompt from a question that has compressed the answer space so much that the missing bridge is effectively completed.

### 2.2 Programming Help Benchmarks And No-Direct-Solution Guardrails

Programming-help systems and benchmarks often include guardrails against providing full solutions or code [liffiton2023codehelp; kazemitabaar2024codeaid]. These constraints are important, but our results show why they are not enough for competitive-programming tutoring. In dialogue-state v3, a no-direct-solution baseline is stronger than prompt-only, yet still produces critical bridge leakage. This motivates evaluating intermediate reasoning leakage, not only final answer leakage.

CP-MissingBridgeBench therefore treats "no full code" as a baseline requirement rather than the main safety criterion. The main question is whether the tutor preserves the student's opportunity to infer the current missing bridge while still moving the student forward.

### 2.3 Decomposition And Step-Based Programming Tutors

DBox and related step-based programming tutors emphasize decomposing programming tasks, tracking substeps, and supporting learners through structured hints [ma2025dbox]. We use DBox as a literature anchor for a DBox-inspired decomposition baseline. However, our condition is not a DBox reproduction: it does not implement the interactive step-tree UI, multi-turn co-decomposition, progressive reveal, code-step alignment, or student learning-gain study from the original system.

This distinction matters because a weak baseline would inflate our claims. In dialogue-state v3, DBox-inspired decomposition is a strong baseline, especially on student-ready and safe-ready counts. We therefore frame Bridge Contract compact + Guard/Repair as showing favorable trends under the primary human-review view, not as comprehensively defeating a weak comparator.

### 2.4 Adaptive Scaffolding And Learner-State Modeling

Adaptive scaffolding systems such as EDF/Copa organize tutoring around evidence, decision, and feedback, using learner-state estimates and dialogue policies to decide how to respond [cohn2026edf]. This is closely related to our view that a tutor response should depend on the student's current state and next useful action.

Our benchmark differs in domain and granularity. EDF/Copa targets multi-turn computational modeling contexts with environment logs, mastery rubrics, and classroom interaction, whereas CP-MissingBridgeBench evaluates single-turn competitive-programming tutor responses with recent dialogue and problem context. We use EDF/Copa as related work and optional inspiration for baselines, not as a direct reproduction or a directly comparable learning-outcome result.

### 2.5 Rubric-Based Evaluation And LLM-as-Judge

Open-ended tutoring responses are difficult to evaluate with deterministic correctness alone. Rubric-based evaluation and LLM-as-judge methods provide scalable ways to compare responses [zheng2023llmjudge; kim2023prometheus; maurya2024mrbench; gunjal2025rar]. CP-MissingBridgeBench adopts the idea that open-ended responses need structured rubrics, but the current evidence shows that automatic graders remain insufficient for high-stakes critical bridge leakage.

In our DeepSeek-backed calibration, case-specific bridge rubrics improve some auxiliary grading signals relative to a generic rubric, but the priority60 critical recall remains 0 and the major-leakage false-negative rate remains 1.000. Thus, LLM graders are useful as auxiliary signals and scaling tools, but human review and adjudication remain necessary.

### 2.6 Agent Evaluation And Harness-Level Measurement

Agent evaluation work argues that evaluations should measure the whole harness: task construction, traces, graders, tools, routing, and final outcomes [anthropic2026agentevals]. This perspective fits LLM tutoring systems, where response quality depends not only on the base model but also on prompts, diagnosis, guardrails, repair, and final-response selection.

CP-MissingBridgeBench follows this harness-level view. We compare offline tutoring harnesses under a common case set, keep runtime guard/repair separate from offline grading, and report reproduction scripts and an evidence manifest. At the same time, we avoid treating internal runtime judges as proof of their own safety; the paper-facing evidence relies on human review, adjudication, paired uncertainty, stress testing, and calibration.

## 3 Related Work Positioning Table

| Area | What prior work contributes | Gap for this paper | Our positioning |
| --- | --- | --- | --- |
| Socratic tutoring | Encourages questions and learner reasoning. | Does not by itself define when a hint leaks the current CP reasoning bridge. | We evaluate whether scaffolding preserves the missing bridge. |
| Programming-help guardrails | Discourage full code or direct solutions. | No-direct-solution can still leak key intermediate reasoning. | Critical bridge leakage extends safety beyond answer leakage. |
| DBox / step decomposition | Structured decomposition and hints for programming tasks. | Full DBox is interactive and multi-turn; our setting is single-turn dialogue-state evaluation. | We use a DBox-inspired strong baseline, not a reproduction. |
| EDF/Copa adaptive scaffolding | Evidence-decision-feedback learner-state adaptation. | Domain, data, and interaction setting differ from CP tutoring. | Related work / optional inspiration, not direct reproduction. |
| LLM-as-judge | Scalable open-ended evaluation. | Critical bridge leakage has high false-negative risk. | LLM graders are auxiliary; human review remains central. |
| Agent evals | Evaluate whole harnesses and traces. | Needs domain-specific tasks and rubrics for tutoring. | We provide case-specific rubrics and evidence-class reporting. |

## 4 Citation Verification Notes

The citation keys above are candidate keys, not final camera-ready bibliography entries. Before submission:

- Verify each candidate source against the paper PDF, proceedings page, DOI page, or official BibTeX entry.
- Prefer final venue citations over arXiv when available, especially for DBox, CodeAid, and MRBench.
- Keep the citation-use boundaries in `paper_citation_checklist_dialogue_state_v3_20260518.md`.
- Do not strengthen any claim because a related-work citation exists.

Do not add a citation unless the paper has been checked for the specific claim being made. This is especially important for DBox and EDF/Copa, where the safe wording is literature-inspired / related work, not reproduction.
