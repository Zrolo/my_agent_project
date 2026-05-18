# Submission Reproduction Log 20260519

## 使用边界

本文档记录 dialogue-state v3 submission-prep 阶段的复现命令执行结果。它不新增实验、不修改线上 AIChat、不修改 prompt、不修改主实验数据。当前 checkpoint 解释如下：

- `dbbbd5c` = evidence content base，可能出现在 machine-readable manifest metadata 中。
- `33a5dd7` = evidence package gates checkpoint。
- `7baa54e` = integrity zh-pairs checkpoint，补齐当前 non-legacy bilingual pairing gap。

## Command Results

| command | exit status | key output files / stdout | reproduced numbers vs reports | mismatched claim IDs | failure stage | blocking? | notes |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| `python3 evals/aichat/verify_dialogue_state_v3_reports.py` | 0 | `Dialogue-state v3 report verification passed.` | Consistent with machine-readable reports. | None reported. | None. | No | Core report verification passed. |
| `python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_external.json` | 0 | `/tmp/dialogue_state_v3_reproduced_external.json` | Reproduced evidence bundle generated successfully. | None reported. | None. | No | Use this JSON as the external-review reproduction output for this run. |
| `python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py` | 0 | `Ran 5 tests ... OK`; temporary DeepSeek calibration pack smoke outputs under `/var/folders/...` | Unit-level evidence package and calibration pack checks passed. | None reported. | None. | No | Temporary files are test artifacts, not paper evidence. |
| `python3 evals/aichat/validate_research_bilingual_docs.py --output-json /tmp/bilingual_docs_validation_external.json` | 0 | `/tmp/bilingual_docs_validation_external.json`; `unpaired_count=0`, `legacy_unpaired_count=23` | Current non-legacy bilingual docs are paired. | None reported. | None. | No | Remaining 23 are legacy documentation debt, not dialogue-state v3 evidence mismatch. |

## Interpretation

- No command failed in this reproduction pass.
- No mismatched claim IDs were reported.
- The reproduction pass does not change any result number or raw experiment file.
- The bilingual validator still reports `legacy_unpaired_count=23`; this is a legacy docs debt category and is not blocking for the dialogue-state v3 evidence package.
- If a web-review bundle omits test-only dependencies, that would be a bundle packaging issue. In the full repository at this checkpoint, the listed unit tests pass.

## Submission Boundary

This log supports submission preparation only. It does not upgrade Coach A, Coach B, or priority60 adjudication to final gold; it does not turn all-50 aggregate into the headline; it does not make Guard-only a rewrite condition; and it does not make LLM grader calibration a substitute for human review.
