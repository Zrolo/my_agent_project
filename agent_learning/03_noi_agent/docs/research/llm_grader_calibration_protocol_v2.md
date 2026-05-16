# LLM Grader Calibration Protocol v2

This document defines the LLM-grader calibration experiment under the v3 evaluation scheme. The goal is to test whether different grader designs align with coach references, not to replace coaches with an LLM judge.

## Graders Compared

We compare three grader types:

1. `likert_only_judge`
   - Produces only a holistic Likert score or simple quality decision.
   - Tests whether direct scoring is unstable.

2. `generic_rubric_judge`
   - Uses a generic tutoring rubric.
   - Does not read case-specific forbidden content or critical bridge boundaries.

3. `case_specific_bridge_rubric_judge`
   - Reads `success_criteria`, `forbidden_content`, `critical_bridge_boundary`, `acceptable_reveal`, and `expected_student_next_action`.
   - Specifically evaluates missing bridge and critical bridge leakage.

## Input

The current 500-row human review is used as a dev reference. Each grader prompt includes:

- problem statement or necessary problem context;
- current student message;
- recent dialogue;
- context AI reply;
- case-specific rubric;
- target AI response;
- no unblinded condition identity.

Note: historical 500-row dev workbooks may not contain v3 case-specific rubric fields. Calibration packs must record `case_specific_rubric_present`; rows without these fields may be used for Likert-only / generic-rubric comparison, but not as headline evidence for the case-specific grader.

## Output Schema

The LLM grader must support:

```text
UNKNOWN / INSUFFICIENT_CONTEXT
```

Minimum output:

```json
{
  "overall_quality": 1,
  "student_ready": "yes|borderline|no|UNKNOWN",
  "leakage_label": "no_leakage|minor_bridge_leakage|major_bridge_leakage|answer_leakage|UNKNOWN",
  "bridge_reveal_justification": "no_reveal|pedagogically_justified|borderline|unjustified|UNKNOWN",
  "scaffold_sufficiency": 0,
  "student_response_burden": "low|medium|high|UNKNOWN",
  "rationale": "..."
}
```

## Metrics

Report:

- overall agreement;
- student-ready agreement;
- leakage precision / recall / F1;
- major leakage false negative rate;
- answer leakage false negative rate;
- UNKNOWN / INSUFFICIENT_CONTEXT rate;
- case-specific rubric coverage;
- qualitative disagreement memo against coach notes.

The most important safety metric is:

```text
major leakage false negative rate
```

because passing a serious critical-bridge leak is more harmful than over-flagging a minor leak.

## Phased Run

1. 20-row calibration smoke: check schema, UNKNOWN behavior, and obvious misses.
2. 500-row dev reference: run dev calibration.
3. Freeze grader prompts.
4. After the 50-case held-out study, only report frozen-grader agreement with coach references; do not tune graders on held-out labels.

## Interpretation Boundaries

- LLM graders are not gold truth.
- If the case-specific grader outperforms the Likert-only grader, the claim is that case-specific rubrics help open-ended evaluation.
- This project does not perform RL and does not train tutors on grader outputs.
- The relation to Rubrics as Rewards is limited to rubric-based evaluation; we do not use rubric-reward RL.
