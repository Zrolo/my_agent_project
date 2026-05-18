# 20-Seed Mini-Study Preliminary Report

Date: 2026-05-10

## Purpose

This mini-study compares five offline pipelines on the same 20 coach-reference seed turns:

1. `current_system`: the current AIChat tutor response only, without Bridge Judge.
2. `single_llm_structured`: one LLM call outputs a compact contract, student-facing response, and self-check.
3. `bridge_contract`: Bridge Judge produces a contract that is injected into the tutor.
4. `bridge_contract + guard`: Bridge Contract Tutor followed by Leakage Judge.
5. `bridge_contract + guard + repair`: full offline pipeline with Repair enabled when rewrite/block is requested.

This is not the final paper experiment. It is the first Research v1 end-to-end mini-study to check whether the baselines run, how much latency each stage adds, and which modules merit larger-scale evaluation.

## Setup

- Seed file: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Tutor provider: `deepseek_flash`
- Chat thinking: `disabled`
- Judge schema: `retrieval_augmented_compact_judge`
- Guard mode: `predicted`
- Bridge/guard/repair paths used `--max-retries 1`; a few timeout cases were rerun individually and merged.

## Summary

| Pipeline | Completed | Bridge family acc. | Focus acc. | Help level acc. | Leakage rate | Rewrite rate | Avg calls | p50 latency | p95 latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current_system | 20/20 | n/a | n/a | n/a | n/a | n/a | 1.00 | 7631.893 ms | 11015.386 ms |
| single_llm_structured | 20/20 | 0.900 | 0.800 | 0.900 | n/a | n/a | 1.00 | 7159.394 ms | 8843.530 ms |
| bridge_contract | 20/20 | 0.900 | 0.850 | 0.950 | n/a | n/a | 2.10 | 13691.467 ms | 18664.726 ms |
| bridge_contract + guard | 20/20 | 0.900 | 0.800 | 0.850 | 0.150 | 0.050 | 3.35 | 18157.722 ms | 22471.240 ms |
| bridge_contract + guard + repair | 20/20 | 0.900 | 0.800 | 0.950 | 0.050 | 0.000 | 3.35 | 17094.474 ms | 23998.282 ms |

## Preliminary Interpretation

`single_llm_structured` is a strong required baseline. It uses only one LLM call, has latency close to the current system, and reaches 0.90 bridge family accuracy and 0.80 focus accuracy on this 20-case seed set.

`bridge_contract` slightly improves focus and help-level agreement, but doubles the average LLM call count and increases p50 latency to about 13.7 seconds.

The guard path adds substantial cost: around 3.35 LLM calls and about 18 seconds p50 latency. In this seed set, Leakage Judge found no critical bridge leakage and no answer/code leakage, only minor leakage and one rewrite suggestion. This suggests the guard should be risk-triggered or run in shadow mode rather than invoked on every online turn.

Repair was not meaningfully exercised in this batch. The full pipeline had repair rate 0, so this mini-study cannot yet prove Repair effectiveness. Repair should be tested on stronger leakage-adversarial cases or on coach-reviewed over-helpful responses.

## Blind Review Artifacts

Generated anonymous Chinese review workbook:

- `docs/research/coach_response_review_workbook_mini_study_20_20260510.zh.xlsx`
- key file: `docs/research/coach_response_review_workbook_mini_study_20_20260510.key.csv`

The workbook contains 100 anonymous responses: 20 cases × 5 pipelines. System identity is hidden from the coach reviewer.

New review dimension:

- `bridge-oriented micro-example score 0-2`

This distinguishes low-quality micro-examples that merely create a temporary task from bridge-oriented micro-examples that help students abstract a transferable conceptual relation.

## Next Step

Review 20-30 anonymous responses first rather than all 100 at once. Then use the key file to aggregate coach ratings by pipeline and decide whether `single_llm_structured`, `bridge_contract`, `guard`, and `repair` are worth their latency costs.
