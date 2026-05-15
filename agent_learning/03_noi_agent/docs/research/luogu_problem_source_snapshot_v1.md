# Luogu Problem Source Snapshot v1

This document records the local Luogu problem-bank snapshot used by Research v1. The snapshot is used to generate the real-problem-grounded held-out v2 draft and is not committed to GitHub.

## Snapshot

- Local path: `data/local_problem_banks/luogu_latest_20260402.ndjson`
- Original local source: `/Users/kongyouli/Downloads/latest.ndjson`
- Record date: 2026-05-13
- Row count: 15,909
- SHA-256: `d0acee875bf0445936e616efc00f9044797384fb9a13648d072bb8e2744902e1`
- Committed to Git: no. The file is excluded by `.gitignore`.

## Usage Boundaries

- The snapshot is a local research source used to select real Luogu problems and generate synthetic-but-grounded student questions.
- The raw problem-bank file is about 139MB and is not part of the public repository.
- Public research artifacts should prefer problem IDs, Luogu links, and rewritten summaries. Full statements or long statement excerpts are for local coach review only.
- v2 student questions do not use old online AI replies and are not claimed to be verbatim real student utterances; they are generated from real problem statements and target bridge labels.

## Downstream Artifacts

- `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- `docs/research/heldout_v2_50_source_and_case_review.zh.xlsx`
- `docs/research/bridgebench_cp_heldout_v2_50_generation_report_20260513.md`

These artifacts remain drafts until coach review, Coach A/B labeling, agreement analysis, and adjudication are complete.
