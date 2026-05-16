# CP-MissingBridgeBench External Review Packet (2026-05-15)

This packet is intended for external AI or coach review. It is not a paper draft and not a final experiment report. Its purpose is to summarize the current project state, evidence, risks, and next plan in one place.

## 1. Current Positioning

The project is no longer framed as proving that a multi-agent architecture is always best. The current framing is:

> **CP-MissingBridgeBench: a turn-level evaluation framework for LLM tutors in competitive programming.**

The central construct is the student's **missing bridge** in a tutoring turn. The central risk metric is **critical bridge leakage**, where the tutor does not necessarily reveal full code or a complete solution, but prematurely completes the key reasoning relation the student should still construct.

Recommended claims:

- We define a CP-specific missing bridge schema.
- We define critical bridge leakage beyond answer/code leakage.
- We build a coach-reference and blind-review workflow.
- We compare strong prompt-only, DBox-inspired, CodeHelp/CodeAid-style, Bridge-inspired, Bridge Contract, Guard, and Repair variants under quality, leakage, latency, and cost trade-offs.

Claims to avoid:

- Bridge Contract always beats all baselines.
- Multi-stage LLM systems are always better than single-LLM prompting.
- LLM judges are gold truth.
- The deployed online AIChat is already a complete Bridge-aware Tutor.

## 2. Current Progress

### 2.1 Research Scope and Baselines

Key files:

- `docs/research/paper_scope_v2.zh.md`
- `docs/research/baseline_strategy_v1.zh.md`
- `docs/research/baseline_protocol_v1.zh.md`
- `docs/research/dbox_reproduction_gap_v1.zh.md`
- `docs/research/dbox_official_materials_review_v1.zh.md`

Important boundaries:

- `current_system` is a deployment baseline, not the only research baseline.
- DBox is not reproduced. It is an interactive learner-LLM co-decomposition system with a step-tree UI, progressive hints, code-step alignment, and a student study. We only implement a DBox-inspired single-turn decomposition baseline.
- CodeHelp/CodeAid-style baselines test whether ordinary no-direct-solution guardrails are already sufficient.
- Bridge-inspired expert-decision prompting tests whether generic expert decision injection already explains the effect.

### 2.2 Prompt and Rubric Governance

Current state:

- Prompt patch logs and judge prompt patch logs exist.
- The review rubric has been upgraded to case-specific rubric v3.
- Review workbooks should display the problem statement, recent dialogue, context AI reply, current student message, target AI reply, and a clear review flow.
- Primary outcome metrics should be limited to a small set: overall quality, student-ready / safe-ready, critical leakage, scaffold sufficiency, and student response burden.
- Diagnostic dimensions should support error analysis rather than serve as the only paper conclusion.

Relevant files:

- `docs/research/response_review_rubric_v3.zh.md`
- `docs/research/evaluation_protocol_v3.zh.md`
- `docs/research/case_specific_rubric_policy_v1.zh.md`
- `docs/research/coach_blind_review_instructions_v1.zh.md`

### 2.3 Current 50-Case Dataset Status

The recommended next dataset is dialogue-state v3:

- Dataset: `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- Chinese review workbook: `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- English review workbook: `docs/research/dialogue_state_v3_50_source_and_case_review.en.xlsx`
- Generator: `evals/aichat/generate_dialogue_state_v3_50.py`
- Chinese generation report: `docs/research/dialogue_state_v3_generation_report_20260513.zh.md`
- English generation report: `docs/research/dialogue_state_v3_generation_report_20260513.md`
- Refresh memo: `docs/research/dialogue_state_v3_50_refresh_20260515.zh.md`
- Context readiness audit: `docs/research/dialogue_state_v3_50_context_readiness_audit_20260515.zh.md`

Dataset status:

- 50 cases are grounded in real Luogu problems.
- Student messages are synthetic-but-grounded: generated from real problem statements and observed student language style, not claimed as real student utterances.
- Legacy online AI replies are not used as dataset answers.
- The current label status is `draft_needs_coach_review`, not gold.

