# NOI Agent 两周执行清单（2026-04）

## 目标

接下来两周只围绕一条主线推进：把学生主链路收成稳定产品。

不再同时发散做：大 UI 改版、新 teacher 页面、更多新 bridge、更多新外部源。

---

## P0：这两周只盯 8 个高频 bridge

- `state_design`
- `transition_design`
- `check_condition`
- `left_bound_update`
- `lazy_semantics`
- `shared_prefix_merging`
- `complexity_fit`
- `method_selection`

验收标准：
- 这 8 个 bridge 作为当前主集合固定下来
- 新 bridge 暂不扩张，长尾继续交给现有 fallback

---

## 第 1 周

### 1. 统一外部 snippet 运行时入口

只保留：
- `docs/common/bridge_external_snippets_v1.jsonl`

不再让运行时直接分散读取：
- `cp_pdf_bridge_snippets_v1.jsonl`
- `oi_wiki_bridge_snippets_v1.jsonl`

验收标准：
- 运行时统一从一份索引取 snippet
- 测试覆盖“统一索引优先于原始来源文件”

### 2. 先把知识卡接线扩到 5 个 bridge

- `shared_prefix_merging`
- `lazy_semantics`
- `check_condition`
- `left_bound_update`
- `state_design`

每个 bridge 至少接入：
- `bridge_explanation`
- `algorithm_overview`
- `mini_example`（没有则补）

验收标准：
- 这 5 个 bridge 的知识卡都能看到外部 snippet 带来的内容变化
- 文案仍然符合“先破误解，再站正解”

### 3. 真实样例复测

每个 bridge 至少审 3 条样例。

重点看：
- 第一轮是否点中桥
- 第二轮是否真的拆半步
- 第三轮/补课是否不再卡住
- 知识卡是否像“小课”

验收标准：
- 至少完成 15 条样例人工审查
- 每条样例的主要问题能落回具体 bridge

---

## 第 2 周

### 4. 收最弱的 3 个 bridge

优先：
- `method_selection`
- `complexity_fit`
- `lazy_semantics`

验收标准：
- 每个 bridge 至少解决 1 个当前最明显问题
- 修完后重新走真实样例复测

### 5. 建 bridge 审查总表

每个 bridge 记录：
- 代表题
- 当前表现
- 主要问题
- 下一步修复点

验收标准：
- 不再靠聊天上下文记忆项目状态
- 后续迭代按 bridge 决策，不按题号拍脑袋

### 6. teacher 侧只补最有价值的统计

先只补：
- `bridge`
- `mastery_status`
- 是否进入 `knowledge_bailout`

验收标准：
- 老师能看出哪个 bridge 最常卡
- 老师能看出哪个 bridge 最常掉到知识兜底

---

## 暂停项

这两周先不要继续做：
- 大 UI 风格迭代
- 新 teacher 页面
- 首轮 review 的大重构
- 新资料源接入
- 高频 bridge 之外的大规模规则扩张

---

## 当前推荐执行顺序

1. 统一 snippet 入口
2. 扩 5 个 bridge 的知识卡接线
3. 跑真实样例审查
4. 收最弱的 3 个 bridge
5. 建 bridge 审查总表
6. 再决定下一阶段
