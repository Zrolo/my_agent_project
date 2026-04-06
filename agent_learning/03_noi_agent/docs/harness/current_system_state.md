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

## 2026-04-04 补充：review mode 路由与 eval 基线骨架

当前代码中已经真实成立：

- `review_engine.generate_review(...)` 入口会先做：
  - `submission_result = (submission_result or "unknown").strip().lower()`
- `review_engine.py` 已新增 `_detect_review_mode(...)`
  - `wa/tle/re/ce -> failed_verdict`
  - `editorial -> editorial_transfer`
  - `unfinished/hinted -> stuck_bridge`
  - 其他 -> `independent_reflect`
- `_build_review_system_prompt(mode=...)` 已在原有 JSON schema / 字段骨架不变的前提下，接入 4 套 supplement
- 当前没有改：
  - `_parse_review(...)`
  - 现有 guard
  - `_call_llm(...)`
  - review JSON schema

当前仓库里已经新增评测骨架：

- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/export_cases.py`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_case.py`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_case_kimi_cli.py`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.yaml`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.kimi-cli.yaml`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/cases.jsonl`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo_tests.jsonl`

其中：

- `export_cases.py` 会从真实 `checkins + reviews` 中筛 `review_status=completed` 且四字段非空的样例
- 当前已导出 `20` 条真实 case：
  - `independent_reflect = 6`
  - `failed_verdict = 6`
  - `stuck_bridge = 6`
  - `editorial_transfer = 2`
- `editorial_transfer` 当前只有 `2` 条，不是脚本 bug，而是现有真实库里满足“非 failed 且 editorial 且四字段完整”的高质量样例本来就少
- `run_review_case.py` 已能直接读取单条 case，并真实调用 `generate_review(...)`
- `run_review_case_kimi_cli.py` 已能：
  - 复用 `review_engine` 当前真实的 system/user prompt builder
  - 显式向 `kimi-cli` 注入 Moonshot OpenAI Legacy 配置，避免默认 `kimi-code` provider 导致的 `LLM not set`
  - 自动剥掉 `kimi-cli` 返回中的 ```json fenced block``` 后再解析 JSON
- 当前已经用 `cases.jsonl` 第一条真实 case 验证过：
  - `run_review_case_kimi_cli.py` 可返回实体 review JSON，不再停在接入错误
- `promptfoo 0.121.3` 已安装，`promptfoo.yaml` 已成功启动评测，不存在 YAML/exec provider 级语法错误
- `promptfoo.kimi-cli.yaml` 也已成功启动 baseline + mode-route 的双 provider 评测，不存在 exec provider 级错误
- `build_promptfoo_sample.py` 已可生成一套更轻的 sample 测试集：
  - 每种 mode 各 `1` 条
  - 当前总计 `4` 条 case、`8` 个 provider-case 组合
- `promptfoo.kimi-cli.sample.yaml` 已能成功启动 sample 版评测
- 已用 `kimi-cli` runner 对“去 editorial、去 llm-rubric”的 `3 case x 2 provider` 组合做了一轮快指标对比：
- 已继续复测同一组快指标；当前最新一轮结果为：
  - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 24.31`
  - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 30.95`
- 已确认上一轮 mode-route 的主要短板确实是 JSON 稳定性；抓到过至少一条真实坏样例是字段内容里出现未转义半角双引号，导致 `invalid_json`
- 已在 `_build_review_system_prompt(...)` 的全局规则中新增：不要在字段内容里使用半角双引号；引用题面词语时直接改写，或不用引号
- 针对 `stuck_bridge_57` 的第一轮直接回测已恢复为合法 JSON，但后续复测中又暴露出第二类 `invalid_json`：`transfer_signal` 会把题面特征再次包进半角双引号
- 已在 `stuck_bridge` supplement 中新增：`transfer_signal` 不要给题面特征加引号
- `stuck_bridge_57` 在第二轮单点回测后已再次恢复为合法 JSON；继续复测同一组快指标后，mode-route 重新稳定在 `fields_ok_rate = 1.0`
- 当前最新一轮快指标为：
  - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 24.31`
  - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 29.98`
- 已继续收“报告太元知识化”的问题：当前在全局规则中新增 `next_action / suggested_topic` 优先回到当前题，不写专项训练、经典题、做3道、变式或拓展；`failed_verdict` supplement 也新增了“先检查当前题哪一处代码、判断或输出”
- 对 `failed_verdict_296` 的直接回测已验证：`next_action` 现可回到当前题里的 `且/或` 判断逻辑，不再默认滑向“做3道”式建议
- 当前已重新切回带 `llm-rubric` 的非 editorial sample promptfoo 长跑，用于验证 mode-route 是否在质量分上优于 baseline
- 当前已新增一条不依赖 promptfoo 落表的直接质量评测脚本：
  - `evals/review/run_review_quality_eval.py`
  - 会沿用同一批 case、同一组 `baseline_current_kimi_cli / mode_route_kimi_cli` 和同一套 rubric 规则，直接输出：
    - `json_ok_rate`
    - `fields_ok_rate`
    - `rubric_avg_score`
- 当前这条质量评测链的 rubric 规则已从脚本内联文本收成独立资产：
  - `evals/review/review_rubric_v2.json`
  - 后续更新 judge 标准时，可优先改 rubric 文件，而不必改脚本主体
- 已用 non-editorial sample 跑出一轮三指标：
  - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 0.667`、`rubric_avg_score = 1.667`
  - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`rubric_avg_score = 2.667`