Update after 2026-05-15: the Chinese and English review workbooks now include structured case/source review columns: `source_ok`, `context_coherent`, `student_message_realistic`, `missing_bridge_ok`, `forbidden_content_ok`, `success_criteria_ok`, `leakage_boundary_ok`, `case_decision`, `issue_type`, `coach_fix_suggestion`, and `reviewer_confidence`. These fields summarize accept/revise/drop/discuss decisions; they are not AI-response quality scores.

Current design constraints:

| Dimension | Current Design |
| --- | --- |
| Row count | 50 |
| Source platform | Luogu 50 |
| Student message length | short 20 / medium_short 15 / medium_long 10 / long 5 |
| Recent dialogue | none 10 / short 25 / long 15 |
| Initial vs follow-up turns | initial 10 / follow-up 40 |
| Student followability state | F1 6 / F2 19 / F3 10 / F4 5 / N/A 10 |
| Code/error-code scenarios | at least 10, currently about 17 |

Bridge bucket quotas:

| Bridge Bucket | Count |
| --- | ---: |
| State/representation semantics | 6 |
| Transition/recurrence source | 5 |
| Check condition | 5 |
| Boundary update / loop direction | 5 |
| Modeling / object relation | 5 |
| Contribution aggregation / difference / prefix | 4 |
| Data structure operation / maintenance semantics | 5 |
| Greedy / invariant / correctness | 5 |
| Implementation boundary / initialization / type | 4 |
| Debugging evidence / minimal counterexample | 3 |
| Direct answer/code/confirmation request | 3 |

### 2.4 Existing Evidence

All current results are development or pilot evidence, not final headline results:

- 20-case fair blind review: Bridge Contract variants showed promising signals, but the sample was small and used for development.
- Prompt-controlled ablation: prompt effects are strong, so strong prompt-only baselines are required.
- Literature-inspired baseline smokes: DBox-inspired, CodeHelp/CodeAid-style, and Bridge-inspired modes run, but are not final comparisons.
- Repair stress: causal repair claims require same-candidate before/after evaluation.
- DBox-Bridge hybrid 50 generation-only runs and human reviews exposed context consistency, reviewer field clarity, and Guard/Repair interpretability issues.

## 3. Main Current Issues

### 3.1 DBox-Inspired Is Strong

This is not a failure. It means the paper is no longer comparing against a weak baseline. If DBox-inspired remains the best method, the paper can still conclude that CP-MissingBridgeBench reveals the strength of decomposition scaffolding and that missing bridge information may be most useful as an evaluation, guard, routing, or high-risk-analysis signal.

### 3.2 The Dataset Still Needs Coach Review

Dialogue-state v3 improves several earlier data problems, but coaches still need to verify:

- problem statement sufficiency,
- recent dialogue coherence,
- student-message authenticity,
- missing bridge correctness,
- forbidden content strictness,
- success criteria usefulness.

### 3.3 Human Review Subjectivity Remains

The next formal phase needs:

- partial double annotation,
- agreement reporting,
- adjudication,
- LLM grader calibration as auxiliary evidence only.

### 3.4 Leakage Should Not Be Overly Strict

Each case should expose:

- `critical_bridge_boundary`,
- `forbidden_content`,
- `acceptable_reveal`,
- `expected_student_next_action`.

This lets reviewers judge whether a reveal harms learning rather than mechanically marking every key concept as leakage.

### 3.5 Guard/Repair Causal Effects Are Not Yet Established

Guard and Repair effects should be tested with same-candidate before/after stress cases. Otherwise the effect can be confounded by run-to-run generation variance.

### 3.6 Prompt Tuning Risk

Before held-out evaluation, freeze:

- enhanced prompt,
- DBox-inspired prompt,
- Bridge Contract prompt,
- Guard prompt,
- Repair prompt,
- review rubric,
- offline grader prompt.

