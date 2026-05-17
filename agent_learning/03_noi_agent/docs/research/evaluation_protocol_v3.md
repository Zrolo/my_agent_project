# Response Evaluation Protocol v3

This protocol defines the v3 workflow for Research v1 dev ablations, 50-case held-out studies, and coach blind review. It replaces the earlier “many parallel scores” presentation with a clearer split between primary outcomes, diagnostic dimensions, and reliability fields.

## Core Principles

1. Define the case-specific rubric before scoring responses.
2. Report only a small set of primary outcomes in main tables.
3. Use diagnostic dimensions for error analysis, not as the only win/loss criterion.
4. Judge micro-example applicability first; non-applicable cases are not penalized.
5. AI preliminary review is only for development triage, not coach gold.
6. LLM judges are calibrated graders, not final truth.

## Coach Workflow

1. Read the problem link, necessary statement, and task context.
2. Read the case-specific rubric:
   - `success_criteria`
   - `forbidden_content`
   - `critical_bridge_boundary`
   - `acceptable_reveal`
   - `expected_student_next_action`
3. Read recent dialogue and the context AI reply to understand the current student turn.
4. Read the current student message; this is the target turn.
5. Score only the target “AI response to review”.
6. Fill primary outcomes first:
   - overall quality
   - show-to-student decision
   - leakage label
   - bridge reveal justification
   - scaffold sufficiency
   - student response burden
7. Fill diagnostic dimensions.
8. Add required notes for flagged rows.

## Required Notes

Notes are required when:

- `critical_leakage_label` is `major_bridge_leakage` or `answer_leakage`
- `would_show_to_student=no`
- `overall_quality<=2`
- the response is ranked first or last for the case
- `reviewer_confidence=low`
- `needs_discussion=yes`

## Analyzer Outputs

The analyzer produces four groups of outputs.

### Primary Table

- overall
- student-ready pass
- safe-ready pass
- major/answer leakage
- scaffold sufficiency
- burden distribution
- development-only `rubric_eval_score_v1`

### Diagnostic Table

- bridge identification
- groundedness
- scaffold appropriateness
- next-step clarity
- single-focus coherence
- bridge-oriented micro-example

### Paired Comparisons

Paired comparisons compare conditions within the same case, including:

- DBox clean vs Bridge Contract clean
- DBox guard vs Bridge-guided DBox guard
- Guard vs no Guard
- Repair vs no Repair

### Case Memo

Major/answer leakage rows are automatically listed for qualitative coding:

- direct bridge completion: completing the student's current cognitive bridge;
- answer-slot compression: turning the bridge into a blank, choice, true/false follow-up action, or operation-location question;
- worked-trace completion: using a complete micro-example or local trace to demonstrate the key relation;
- local implementation completion: completing the key local implementation, condition, update statement, or code diagnosis;
- proof / invariant completion: completing the correctness, invariant, exchange, dominance, or safety argument;
- decision-rule completion: directly telling the student which side to keep, branch to take, candidate to skip, or operation to apply;
- debugging diagnosis completion: directly naming the bug cause and fix instead of eliciting minimal evidence;
- modeling-plan completion: giving the complete object/relation/constraint/structure mapping;
- over-constrained scaffold: using question form while narrowing the answer space to the current bridge;
- context mismatch
- unclear rubric boundary

Bridge buckets such as `state_representation_semantics` and `predicate_check_semantics` are Research v1 operational cognitive bridge families. DP states, binary-search checks, lazy propagation, tree-difference marking, and local code are surface anchors: concrete algorithm instances of broader bridge families and leakage mechanisms.

## Relation To Rubrics as Rewards

This project only adopts the idea that open-ended responses require structured, case-specific rubrics. We do not perform RL training and do not treat rubric scores as reward signals.

Suggested paper wording:

```text
We use case-specific rubrics for open-ended tutor-response evaluation, but do not perform rubric-reward RL training.
```

## Interpreting Results

- A strong baseline winning does not invalidate the paper; it shows that CP-MissingBridgeBench can reveal real trade-offs.
- A high-quality condition with high leakage should not be ranked by overall score alone.
- A no-leakage condition with low sufficiency is not a good tutor.
- Dev/regression results may guide prompt revision; only held-out results support headline claims.