- 当前这轮直接质量评测已证明：mode-route 不只是追平快指标，而且在 non-editorial sample 上已经明显优于 baseline
- 继续针对 `stuck_bridge_57` 做低分 case 回测时，又观察到同一 prompt 存在轮次波动：
  - 单点直接回测可返回合法 JSON 和完整四字段
  - 但单 case 质量评测中，mode-route 偶发仍可能掉到 `fields_ok = 0`
- 当前剩余问题已从“提示词规则缺失”收窄到“同一 prompt 的稳定性波动”；后续评测更适合引入重复跑或聚合分数，而不是只看单次结果
- `run_review_quality_eval.py` 当前已支持 `repeats` 参数，可对同一 case/provider 做重复跑并输出聚合均值与逐次 `attempts`
- 已用 `stuck_bridge_57` 做 `repeats=2` 的最小聚合验证：
  - `baseline_current_kimi_cli`：`rubric_avg_score = 2.0`
  - `mode_route_kimi_cli`：`rubric_avg_score = 2.0`
  - mode-route 当前在这条 case 上仍会出现 `3 分 / 1 分` 的波动，说明这条样例的主要剩余风险已从“必然失败”变成“表达稳定性不足”
- 已继续收这条低分样例：在 `stuck_bridge` supplement 中新增“不要只写限制条件、最优选择、当前进度这些抽象词”
- 当前真实瓶颈是：全量 `40` 个 provider-case 组合跑得很慢，不是评测骨架起不来

## 一、当前学生端主结构

学生端当前已经是三个一级入口：

- `AI 解答`
- `打卡复盘`
- `历史打卡`

其中：

- `AI 解答` 是聊天工作区，按 `student_id + problem_id + session_id` 维持会话历史
- `打卡复盘` 是统一工作台，当前只保留提交表单和当前选中记录的工作台
- `历史打卡` 是学生区内部独立标签，用现有 `GET /api/checkins/me` 数据源展示紧凑历史列表

学生端工作台已经接通：

- 左侧：提交表单
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
- `GET /api/checkins/{checkin_id}`
- `GET /api/checkins/{checkin_id}/stream`
- `POST /api/checkins/{checkin_id}/review/retry`
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

其中学生端打卡复盘当前已经接通一条“流式状态、非流式正文”的等待链：

