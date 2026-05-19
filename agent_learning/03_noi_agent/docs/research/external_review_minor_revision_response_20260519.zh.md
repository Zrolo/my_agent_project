# External Review Minor-Revision Response 20260519

## 范围

本文档记录对 `f3f281b` dialogue-state v3 evidence bundle 外部网页 AI 审核意见的回应。它是 packaging 和 reproducibility 记录，不是新实验。

## Reviewer Verdict

```text
needs minor revision
```

外部审核没有发现会推翻 dialogue-state v3 evidence package 的 blocking issue。核心 `verify` 与 `reproduce` 命令通过，复算 JSON 与 bundle 内输出一致。

## 已处理的问题

网页 reviewer 在缺少 `openai` 包的环境中无法运行 focused unit tests。失败来自 import-time dependency chain：

```text
test_llm_grader_calibration_pack_unit.py
-> evals/aichat/run_llm_grader_calibration.py
-> evals.review.run_review_case_kimi_cli
-> review_engine.py
-> openai.OpenAI
```

该依赖只在 live model calls 中需要；dry-run unit tests、report verification 和 table reproduction 不需要它。

## 修复

- 将 `evals/aichat/run_llm_grader_calibration.py` 中的 live-backend imports 移入真正调用对应 backend 的函数中。
- 增加本地 JSON-fence stripping helper，使 dry-run 和 parser tests 不再因导入 Kimi review runner 而需要 `openai`。
- 新增 `requirements-for-web-review.txt`，说明网页审核复现命令只需要 Python 3.10+ 标准库；`openai` 只在 evidence bundle 外部进行 live model calls 时才是可选依赖。

## 证据边界

本次修改不改变：

- 主实验数据；
- 人审标签；
- 论文结果数字；
- prompts；
- 线上 AIChat；
- 实验 conditions。

## 仍需保持的解释边界

DeepSeek LLM grader calibration 仍是 same-backend-coupled auxiliary limitation evidence。GPT-5.4 subagent review 仍只是 method review / reproducibility audit，不是实验性 calibration result。
