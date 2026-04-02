# 当前系统状态（以代码为准）

## 本文件的写入标准

只写**当前已经在代码中真实成立**的系统状态：

- 已接通的 API
- 已入库的字段
- 已跑通的状态流
- 仍然只是骨架或 fallback 的功能
- 已知但尚未解决的边界

不要写：

- 长期产品原则
- 理想上未来应该怎样
- 尚未落地的方案设想

---

## 一、当前学生端主结构

学生端当前已经是两个一级入口：

- `AI 解答`
- `打卡复盘`

其中：

- `AI 解答` 是聊天工作区，按 `student_id + problem_id + session_id` 维持会话历史
- `打卡复盘` 是统一工作台，不再把历史记录做成独立页面

学生端工作台已经接通：

- 左侧：提交表单 + 历史打卡
- 中间：理解检查 / quiz / self-check / remedy
- 右侧：AI 复盘 + 同类题 + 同题最近 AI 解答摘要

移动端折叠顺序已经在前端实现为：

1. 右侧复盘区
2. 中间小测区
3. 左侧提交与历史区

---

## 二、当前已接通的主要 API

### 认证与聊天

- `POST /auth/login`
- `POST /chat`
- `GET /quota/{student_id}/{problem_id}`
- `POST /quota/reset`

### 学生端题目导入 / 打卡 / 复盘

- `POST /api/problem-import`
  - 当前支持洛谷题号或公开题目链接
  - 本地题库优先，网页抓取兜底
- `GET /api/problems/related`
  - 基于本地洛谷题库按 `algo_tags + difficulty` 找同类题
- `POST /api/checkins`
- `GET /api/checkins/me`

### 理解检查链路

- `POST /api/reviews/{review_id}/quiz/generate`
- `POST /api/quizzes/{quiz_id}/answer`
- `POST /api/reviews/{review_id}/self-check`
- `POST /api/reviews/{review_id}/remedy`
- `POST /api/reviews/{review_id}/remedy/resolve`

### 教师端

- `GET /api/teacher/checkins`
- `GET /api/teacher/stats`
- `GET /api/teacher/flags`
- `GET /api/teacher/usage`
- `POST /api/teacher/reviews/retry-pending`
- `GET /api/teacher/problems/analysis-failures`
- `POST /api/teacher/problems/analysis/retry`

### 页面入口

- `GET /`
- `GET /app`

---

## 三、数据库已入库的关键结构

### 1. `checkins`

当前已经包含：

- 基础字段：
  - `student_id`
  - `problem_url`
  - `problem_title`
  - `oj_source`
  - `completion_status`
  - `bottleneck_text`
  - `error_types`
  - `reflection`
- v2.1 输入增强字段：
  - `problem_context`
  - `submission_result`
  - `student_code`
  - `problem_tags`
  - `chat_context_summary`

### 2. `reviews`

当前已经包含：

- 旧字段：
  - `error_tags`
  - `diagnosis`
  - `next_action`
  - `suggested_topic`
- 当前结构化复盘字段：
  - `review_status`
  - `error_layer`
  - `error_layer_confidence`
  - `core_design_subtags`
  - `main_block`
  - `key_bridge`
  - `next_step`
  - `transfer_signal`
  - `review_quality_flags`
- 学习状态流字段：
  - `learning_status`
  - `understanding_self_check`
  - `bridge_path`
  - `remedy_count`
- 异常 / 重试字段：
  - `retry_count`
  - `last_error`
  - `last_attempt_at`

### 3. `review_quizzes`

当前已经包含：

- `quiz_role`
- `quiz_type`
- `question_text`
- `options_json`
- `correct_answer`
- `explanation`
- `bridge_feedback`
- `distractor_feedback`
- `target_bridge`
- `source_error_layer`
- `status`
- `meta_json`

### 4. `quiz_attempts`

当前已记录：

- `answer_text`
- `is_correct`
- `feedback_text`

### 5. 本地题库

#### `problems`

当前已经包含：

- `luogu_pid`
- `title`
- `difficulty`
- `statement_json`
- `samples_json`
- `time_limit_ms`
- `memory_limit_kb`
- `raw_json`
- `source`
- `source_url`
- `imported_at`
- `updated_at`

#### `problem_tags`

当前已经包含：

- `problem_id`
- `tag_name`
- `tag_type`

并且已经有：

- `(problem_id, tag_name)` 唯一约束
- `(tag_type, tag_name)` 索引

#### `problem_analysis`

当前已经包含：

- `summary`
- `strategy_types`
- `knowledge_points`
- `common_mistakes`
- `analysis_version`
- `status`
- `last_error`
- `retry_count`

#### `review_sessions`

当前已经包含：

- `student_id`
- `problem_id`
- `checkin_id`
- `prompt_tokens`
- `completion_tokens`
- `latency_ms`
- `model_tier`
- `analysis_source`
- `prompt_cache_hit`
- `review_result_json`

---

## 四、题库与题目卡当前状态

当前本地洛谷题库链路已经成立：

- `import_luogu_problemset.py` 可从本地 `latest.ndjson` 导入题库
- `problem_bank.py` 已负责：
  - 洛谷题号 / 链接归一化
  - `tag_type` 分类
  - `build_problem_context`
  - `build_compact_card`
  - `build_full_card`
  - `problem_analysis` 懒加载
  - 失败后重试

