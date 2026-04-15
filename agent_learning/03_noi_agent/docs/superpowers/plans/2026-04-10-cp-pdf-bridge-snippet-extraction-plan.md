# 2026-04-10 cp-pdf bridge 片段抽取计划

## 目标

把已经选好的 `cp-pdf` 来源，往前推进到：

- 有统一片段格式
- 有第一批高频 bridge 的可抽取目标
- 后续能逐步接进 `knowledge_bailout`

## 本轮范围

只做第一批高频 bridge：

- `complexity_fit`
- `method_selection`
- `shared_prefix_merging`
- `left_bound_update`
- `check_condition`
- `state_design`
- `transition_design`
- `lazy_semantics`

## 执行顺序

### 1. 先定片段格式

输出：

- `docs/common/cp_pdf_bridge_snippet_schema_v1.md`

目标：

- 统一 `excerpt`、`bridge`、`snippet_type`
- 避免后面每次抽片段都换格式

### 2. 再做第一批抽取清单

基于：

- `docs/common/cp_pdf_bridge_sources_v1.jsonl`

按 bridge 拆出“下一步优先抽谁”。

目标：

- 每个高频 bridge 先锁 1 到 2 个优先来源

### 3. 最后再做真实 snippet 文件

第一版 snippet 文件建议单独放：

- `docs/common/cp_pdf_bridge_snippets_v1.jsonl`

第一轮先不追求多，只追求：

- 每个高频 bridge 至少 1 条 `bridge_explanation`
- 条件允许时再补：
  - `misconception`
  - `mini_example`

## 验收标准

- 已有 `cp_pdf_bridge_sources_v1.jsonl`
- 已有 snippet schema 文档
- harness 已记录当前主线已经推进到“来源索引 -> 准备抽片段”
- 后续新会话一眼能看懂：
  - 该抽哪些 bridge
  - 抽成什么格式
  - 先接到系统哪里

## 当前不做

- 不做整库 clone + 全量自动抽取
- 不做大规模 RAG
- 不改学生端运行逻辑

## 下一步

- 先落 `cp_pdf_bridge_snippets_v1.jsonl` 的第一版高频 bridge 片段
- 然后选 1 到 2 个 bridge 接进知识卡生成流程
