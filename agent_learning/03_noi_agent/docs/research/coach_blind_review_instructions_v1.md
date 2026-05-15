# External Coach Blind Review Instructions v1

Date: 2026-05-12

This guide is for competitive-programming coaches who are not familiar with the internal system. Reviewers do not need to understand Bridge Contract, DBox-inspired baselines, Guard, Repair, or any runtime module. They should judge only the problem statement / necessary statement, student turn, problem context, recent dialogue, and the final AI response.

## One-Sentence Goal

The blind review is not about choosing which system looks smarter. It asks:

> Does this AI response identify the student's current missing reasoning bridge and provide an appropriate next step without directly completing that bridge for the student?

## Standard Review Workflow

Before formal review, run a small calibration round:

1. Sample 5 cases and have two coaches review them.
2. Coaches first judge independently, then discuss disagreements.
3. Calibrate what counts as major bridge leakage, justified concept explanation, safe-but-insufficient scaffolding, and excessive student response burden.
4. Calibration samples are used to align review standards and should not enter headline results.

During formal review, at least 20%-40% of cases should be independently reviewed by a second coach. Major disagreements should enter adjudication. Final labels should be called `coach reference` or `adjudicated reference`, not absolute ground truth.

## Ignore During Review

- Do not guess which system or model produced the response.
- Do not automatically reward longer or more complete responses.
- Do not automatically reward responses merely because they avoid full answers.
- Do not evaluate the response as a full solution write-up.
- Do not expect every response to provide the full algorithm, proof, code, or template.

## Read Before Scoring

For each row, read fields in a fixed order. This avoids mixing up `recent_dialogue`, the extracted prior AI prompt, and the current student turn.

1. First read `problem_source_platform`, `problem_source_id`, `problem_source_url`, `problem_statement`, and `problem_context`.
2. Then read `recent_dialogue` only to understand why the student asks the current turn.
3. Then read `prior AI prompt/hint extracted from recent dialogue`. This is a derived display field, not an extra model input and not an independent data source.
4. Then read `student_message`. This is the core turn the AI must answer.
5. Finally evaluate only `AI response to score`. All quality scores, leakage labels, and show-to-student decisions apply only to this response.

The source and statement both matter. Coaches need to know where the problem comes from and enough task information to identify the student's local bridge and to decide whether the AI reveals a relation not already given by the task statement. `problem_context` is a compressed context field and should not replace the statement.

Recent dialogue matters. The same AI response may be justified confirmation if the student already stated the bridge, but leakage if the student has not.

### Handling Context Problems

- If `recent_dialogue` and `student_message` clearly do not align: mark `needs_discussion=yes`, note “possible context mismatch,” and avoid forcing a high or low score.
- If the AI response only follows the statement or gives generic algorithm talk without answering `student_message`: lower `groundedness` and `bridge identification`.
- If the AI response answers the current student turn but does not continue the prior AI prompt/hint: reflect that in `next-step clarity` and notes.
- The extracted prior AI prompt/hint is only a reading aid for short student turns. Do not score it separately.

## When Notes Are Required

Please write a short reason in `coach_notes` when:

- `leakage_label = major_bridge_leakage`;
- `leakage_label = answer_leakage`;
- `would_show_to_student = no`;
- `overall_quality <= 2`;
- you rank a response as best or worst within the same case;
- `needs_discussion = yes`;
- the context appears mismatched;
- reviewer confidence is low.

Recommended format:

```text
Strength: ...
Issue: ...
Suggestion: ...
```

## Core Concepts

### Missing Bridge

A `missing bridge` is the key reasoning relation between what the student already knows and what they need in order to make the next meaningful step.

Examples:

- The student knows DP is relevant but cannot define what `dp[i][j]` means.
- The student knows answer binary search is relevant but cannot decide what `check(mid)` means.
- The student knows tree path difference is relevant but cannot map path endpoints and LCA to marks.
- The student knows lazy propagation is needed but cannot explain what `lazy` records as already applied versus not yet pushed down.

### Critical Bridge Leakage

`Critical bridge leakage` occurs when the AI does not reveal a full solution or code, but still directly reveals the key intermediate reasoning bridge the student should construct.

Common cases:

- complete state definition;
- complete recurrence;
- complete `check` predicate and boundary update;
- complete greedy criterion;
- complete marking or contribution formula;
- a fully worked micro-example that demonstrates the exact relation the student was supposed to infer.

## Scoring Dimensions

Use `0/1/2` for detailed dimensions:

- `2`: good
- `1`: partial or mixed
- `0`: poor or risky

### 1. Bridge Identification

Does the response address the student's actual bottleneck?

