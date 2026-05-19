# Submission Readiness Checklist 20260519

## Scope

This checklist summarizes submission-prep readiness for the dialogue-state v3 evidence package. It does not add experiments, change prompts, alter AIChat, or modify main experiment data.

| Area | Status | Notes |
| --- | --- | --- |
| A. Evidence readiness | ready | Evidence package, manifest, main tables, pairwise uncertainty, stress, fairness sensitivity, and calibration reports exist and reproduce. |
| B. Claim safety | ready | Final claim gate exists; main wording is restricted to trade-offs and favorable trends. |
| C. Human review validity | ready | Coach A/B completed 350 reviews; priority60 adjudication and sensitivity analysis exist. Must not call labels final gold. |
| D. Baseline fairness | ready with limitation | Strong baselines are documented; DBox+Repair exists only as targeted sensitivity, not full main validation. |
| E. Repair causal boundary | ready | Same-candidate stress supports leakage reduction with burden trade-off; main means are not used as causal proof. |
| F. LLM grader calibration boundary | ready with limitation | DeepSeek calibration supports auxiliary-only framing; critical recall risk and same-backend coupling block replacement or cross-backend validation claims. |
| G. AI writing compliance | needs work | Disclosure and verification logs exist; human author must complete citation and section-by-section verification. |
| H. Ethics / privacy / student data | needs work | Data boundary is documented, but final manuscript still needs venue-specific ethics/privacy wording. |
| I. Reproducibility | ready | Verify, reproduce, unit tests, and bilingual validator pass at this checkpoint; legacy unpaired docs remain non-blocking debt. |
| J. Formatting and submission | needs work | Markdown sources are ready; venue template, BibTeX, rendered figures/tables, and final PDF are not done. |

## Current Readiness

```text
draft-ready / workshop-prep ready
not yet camera-ready conference submission
```

## Remaining Work Before arXiv

1. Human author line-edits the full manuscript skeleton into a readable draft.
2. Verify every external citation and replace placeholder metadata.
3. Render tables and figures.
4. Complete AI writing disclosure and ethics/data-governance wording.
5. Run final claim-gate scan and reproduction commands.

## Remaining Work Before Conference Submission

1. Choose target venue and page limit.
2. Convert manuscript to the venue template.
3. Move appendix-only material out of the main text.
4. Complete bibliography and DOI/proceedings checks.
5. Run an external evidence audit on the final assembled PDF and supplement.
