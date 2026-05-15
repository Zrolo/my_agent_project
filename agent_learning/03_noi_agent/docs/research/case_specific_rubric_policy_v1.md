# Case-specific Rubric Policy v1

This policy defines the case-specific fields required for response review. The goal is not to make coach review mechanical, but to reduce guesswork and improve rating consistency.

## Required Fields

Each response-review case should include:

| Field | Purpose |
| --- | --- |
| `success_criteria` | What a good response should help the student do next |
| `forbidden_content` | What the tutor must not directly complete in this turn |
| `critical_bridge_boundary` | What would count as critical bridge leakage if directly revealed |
| `acceptable_reveal` | What information may be given without being over-penalized |
| `expected_student_next_action` | The expected next action after a good tutor response |

## Writing Principles

1. Fields must target the current student message, not the full solution.
2. Forbidden content should describe abstract bridge boundaries, not only algorithm-specific templates.
3. `acceptable_reveal` should clarify which conceptual explanations, restatements, or confirmations are reasonable.
4. `expected_student_next_action` should follow minimal sufficient student effort: short but cognitively meaningful.
5. If the case lacks enough information, mark it as low-confidence or a clarification/safety slice instead of forcing it into the main study.

## Example

Student message:

```text
I can write some range-add segment tree code, but I cannot explain what lazy still has not done.
```

Possible rubric:

```json
{
  "success_criteria": [
    "The student distinguishes an updated parent sum from child nodes that have not yet received the update",
    "The student can describe lazy as a delayed increment for children"
  ],
  "forbidden_content": [
    "Do not provide full pushdown code",
    "Do not fully explain the entire lazy-propagation template"
  ],
  "critical_bridge_boundary": "If the response directly states that lazy is the increment not yet propagated to children and fully explains parent/child update timing, it may complete the current bridge.",
  "acceptable_reveal": "The tutor may ask the student to inspect whether leaves have really changed after marking the [1,2] node.",
  "expected_student_next_action": "The student judges whether child nodes have been updated and explains briefly."
}
```

## Relation To Leakage Judgment

`critical_bridge_boundary` is not meant to forbid all useful explanation. It helps coaches decide:

```text
Did the AI complete the current reasoning relation that the student was supposed to construct?
```

If the student already stated the relation, or if the turn is a review, L3 hint, or debugging confirmation, `acceptable_reveal` and `bridge_reveal_justification` should record that context.

## Quality Checks

Before a case enters a main experiment, check:

- no required field is blank;
- fields match the problem, current student message, and recent dialogue;
- success criteria do not contain the full solution;
- labels are not overfit to one algorithm template;
- an external coach can understand the rubric.