- 提交打卡后，前端优先用 `fetch + ReadableStream` 订阅 `GET /api/checkins/{checkin_id}/stream`
- 后端通过固定阶段埋点推送状态事件，不直接流正文 token
- 当前阶段包括：
  - `received`
  - `queued`
  - `llm_start`
  - `llm_done`
  - `review_parse`
  - `review_saved`
  - `quiz_generating`
  - `completed`
  - `failed`
- 当前前端不会用裸 `EventSource`，因为认证仍依赖 `Authorization: Bearer ...` 请求头
- 流式状态链断开或不可用时，前端会自动退回现有单条 checkin 轮询

在此基础上，当前又补了一层“流式正文草稿预览”：

- review 调用仍保持结构化 JSON 输出，不改最终 schema
- 后端会在模型流式 chunk 到来时，尽量从累计 JSON 文本里抽出：
  - `main_block`
  - `key_bridge`
  - `next_step`
  - `transfer_signal`
- SSE 当前除了 `status / review_ready / error / keepalive` 之外，还会发：
  - `review_chunk`
- 前端 `pending` 卡会优先显示：
  - 当前阶段
  - 已等待秒数
  - `AI 草稿预览`
- 正式复盘完成后，右侧仍由现有详情接口覆盖成正式内容

学生端最终复盘卡当前也已收成两层：

- 默认只展示：
  - `你卡在哪`
  - `关键一步`
  - `现在先做`
  - `下次提醒`
- `错误标签 / 统一归类 / 判断把握 / 子标签 / 详细诊断 / 下一步行动 / 推荐专题`
  只有在有内容时才进入折叠层显示

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

### 6. `confirm_pool`

当前已经新增：

- `problem_id`
- `problem_url`
- `structure_type`
- `difficulty`
- `bridge_note`
- `status`
- `skip_count`

并且已经有：

- `(status, structure_type)` 索引
- `structure_type` 唯一约束

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

### review 上游桥梁稳定性当前已落地状态

针对高风险 review focus，当前代码里已经有第一轮专门收紧：

- `general_modeling`
- `constraint_modeling`
- `greedy_basis`
- `method_selection`

当前这轮已真实落地的内容包括：

- `test_review_regression.py` 已把这 4 个 focus 纳入回归门
- `B1 / D1` 已不再只靠固定短词命中；当前脚本里已经增加独立结构断言函数，并新增 `test_review_regression_unit.py` 做正反例单测
- 回归脚本会把以下情况直接判失败：
  - `review_status != completed`
  - 请求异常
  - 明显泛建议
  - 结构词命中明显不足
- `B1` 当前会额外检查：
  - 时间 / 地点两个条件是否被讲成平级同时成立
  - 是否滑成“先满足 A，再检查 B”的顺序结构
  - `next_step` 是否仍是学生可直接执行的动作
- `D1` 当前会额外检查：
  - 是否先看规模 / 范围再决定方法
  - 是否明确落到可直接枚举而不是先上 DP
  - `next_step` 是否给出规模判断或枚举起手动作
- `review_engine.py` 已对这 4 个 focus 增加更积极的 bridge stability guard
- guard 当前不只会兜底 `key_bridge / next_step`，也会兜底 `main_block / transfer_signal`
- `general_modeling` 已补过一次 focus 优先级修正，避免对象-关系题被过早拉到约束建模
- `method_selection` 已补过一次 topic drift 修正，避免“小规模先看范围”的题因为学生提到 DP 就被拉回 DP 兜底文案

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

- `历史打卡` 标签内的历史卡点击后，会切换整条工作台上下文
- 点击历史记录后，前端会自动切回 `打卡复盘` 标签
- 中间区和右侧区会随当前选中 checkin 一起更新
- 学生提交打卡后，`POST /api/checkins` 已改成立即返回 `review_status = pending`
- 前端会轮询单条状态接口，而不是反复拉整页历史列表
- 右侧工作区当前已区分：
  - `pending` 等待卡
  - `failed` 失败卡 + 重新生成按钮
  - `timeout` 超时提示卡
  - `completed` 正式复盘内容

