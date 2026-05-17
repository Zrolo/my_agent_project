# AIChat Response Review Rubric v3

This document defines the v3 rubric for Research v1 response review. The goal is not to add more scores, but to separate primary outcomes, diagnostic dimensions, and reliability fields so that coach ratings become more stable and less redundant.

## Scope

- This rubric is used for offline response review, dev ablations, 50-case held-out studies, and LLM-judge calibration.
- It is not used for RL training, and rubric scores are not treated as rewards.
- Coach labels are expert references, not absolute truth; formal experiments still require calibration rounds, partial double annotation, and adjudication.
- The current 500-row human review remains dev/regression evidence, not a final headline result.

## Primary Outcomes

These fields are eligible for main paper tables and primary analysis.

| Field | Meaning | How to Score |
| --- | --- | --- |
| `overall_quality` | Coach holistic quality judgment | 1-5; whether this is a strong tutoring response |
| `student_ready_pass` | Composite student-ready gate | Derived: overall >= 4, show=yes, no major/answer leakage, and no zero core diagnostic score |
| `critical_leakage_label` | Critical bridge / answer leakage label | `no_leakage` / `minor_bridge_leakage` / `major_bridge_leakage` / `answer_leakage` |
| `scaffold_sufficiency` | Whether the response is useful enough | 0-2; prevents “safe but not helpful” responses from scoring highly |
| `student_response_burden` | Expected next-turn effort for the student | `low` / `medium` / `high`; an interaction-cost signal, not part of the core score |

## Diagnostic Dimensions

These dimensions support error analysis, prompt revision, and LLM-judge calibration. They should not be used as the only paper conclusion.

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Bridge identification | Misses the current missing bridge | Related but broad/partial | Directly targets the current missing bridge |
| Groundedness | Generic algorithm talk | Partly grounded | Clearly uses the problem, student message, or dialogue |
| Scaffold appropriateness | Too strong or too weak | Slightly strong/weak but usable | Appropriate for the student state |
| Next-step clarity | No actionable next step | Next step exists but broad or effortful | Clear, concrete, low-burden next step |
| Single-focus coherence | Multiple goals mixed together | Minor drift | One coherent tutoring focus |
| Bridge-oriented micro-example | Unrelated or leaks the bridge | Relevant but task-like | Helps the student abstract a transferable relation |

## Micro-example Applicability

`bridge_oriented_micro_example_score` must be interpreted with `micro_example_applicability`.

- `applicable`: the response uses an example, or the turn clearly needs a small example.
- `not_applicable`: the turn does not need a separate micro-example evaluation.

When `not_applicable` is selected, the micro-example score may be blank. The analyzer does not treat it as zero.

## Leakage And Reveal Justification

In v3, `bridge_leakage_control_score` is no longer the main paper safety metric. The main safety judgment is:

```text
critical_leakage_label + bridge_reveal_justification
```

`bridge_reveal_justification` means:

- `no_reveal`: no substantial reveal of the current bridge.
- `pedagogically_justified`: the student already stated it, the turn permits a stronger hint, or the response is a summary/review.
- `borderline`: some reveal exists but its timing or completeness is unclear.
- `unjustified`: the response prematurely or completely supplies the current missing bridge.

This prevents all useful instructional information from being over-penalized as leakage.

## Leakage Mechanisms Are Not Algorithm Categories

Leakage labels ask whether the response completes the student's current missing bridge, not which algorithm family the problem belongs to. Buckets such as `state_representation_semantics`, `transition_recurrence_source`, and `predicate_check_semantics` are Research v1 operational cognitive bridge families. DP states, binary-search checks, lazy propagation, tree-difference marking, and local code are surface anchors.

Common leakage mechanisms include:

- direct bridge completion: completing the current cognitive bridge;
- answer-slot compression: turning the bridge into a blank, choice, true/false follow-up action, or key location/direction question;
- worked-trace completion: using a complete micro-example or local trace to demonstrate the key relation;
- local implementation completion: completing the key local implementation, condition, update statement, or code diagnosis;
- proof / invariant completion: completing the correctness, invariant, exchange, dominance, or safety argument;
- decision-rule completion: directly telling the student which side to keep, branch to take, candidate to skip, or operation to apply;
- debugging diagnosis completion: directly naming the bug cause and fix instead of eliciting evidence;
- modeling-plan completion: giving the complete object/relation/constraint/structure mapping;
- over-constrained scaffold: using question form while narrowing the answer space to the current bridge.

## Reliability Fields

| Field | Purpose |
| --- | --- |
| `reviewer_confidence` | Records how confident the coach is |
| `needs_discussion` | Flags rows for discussion/adjudication |
| `coach_notes` | Required for major leakage, show=no, overall<=2, first/last rank, low confidence, and discussion cases |
| `review_status` | Tracks unlabeled / labeled / needs_discussion / ai_prelim_reviewed |

## Development-Only Composite Score

`rubric_eval_score_v1` is only for development triage. It does not replace raw coach labels and must not be used as the sole paper conclusion.

It rewards:

- high `overall_quality`
- `student_ready_pass`
- high `scaffold_sufficiency`
- clear next-step guidance
- bridge identification

It penalizes:

- `major_bridge_leakage` / `answer_leakage`
- `show=no`
- `student_response_burden=high`

Formal reporting should use the raw primary outcomes and paired comparisons, not only this composite score.
