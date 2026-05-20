# Real-Student Online 5-Case Human Coach Review Public Status 20260520

## 使用边界

本文档记录 5-case real-student online AIChat dry run 已完成人类教练内部复核后的公开安全状态。它只报告流程状态、结构校验和 consent/reporting gate 边界；不公开学生原文、完整代码、完整 AIChat 回复、case-level labels、教练逐例备注、student hashes、problem hashes、hash salt 或可逆映射。

本状态记录不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

## Source Status

| item | value | public reporting boundary |
| --- | ---: | --- |
| human coach reviewed dry-run cases | 5 | process status only |
| structure validation errors | 0 | validator status only |
| consent/reporting warnings | 5 | expected because reporting gate is pending |
| cases passing privacy review for internal review | 5 | internal review only, not public case release |
| cases reportable after consent/status gate | 0 | no case-level evidence may be publicly reported yet |
| leakage / score distributions | suppressed | stored only in private summary while gate is pending |
| raw student text / complete code / full AIChat response | not reported | forbidden in public material |

## What This Supports Now

The completed 5-case review supports a narrow process claim:

```text
A human coach was able to complete the 5-case real-student online AIChat dry-run review using the coach-facing form aligned with the 50-case review rubric. The review remains internal because consent/reporting eligibility is not complete.
```

This can be used as documentation that the real-student pilot workflow is executable. It should not be written as model-performance evidence, learning-outcome evidence, or an update to dialogue-state v3 results.

## What Remains Private

The following materials remain in `.local_private/` and should not be copied into public docs or GitHub:

- the filled coach workbook;
- private score-only extraction;
- private validation JSON;
- private aggregate summary with score and leakage distributions;
- any student message, recent dialogue, code excerpt, complete AIChat response, case-level coach label, or coach note.

## Manuscript-Safe Wording

```text
As a dry-run step for the real-student AIChat pilot, five privacy-reviewed cases were reviewed internally by a human coach using a coach-facing form aligned with the 50-case response-review rubric. The review confirmed that the form can be completed on real AIChat cases, but the cases remain behind a consent/reporting gate. We therefore treat this step as process evidence for pilot feasibility and do not report case-level labels, leakage rates, model-performance results, or learning outcomes.
```

## Forbidden Wording

- Do not write that the 5-case dry run is a main result.
- Do not report it as a deployed system evaluation.
- Do not report leakage rates or score distributions publicly while the consent/reporting gate is pending.
- Do not say that real students learned, improved, or achieved learning gains.
- Do not compare the observed current AIChat response to the seven offline conditions.
- Do not merge the 5 cases into dialogue-state v3 main tables.
- Do not call observed current AIChat response a baseline, condition, control, or repair output.

## Claim Gate

| check | result |
| --- | --- |
| 新增 dialogue-state v3 主实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改线上 AIChat / prompt / active mode | no |
| 改变 evidence class | no |
| 把 pilot 写成 main result | no |
| 把 pilot 写成 learning outcome study | no |
| 公开 case-level labels while gate pending | no |
| 公开学生原文 / 完整代码 / 完整 AIChat 回复 | no |

## Next Gate

Before any case-level example, leakage distribution, or score distribution can enter a manuscript appendix, the authors must complete and document the consent/reporting gate. Until then, only workflow status and aggregate process counts may be referenced publicly.
