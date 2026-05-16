# Critical Bridge Leakage Calibration Policy v1

This file prevents the Research v1 leakage rubric from becoming overly sensitive. Core principle:

```text
We do not penalize every mention of bridge-related knowledge.
We penalize unjustified, premature, or overly complete completion of the student's current missing bridge.
```

## Why Calibration Is Needed

In competitive-programming tutoring, never explaining concepts can frustrate students. But directly revealing the current state definition, recurrence, predicate condition, boundary update, marking rule, or local code condition can bypass the reasoning step the turn is meant to train.

Critical bridge leakage is therefore an instructional risk, not an absolute ban. It must be judged with:

- whether the student has already stated the bridge;
- whether the turn is active problem solving, review, reflection, or direct-answer seeking;
- whether the allowed help level is L1/L2 or L3;
- whether the response still leaves a meaningful next reasoning step;
- whether the response asks for upstream observation or directly fills the current answer slot.

## Three-Layer Judgment

### 1. Bridge Information Present

The response mentions related bridge information, such as state, transition, `check`, boundary, lazy tag, LCA, or prefix sum.

This alone is not leakage.

### 2. Bridge Reveal

The response reveals part of the key relation and moves the student closer to the answer.

This may be legitimate scaffolding or may be too strong, depending on the student's state and allowed help level.

### 3. Unjustified Critical Bridge Leakage

The student has not constructed the current missing bridge, and the AI directly completes the precise relation, formula, direction, rule, or code condition. Headline leakage analysis should primarily penalize this case.

## New Review Field

Future response blind-review workbooks include:

```text
coach_bridge_reveal_justification
```

Allowed values:

- `no_reveal`: no material reveal of the current bridge;
- `pedagogically_justified`: the reveal has a pedagogical reason, such as the student already stated it, the turn is review/summary, L3-level help is appropriate, or the AI only confirms the student's own statement;
- `borderline`: boundary case where it is unclear whether the reveal is premature or too complete;
- `unjustified`: no pedagogical justification; the AI prematurely or completely performs the current missing bridge for the student.

This field complements `coach_leakage_label`:

```text
coach_leakage_label = leakage type / severity
coach_bridge_reveal_justification = whether the reveal has pedagogical justification
```

## Examples

### Not Unjustified Leakage

Student:

```text
I think dp[j] means the maximum value at capacity j.
```

AI:

```text
That state direction is reasonable. Next, try saying which two old states dp[j] may come from when the current item is considered.
```

The student already stated the bridge, so the AI is confirming and moving to the next step.

### Potentially Justified Concept Explanation

Student:

```text
What exactly does lazy mean has not been done yet?
```

AI:

```text
You can first view lazy as an update recorded at the parent that has not yet been synchronized to the children. Now judge: if the parent interval has already been updated as a whole, must the two child nodes already be individually updated?
```

This gives a semi-abstract concept while still asking the student to reason about the parent-child relation.

### Unjustified Critical Bridge Leakage

Student:

```text
I do not know whether check(mid) should return true or false.
```

AI:

```text
If mid is feasible, return true and move the right boundary; if infeasible, return false and move the left boundary.
```

If the current missing bridge is the true/false semantics and boundary update direction, this is usually `unjustified`.

## Impact On Static Lint And Guard

- `static lint` only flags form-level risk; it does not adjudicate leakage.
- The Leakage Guard should judge semantic leakage, but must be calibrated against coach labels.
- With the new justification field, reports should include:
  - coach leakage label;
  - bridge reveal justification;
  - automatic Guard label;
  - static lint risk;
  - Guard false positives / false negatives;
  - overlap between static lint and `unjustified` reveals.

## Paper Wording

Recommended wording:

```text
Critical bridge leakage is not defined as the presence of any bridge-related information.
It refers to unjustified, premature, or overly complete completion of the student's current missing bridge.
```