- `2`: directly targets the current missing bridge.
- `1`: relevant but broad or partial.
- `0`: misses the bottleneck or gives a generic algorithm explanation.

### 2. Groundedness

Does the response use the problem, student wording, recent dialogue, or code evidence?

- `2`: clearly grounded in the current context.
- `1`: somewhat grounded but still template-like.
- `0`: generic and weakly related to context.

### 3. Scaffold Appropriateness

Is the help level suitable?

- `2`: neither too weak nor too strong.
- `1`: slightly weak or strong but still useful.
- `0`: gives the answer/critical bridge, or only gives empty encouragement.

### 4. Scaffold Sufficiency

Does the response give enough help to continue?

- `2`: enough local direction or a micro-task to make progress without completing the bridge.
- `1`: somewhat conservative or generic, but still usable.
- `0`: over-withholding; safe but not useful; only says “think again,” asks for problem ID/code despite a visible bottleneck, or gives no meaningful next direction.

This prevents reviewers from rewarding responses simply because they avoid leakage. A safe but empty response is still a weak tutor response.

### 5. Bridge Leakage Control

After reading the response, does the student still need to construct the current key bridge?

- `2`: the bridge is not revealed.
- `1`: the hint is strong, but the student still needs to reason.
- `0`: the response directly completes the bridge or gives full answer/code.

### 6. Next-Step Clarity

Does the student know what to do next?

- `2`: the next step is concrete, executable, not heavier than necessary, and cognitively useful.
- `1`: there is a next step, but it is broad, mechanical, or somewhat burdensome.
- `0`: no actionable next step, or it asks for a long derivation/table/proof.

Online students often reply briefly. A good next step should not require a long essay, but should still require a meaningful judgment, comparison, attribution, or short explanation.

### 7. Single-Focus Coherence

- `2`: keeps one main focus.
- `1`: mostly focused with minor drift.
- `0`: mixes too many goals.

### 8. Bridge-Oriented Micro-Example

If no micro-example is used or needed, mark it as not applicable.

If a micro-example is used:

- `2`: helps the student abstract a transferable relation.
- `1`: relevant but mostly a temporary task.
- `0`: directly reveals the bridge or is weakly related to the bottleneck.

## Overall Judgment

### Overall Quality 1-5

- `5`: excellent, very ready to show to students.
- `4`: good, ready with only minor issues.
- `3`: usable but clearly flawed.
- `2`: weak, not recommended without editing.
- `1`: unusable.

This is not a mechanical average of detailed scores.

### Would Show to Student

- `yes`: can be shown directly.
- `borderline`: needs light human editing.
- `no`: should not be shown.

Major bridge leakage usually means this should not be `yes`, even if the writing is fluent.

### Student Response Burden

How much does the student need to type next?

- `low`: one or two keywords, a short judgment, or one short reason.
- `medium`: one or two sentences, a local example, or a small calculation.
- `high`: a full table, multi-step derivation, full formula, pseudocode, or code.

Low burden is not automatically good. If the student can answer mechanically without thinking, score next-step clarity or micro-example quality lower.

## Leakage Label

Use one label:

- `no_leakage`: no current critical bridge is revealed.
- `minor_bridge_leakage`: strong hint, but the student still needs to reason.
- `major_bridge_leakage`: directly completes the current critical bridge.
- `answer_leakage`: gives full solution, full steps, or submit-ready code.

Ask:

> Did this response do the key step for the student?

If yes, it is usually at least `major_bridge_leakage`.

## Common Boundary Cases

### Not Every Explanation Is Leakage

Background explanation or terminology clarification is not necessarily leakage if it does not complete the current bridge.

### Student-Stated Bridges Are Different

If the student already stated the bridge, confirmation is often not leakage.

### Worked Examples Can Leak

A small but fully worked example can still reveal the critical bridge. Do not assume it is safe just because it is a micro-example.

### Multiple Choice Needs Caution

Multiple choice is not inherently wrong, but if the options contain the critical bridge answer, the student may only guess. Short constructed responses are often better: a keyword, local judgment, or very short reason.

## Notes

Keep comments short and specific:

```text
Strength: targets lazy semantics and gives a clear next step.
Issue: the example demonstrates the full pushdown relation, so it is too revealing.
Suggestion: keep the example but remove the complete rule; ask the student to judge which layer has been updated.
```

If uncertain, write:

```text
needs_discussion: ...
```

## Final Reminder

The review is not meant to prove one system is always best. It supports fair comparison across three trade-offs:

1. whether the response helps the current bottleneck;
2. whether it avoids prematurely revealing the critical bridge;
3. whether it gives enough help rather than over-withholding;
4. whether it lets the student continue with low to medium effort while still thinking.
