# AI Writing Disclosure and Verification Log

## 使用边界

本文档记录论文准备阶段如何使用生成式 AI 辅助写作。它不新增实验、不修改数据、不改变 evidence package。

## 允许的 AI 辅助范围

生成式 AI 工具可以用于：

- 草稿辅助；
- 编辑和语言润色；
- 检查清单生成；
- 证据组织；
- 格式辅助；
- forbidden wording 一致性扫描。

生成式 AI 工具不能作为科学证据来源。AI 生成文本只有在人类作者核验其 claim、数字、引用和解释之后，才能进入论文。

## 人工核验要求

人类作者必须人工核验：

- 所有科学主张；
- 所有实验结果；
- 所有引用和 bibliographic metadata；
- 所有表格和图；
- 所有人审、stress test、sensitivity 和 calibration 证据的解释；
- 所有涉及 Guard-only、Repair、DBox+Repair、priority60 adjudication、all-50 sensitivity 和 LLM grader 的表述。

AI 不列为作者。人类作者对全文内容负责。

## 建议论文披露文本

English:

```text
We used generative AI tools to assist with drafting, editing, and checklist generation. All scientific claims, experimental results, citations, tables, and interpretations were manually verified by the authors, who take full responsibility for the content.
```

Chinese:

```text
我们使用生成式 AI 工具辅助草稿、润色和检查清单生成。所有科学主张、实验结果、引用、表格和解释均由作者人工核验，作者对全文内容负责。
```

## 配套核验表

论文准备时配套使用：

- `citation_verification_log.csv`
- `result_number_verification_log.csv`
- `manuscript_human_revision_checklist.zh.md`

任何 citation 只有在 `manually_opened_yes_no` 和 `quote_or_paraphrase_checked_yes_no` 都填为 `yes` 后，才可视为 submission-ready。
