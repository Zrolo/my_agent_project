# Manuscript Human Revision Checklist

## Scope

Use this checklist before any external release. It is a human-author checklist; AI-generated text is not submission-ready until the relevant boxes are reviewed.

| Section | Human line edit done | AI meta-comments removed | Citations verified | Numbers reproduced | Forbidden wording avoided | Tone is restrained | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Abstract | no | no | n/a | no | no | no | Check that claims are framework/trade-off claims. |
| Introduction | no | no | no | n/a | no | no | Verify related-work positioning and avoid system-victory framing. |
| Related Work | no | no | no | n/a | no | no | Open every cited paper and verify BibTeX. |
| Task Definition | no | no | n/a | n/a | no | no | Keep missing bridge and critical bridge leakage definitions precise. |
| Dataset / Protocol | no | no | n/a | no | no | no | Do not call 50 cases universal or final gold. |
| Baselines | no | no | no | n/a | no | no | DBox-inspired is not faithful DBox reproduction. |
| Results | no | no | n/a | no | no | no | Main headline uses `main_scaffold_eval`; all-50 only appendix. |
| Repair Stress | no | no | n/a | no | no | no | Causal wording only from same-candidate stress; include burden trade-off. |
| LLM Grader Calibration | no | no | no | no | no | no | Auxiliary only; do not imply replacement for human coaches. |
| Discussion | no | no | n/a | no | no | no | Make limitations visible, not hidden. |
| Limitations | no | no | n/a | n/a | no | no | Include rater sensitivity, coverage, DBox+Repair, and LLM grader limits. |
| Ethics / AI Use | no | no | n/a | n/a | no | no | Include AI writing disclosure and data governance statement. |

## Required Manual Actions

1. Replace `no` with `yes` only after a human author checks the section.
2. Verify citations using `citation_verification_log.csv`.
3. Verify result numbers using `result_number_verification_log.csv`.
4. Run the final claim gate scan before submission.