After freezing, held-out results should not be used to tune prompts.

## 4. Recommended Next Plan

### Step 1: Case/Source Review

Review `dialogue_state_v3_50_source_and_case_review.zh.xlsx` first:

1. Read the instruction sheet.
2. Review by bridge-bucket sheets.
3. Evaluate the case itself, not AI responses.
4. Focus on source/problem fit, dialogue coherence, student-message realism, missing bridge, forbidden content, and success criteria.
5. Fill the structured review columns with `accept / revise / drop / discuss`; when a case needs revision, also fill `issue_type` and `coach_fix_suggestion`.

### Step 2: Freeze Main Conditions

Keep the main experiment compact, around 6-8 systems:

- `enhanced_prompt_only_clean`
- `dbox_inspired_clean`
- `dbox_inspired_guard`
- `bridge_guided_dbox_style_guard` if the hybrid is kept
- `bridge_contract_compact_clean`
- `bridge_contract_compact_guard`
- `bridge_contract_compact_guard_repair`
- optional: `codehelp_codeaid_no_direct_solution` or `bridge_inspired_expert_decision`

Put additional ablations in the appendix.

### Step 3: Generate 50-Case Response Review Workbook

Each condition must see the same input:

- problem statement / public summary,
- recent dialogue,
- context AI reply if present,
- current student message,
- student code excerpt if present,
- case-specific rubric fields.

The review workbook must hide condition and model identifiers.

### Step 4: Human Blind Review + AI Preliminary Review

Suggested workflow:

1. AI preliminary review only for development screening.
2. Human coach review on the Chinese workbook.
3. At least 20% double annotation by a second coach.
4. Mandatory notes for major leakage, show=no, overall<=2, first/last rank, and low confidence.

### Step 5: Analysis

Do not treat 50 × N responses as independent samples. Analyze by paired case:

- win/tie/loss,
- paired bootstrap confidence intervals,
- student-ready pass,
- safe-ready pass,
- major/answer leakage,
- p50/p95 latency,
- LLM calls,
- static lint as a risk screen only, not human gold.

## 5. Questions for External Reviewers

1. Should the paper remain framed as an evaluation framework rather than a strongest-architecture paper?
2. Are DBox-inspired, CodeHelp/CodeAid-style, and Bridge-inspired baselines sufficient to avoid weak-baseline bias?
3. Is the synthetic-but-grounded 50-case dialogue-state v3 dataset acceptable?
4. Are recent dialogue, current student message, problem statement, and missing bridge aligned?
5. Is critical bridge leakage too strict? Does `acceptable_reveal` address this?
6. Is the main condition set still too large?
7. If DBox-inspired wins, does the contribution still hold?
8. Are there copyright or citation issues with using Luogu problem sources?
9. Is the coach workbook understandable enough?
10. What remaining experimental design issues would concern a reviewer?

## 6. Files to Inspect

Recommended:

- `docs/research/external_review_packet_20260515.zh.md`
- `docs/research/dialogue_state_v3_50_refresh_20260515.zh.md`
- `docs/research/dialogue_state_v3_50_context_readiness_audit_20260515.zh.md`
- `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- `docs/research/response_review_rubric_v3.zh.md`
- `docs/research/evaluation_protocol_v3.zh.md`
- `docs/research/baseline_protocol_v1.zh.md`
- `docs/research/dbox_reproduction_gap_v1.zh.md`

For English review, use corresponding `.md` files and `dialogue_state_v3_50_source_and_case_review.en.xlsx`.

## 7. One-Sentence Summary

The project has moved from feature accumulation toward a competitive-programming LLM tutor evaluation framework. The next priority is to review and clean the 50-case dialogue-state v3 dataset, freeze prompts and rubrics, then run a compact strong-baseline comparison. The paper should not depend on Bridge Contract always winning; it should argue that CP-MissingBridgeBench can rigorously reveal quality, leakage, latency, and student-burden trade-offs across tutoring harnesses.
