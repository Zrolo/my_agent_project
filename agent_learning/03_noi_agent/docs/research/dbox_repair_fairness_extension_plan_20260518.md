# DBox+Repair Fairness Extension Plan 20260518

This plan only defines optional next steps. It does not automatically create new experiments, add a main-experiment condition, or change the online system. The existing DBox+Repair result should remain targeted fairness sensitivity evidence, not a main headline.

## Current State

- A 20-case targeted `dbox_inspired_guard_repair` review is complete.
- The review covers headline-sensitive cases, not a random full 50-case sample.
- Current result: DBox+Repair overall 3.55, safe-ready 11/20, major+answer leakage 0.
- Compared with the same 20-case DBox Guard subset, DBox+Repair mainly reduces severe leakage and slightly improves overall.
- Compared with the same 20-case Bridge Contract compact + Guard/Repair subset, Bridge still has higher overall / safe-ready.
- Limitation: single supplemental review, targeted sample, and reviewer/protocol mismatch with the main A/B review.

## Option A: Second-Coach Review Of 20-Case Risk/Discussion Rows

Method:

- Select rows with `needs_discussion=yes`, borderline show, minor leakage, or high burden from the existing 20-case review.
- Ask a second coach to review only those risk/discussion rows.
- Do not add conditions or regenerate responses; only re-review existing DBox+Repair outputs.

Pros:

- Lowest cost.
- Reduces reviewer/protocol mismatch.
- Improves confidence in the current appendix sensitivity result.

Limitations:

- Still not a full 50-case DBox+Repair evaluation.
- Still not a main condition-level result.

Safe wording:

```text
We additionally double-checked the highest-risk DBox+Repair add-on rows; the add-on remains a fairness sensitivity analysis rather than a main condition.
```

## Option B: Full 50-Case DBox+Repair Review

Method:

- Use the existing 50-row `dbox_inspired_guard_repair` generation package.
- Run the same rubric / blind-review workflow as the main experiment.
- Ideally use Coach A/B double review, or at least priority disagreement adjudication.

Pros:

- Strongest response to the baseline fairness concern.
- Directly compares:
  - `dbox_inspired_guard`
  - `dbox_inspired_guard_repair`
  - `bridge_contract_compact_guard_repair`

Limitations:

- Highest cost.
- If single-coach only, it still belongs in supplemental analysis.
- Adds result complexity and may dilute the main contribution.

Safe wording:

```text
In a full supplemental DBox+Repair review, we compare repair-enabled DBox against repair-enabled Bridge Contract under the same rubric.
```

## Option C: Keep Current Appendix Sensitivity With Explicit Limitation

Method:

- Do not add review.
- Keep the current 20-case targeted review.
- State clearly in Results / Discussion:
  - DBox+Repair is fairness sensitivity;
  - it is not a full 50-case double-coach main condition;
  - it cannot prove Bridge+Repair significantly beats all repair-enabled baselines.

Pros:

- No added experimental cost.
- Current evidence already shows the fairness concern was checked.
- Keeps the paper storyline clean.

Limitations:

- Reviewers may still request a fuller repair-enabled DBox baseline.
- This supports limitation wording, not a strong comparison.

Safe wording:

```text
We include a targeted DBox+Repair fairness add-on as appendix sensitivity. It reduces major/answer leakage on the targeted subset but does not replace a full double-coach 50-case add-on review.
```

## Recommendation

The safest pre-submission choice is **Option C**, with **Option A** if time permits. Use **Option B** only if the target review standard requires a complete repair-enabled DBox baseline.
