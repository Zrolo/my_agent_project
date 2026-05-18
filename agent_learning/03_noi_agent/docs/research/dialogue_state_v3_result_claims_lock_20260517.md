# Dialogue-State v3 Result Claims Lock 20260517

## Purpose

This document locks what the dialogue-state v3 50-case human review can and cannot support. The current results are formal human-review evidence candidates, not final gold labels. Claims must be reported with slice separation, rater sensitivity, adjudication status, and paired uncertainty.

## Claims We Can Make

1. CP-MissingBridgeBench reveals quality-safety-burden trade-offs across LLM tutoring harnesses.
2. DBox-inspired decomposition is a strong baseline and should not be treated as a weak comparator.
3. Bridge Contract compact + Guard/Repair shows a relatively stable advantage in overall quality and critical-leakage control.
4. No-direct-code / no-direct-solution baselines can still produce critical bridge leakage; not giving full code or a full solution is not sufficient.
5. Student-ready, safe-ready, and rank preference are sensitive to rater strictness, so Coach A/B agreement, priority60 adjudication, and sensitivity analysis must be reported.
6. Guard-only conditions are guard-instrumented / guard-signal variants in the current main experiment; unless a block fallback fires, they do not rewrite final student-visible responses.
7. The repair-enabled condition performs well; the same-candidate stress test shows Repair can reduce leakage severity under fixed candidates, with student-burden trade-offs.
8. The targeted DBox+Repair fairness add-on shows that Repair can also help a DBox-inspired baseline reduce high-risk leakage; it is 20-case sensitivity evidence, not a new main-experiment condition.

## Claims We Cannot Make

1. Bridge Contract significantly and comprehensively outperforms all baselines.
2. Guard-only fixes final outputs.
3. Repair's causal effect has been proven by the main experiment.
4. Coach A or Coach B is gold.
5. Priority60 adjudicated labels are final gold.
6. All 50 cases can be pooled into one headline average.
7. The 50-case set covers all CP tutoring situations.
8. DBox / CodeHelp / CodeAid conditions are reproductions of the original systems; they are literature-inspired baselines.
9. DBox+Repair has completed full 50-case double-coach review, or Bridge+Repair has a confirmed advantage over every repair-enabled baseline.

## Recommended Wording

Use:

```text
trade-off
trend
stable advantage in overall quality
stable advantage in critical-leakage control
rater-sensitive student-ready preference
formal human-review evidence candidate
```

Avoid:

```text
absolute winner
fully solved
significant dominance
final gold
Guard-only rewrite / repair claim
Repair causally proven by the main experiment
```

## Suggested Paragraph

```text
CP-MissingBridgeBench distinguishes tutor harnesses by their quality-safety-burden trade-offs rather than by a single global winner. In the dialogue-state v3 human-review candidate evidence, DBox-inspired decomposition is a strong baseline, while Bridge Contract compact + Guard/Repair shows a stable advantage in overall quality and critical-leakage control. Same-candidate Repair stress testing and the targeted DBox+Repair fairness add-on support Repair as a leakage-reduction mechanism with burden / over-strong-hint trade-offs. However, student-ready and rank preferences are rater-sensitive, Guard-only variants are instrumentation rather than rewrite conditions, and DBox+Repair remains sensitivity evidence rather than a full main condition.
```

## Scope

The main paper headline should prioritize the `main_scaffold_eval` slice. `main_eval_with_caution`, `clarification_safety_slice`, and `policy_safety_slice` should be reported separately or in sensitivity / appendix analyses. All-case averages are supplementary sensitivity checks, not undifferentiated headlines.

Precise Repair wording: the same-candidate stress test supports "Repair reduces leakage under fixed-candidate stress testing, with burden trade-offs"; the main experiment still supports only repair-enabled condition-level trends.

Precise DBox+Repair wording: the 20-case targeted fairness add-on supports "DBox+Repair reduces major/answer leakage on headline-sensitive cases and does not overturn the Bridge+Repair trend", but not a full 50-case fair-baseline conclusion.
