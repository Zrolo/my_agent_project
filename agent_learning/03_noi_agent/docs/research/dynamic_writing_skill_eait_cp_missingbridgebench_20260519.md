# Dynamic Writing Skill: Education and Information Technologies for CP-MissingBridgeBench

Generated: 2026-05-19
Primary corpus papers analyzed: 5
Secondary corpus papers analyzed: 2
User/lab exemplars analyzed: 0
Static base skill: general_academic.md

## PRIORITY RULES (Non-Negotiable)

### Priority 1 - HARD PRESERVE

Never modify:

- All citation keys and bibliography decisions unless the human author requests citation work.
- All numerical results and quantitative claims from the dialogue-state v3 evidence package.
- All experimental conditions, slices, labels, file paths, reproduction commands, and model/backend names.
- All explicit evidence-class boundaries: main result, sensitivity, stress test, calibration, taxonomy/error analysis.
- All forbidden-claim constraints in `paper_claims_final_submission_gate_20260519.zh.md`.

### Priority 2 - CP-MissingBridgeBench Claim Gate

- Do not add experimental conditions.
- Do not modify online AIChat, active mode, prompts, or main experiment data.
- Do not write sensitivity, stress, or calibration as main results.
- Do not write Coach A, Coach B, or priority60 adjudication as final gold.
- Do not use all 50 cases as the headline aggregate.
- Do not claim Bridge Contract significantly or comprehensively outperforms all baselines.
- Do not say Guard-only fixes final output.
- Do not infer Repair causality from main-condition means.
- Do not claim LLM graders can replace human coaches.
- Do not add citations or facts without source verification.

### Priority 3 - TARGET JOURNAL PATTERNS

- Frame the paper as an educational-technology evaluation and benchmark paper, not a product-deployment victory.
- Start from the learning/assessment failure: no-direct-answer rules do not fully protect the student's missing bridge.
- Use explicit research questions or evaluation criteria.
- Explain instruments and rubric workflow before results.
- Report AI/tutor comparisons by dimensions: quality, safety/leakage, burden, rater sensitivity, and grader reliability.
- Keep human/expert review central when evaluating pedagogical quality and critical leakage.
- Use limitations proactively; rater sensitivity and coverage limits are part of the contribution's honesty.

### Priority 4 - SECONDARY CORPUS FOLLOW

- From DBox: preserve the learner-cognition/process framing and distinguish scaffolding from answer delivery.
- From MRBench: treat taxonomy, human annotation, and automatic evaluator reliability as separate research objects.
- Apply secondary patterns only when they do not override EAIT caution.

### Priority 5 - STATIC BASE DEFAULT

- One claim per paragraph.
- Claim first, evidence second.
- State what the study shows, not what it hopes to show.
- Write for education-technology readers outside competitive programming.
- Remove filler and hollow transitions.

### Priority 6 - ALWAYS REMOVE

- "This paper explores..."
- "In this study, we aim to..."
- "To the best of our knowledge..."
- "This is the first..."
- "Future research should explore..." unless followed by a concrete agenda tied to the limitations.
- Any wording that implies final gold, full deployment validation, full CP coverage, or automatic-grader replacement.

## SECTION-SPECIFIC GUIDANCE

### Abstract

Use a single restrained paragraph of about 180-240 words:

1. Educational problem: AI tutors may avoid direct answers while still revealing a critical bridge.
2. Construct: CP-MissingBridgeBench evaluates missing-bridge scaffolding and critical-bridge leakage.
3. Design: dialogue-state v3, 50 reviewed cases, 7 conditions, 350 responses, expert blind review, with a 31-case main scaffold headline.
4. Finding: quality-safety-burden trade-offs; DBox-inspired baseline strong; Bridge Contract compact + Guard/Repair shows favorable but bounded trends under the primary human-review view.
5. Boundary: human review remains necessary; sensitivity/stress/calibration are not main-result substitutes.

Do not:

- Put all-50 aggregate in the abstract headline.
- Say the system solves CP tutoring.
- Present LLM grader calibration as a main result.

### Introduction

Recommended sequence:

1. Open with tutoring tension: students need help before they can finish a reasoning bridge, but premature completion undermines learning.
2. Explain why direct-code or direct-answer avoidance is insufficient.
3. Define missing bridge and critical bridge leakage in education-facing prose.
4. State why competitive programming is a useful stress domain: multi-step reasoning, concise student messages, and high risk of premature answer-bearing hints.
5. Present three contributions:
   - A CP-specific benchmark construct and case-specific rubric workflow.
   - A human-review evaluation protocol for quality, leakage, and burden.
   - Bounded empirical evidence showing quality-safety-burden trade-offs across strong offline tutoring harnesses.
6. Roadmap.

Do not:

- Open with generic AI hype.
- Lead with Bridge Contract as if it is the whole paper.
- Claim prior systems are strawmen.

### Related Work

Organize by theme:

