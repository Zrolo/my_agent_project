# 打卡复盘正文流式输出 + Quiz 模板复用设计

## 目标

在当前“流式状态、非流式正文”的基础上，继续推进三件事：

1. 学生端在 `pending` 时能看到 **复盘正文草稿** 持续长出来，而不是只看阶段名称
2. 最终复盘卡更精简，默认只展示最关键的 4 条，不把太多元信息堆给学生
3. 首次生成的小测内容可以沉淀到数据库，后续为“类似桥梁 / 类似路径”复用做准备

---

## 一、范围边界

### 本轮做

- 在 SSE 状态流里新增 `review_chunk` 事件
- 基于模型流式 chunk，推送 4 个学生端核心字段的草稿预览：
  - `main_block`
  - `key_bridge`
  - `next_step`
  - `transfer_signal`
- 前端 `pending` 卡新增“AI 草稿预览”
- 最终复盘卡瘦身，默认只保留 4 条核心内容，详细诊断折叠
- review 输出再加一层“去元知识化”保护，减少“当前对象/后续空间”这类空泛表述
- 新增 quiz 模板库与路径边表的最小数据库骨架
- 首次 LLM 生成 quiz 后入库模板，为后续复用准备数据

### 本轮不做

- review JSON schema 改版
- review 多段生成 / 多轮拼装
- 真正 token 级逐字显示原始 JSON
- 本轮就让 quiz 全量改走模板复用
- 全量图算法式推荐或复杂检索

---

## 二、正文流式输出设计

### 1. 后端事件模型

在现有 SSE 事件基础上增加：

- `review_chunk`

事件体最小字段：

- `checkin_id`
- `review_status`
- `phase`
- `message`
- `elapsed_seconds`
- `draft_review`

其中 `draft_review` 只包含：

- `main_block`
- `key_bridge`
- `next_step`
- `transfer_signal`

### 2. 草稿来源

当前 review 调用已经是 `stream=true`，但之前只在服务端拼接完整正文。
本轮改成：

- `review_engine._call_llm(...)` 支持接收 `chunk_callback`
- 每次收到新的文本 chunk，就把累计文本传给 callback
- callback 用“宽松 JSON 提取”从累计文本里尽量抽出 4 个核心字段
- 后端把这 4 个字段写进运行时状态，再由 SSE 发给前端

### 3. 前端展示

在 `pending` 卡中新增：

- 当前阶段
- 当前阶段文案
- 已等待时间
- `AI 草稿预览`

草稿区只显示已经抽出来的字段，不显示半截 JSON，不显示原始代码块。

### 4. 完成时机

- `review_ready` / `completed` 后，前端仍调用现有 `GET /api/checkins/{checkin_id}`
- 正式详情会覆盖掉 pending 草稿区

---

## 三、复盘卡瘦身与去元知识化

### 1. 学生默认层

最终复盘卡默认只展示：

- 你卡在哪
- 关键一步
- 现在先做
- 下次提醒

### 2. 详细层

折叠区只在有内容时显示：

- 错误标签
- 统一归类
- 判断把握
- 子标签
- 详细诊断 / 下一步行动 / 推荐专题

### 3. 去元知识化规则

如果学生端 4 个核心字段里出现以下过于空泛的表述：

- 当前对象
- 后续空间
- 不吃亏
- 留空间
- 先报方法名 / 先记结论

且这些词与学生原始卡点、题目摘要、代码片段没有明显对应，就优先回退到：

- 更贴近学生 `bottleneck_text`
- 更贴近 `diagnosis`
- 更贴近题目对象和关系

目标不是完全禁掉抽象词，而是避免它们在不落题时直接出现在学生主视图。

---

## 四、Quiz 模板复用与路径存储

### 1. 为什么不是只用树

对单个学生的一次 quiz 链路，`main -> followup -> confirm` 很像树。
但对全平台模板复用来说：

- 多个 `main` 可能共享同一个 `followup`
- 多个 `followup` 也可能汇到同一个 `confirm`

因此模板层更适合 **DAG（有向无环图）**，不是严格树。

### 2. 最小数据结构

新增两张表：

#### `quiz_templates`

- `id`
- `quiz_role`
- `quiz_type`
- `source_error_layer`
- `target_bridge`
- `structure_type`
- `question_text`
- `options_json`
- `correct_answer`
- `explanation`
- `bridge_feedback`
- `distractor_feedback`
- `meta_json`
- `quality_score`
- `usage_count`
- `created_at`

#### `quiz_template_edges`

- `id`
- `parent_template_id`
- `option_key`
- `child_template_id`
- `edge_type`
- `created_at`

### 3. 本轮落地边界

本轮只做：

- 首次生成 quiz 后，把 payload 写入 `quiz_templates`
- 如果当前 quiz 是由某个上一题导出的 followup/confirm/remedy，再写一条 `quiz_template_edges`

本轮不做：

- 大规模检索召回
- 模板打分重排
- 复杂相似度匹配
- 全链路改成模板优先

---

## 五、执行顺序

1. 先补 review chunk 流式草稿
2. 再瘦身最终复盘卡
3. 再补去元知识化保护
4. 最后落 quiz 模板库最小骨架与入库

---

## 六、验收标准

1. `pending` 时页面不只显示阶段，还能看到 4 字段草稿至少有一部分逐步出现
2. `completed` 后仍由现有详情接口渲染正式复盘，不打坏当前 parse / guard 主链
3. 学生默认复盘卡明显变短，不再默认展示一大段结构化元信息
4. `P5536` 这类样例的主视图，不再优先出现“当前对象/后续空间”这类空泛表述
5. 新生成的 quiz 能沉淀到模板表
6. followup / confirm 路径可写入边表，为后续 DAG 复用打基础
