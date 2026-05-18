# Submission Readiness Checklist 20260519

## 使用边界

本清单总结 dialogue-state v3 evidence package 的投稿准备状态。它不新增实验、不修改 prompt、不改 AIChat、不修改主实验数据。

| Area | Status | Notes |
| --- | --- | --- |
| A. Evidence readiness | ready | evidence package、manifest、main tables、paired uncertainty、stress、fairness sensitivity 和 calibration reports 均已存在且可复算。 |
| B. Claim safety | ready | 已有 final claim gate；主表述限制为 trade-offs 和 favorable trends。 |
| C. Human review validity | ready | Coach A/B 完成 350 条评审；已有 priority60 adjudication 和 sensitivity analysis。不能把 labels 写成 final gold。 |
| D. Baseline fairness | ready with limitation | 强 baseline 已记录；DBox+Repair 只作为 targeted sensitivity，不是 full main validation。 |
| E. Repair causal boundary | ready | same-candidate stress 支持 leakage reduction with burden trade-off；主均值不作为因果证明。 |
| F. LLM grader calibration boundary | ready | DeepSeek calibration 支持 auxiliary-only 口径；critical recall 风险阻止 replacement claim。 |
| G. AI writing compliance | needs work | disclosure 和 verification logs 已建立；还需要人类作者完成 citation 和逐节人工核验。 |
| H. Ethics / privacy / student data | needs work | 数据边界已有记录，但最终 manuscript 仍需按 venue 写 ethics/privacy。 |
| I. Reproducibility | ready | 当前 checkpoint 下 verify、reproduce、unit tests 和 bilingual validator 均通过；legacy unpaired docs 是非阻塞文档债。 |
| J. Formatting and submission | needs work | Markdown sources 已就绪；venue template、BibTeX、渲染后的 figures/tables 和最终 PDF 未完成。 |

## Current Readiness

```text
draft-ready / workshop-prep ready
not yet camera-ready conference submission
```

## Remaining Work Before arXiv

1. 人类作者把 manuscript skeleton 逐句改成可读论文草稿。
2. 核验所有外部引用，并替换 placeholder metadata。
3. 渲染 tables 和 figures。
4. 完成 AI writing disclosure 和 ethics/data-governance wording。
5. 运行 final claim-gate scan 和 reproduction commands。

## Remaining Work Before Conference Submission

1. 选择目标 venue 和 page limit。
2. 转换到 venue template。
3. 把 appendix-only material 移出主文。
4. 完成 bibliography、DOI 和 proceedings 检查。
5. 对 final assembled PDF 和 supplement 做一次外部 evidence audit。