1. AI tutoring and intelligent tutoring systems for programming.
2. LLM-assisted feedback and scaffolding.
3. Rubric-based and human/expert evaluation in educational technology.
4. AI/LLM graders and why calibration matters.
5. Algorithmic-programming scaffolding and AI tutor benchmark work.

Do not:

- Claim faithful reproduction of DBox, CodeHelp, CodeAid, EDF/Copa, or any cited system unless settings match.
- Add unverified citations.

### Methods / Evaluation

EAIT-facing order:

1. Benchmark construct: missing bridge, critical bridge leakage, acceptable reveal, forbidden content, expected next action.
2. Dataset/evidence candidate: 50 reviewed dialogue-state cases and slice structure.
3. Conditions: 7 offline human-review harnesses; keep Guard-only and Repair boundaries explicit.
4. Review protocol: blind review, Coach A/B, priority60 adjudication, agreement and sensitivity.
5. Metrics: overall, student-ready, safe-ready, leakage severity, burden, paired W/T/L, uncertainty.
6. Analysis hierarchy: main scaffold headline first; sensitivity/stress/calibration separately.
7. Reproducibility and evidence manifest.

Do not:

- Describe online AIChat as if the offline harness is deployed.
- Hide the main/sensitivity/stress/calibration hierarchy.
- Treat Coach A/B/priority60 as gold.

### Results

Recommended order:

1. Human review reliability.
2. Main scaffold evaluation on 31 cases.
3. Paired uncertainty and rater/slice sensitivity.
4. Observed error taxonomy.
5. Repair same-candidate stress and DBox+Repair fairness sensitivity, clearly labelled as secondary evidence.
6. LLM grader calibration as auxiliary limitation evidence.

Preferred claim language:

- "shows favorable trends"
- "reveals trade-offs"
- "under the primary human-review view"
- "in the main scaffold slice"
- "requires sensitivity reporting"

Do not:

- Say significant dominance unless the evidence and design support it.
- Use all-case averages as the headline.
- Use Repair stress or calibration to inflate main results.

### Discussion

Recommended order:

1. What CP-MissingBridgeBench contributes to AI tutoring evaluation.
2. Why critical bridge leakage differs from direct answer leakage.
3. What the results imply for scaffolding, guard instrumentation, and repair.
4. Why expert review remains necessary.
5. Practical implications for education-technology evaluation.
6. Limitations.

Do not:

- End with a product-victory paragraph.
- Minimize limitations.
- Claim universal CP tutoring coverage.

### Conclusion

Use a short bounded close:

- Restate the construct and evaluation contribution.
- Summarize the main scaffold trade-off finding.
- State that human review, rater sensitivity, and evidence-class separation are necessary for this kind of evaluation.
- Give concrete future work only: larger case coverage, cross-backend grader calibration, online/shadow-mode validation, and stronger adjudication if those are intended by the human author.

Do not:

- Add new experiments by implication.
- Promise deployment validation already not present.

## MANUSCRIPT-SPECIFIC SECTION PLAN

### Abstract

Convert the current abstract into EAIT's context-gap-method-finding-implication form. Keep one main numerical design sentence. Mention stress/calibration only as evidence boundaries if space permits.

### Introduction

Move from "benchmark/system" framing to "learning failure after no-direct-answer compliance" framing. Put CP-specific terminology after the education-facing problem. State contributions as construct, protocol, and bounded empirical evidence.

### Methods

Combine current task definition, dataset, baselines, human review, metrics, and analysis hierarchy into a single education-evaluation logic. This section should convince an EAIT reader that the rubric and human review protocol are the core method.

### Results

Use the existing Results draft but compress it into EAIT's RQ/evaluation-criterion style. Main result first; sensitivity/stress/calibration as explicitly labelled subsections.

### Discussion

Shift from condition comparison toward implications for AI tutoring evaluation: answer avoidance is insufficient; bridge leakage requires case-specific human judgment; repair is promising but trade-off-bearing; automatic graders remain auxiliary.

## CAUTIONS AND CONFLICTS

- Secondary HCI/NLP papers use stronger artifact-first language than EAIT; do not import that strength into headline claims.
- EAIT accepts system/framework evaluation, but expects educational context and limitations to be visible.
- CP-MissingBridgeBench has enough evidence for a benchmark/evaluation paper, not for a deployed tutoring-system effectiveness paper.
- LLM grader calibration is a limitation/evaluation-method section, not a replacement for human review.

## LANGUAGE REGISTER

- Voice: Use active voice for claims; passive is acceptable for procedures and scoring.
- Sentence length: Use shorter sentences around claim boundaries and forbidden interpretations.
- Hedging: Use specific hedging such as "under the primary human-review view", "in the main scaffold slice", and "same-candidate stress evidence".
- Transitions: Prefer RQ/criterion/evidence-class headers over generic transitions.
- Technical prose: Define CP, missing bridge, and critical bridge leakage before condition names.

