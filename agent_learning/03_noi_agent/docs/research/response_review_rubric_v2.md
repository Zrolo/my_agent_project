# AIChat Response Blind-Review Rubric v2

This file defines the standard rubric for all Research v1 response blind reviews. It evaluates the student-facing `final_response_text`, not the runtime judge, routing, or repair trace. Every exported Chinese review workbook should include these criteria and examples.

## General Rules

1. The target of evaluation is the AI response, not the student.
2. Dimension-level scores use `0/1/2`: `2=good`, `1=partial`, `0=poor`.
3. Overall quality uses `1/2/3/4/5` to preserve the coach's holistic judgment.
4. If a dimension is not applicable, use the applicability field or explain in notes instead of forcing a penalty.
5. Low-confidence, boundary, and multi-bridge cases should be marked with `needs_discussion=yes`.
6. Coach labels are expert references, not absolute ground truth; uncertain rows should enter double review or adjudication.

## Dimension Scores

### Bridge Identification `coach_bridge_identification_score`

- `2`: Directly targets the student's current missing bridge or bottleneck.
- `1`: Related, but too broad, indirect, or only partially identifies the bottleneck.
- `0`: Misses the bottleneck or answers the wrong question.

Example: If the student says “I don't know how to define the state,” a high-scoring response should guide what information the state must preserve; a low-scoring response only says “DP needs state and transition.”

### Groundedness `coach_groundedness_score`

- `2`: Clearly uses the problem, student wording, recent dialogue, or code evidence.
- `1`: Somewhat grounded, but still generic.
- `0`: Template-like and weakly connected to context.

Example: For a lazy propagation question, a response grounded in “range add, range sum, node interval” is stronger than a generic statement that “lazy means delayed update.”

### Scaffold Appropriateness `coach_scaffold_appropriateness_score`

- `2`: Help strength fits the student's current state.
- `1`: Slightly too weak or too strong, but still useful.
- `0`: Gives the answer/code, or only asks a vague question.

Example: If the student only says “I don't know,” giving the full recurrence is too strong; saying only “think again” is too weak.

### Critical Bridge Leakage Control `coach_bridge_leakage_control_score`

- `2`: Does not reveal the current critical bridge.
- `1`: Gives a strong hint, but the student still needs to reason.
- `0`: Directly completes the critical bridge or gives the full answer/code.

Key question: after reading the AI response, does the student still need to construct the current bridge? If not, this is usually a `0`.

Example: If the student asks how `check(mid)` should return true/false, directly giving the full feasibility condition and boundary update is usually critical bridge leakage.

### Next-Step Clarity `coach_next_step_clarity_score`

- `2`: The next student action is clear, specific, and answerable.
- `1`: There is a next step, but it is broad, overloaded, or not concrete.
- `0`: No executable next step.

Example: “First write one sentence describing what `dp[j]` should store” is clearer than “think about the state and transition.”

### Single-Focus Coherence `coach_single_focus_coherence_score`

- `2`: Stays on one main bottleneck.
- `1`: Mostly focused, with minor drift.
- `0`: Mixes several goals and may confuse the student.

Example: If the student is stuck on state semantics, explaining state, transition, complexity, and code template at once should be penalized.

### Bridge-Oriented Micro-Example `coach_bridge_oriented_micro_example_score`

First mark `coach_micro_example_applicability`:

- `applicable`: This response uses or should use a micro-example.
- `not_applicable`: This turn does not require a micro-example; the micro-example score may be left blank.

Score:

- `2`: The example helps the student abstract a transferable bridge relation.
- `1`: The example is relevant but behaves more like a temporary task.
- `0`: The example is weakly connected to the bottleneck or directly completes the bridge.

A high-quality micro-example does not merely ask the student to fill in a local answer; it frames what relation to observe and asks the student to generalize it.

Example: In lazy propagation, asking only “have the children been incremented by 5?” is a local check; a stronger example asks what this says about where the update has already taken effect and where it has not yet been pushed.

## Leakage Label `coach_leakage_label`

- `no_leakage`: No current critical bridge is revealed.
- `minor_bridge_leakage`: The hint is strong, but the student still needs to reason.
- `major_bridge_leakage`: The current critical bridge is directly completed.
- `answer_leakage`: The response gives a full solution path, complete steps, or submit-ready code.

Leakage labels and leakage-control scores are related but not identical. The label describes the type of leakage; the score captures how well the response controlled instructional risk.

## Holistic Fields

### Overall Quality `coach_overall_quality_score`

- `5`: Excellent; strongly willing to show it to the student.
- `4`: Good; showable with only minor issues.
- `3`: Usable; helpful but has clear weaknesses.
- `2`: Borderline; many issues, weak reference only.
- `1`: Unusable; should not be shown to the student.

Overall quality is not a mechanical average of dimension scores. It preserves the coach's holistic judgment.

### Would Show To Student `coach_would_show_to_student`

- `yes`: Can be shown directly.
- `borderline`: Needs human edits or has clear risk.
- `no`: Should not be shown.

### Reviewer Confidence `coach_reviewer_confidence`

- `high`: The rating is confident.
- `medium`: Mostly confident, but there may be boundary issues.
- `low`: Evidence is insufficient or the judgment is difficult.

### Needs Discussion `coach_needs_discussion`

- `no`: No discussion needed.
- `yes`: Needs discussion.

Use `yes` for multi-bridge bottlenecks, insufficient context, ambiguous leakage severity, or uncertainty about how much help should be allowed.

## Analysis Guidance

1. Do not treat all rows as independent samples; use paired comparisons by `case_id`.
2. For `0/1/2` scores, report both means and distributions, but also inspect system win rates, overall quality, and would-show decisions.
3. Rows with `coach_reviewer_confidence=low` or `coach_needs_discussion=yes` should be reported separately and not overused for headline claims.
4. `bridge-oriented micro-example` should be analyzed only on applicable rows; non-applicable rows should not count as zero.
