# Dynamic Writing Skill: EAIT-Facing CP-MissingBridgeBench Recent-Corpus Layer

Generated on 2026-05-19 from `docs/research/eait_recent_corpus_20260519/`.

Use this as an additional `journal-adapt` layer for revising CP-MissingBridgeBench toward Education and Information Technologies (EAIT). It complements the earlier file `docs/research/dynamic_writing_skill_eait_cp_missingbridgebench_20260519.md`.

## Corpus Basis

- Primary EAIT style-extraction papers: 7 fully readable recent EAIT papers on ChatGPT/programming interaction, programming-education rapid review, adaptive feedback, AI-assisted grading/feedback, automated writing evaluation, AI-generated quizzes with expert review, and LLM conversational agents for assessment burden.
- Secondary topic-similar papers: 4 fully readable papers on algorithmic-programming scaffolding, AI tutor evaluation taxonomy, human-LLM competitive programming benchmark, and answer-leakage robustness.
- Requested but excluded from style extraction: `eait_recent_001_generative_ai_dialogic_feedback_programming_2025`, because the downloaded Springer page was closed-access metadata/abstract HTML rather than full text.

## Non-Negotiable Manuscript Constraints

- Do not add experimental conditions.
- Do not modify AIChat, active mode, prompts, or main experimental data.
- Do not change numbers.
- Do not change evidence class.
- Do not add citations or factual claims unless the user separately asks for citation integration and sources are verified.
- Do not write sensitivity, stress, or calibration analyses as main results.
- Do not write Coach A, Coach B, or priority60 adjudication as final gold.
- Do not use the all-50-case aggregate as the headline.
- Do not claim Bridge Contract is significantly or comprehensively superior to all baselines.
- Do not say Guard-only repairs final output.
- Do not infer Repair causality from main-experiment means.
- Do not claim LLM graders can replace human coaches.

## EAIT Rhetorical Target

The manuscript should read as an education-technology evaluation paper, not as a systems paper seeking victory language. The core story is:

1. Programming learners need scaffolding before they complete a reasoning bridge.
2. LLM tutors risk completing that bridge too early.
3. CP-MissingBridgeBench evaluates this bridge-leakage risk under blind human review and evidence-class hierarchy.
4. The current evidence supports bounded scaffold-quality and leakage-risk claims, plus auxiliary calibration/stress observations.

## Abstract Rule

Use a 180-240 word context-gap-method-finding-boundary structure:

- Context: AI tutoring and programming help create a support-versus-premature-completion tension.
- Gap: no-direct-answer rules do not directly assess case-specific critical bridge leakage.
- Method: describe benchmark construct, reviewed cases, offline harnesses, blind human review, and evidence hierarchy.
- Finding: state only safe, evidence-gated findings from the manuscript.
- Boundary: note uncertainty, human-review dependence, and auxiliary status of calibration/stress analyses.

Avoid:
- product-victory wording;
- comprehensive superiority;
- final-answer repair claims;
- AI grader replacement language.

## Introduction Rule

Open with the tutoring tension:

> Students need help before completing a reasoning bridge, but premature completion undermines learning.

Then move through:

1. why competitive programming makes this tension acute;
2. why final-answer leakage and critical-bridge leakage are not identical;
3. why simple no-direct-answer rules are insufficient;
4. why human review is necessary for case-specific bridge judgment;
5. what this paper evaluates and what it does not evaluate.

Contributions should be prose or a short numbered list, each tied to an evidence class.

## Related Work Rule

Use five thematic paragraphs or subsections:

1. AI tutoring / ITS and programming education.
2. LLM/GenAI feedback and scaffolding in programming or adjacent learning contexts.
3. Rubric-based expert and human evaluation.
4. LLM graders, AI assessment support, and calibration as auxiliary evidence.
5. Algorithmic-programming scaffolding, AI tutor benchmarks, CP benchmarks, and leakage robustness.

In the final paragraph, delimit CP-MissingBridgeBench:

- It is CP-specific.
- It evaluates missing reasoning bridge leakage.
- It uses human review as the primary evidential layer.
- It does not claim to evaluate every tutoring quality dimension.

## Methods / Evaluation Rule

Write Methods and Evaluation as one transparent evaluation account:

1. benchmark construct and unit of analysis;
2. 50 reviewed cases and the reason the main headline remains the evidence-gated subset;
3. seven offline human-review harnesses;
4. blind review protocol and label status;
5. metrics and what each metric can and cannot establish;
6. main/sensitivity/stress/calibration hierarchy;
7. evidence manifest as the audit trail.

Style:
- Use EAIT-style procedural clarity.
- Keep technical detail sufficient but not conference-dense.
- Explain human review as an educational-evaluation safeguard.

## Results Rule

Use this order:

1. human review reliability and evidential status;
2. main scaffold evaluation on the 31-case evidence-gated subset;
3. pairwise uncertainty and sensitivity;
4. observed error taxonomy;
5. Repair stress and DBox+Repair fairness;
6. LLM grader calibration.

Writing boundaries:
- The 31-case main evaluation is the main scaffold result.
- Sensitivity/stress/calibration are supporting evidence.
- Error taxonomy is observational unless the underlying evidence supports stronger claims.
- Repair can be described as promising and burden-bearing, not causally proven by main means.
- LLM grader calibration can be described as auxiliary and imperfect, not as a replacement for coaches.

## Discussion Rule

Turn the discussion toward education-technology implications:

- No-direct-answer rules are insufficient because leakage can happen at a missing-bridge level.
- Critical bridge leakage requires case-specific human judgment.
- Scaffold contracts can help structure tutor output, but the evidence should remain bounded.
- Repair is promising but burden-bearing; report what the stress/fairness analyses do and do not show.
- LLM graders remain auxiliary and require calibration against human review.

Use the EAIT pattern: implication -> evidence boundary -> design/practice consequence.

## Conclusion Rule

Write a bounded close:

- Restate the evaluation contribution.
- Summarize the safest finding in evidence-gated language.
- Emphasize human review and construct clarity.
- End with future-work or deployment boundary, not product victory.

## Local Corpus Files

- Style profile: `docs/research/eait_recent_corpus_20260519/_style_cards/journal_style_card.md`
- Style cards: `docs/research/eait_recent_corpus_20260519/_style_cards/*_style_card.md`
- Access note: `docs/research/eait_recent_corpus_20260519/_style_cards/eait_recent_001_generative_ai_dialogic_feedback_programming_2025_access_note.md`
- Converted text: `docs/research/eait_recent_corpus_20260519/text/` and `docs/research/eait_recent_corpus_20260519/secondary_text/`
