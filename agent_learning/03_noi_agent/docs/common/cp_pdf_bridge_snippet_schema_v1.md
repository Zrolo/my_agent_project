# cp-pdf Bridge Snippet Schema v1

## 目标

这份文档定义：

- 我们怎么把 `cp-pdf` 里的 PDF 内容切成可复用的 bridge 片段
- 这些片段最小需要哪些字段
- 这些片段先接到系统的哪里

当前不是做整库 RAG。

当前目标只是：

- 先把高频 bridge 的外部知识来源切成小片段
- 再接到：
  - `knowledge_bailout`
  - 高频 deterministic remedy 的内容精修

## 片段粒度

每个 snippet 只允许服务**一座 bridge**。

不要把这些混在一个片段里：

- 方法选择
- 机制理解
- 复杂度判断
- 完整算法综述

正确粒度应该像这样：

- `method_selection`
  - 题面里什么信号支持这个方法
- `shared_prefix_merging`
  - 为什么很多字符串相同开头值得先合起来看
- `lazy_semantics`
  - lazy 标记到底表示什么
- `left_bound_update`
  - 为什么 `a[mid] == x` 时要保留 `mid`

## 最小字段

建议统一成：

```json
{
  "source_family": "cp-pdf",
  "source_title": "Competitive Programmer’s Handbook",
  "source_file": "Competitive Programmer’s Handbook.pdf",
  "chapter_or_section": "Binary Search",
  "topic_l1": "basic",
  "topic_l2": "binary_search",
  "bridge": "left_bound_update",
  "snippet_type": "bridge_explanation",
  "excerpt": "...",
  "teaching_value": "适合讲为什么要保留 mid",
  "needs_manual_review": false
}
```

## `snippet_type`

第一版只建议这 4 类：

- `misconception`
  - 适合写“最容易误会的是”
- `bridge_explanation`
  - 适合写“真正要站稳的是”
- `mini_example`
  - 适合写一个小例子
- `algorithm_overview`
  - 适合写“这一步在整套方法里负责什么”

## 和学生端知识卡的关系

一个 bridge 的知识卡，不需要从单个 snippet 全部生成。

更合理的是：

- `misconception` 类 snippet
  - 填到 `opening` 或 `misconception`
- `bridge_explanation` 类 snippet
  - 填到 `bridge_explanation`
- `mini_example` 类 snippet
  - 填到 `visual_hint` 或 `micro_action`
- `algorithm_overview` 类 snippet
  - 填到 `algorithm_overview`

## 第一版接入范围

先只接这些高频 bridge：

- `complexity_fit`
- `method_selection`
- `shared_prefix_merging`
- `left_bound_update`
- `check_condition`
- `state_design`
- `transition_design`
- `lazy_semantics`

## 不做什么

第一版不做：

- 不做整篇 PDF 全文检索
- 不做题号级检索
- 不把 PDF 原文直接给学生看
- 不让 snippet 直接替代现有知识卡模板

## 一句话

`cp-pdf` 在我们系统里，不是“题解库”，而是：

- **bridge 片段来源库**
