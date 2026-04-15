# Review Streaming Content + Quiz Template Implementation Plan

> Goal: 在不改 review schema 的前提下，补正文草稿流式输出、复盘卡瘦身、去元知识化保护，并把 quiz 首次生成结果沉淀成模板与边。

## 文件

- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`

## Task 1: 补 review 草稿流式输出

- [ ] 在 `review_engine._call_llm(...)` 增加 `chunk_callback`
- [ ] 每次收到新的 chunk 时，把累计正文回调出去
- [ ] 用现有宽松 JSON 提取逻辑，从累计文本中抽 4 个核心字段草稿
- [ ] 后端 SSE 在 `status` 之外新增 `review_chunk`
- [ ] 前端 pending 卡显示草稿预览
- [ ] 回归：SSE 至少能发出一个 `review_chunk`

## Task 2: 复盘卡瘦身

- [ ] `renderReviewHtml(...)` 只保留 4 条学生主视图
- [ ] 折叠区只在确实有诊断内容时显示
- [ ] 去掉“无/空白字段”占位堆叠

## Task 3: 去元知识化保护

- [ ] 补一条 review 后处理：如果主视图 4 字段过于空泛且与学生卡点弱相关，则优先回退到更贴题的 bottleneck/diagnosis
- [ ] 补回归：`P5536` 类“公式为什么成立”样例不应默认落成纯抽象贪心话术

## Task 4: Quiz 模板库最小骨架

- [ ] 新增 `quiz_templates`
- [ ] 新增 `quiz_template_edges`
- [ ] 创建 quiz 时把 payload 写入模板表
- [ ] followup / confirm / remedy 若存在上一题模板，写一条边
- [ ] 本轮先不改检索主链，只做“先存下来”

## Task 5: 回归与文档

- [ ] 跑 `test_review_stream_api_unit.py`
- [ ] 跑 `test_review_engine_messages_unit.py`
- [ ] 跑 `node --check static/app.js`
- [ ] 同步 harness 文档
