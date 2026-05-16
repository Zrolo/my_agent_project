# AIChat Response Blind-Review Rubric v2

This file defines the standard rubric for all Research v1 response blind reviews. It evaluates the student-facing `final_response_text`, not the runtime judge, routing, or repair trace. Every exported Chinese review workbook should include these criteria and examples.

## General Rules

1. The target of evaluation is the AI response, not the student.
2. Dimension-level scores use `0/1/2`: `2=good`, `1=partial`, `0=poor`.
3. Overall quality uses `1/2/3/4/5` to preserve the coach's holistic judgment.
4. If a dimension is not applicable, use the applicability field or explain in notes instead of forcing a penalty.
5. Low-confidence, boundary, and multi-bridge cases should be marked with `needs_discussion=yes`.
6. Coach labels are expert references, not absolute ground truth; uncertain rows should enter double review or adjudication.
7. Online student replies are usually short, but the review target is not “shorter is always better.” When scoring next-step clarity, check whether the requested action follows minimal sufficient student effort: no more burdensome than necessary, while still cognitively and diagnostically informative.
8. Starting from this version, review workbooks should include `coach_student_response_burden`. This field does not replace `coach_next_step_clarity_score`; it specifically records how much the student must type or work out in the next turn.
9. Starting from this version, review workbooks should also include `coach_scaffold_sufficiency_score`. This field prevents the rubric from rewarding over-withholding: a response can be safe from leakage but still poor if it gives too little usable help.
10. Starting from this version, formal review must include a calibration round before blind review; at least 20%-40% of cases should be independently reviewed by a second coach, with agreement / adjudication reported.
11. Notes are not optional decoration. Rows with major leakage, answer leakage, no-show decisions, low overall quality, best/worst rank, low confidence, or discussion flags must include a short reason.

## Reliability Workflow

### Calibration round

Before formal evaluation, sample 5 cases for calibration. Two coaches first judge independently, then discuss boundaries:

- when concept explanation becomes critical bridge leakage;
- when a response is safe but insufficient;
- when a micro-example is scaffolding versus worked-example leakage;
- when student response burden is too high;
- when context mismatch should be marked for discussion instead of forced into a score.

Calibration samples align standards and are not headline results.

### Partial double annotation

For formal 50-case evaluation, Coach A reviews all samples and Coach B independently reviews 20%-40% of cases. The overlap should cover bridge types, difficulty levels, code/no-code cases, follow-up turns, and AI-prelim high-risk rows.

Reports should include:

- percent agreement for categorical labels;
- weighted agreement / weighted kappa for ordinal scores;
- win/tie/loss agreement for same-case preferences;
- agreement on major bridge leakage;
- agreement on would-show-to-student;
- needs_adjudication_case_ids.

### Adjudication

Adjudicate rows with:

- `no_leakage` vs `major_bridge_leakage / answer_leakage`;
- `would_show_to_student=yes` vs `no`;
- overall quality differs by 2 or more levels;
- either coach marks `needs_discussion=yes`;
- possible context mismatch.

Final labels should be called `coach reference` or `adjudicated reference`, not absolute ground truth.

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

### Scaffold Sufficiency `coach_scaffold_sufficiency_score`

- `2`: The response gives enough observation direction, local evidence, or a next micro-task for the student to make progress, while still not completing the current bridge.
- `1`: The response is somewhat conservative or generic, but the student can still continue.
- `0`: The response over-withholds help: it is safe but not useful, only says “think again,” only asks for problem ID/code despite an already visible bottleneck, or gives no meaningful way forward.

This dimension should be read together with leakage control. A high-quality tutor response is not merely non-leaky; it should provide enough scaffolding for the student to continue thinking.

Example: If the student has already asked what lazy propagation means, “please paste the code” is usually insufficient. A better response gives a non-revealing observation prompt about which level has been updated and which level has not yet been synchronized.

### Critical Bridge Leakage Control `coach_bridge_leakage_control_score`

- `2`: Does not reveal the current critical bridge.
- `1`: Gives a strong hint, but the student still needs to reason.
- `0`: Directly completes the critical bridge or gives the full answer/code.

Key question: after reading the AI response, does the student still need to construct the current bridge? If not, this is usually a `0`.

