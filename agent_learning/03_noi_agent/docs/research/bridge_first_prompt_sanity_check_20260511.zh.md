# Bridge-first Prompt Sanity Check - 2026-05-11

本文件记录一次很小的 dev sanity check。它不是论文实验，也不进入 headline metrics。

## 背景问题

项目讨论了一个风险：

```text
如果 prompt 只覆盖 DP、二分、LCA、lazy 等部分算法，是否会导致未覆盖算法效果差？
```

我们的原则调整为：

```text
bridge-first, topic-second, focus-top-k
```

含义是：

- 先用 `primary_bridge_family` 决定教学动作；
- `algorithm_topic` 只作为轻量上下文；
- `selected_focus_id` 只从 top-k focus 中选，不全局编造；
- 具体算法例子只作为 regression boundary，不作为完整算法清单。

## Prompt Patch

本次只修改离线研究链路：

- `single_llm_structured` system prompt；
- offline Bridge Contract control message。

线上学生 AIChat 未接入本补丁。

## Smoke 设置

- Seed file: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Cases: 前 3 条 dev seed
  - `cp_bridge_001` 树上差分 / LCA 标记
  - `cp_bridge_002` 二分 check 语义
  - `cp_bridge_003` DP 状态语义
- Tutor mode: `single_llm_structured`
- Pipeline: `tutor_only`
- Judge schema mode: `retrieval_augmented_compact_judge`
- Output:
  - `evals/aichat/ad_hoc_runs/bridge_first_single_llm_structured_smoke3_20260511.jsonl`
  - `evals/aichat/ad_hoc_runs/bridge_first_single_llm_structured_smoke3_20260511_v2.jsonl`

## 结果

工程层面：

- 3/3 case 正常输出；
- `stage_errors={}`；
- 每条 `llm_call_count=1`；
- schema 没有被 prompt patch 破坏。

教学安全层面：

- `cp_bridge_001` 仍然把端点标记预填出来，让学生补调整位置，接近 critical bridge leakage；
- `cp_bridge_002` 仍然直接把 `check(mid)` 的可行性语义说得很明确；
- `cp_bridge_003` 仍然接近直接问出背包状态需要记录的对象。

## 解释

这次 sanity check 说明：

```text
bridge-first prompt 原则是必要的，但不足以单独防止 over-complete micro-example。
```

它不能被解读为：

```text
抽象 bridge prompt 已经解决泄露。
```

更合理的结论是：

```text
不要继续通过无限增加具体算法规则来修补 prompt；
需要把过强微型例子作为 Guard / Leakage Judge / coach review 的重点对象。
```

## 后续处理

1. 保留 `bridge-first, topic-second, focus-top-k` 作为 prompt 设计原则。
2. 不再为了单个算法继续追加专门规则，避免 prompt 膨胀。
3. 将 `cp_bridge_001`、`cp_bridge_002`、`cp_bridge_003` 作为 dev/regression case。
4. 在 10-20 case dev ablation 中检查：
   - `enhanced_prompt_only`
   - `single_llm_structured`
   - `single_llm_structured + guard`
   - `bridge_contract_predicted`
   - `bridge_contract_predicted + guard`
5. 正式 50-case held-out 前再 freeze prompt。
