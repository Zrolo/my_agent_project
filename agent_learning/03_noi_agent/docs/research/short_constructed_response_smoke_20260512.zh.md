# 短生成优先 Prompt Smoke 2026-05-12

本报告记录一次开发阶段 smoke，用于检查“优先短生成式回答、慎用选择题”的 prompt patch 是否能减少答案槽位式关键桥泄露。它不是正式 held-out 结果，也不是教练盲评结果。

## 设置

- 输入：`docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- 样本：前 3 条 dev cases
- 输出目录：`evals/aichat/ad_hoc_runs/short_constructed_response_smoke_20260512_after_answer_slot_patch/`
- 条件：
  - `enhanced_prompt_only`
  - `dbox_inspired_decomposition_tutor`
  - `bridge_contract`
- 检查方式：runner stage error + 静态泄露风险 lint。

## 结果

| 条件 | 完成/总数 | runner error | final static risk | answer-slot | filled-trace | worked-example | 平均 LLM 调用 | P50 延迟 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| enhanced_prompt_only | 3/3 | 0 | 0.667 | 0.333 | 0.333 | 0.000 | 1.0 | 38432.719 |
| dbox_inspired_decomposition_tutor | 3/3 | 0 | 1.000 | 0.333 | 0.667 | 0.000 | 1.0 | 19932.202 |
| bridge_contract | 3/3 | 0 | 0.667 | 0.667 | 0.333 | 0.000 | 2.0 | 47519.210 |

## 主要发现

1. 技术链路稳定：三组各 3 条都完成，`error_count=0`。
2. “不要默认选择题”不等于“不会答案槽位化”。模型仍会把关键桥改写成短答槽位，例如：
   - `check(4) 应该返回 true 还是 false`
   - `应该在什么位置处理`
   - `每个节点最终值是多少`
   - `dp[i][j] 应该记录什么`
3. DBox-inspired baseline 仍会出现显著 filled-trace / answer-slot 风险，说明单轮 step-tree-style prompt 不能稳定替代 leakage control。
4. Bridge Contract 组仍最容易把“知道 missing bridge”转成“直接让学生补 missing bridge 本身”的问题。这个现象支持之前判断：诊断正确不等于辅导安全。

## 对 Research v1 的影响

这次 smoke 不支持继续无限加 prompt 规则。更稳的结论是：

```text
短生成优先是交互设计原则，不是泄露控制机制。
Prompt wording 可以降低部分选择题化倾向，但不能稳定防止 answer-slot leakage。
```

下一步应把 answer-slot / filled-trace 作为 Guard、Repair、static lint 和教练盲评中的独立失败类型，而不是继续只靠 Tutor prompt 控制。

## 建议

1. 不再继续围绕同一问题追加长 prompt 规则，避免 prompt creep。
2. 在 dev ablation 报告中保留 `answer-slot` 与 `filled-trace` 风险列。
3. 对高风险 bridge family，优先评估 `+ guard`、`+ repair` 或 deterministic fallback，而不是期待 `tutor_only` 自动安全。
4. 正式 50-case 前，freeze prompt 后用 held-out 数据评估：强 prompt、DBox-inspired、Bridge Contract 在 answer-slot leakage 上的差异。