### 2.1 打卡复盘的快反馈状态流

当前已经真实成立：

- checkin 入库成功后，请求线程不再等待整条 review 生成完成
- review 生成已改为后台任务执行
- 当前代码已增加“最多 5 个并发 review 生成”的上限控制
- `review_engine.py` 当前已给 LLM 调用补上请求级 timeout，避免后台线程无限挂住
- 学生端单条状态接口当前有鉴权边界：
  - 必须是当前登录学生本人
  - 不属于当前学生的 checkin 返回 `404`
- retry 接口当前只允许：
  - `review_status = failed`
- retry 接口当前明确拒绝：
  - `pending`
  - `completed`
- 学生端单条状态接口不会暴露真实 `review_last_error`

### 3. 复盘 → 同类题

当前已经接通：

- 右侧可以按题号调用 `/api/problems/related`
- 当前规则基于 `algo_tags + difficulty`

---

## 八、仍然只是骨架或半成品的部分

### 学生分流 / confirm 当前已落地边界

当前后端已经有统一学习路由入口：

- `A` 类显式卡住信号：
  - 关键词枚举：`不会`、`卡住`、`需要提示`、`看不懂`、`没思路`
  - `completion_status = hinted`
  - `submission_result in {wa, tle, re, ce}`
- `B` 类解释层过线：
  - `main` 必须答对
  - `followup` 若存在必须答对
  - `confirm` 若存在必须答对
  - `self-check = clear`

当前 `A` 类已经真实接进主链：

- 当复盘命中显式卡住信号后，调用 `POST /api/reviews/{review_id}/quiz/generate`
  - 不再继续生成 `main` quiz
  - 直接返回 `learning_status = remedy_available`
  - `next_state = remedy_available`
  - 前端应直接引导学生先回到卡住点，而不是继续做理解小测

当前 `self-check` 状态流已经收成：

- `clear`
  - 若解释层过线，且 `transfer_signal` 含明确触发信号，则进入 `confirm`
  - 否则直接 `resolved`
- `confused`
  - 进入 `remedy_available`
- `guessed`
  - 进入 `remedy_available`

当前 `confirm` 已接通：

- 固定池优先：先按 `problem_tags -> structure_type` 命中 `confirm_pool`
- LLM 兜底：固定池未命中时最多重试 2 次
- 若某个 `structure_type` 连续跳过累计达到 4 次，会自动标记为 `needs_backfill`
- `test_learning_routing_unit.py` 当前已明确断言：命中固定池时，返回的 `confirm` quiz 必须带 `meta.confirm_mode = fixed_pool`
- 当前固定池已实际导入 8 个结构类型种子题：
  - `difference_constraints`
  - `topological_sort`
  - `bipartite_graph`
  - `monotonic_queue`
  - `shortest_path`
  - `union_find`
  - `tree_dp`
  - `interval_dp`

当前 `remedy` 已收紧为：

- 必须带回学生原始 `bottleneck_text` 或当前 `main_block`
- 不再只输出泛化讲解
- 当前真实接口联调已确认：
  - `B` 类：`self-check = clear` 且解释层不过线时，会进入 `remedy_available`
  - `C` 类：解释层过线且固定池命中时，会返回 `confirm_quiz`
  - `A` 类：显式卡住信号存在时，`quiz/generate` 会直接短路到 `remedy_available`
  - `A -> remedy -> resolve` 这一整段接口链已经跑通
  - `C -> confirm answer -> resolved` 这一整段接口链已经跑通
  - 上面两段链路都已经补到从 `POST /api/checkins` 起步的更长接口链，不再只是从 `review_id` 中段开始测

### confirm_pool 数据准备产物

当前仓库已经有：

- `prepare_confirm_pool.py`
  - 读取 `latest.ndjson`
  - 输出 `total_rows / tag_type_counts / top_algo_tags / top_tag_pairs`