Example: If the student asks how `check(mid)` should return true/false, directly giving the full feasibility condition and boundary update is usually critical bridge leakage.

### Next-Step Clarity `coach_next_step_clarity_score`

- `2`: The next student action is clear and specific, no more burdensome than necessary, and cognitively and diagnostically informative.
- `1`: There is a next step, but it is broad, overloaded, effortful, not concrete enough, or so short that it has little thinking value.
- `0`: No executable next step, or it requires a long explanation, complete table, or multi-step derivation.

Example: asking for one or two keywords, a local judgment, or one short sentence is more suitable for online AIChat than “fully explain the state and transition.” However, if the options themselves contain the critical bridge, the student may only guess rather than construct the relation. A good next step should be low-burden without being low-thinking.

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

## Leakage Label And Reveal Justification

### Leakage Label `coach_leakage_label`

- `no_leakage`: No current critical bridge is revealed.
- `minor_bridge_leakage`: The hint is strong, but the student still needs to reason.
- `major_bridge_leakage`: The current critical bridge is directly completed.
- `answer_leakage`: The response gives a full solution path, complete steps, or submit-ready code.

Leakage labels and leakage-control scores are related but not identical. The label describes the type of leakage; the score captures how well the response controlled instructional risk.

Do not treat every informative explanation as leakage. The key question is not whether the response mentions relevant knowledge, but whether it prematurely or completely performs the student's current missing bridge.

### Bridge Reveal Justification `coach_bridge_reveal_justification`

This field separates justified instructional disclosure from unjustified critical-bridge leakage.

- `no_reveal`: The response does not materially reveal the current bridge.
- `pedagogically_justified`: The reveal has a pedagogical reason. Common cases: the student already stated the bridge, the turn is a review/summary turn, L3-level help is appropriate, or the response merely confirms the student's own statement.
- `borderline`: The response reveals some bridge information, but it is unclear whether the reveal is premature or too complete.
- `unjustified`: The response prematurely or completely performs the current missing bridge for the student, such as giving the full state meaning, recurrence, predicate condition, boundary update, marking rule, or local code condition.

Examples:

- If the student has already said “I think `dp[j]` means the maximum value at capacity `j`,” confirming that the state direction is reasonable is usually not an unjustified leak.
- If the student only says “I don't know what `dp[j]` means,” directly giving the full state definition is usually `unjustified`.
- For lazy propagation, saying that a lazy tag records a parent-level update not yet synchronized to children may be a reasonable concept explanation; directly adding the child-state answer, pushdown timing, and clear-tag rule may become unjustified bridge completion.

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

### Student Response Burden `coach_student_response_burden`

This field measures how much the student must produce in the next turn after reading the AI response. It evaluates the **student's requested action**, not the length of the AI response.

- `low`: The student can answer with one or two keywords, a local judgment, or one short sentence. Multiple-choice only counts as healthy low burden when the options do not contain the critical bridge answer and only compare low-risk observations.
- `medium`: The student needs one or two short reasons, a local judgment, a small calculation, or a tiny example.
- `high`: The student needs a complete table, multi-step derivation, full simulation, complete rule, full formula, pseudocode, or code.

Examples:

- “Name whether you observed the old value or the new value, and add one very short reason” is usually `low` or `medium`.
- “For this small example, decide whether the child node value has already changed and give one short reason” is usually `medium`.
- “Fill in every step of the state table and summarize the complete rule” is usually `high`.

Educational rationale: in real AIChat use, students often reply briefly. A response may be conceptually relevant but still fail interactionally if it asks the student to write a long explanation, complete table, or multi-step derivation. However, `low` burden is not automatically good: if the student only mechanically clicks or selects without judging, comparing, attributing, or explaining, the cognitive and diagnostic value may be weak. Reports should therefore inspect `next-step clarity`, `student_response_burden`, and `student_ready_pass` together.

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
5. Report the low/medium/high distribution for `coach_student_response_burden`. For older workbooks without this field, a heuristic `student_response_burden` can support development analysis, but the 50-case held-out review should prefer coach labels.
6. Report `coach_scaffold_sufficiency_score` alongside leakage metrics. A system that has low leakage but low sufficiency may be over-withholding; it should not be treated as pedagogically successful.
