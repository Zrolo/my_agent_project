# Dialogue-State v3 AI 预评拒绝语误判修复（2026-05-13）

本文档记录 10-case dev AI 预评中的一次规则修复。它只影响开发阶段 AI 预评工具，不改变学生端 AIChat，也不改变离线生成回复。

## 背景

在 `dialogue_state_v3_dev10_20260513_merged` 的首次 AI 预评中，有 4 条回复被标成 `answer_leakage`。人工快速查看后发现，这些红标多半不是系统给出了完整答案或代码，而是回复中出现了类似：

- “不能直接给完整代码”
- “不看完整代码”
- “不能直接给出完整思路或代码”

这类文字本身是在拒绝完整答案，但旧规则只要看到“完整代码 / 完整思路”就容易误判为答案泄露。

## 修复内容

更新 `evals/aichat/auto_fill_response_review.py`：

- 将“真实代码/答案交付”与“拒绝完整答案的课堂控制语”分开；
- 只有出现 `代码如下`、代码块、`#include`、`完整代码如下`、`完整思路如下`、`给出完整代码` 等交付型表达时，才触发 answer/code leakage；
- 对 `不能直接给完整...`、`不能直接给出完整...`、`不直接给完整...`、`不会直接给完整...`、`不提供完整...` 等拒绝语不再自动判为 answer leakage。

新增回归测试：

- 拒绝完整代码不应被标成 answer leakage；
- “先不看完整代码”不应被标成 answer leakage；
- “不能直接给出完整思路或代码”不应被标成 answer leakage；
- 真正贴出代码 artifact 仍应被标成 answer leakage。

测试命令：

```text
python3 -m unittest test_auto_fill_response_review_unit.py
```

结果：5 tests OK。

## 前后对比

首次 AI 预评：

```text
no_leakage: 63
minor_bridge_leakage: 13
answer_leakage: 4
```

修复后 AI 预评：

```text
no_leakage: 67
minor_bridge_leakage: 13
answer_leakage: 0
```

修复后报告：

`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/dev10_ai_prelim_refusal_fix_final_analysis.zh.md`

修复后盲评表：

`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/coach_response_review_workbook_dev_ablation.ai_prelim_refusal_fix_final.zh.xlsx`

## 解释边界

这次修复不表示所有回复都没有教学风险。它只说明原来的 `answer_leakage` 红标主要来自拒绝语误判。

仍然需要人工关注：

- `minor_bridge_leakage` 是否其实是 major leakage；
- 微型例子是否说穿关键桥；
- 选项题是否把关键桥藏在选项里；
- 拒绝完整答案后给出的替代任务是否真的有教学价值。

AI 预评仍然只是 dev triage，不是教练 gold label。
