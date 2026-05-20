# Real-AIChat-100 Selection Patch Log

Date: 2026-05-20

## Scope

This patch creates a public, redacted Real-AIChat-100 observational selection manifest from the existing 137-row real-student online candidate-turn screening CSV. It does not read `.local_private/`, does not publish student raw text, complete code, complete AIChat responses, row-level hashes, hash salt, or reversible mappings, and does not modify dialogue-state v3 main results.

## Files Added / Updated

| file | purpose |
| --- | --- |
| `evals/aichat/select_real_aichat_100_observational_validation.py` | Deterministic stratified purposive selector from 137 screening rows to a 100-row public redacted manifest. |
| `evals/aichat/tests/test_validate_real_aichat_external_validation.py` | Added selection tests for eligibility filtering and row-level hash redaction. |
| `docs/research/real_aichat_100_observational_validation_manifest_20260520.csv` | 100-row public redacted Real-AIChat-100 observational manifest. |
| `docs/research/real_aichat_100_selection_summary_20260520.json` | Aggregate selection summary and coverage counts. |
| `docs/research/real_aichat_100_selection_log_20260520.zh.md` | Human-readable selection log and reporting boundary. |
| `docs/research/real_aichat_100_observational_validation_protocol_20260520.zh.md` | Updated execution status to point to the generated public redacted manifest. |

## Selection Result

| field | value |
| --- | ---: |
| source screening rows | 137 |
| eligible screening rows | 137 |
| selected manifest rows | 100 |
| selected unique sessions | 59 |
| selected unique students | 13 |
| selected unique problems | 25 |
| public reporting allowed rows | 0 |
| candidate_for_replay=yes rows | 84 |

## Claim-Gate Status

- 新增 dialogue-state v3 main experiment: no
- 新增 main condition: no
- 重算主表: no
- 修改线上 AIChat / prompt / active mode: no
- 生成或伪造 deep annotation result: no
- 生成 Replay-30/50 responses: no
- 写成 learning outcome study: no
- 公开学生原文、完整代码、完整 AIChat 回复、身份、hash salt、可逆映射: no
- 公开 row-level student/problem/session hash 表: no

## Remaining TODO

1. Real-AIChat-100 lightweight human annotation is not complete; the manifest is selection-only.
2. Consent/reporting gate remains pending, so public reporting is limited to aggregate/process counts.
3. Replay-30 candidates are candidates only; no generation or coach review has been conducted.
4. Any manuscript claim using this layer must describe it as observational ecological-validity selection / protocol evidence, not as main result.
