# Minimal Sufficient Student Effort Policy v1

This file records an important Research v1 interaction constraint and design principle:

```text
Student replies in online AIChat are usually short.
```

Reasons:

- typing cost is high, and students often avoid long explanations;
- students usually answer only the specific question the AI asks;
- detailed reasoning takes time and is often compressed into a few words, a local judgment, or one short sentence;
- if the AI asks for a complete table, full derivation, or multi-step explanation, students may disengage, answer superficially, or ask for the answer.

This does not mean that shorter is always better. The target principle is:

```text
minimal sufficient student effort: the requested action should be no more burdensome than necessary, but still cognitively and diagnostically informative.
```

Low typing cost must not mean low thinking. A mechanical A/B question can have low burden and still provide little learning value. If the options themselves contain the critical bridge, the student may only guess rather than construct the relation.

## Impact On Tutor Generation

Tutor prompts should follow:

- ask only one question;
- prefer short constructed responses, such as `one or two keywords, a local judgment, or one short sentence`;
- use multiple-choice sparingly; do not over-formalize small questions into forced choice tasks;
- if multiple-choice is used, options must not carry the critical bridge answer and should only compare non-critical observations; it is better as a fallback after the student is stuck;
- for small and clear questions, use a short answer plus a light confirmation instead of a formal choice scaffold;
- near a critical bridge, prefer short constructed observations; if phenomenon-choice plus reason-choice is used, require a very short reason to reduce guessing;
- do not require long explanations;
- do not require complete tables;
- do not require multi-step derivations;
- do not ask the student to abstract a full general rule in one turn;
- if using a micro-example, ask for one local observation or short judgment.

## Impact On Bridge-Oriented Micro-Examples

A high-quality micro-example is not a complex mini-assignment. It should create a low-input observation point.

Weak:

```text
Please simulate the entire array and summarize why reverse iteration is correct.
```

Better:

```text
Only look at capacity 4: in one short phrase, is it looking at the “old capacity 2” or the “just-updated capacity 2”? Add a 3-8 word reason.
```

If the student is stuck, you may downgrade to a low-risk choice format, but the options must not directly state the final rule:

```text
Only look at capacity 4. Reply with one combination:
A. It uses the just-updated capacity 2
B. It does not use the just-updated capacity 2
Reason:
1. The value comes from a cell updated in the current pass
2. The value can only come from an old cell from the previous pass
Reply A-1 / A-2 / B-1 / B-2.
```

Weak:

```text
Complete the table of how many times every node is passed and write all add/subtract marks.
```

Better:

```text
Only look at node 2: answer “passes” or “does not pass” for whether the path actually goes through it. Then we can check how to make the aggregate result reflect that fact.
```

## Impact On Blind Review

`coach_next_step_clarity_score` should include input cost:

- `2`: clear, specific next step whose burden is no higher than necessary and whose answer has cognitive and diagnostic value;
- `1`: there is a next step, but it is broad, overloaded, effortful, not concrete enough, or so short that it lacks thinking value;
- `0`: no executable next step, or the next step requires a long explanation, complete table, or multi-step derivation.

This does not weaken the learning goal and does not mean every turn should become a short multiple-choice item. It turns “make the student think” into a short constructed-response format that fits real online tutoring:

```text
low-burden but informative reply -> AI diagnoses / confirms -> gradual bridge crossing
```

instead of:

```text
ask the student to produce the full reasoning chain in one turn.
```

## Routing Guidance

- Small and clear questions: short answer plus light confirmation; do not force a choice scaffold.
- Conceptually fuzzy turns or critical-bridge-adjacent turns: micro-example plus a short constructed observation, so the student types little but must judge; use non-answer-bearing choices only as a fallback after the student is stuck.
- Transfer or summary turns: ask for one short explanation, not a long essay.
- Review, practice, or explicitly deep-diving turns: longer explanations, full tables, or multi-step derivations may be appropriate.

## Paper Wording

Recommended wording:

```text
We optimize for minimal sufficient student effort: the requested action should be no more burdensome than necessary, but still cognitively and diagnostically informative.
```