当前题目卡分为两种：

- `compact_fallback`
  - 不经过 LLM
  - 直接由官方题面裁剪
- `full_card`
  - 依赖 `problem_analysis.status = completed`
  - 含 `summary / strategy_types / knowledge_points / common_mistakes`

当前复盘时：

- 如果有 `full_card`，优先传结构化完整卡
- 否则传 `compact_fallback`

---

## 五、AI 复盘当前真实行为

### 复盘输入当前可利用的上下文

`generate_review(...)` 当前已经会综合：

- 题目标题
- 来源
- 完成状态
- `problem_card`（优先）
- 或 `problem_context`
- 平台标签（仅辅助）
- 同题最近 AI 解答摘要 `chat_context_summary`
- 提交现象
- 卡点描述
- 错误类型
- 反思
- 学生代码

### 复盘输出当前已稳定字段

- `error_tags`
- `error_layer`
- `error_layer_confidence`
- `core_design_subtags`
- `diagnosis`
- `next_action`
- `suggested_topic`
- `main_block`
- `key_bridge`
- `next_step`
- `transfer_signal`
- `review_quality_flags`

### 当前已知复盘守卫

代码里已存在多层 guard，用于：

- topic drift 收紧
- overclaim 收紧
- teacher guidance 收紧
- insufficient 保守处理
- 学生语言简化
- review quality flag 检查

---

## 六、quiz / 理解检查当前真实状态

当前理解检查链路已经跑通：

- `main`
- `followup`
- `confirm`
- `remedy`

当前 quiz 已经具备：

- `bridge_feedback`
- `distractor_feedback`
- `answer_type`
- `fallback_explain`

当前已经做过的收紧包括：

- judgement（对/错）题已被禁用
- 元认知口号题被 prompt 规则和后端双重过滤
- `answer_type = learning_advice` 时会退回 `fallback_explain`
- `general_modeling / constraint_modeling / greedy_basis / method_selection` 等易滑回口号题的 focus，当前在部分场景下会“宁可 fallback，也不放坏题”

---

## 七、学生端当前数据流已接通情况

### 1. AI 解答 → 复盘工作台

当前已经接通：

- 同题最近 AI 解答会在前端本地缓存为摘要
- 学生提交打卡时，`chat_context_summary` 会一起带给后端
- AI 复盘会把它作为辅助线索，不替代本次卡点
- 右侧复盘区可展示这条关联摘要

### 2. 历史记录 → 工作台切换

当前已经接通：

- 左侧历史卡点击后，会切换整条工作台上下文
- 中间区和右侧区会随当前选中 checkin 一起更新

### 3. 复盘 → 同类题

当前已经接通：

- 右侧可以按题号调用 `/api/problems/related`
- 当前规则基于 `algo_tags + difficulty`

---

## 八、仍然只是骨架或半成品的部分

以下能力已经有骨架，但还不算完全成熟：

### 1. `problem_analysis` 懒加载链路

已有：

- placeholder
- failed 状态
- retry_count
- 老师端失败列表和手动重试 API

但仍然是第一版，缺少：

- 更细的任务调度策略
- 批量/延迟重试策略
- 更完整的教师端可视化

### 2. `review_sessions.prompt_cache_hit`

字段已建表，能写入，但目前主要是骨架字段。

当前没有 provider 级真实 Prompt Caching 统计闭环，因此：

- 字段存在
- 但不应被当成“缓存系统已经真正上线”

### 3. 同类题推荐

当前已经能用，但还是规则版：

- 只按 `algo_tags + difficulty`
- 还没有接 `focus / bridge_path / problem_bridge_labels`

### 4. 学生端视觉与信息层级

整体工作台结构已经成立。

当前已知现状包括：

- 文本溢出问题最近已收一轮
- 视觉层级、阶段感、细节交互目前还不完全统一

---

## 九、已知但尚未彻底解决的边界问题

1. 某些 focus 当前仍会因为“结构题生成质量不稳”而 fallback，尤其是：
   - `general_modeling`
   - `constraint_modeling`
   - `greedy_basis`
   - `method_selection`

2. `problem_analysis` 和 prompt/snippet 规则之间，目前仍依赖人工保持一致，没有自动冲突检查。

3. 学生端虽然已经按工作台重排，但老师端还没有完全统一到同一套布局语言。

4. `problem_context` 对洛谷题虽然已经明显弱化，但当前前端仍保留该输入入口。

5. 当前项目 still 依赖 Moonshot API 环境变量和本地运行环境。

---

## 十、当前稳定可用的验证入口

### 基础测试

- `python3 -m py_compile api_server.py database.py review_engine.py problem_bank.py`
- `node --check static/app.js`
- `python3 test_problem_bank.py`
- `python3 test_review_api_flow.py`
- `python3 test_focus_detection.py`
- `python3 test_v1_2_flow.py`

### 页面联调

- 启动：`uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload`
- 页面：`/app`

当前人工联调最该重点看：

- 洛谷题导入
- 提交打卡后工作台右侧/中间联动
- quiz 流转（main/followup/confirm/remedy）
- 长文本是否继续溢出
- 同类题推荐是否正常出现
