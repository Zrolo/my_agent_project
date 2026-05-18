# Post-Level-Tag Patch Smoke 3 Report (2026-05-14)

This report records a 3-case smoke after `patch_20260514_remove_internal_level_tags_from_offline_research_outputs`. It is development-stage engineering evidence, not a formal paper result.

## Purpose

- Check whether offline research responses still contain internal `[LEVEL:Lx]` tags.
- Check whether Guard / Repair pipelines still export complete `final_response_text` after internal tags are removed.
- Identify runtime parameters that should be fixed before the 50-case generation run, especially Judge timeout and retry.

## Input And Setting

- Input data: `docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl`
- Cases: first 3 rows
  - `heldout_v4_luogu_001`
  - `heldout_v4_luogu_002`
  - `heldout_v4_luogu_003`
- Generation model: `deepseek_flash`
- Tutor thinking: `enabled`
- Judge provider: `deepseek`
- Tutor max tokens: `NOI_CHAT_MAX_COMPLETION_TOKENS=128000`
- Judge / Repair max tokens: `20000`

## First Run: No Retry / Default 5s Timeout

Output directories:

- `evals/aichat/ad_hoc_runs/post_level_tag_patch_smoke3_core_20260514`
- `evals/aichat/ad_hoc_runs/post_level_tag_patch_smoke3_guard_repair_20260514`

Results:

| Run | Rows | `[LEVEL]` hits | Empty final_response | stage_errors |
|---|---:|---:|---:|---:|
| core | 15 | 0 | 2 | 3 |
| guard_repair | 15 | 0 | 3 | 5 |

Main issues:

- `[LEVEL]` tags were removed.
- The default 5s Judge timeout was too tight and caused Bridge Judge / Leakage Judge timeouts.
- One Bridge Judge schema-invalid result appeared: `problem_solving_state has invalid enum: representation_state_bridge`.
- Empty final responses came from Judge-stage failures, not from removing `[LEVEL]`.

## Second Run: retry=1 / Judge timeout=25s

Output directories:

- `evals/aichat/ad_hoc_runs/post_level_tag_patch_smoke3_core_retry_20260514`
- `evals/aichat/ad_hoc_runs/post_level_tag_patch_smoke3_guard_repair_retry_20260514`

Results:

| Run | Rows | `[LEVEL]` hits | Empty final_response | stage_errors | review rows |
|---|---:|---:|---:|---:|---:|
| core_retry | 15 | 0 | 0 | 0 | 15 |
| guard_repair_retry | 15 | 0 | 0 | 0 | 15 |

Condition summary:

| Condition | Rows | Final source | Repair count | Retry count |
|---|---:|---|---:|---:|
| `enhanced_prompt_only_clean` | 3 | candidate ×3 | 0 | 0 |
| `dbox_inspired_clean` | 3 | candidate ×3 | 0 | 0 |
| `dbox_inspired_guard` | 3 | candidate ×3 | 0 | 0 |
| `bridge_contract_compact_guard` | 3 | candidate ×3 | 0 | 0 |
| `bridge_guided_dbox_style_guard` | 3 | candidate ×3 | 0 | 2 |
| `enhanced_prompt_only_guard` | 3 | candidate ×3 | 0 | 0 |
| `enhanced_prompt_only_guard_repair` | 3 | repair ×2, candidate ×1 | 2 | 0 |
| `dbox_inspired_guard_repair` | 3 | repair ×2, candidate ×1 | 2 | 1 |
| `bridge_contract_compact_clean` | 3 | candidate ×3 | 0 | 0 |
| `bridge_contract_compact_guard_repair` | 3 | repair ×2, candidate ×1 | 2 | 0 |

## Observations

1. Removing `[LEVEL]` did not structurally affect Bridge Judge. Bridge Judge still outputs `allowed_help_level`; only student-visible offline exports no longer contain internal tags.
2. The formal 50-case generation run should not use the default 5s Judge timeout. Recommended settings:
   - `NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=25`
   - `NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25`
   - `NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=25`
   - `--max-retries 1`
3. This patch improves output hygiene, not tutoring quality. A spot check on `heldout_v4_luogu_001` still found some responses that may over-complete the representation bridge, such as guiding too directly toward the `i..j` substring / interval representation.
4. Therefore this smoke should not be interpreted as evidence that Bridge Contract quality improved. It only shows that, with suitable timeout/retry settings, the offline export pipeline can produce reviewable responses without internal control tags.

## Recommended Next Steps

1. Add the timeout / retry settings above to the 50-case generation runbook.
2. Avoid further large prompt edits based on single examples before the formal 50-case run.
3. Do a quick human spot check of 5-10 v4 cases for context alignment and problem-statement readability.
4. Then run 50-case generation-only and export:
   - AI preliminary review workbook;
   - human blind review workbook;
   - unfilled coach workbook.
