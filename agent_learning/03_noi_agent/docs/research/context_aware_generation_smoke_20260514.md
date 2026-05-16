# Context-aware Generation Smoke Report 20260514

中文版本：`context_aware_generation_smoke_20260514.zh.md`

## Purpose

This report records two development smoke runs after fixing offline generation to mimic the online AIChat context path. The goal is not to produce paper results, but to verify that the runner now sees the intended context and to identify remaining response-quality risks before a larger 50-case generation run.

## Runs

| Run | Input | Conditions | Rows | Context focus | Integrity |
| --- | --- | --- | ---: | --- | --- |
| `context_aware_smoke10_20260514` | `bridgebench_cp_heldout_v3_50_draft.jsonl`, first 10 cases | `dbox_bridge_hybrid` | 50 | no recent dialogue cases | pass |
| `context_aware_followup_smoke5_20260514` | selected follow-up cases | `dbox_bridge_hybrid` | 25 | parsed recent dialogue | pass |

Conditions: `enhanced_prompt_only_clean`, `dbox_inspired_clean`, `dbox_inspired_guard`, `bridge_contract_compact_guard`, `bridge_guided_dbox_style_guard`.

Artifacts:

- `evals/aichat/ad_hoc_runs/context_aware_smoke10_20260514/`
- `evals/aichat/ad_hoc_runs/context_aware_followup_smoke5_20260514/`
- `docs/research/context_aware_smoke10_integrity_20260514.json`
- `docs/research/context_aware_followup_smoke5_integrity_20260514.json`

## What Passed

- The v3 held-out data no longer has recent-dialogue/current-message mismatch in validation.
- The offline runner now injects parsed recent dialogue before the current student message when `recent_dialogue` is available.
- The follow-up smoke recorded `generation_context_source=parsed_recent_dialogue` for all follow-up rows.
- The follow-up smoke used multi-message generation contexts: most rows had 3 messages and the long-context row had 5 messages.
- No rows had empty final responses.
- No rows had duplicate or missing condition/case pairs.
- No visible `[LEVEL:Lx]` tags remained in final student-visible responses.
- Review CSV/XLSX exports now include `context_alignment_flag`, so researchers can separate `no_recent_dialogue`, `aligned_prior_context_ends_with_assistant`, and mismatch cases before interpreting coach scores.

## What The Smoke Revealed

The context plumbing is fixed, but quality and leakage risks remain. In the follow-up smoke, responses generally followed the current student question and prior AI turn, but several high-risk contribution/aggregation cases still produced over-complete hints. In particular, the P3948-style path/interval marking case still triggered responses that effectively told the student to turn an interval contribution into endpoint difference markers. This suggests the previous poor review scores were partly caused by context mismatch, but not only by context mismatch.

## Interpretation

This smoke should be treated as a development check only. It supports moving from data-integrity debugging to a small human/AI review of context-aware outputs, but it does not yet justify a formal 50-case headline run.

Recommended next gate:

1. Inspect the 5 follow-up cases in the generated review workbook.
2. Decide whether the remaining over-complete contribution/aggregation hints are acceptable for the current dev prompt.
3. If unacceptable, patch prompts/guard on the dev set and rerun the same smoke.
4. If acceptable, run the 50-case generation-only suite with the same context-aware runner.