- `docs/subjects/noi/confirm_pool_tag_stats_v1.json`
  - 已基于真实 `latest.ndjson` 跑出第一轮标签统计
- `docs/subjects/noi/confirm_pool_mapping_v1.json`
  - 第一版 10 个 `structure_type` 草案
  - `bridge_note` 模板
  - 当前已经补上第一轮 `usable / defer` 与 `luogu_tags`
  - 当前保守策略是：直接能和真实细粒度标签对上的先 `usable`，过粗的先 `defer`
- `docs/subjects/noi/confirm_pool_seed_v1.json`
  - 第一批 8 个固定池种子题清单
- `seed_confirm_pool.py`
  - 支持 dry-run 和实际导入

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

### 2.1 review / quiz / problem_analysis 的消息结构

当前代码里已经完成：

- `_call_llm(...)` 不再接收单条字符串 prompt，而是接收 `messages`
- `generate_review(...)` 已改成 `system + user` 两条消息
- `generate_problem_analysis(...)` 已改成 `system + user` 两条消息
- 结构型 quiz 生成当前也已改成 `system + user` 两条消息

当前已新增单测：

- `test_review_engine_messages_unit.py`
  - 检查 review / problem_analysis / structural quiz 三条链都不再把 system 和 user 拼成一坨字符串

### 3. 同类题推荐

当前已经能用，但还是规则版：

- 只按 `algo_tags + difficulty`
- 还没有接 `focus / bridge_path / problem_bridge_labels`

### 4. 学生端视觉与信息层级

整体工作台结构已经成立。

当前已知现状包括：

- 文本溢出问题最近已收一轮
- 学生端当前已经把历史记录从 `打卡复盘` 页抽离到独立 `历史打卡` 标签
- 历史卡摘要、推荐方向说明等原先纯文本输出位，当前已统一接入 `.rich-text` + KaTeX hydration
- 视觉层级、阶段感、细节交互目前还不完全统一

---

## 九、已知但尚未彻底解决的边界问题

1. 某些 focus 当前仍会因为“结构题生成质量不稳”而 fallback，尤其是：
   - `general_modeling`
   - `constraint_modeling`
   - `greedy_basis`
   - `method_selection`

2. `review -> key_bridge / next_step` 在高风险 focus 上已经比上一轮更稳：
   - `A1`、`D2` 当前可稳定通过
   - `B1 / D1` 当前在新结构回归门下已完成一次真实 AI 联跑 `2/2` 通过
   - `B1` 这轮已补过一次 focus 检测顺序修正，避免并列约束题被 `general_modeling` 抢走
   - 当前 `B1 / D1` 的主要风险已从“固定词表误伤”收回到“真实输出表述仍会波动，但新结构门已能更稳地兜住”

3. `problem_analysis` 和 prompt/snippet 规则之间，目前仍依赖人工保持一致，没有自动冲突检查。

4. 学生端虽然已经按工作台重排，但老师端还没有完全统一到同一套布局语言。

5. `problem_context` 对洛谷题虽然已经明显弱化，但当前前端仍保留该输入入口。

6. 当前项目 still 依赖 Moonshot API 环境变量和本地运行环境。

7. “复盘提速 + 快反馈”当前已完成两组第一版落地：
   - 第一组：后台生成 + 前端轮询 + 单条状态接口 + retry
   - 第二组：`system/user` 分离
   - 当前仍未做全文 streaming

---

## 十、当前稳定可用的验证入口

### 基础测试

- `python3 -m py_compile api_server.py database.py review_engine.py problem_bank.py`
- `python3 -m unittest test_review_async_api_unit.py`
- `python3 -m unittest test_review_engine_messages_unit.py`
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
- `历史打卡` 标签点击后是否能回切到当前工作台
- 题干/选项/复盘/历史摘要里的 LaTeX 是否稳定渲染
- quiz 流转（main/followup/confirm/remedy）
- 长文本是否继续溢出
- 同类题推荐是否正常出现

