# Paper Abstract / Conclusion Draft: Dialogue-State v3 20260518

## Scope

This document provides submission-safe abstract and conclusion drafts for the dialogue-state v3 paper package. It adds no experiment, changes no data, and connects no online active mode. The wording follows `dialogue_state_v3_paper_claims_final_gate_20260518.md`.

Core boundaries:

- The paper is an evaluation-framework paper, not an online deployment paper.
- The primary headline uses only the 31-case `main_scaffold_eval` slice.
- The 50-case evidence package is a formal human-review evidence candidate, not final gold.
- Guard-only is instrumentation, not final-response rewrite.
- Repair causal evidence comes from same-candidate stress testing, not main-condition means alone.
- LLM graders are auxiliary only.

## Candidate Title

```text
CP-MissingBridgeBench:
Turn-Level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation
for LLM Tutors in Competitive Programming
```

## Abstract Draft

Large language models are increasingly used as programming tutors, but avoiding final code or direct answers is not sufficient for pedagogically safe help. In competitive programming, a short hint can still reveal the key intermediate reasoning step the student should derive next. We call this local reasoning gap a missing bridge, and define critical bridge leakage as prematurely completing that bridge without necessarily giving the full solution.

We introduce CP-MissingBridgeBench, a turn-level evaluation framework for LLM tutors in competitive programming. Each case includes problem context, recent dialogue, a student message, and a case-specific rubric specifying success criteria, forbidden content, acceptable reveal, and the expected next student action. Our dialogue-state v3 evidence package contains 50 reviewed candidate cases, 7 anonymized tutoring-harness conditions, and 350 AI responses double-reviewed by two coaches with priority adjudication, paired uncertainty, slice analysis, Repair same-candidate stress testing, DBox+Repair fairness sensitivity, and DeepSeek LLM-grader calibration.

The evidence shows that CP-MissingBridgeBench reveals quality-safety-burden trade-offs across tutoring harnesses. DBox-inspired decomposition is a strong baseline; no-direct-solution prompting does not eliminate critical bridge leakage; and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view. At the same time, student-ready and rank judgments are rater-sensitive, Guard-only is only instrumentation in the current pipeline, Repair reduces leakage in same-candidate stress testing with a student-burden trade-off, and LLM graders remain auxiliary rather than replacements for human review.

## Short Abstract Draft

We introduce CP-MissingBridgeBench, a turn-level evaluation framework for LLM tutors in competitive programming. The benchmark focuses on missing bridges: local reasoning gaps between a student's current understanding and the next useful solving action. It also defines critical bridge leakage, where a tutor avoids full code or final answers but prematurely reveals the key intermediate reasoning the student should infer. In dialogue-state v3, 50 reviewed cases, 7 anonymized tutor harnesses, and 350 AI responses are evaluated by two coaches with priority adjudication, paired uncertainty, stress testing, and LLM-grader calibration. The evidence supports a trade-off claim: DBox-inspired decomposition is a strong baseline, no-direct-solution prompting is not safety-complete, and Bridge Contract compact + Guard/Repair shows favorable quality and high-severity leakage-control trends, while rater sensitivity, Repair burden trade-offs, and automatic-grader limitations remain important.

## Conclusion Draft

This paper argues that competitive-programming tutoring needs an evaluation target finer than direct answer or code leakage. The central pedagogical risk is often local: a tutor can preserve the final answer while still completing the student's current missing bridge. CP-MissingBridgeBench makes this risk explicit through case-specific rubrics, human review, and evidence-class reporting.

The dialogue-state v3 evidence package supports three main conclusions. First, the benchmark exposes quality-safety-burden trade-offs that are not visible from generic helpfulness or no-direct-solution checks alone. Second, strong baselines matter: DBox-inspired decomposition performs well, and no-direct-solution prompting improves over prompt-only while still allowing critical bridge leakage. Third, Bridge Contract compact + Guard/Repair shows favorable trends in overall quality and high-severity leakage control under the primary human-review view, but the result should be interpreted as a bounded trend rather than broad significant dominance.

The study also clarifies what current evidence does not establish. The 50-case set is not universal CP tutoring coverage. Coach labels and priority60 adjudication are expert reference views, not final gold. Guard-only conditions provide runtime leakage signals but do not rewrite final responses in the main experiment. Repair has causal support from same-candidate stress testing, where leakage severity improves but student burden can increase. DeepSeek-backed LLM graders remain useful as auxiliary signals but miss critical leakage too often to replace human review.

Future work should broaden the benchmark across more topics, student states, and real dialogue distributions; add stronger multi-rater adjudication for rater-sensitive outcomes; run fuller repair-enabled baseline comparisons where needed; and improve automatic graders for critical bridge leakage without treating them as gold. The current contribution is therefore a reproducible evaluation framework and evidence package for studying missing-bridge preservation, not a claim that one tutor harness has fully solved competitive-programming tutoring.

## Paper-Safe Closing Sentence

```text
CP-MissingBridgeBench turns missing-bridge preservation and critical-bridge leakage into auditable evaluation objects, enabling more precise analysis of how LLM tutoring harnesses trade off helpfulness, safety, and student reasoning burden.
```

## Unsafe Abstract / Conclusion Patterns

Do not write:

- Bridge Contract significantly outperforms all baselines.
- Guard-only fixes or rewrites final student-visible responses.
- Repair causality is proven by the main experiment alone.
- priority60 adjudication is final gold.
- The 50-case set covers all competitive-programming tutoring situations.
- DeepSeek or any LLM grader can replace human coaches.