### 真实联调补充

当前已经做过一轮真实接口联调验证：

- 在最新代码实例上，`POST /api/checkins` 已可在极短时间内直接返回 `review_status = pending`
- 后台 review 失败后，单条状态接口可读到 `failed`
- `POST /api/checkins/{checkin_id}/review/retry` 已可把失败记录重新切回 `pending`
- 前端轮询当前已不再优先读本地旧缓存，而会真实请求单条状态接口
- 单条状态接口返回的嵌套 `review` 当前已在前端摊平到现有工作区渲染字段

已知运行边界：

- 如果本地正在跑的 `uvicorn` 不是最新代码实例，旧进程不会自动吃到这轮改动
- startup 阶段的待生成复盘修复任务当前已改成后台线程，不再阻塞服务启动
- 当前真实 review 生成延迟仍偏长，最近一批 `review_sessions` 平均耗时约 48 秒，因此页面出现较长 `pending` 可能是后端真实仍在生成，而不一定是前端卡住
- 已确认一次真实故障边界：旧进程里模型调用可能长期挂住并把单条记录卡在 `pending`；重启到带 timeout 的实例后，该记录可继续推进到 `completed` 或 `failed`
- 在当前 `kimi-k2.5` 实例上，已真实观测到 `Request timed out.`；这时学生端会看到“复盘生成失败”，而不是无限停在 `pending`
- 已用真实服务复现 `P5536` 树直径卡点样例：打卡内容可通过校验并创建记录，但后台 review 生成在当前环境里可能出现两种不稳定表现：
  - 超时后进入 `failed`
  - 超过 50 秒仍停在 `pending`
- 已确认真实 `review_sessions` 存在超长生成：`checkin 254` 曾出现 `completion_tokens = 9663`、`latency_ms = 263682`；`checkin 260` 的未限流成功样例也有 `completion_tokens = 1620`、`latency_ms = 134507`
- `review_engine.py` 当前已给 `_call_llm()` 增加 `max_tokens` 上限；对 `P5536` 样例的直接烟雾验证里，`generate_review(...)` 耗时已降到约 `35.92s`
- 但当前 `1200` 上限会把部分复盘压成“信息不足”式保守输出，说明“限制输出长度”方向有效，但参数仍需继续校准
- `P5536` 这类“树直径公式来源”题还暴露出另一条质量边界：模型可能给出较准的 `diagnosis`，但 `core_design_subtags=["greedy_basis", ...]` 会把学生端字段拉回贪心模板；当前已增加“无贪心信号时不直接套 greedy_basis 模板”的保护
- review prompt 压缩 v1 当前已补 3 条输入保护，避免“压短后把关键信号裁没”：
  - 只有泛标签时不再回填 `O2优化 / NOIP / 模板` 这类标签
  - 代码裁剪不再只保留头尾，而会优先带上中段的关键公式/赋值行
  - `problem_card` 存在时，仍允许补一小段 `problem_context` 作为题目补充，避免证明/关系类细节被完全遮掉
- 已用真实 `P5536` 样例再次做压缩版 prompt 烟雾验证：
  - `generate_review(...)` 约 `37.82s` 返回成功，未超时
  - `prompt_tokens = 841`，`completion_tokens = 1200`
  - 但当前输出被压成 `error_layer = insufficient`、`error_layer_confidence = low`
  - 说明“压缩 prompt + 当前 1200 上限”已能保住可用性，但仍会把“知道直径、卡在公式证明”误判成信息不足
- 已进一步拆链验证：上述 `insufficient` 不是后处理 guard 拉回去，而是 `_call_llm()` 在 `completion_tokens = 1200` 时直接返回空字符串 `content=""`
- 已确认这条边界同样适用于评测链：若把 `max_tokens/max_completion_tokens` 压得过低，`kimi-k2.5` 会出现空输出、`invalid_json` 或直接错误；这类结果反映的是预算过低，不应当被当作 prompt 质量结论。
  - `_parse_review("")` 因此回落到默认 `insufficient + low`
  - `_guard_review_against_topic_drift(...)`、`_guard_review_for_insufficient(...)` 在这条样例上没有进一步改坏结果
  - 当前主风险已收敛为：`kimi-k2.5 + 压缩版 prompt + max_tokens=1200` 会出现“请求成功但正文为空”的输出阶段边界
- 已补双轨实验验证输出阶段边界：
  - `compressed prompt + max_tokens=1400`：约 `41.31s`，`prompt_tokens = 841`，`completion_tokens = 1400`，仍返回空字符串
  - `4 字段极简 prompt + max_tokens=1200`：约 `35.17s`，`prompt_tokens = 240`，`completion_tokens = 1200`，仍返回空字符串
  - 说明当前问题不只是“字段太多”或“1200 太紧”，而是 `kimi-k2.5` 在这类结构化 review 请求上存在“成功但空 content”的输出阶段异常
- 已按 Moonshot 官方文档收正 `_call_llm()` 的调用方式：
  - review 调用已改成 `response_format={"type":"json_object"}`
  - 已由 `max_tokens` 切到 `max_completion_tokens`
  - 对 `kimi-k2.5` 不再显式传 `temperature`
  - 已开始记录 `finish_reason`
- 改正后补了真实烟雾验证：
  - 极简 JSON 请求不再出现“成功但空正文”
  - 当前新的真实边界变成：`finish_reason = length`，`completion_tokens = 1200` 时会被明确判成截断失败
  - 说明“Moonshot 接法不规范”这条问题已收掉一部分，但 review 任务本身仍然会撞到输出上限
- 已继续对 `P5536` 样例做 `max_completion_tokens` 档位实测（在已对齐 Moonshot 文档的接法上）：
  - `1200`：约 `41.69s`，`prompt_tokens = 582`，`completion_tokens = 1200`，`finish_reason = length`
  - `1400`：约 `138.39s`，最终 `Request timed out.`
  - `1600`：约 `83.19s`，`completion_tokens = 1600`，`finish_reason = length`
  - `1800`：约 `87.44s`，`completion_tokens = 1800`，`finish_reason = length`
  - 当前没有出现“略微提高上限就自然恢复可用正文”的稳定窗口
- 已单独验证 timeout 语义：
  - 将 `LLM_REQUEST_TIMEOUT_SECONDS` 压到 `5` 后，同样的 review 请求会在约 `19.5s` 后报 `Request timed out.`
  - 说明当前 SDK 调用里的 `timeout` 不是严格硬上限，不能把它当作“到了 N 秒一定会立刻中断”的保护
- review 主链当前已改为 `stream=true` 按 chunk 收集正文，并对空正文/超时/截断增加一次定向重试
- 但真实 `P5536` 默认样例在新链路下仍未恢复可用正文：
  - 第一次流式请求先落到 `finish_reason = length`
  - 一次重试后仍失败，整次调用约 `83.78s`
  - 说明“stream + 单次重试”本身还不足以把当前 Kimi review 主链救活
- 当前 `NOI_REVIEW_MAX_TOKENS` 的代码默认值已从 `1200` 调回 `32768`
- 这一步的含义是：不再默认用一个极保守上限人为截断 review；但是否稳定、是否会重新拉长耗时，仍需要新的真实样例验证
- 已补真实默认链路验证：当前代码默认 `32768` 下，`P5536` 样例在约 `80.04s` 后恢复出了实体正文，`finish_reason = stop`
- 当前新边界是：
  - 默认上限 `32768` 已足以让这条样例不再被 `length` 截断
  - 但代价是单次 review 耗时明显变长
  - 当前流式调用下这次未拿到 `usage`，所以 `prompt_tokens/completion_tokens` 记为 `0`
