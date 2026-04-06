# Review 上线观测埋点 Spec

## 1. 目标

这份文档定义 NOI review 系统上线后的最小观测方案，用来回答四个问题：

1. `mode routing` 是否分对。
2. 学生看完复盘后是否真的看懂，是否继续追问。
3. 哪类输入最容易导致复盘质量差。
4. 单次生成等待时间是否可接受。

这份 spec 的目标不是做全量 BI，而是提供一套开发可以直接落地、教研可以直接复盘的最小数据闭环。

---

## 2. 范围

本 spec 只覆盖 review 主链路的上线观测，不覆盖：

- rubric / gate 离线评测日志
- prompt 实验脚本内部埋点
- quiz 流程的细粒度交互日志

本 spec 覆盖三层数据：

1. 前端事件
2. 后端日志
3. 人工抽样复核

---

## 3. 核心原则

### 3.1 先保证能回答问题，再追求埋点全面

第一版只保留能直接支撑决策的字段，不为“以后可能会用”预留大量空字段。

### 3.2 用同一条 `session_id` 串起前后端和人工复核

所有事件、日志和人工标注必须能通过同一个 `session_id` 对齐。

补充约束：
- 第一阶段 `session_id` 与一次 checkin / 一次 review 会话 1:1 对应。
- `session_id` 在 checkin 创建时生成并写入数据库，后续由详情接口直接带回，不额外引入 1:n 的 session 层。

### 3.3 先采集学生是否看懂，再讨论更细的学习收益

第一阶段先判断“这条 review 对学生有没有立即帮助”，不急着直接判断长期学习效果。

### 3.4 离线评测保留为回归工具，线上观测才是后续主信号

cases + rubric + gate 继续保留，但上线后的 prompt 迭代优先看真实使用数据。

---

## 4. 事件定义

第一版只定义 4 个核心事件：

1. `review_request_submitted`
2. `review_generated`
3. `review_shown`
4. `review_feedback_submitted`

### 4.1 `review_request_submitted`

含义：
- 学生提交了一次 review 请求。

触发时机：
- 前端点击提交并成功发出请求后立即记录。

用途：
- 统计请求量。
- 作为漏斗起点。

### 4.2 `review_generated`

含义：
- 后端已成功生成一条结构完整的 review。

触发时机：
- review JSON 解析成功，且核心字段已齐全后记录。

用途：
- 统计生成成功率。
- 统计 mode 分布、输入特征与生成质量关系。
- 统计时延。

### 4.3 `review_shown`

含义：
- 前端已成功把 review 展示给学生。

触发时机：
- 页面实际渲染完成后记录。

用途：
- 区分“后端成功生成”和“学生真的看到了”。

### 4.4 `review_feedback_submitted`

含义：
- 学生对本次 review 提交了反馈。

触发时机：
- 学生点击反馈按钮或提交追问后记录。

用途：
- 判断学生是否看懂。
- 判断差评原因。
- 判断追问意愿。

---

## 5. 公共字段

以下字段建议所有事件统一携带：

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 一次 review 会话的唯一标识 |
| `user_id` | string | 学生标识；如有隐私要求可脱敏 |
| `problem_id` | string | 题目标识；没有时可为空 |
| `problem_title` | string | 题目标题 |
| `review_mode` | enum | `failed_verdict / stuck_bridge / independent_reflect / editorial_transfer` |
| `client_ts` | string | 前端事件时间，ISO8601 |
| `server_ts` | string | 后端记录时间，ISO8601 |
| `app_version` | string | 前端版本或部署版本 |

---

## 6. 前端埋点字段

### 6.1 `review_request_submitted`

```json
{
  "event": "review_request_submitted",
  "session_id": "uuid",
  "user_id": "string",
  "problem_id": "string",
  "problem_title": "string",
  "review_mode": "failed_verdict | stuck_bridge | independent_reflect | editorial_transfer",
  "client_ts": "iso_datetime",
  "server_ts": "iso_datetime",
  "app_version": "string",
  "has_code": true,
  "problem_context_length": 320,
  "bottleneck_text_length": 48
}
```

说明：
- `problem_context_length` 与 `bottleneck_text_length` 可以由前端直接上报，也可以由后端回填。
- 第一版不要求前端上传原文，只要求上传长度和是否有代码。

### 6.2 `review_shown`

```json
{
  "event": "review_shown",
  "session_id": "uuid",
  "user_id": "string",
  "problem_id": "string",
  "problem_title": "string",
  "review_mode": "failed_verdict | stuck_bridge | independent_reflect | editorial_transfer",
  "client_ts": "iso_datetime",
  "server_ts": "iso_datetime",
  "app_version": "string",
  "latency_ms": 12345,
  "review_text_length": 268
}
```

说明：
- `latency_ms` 以前端从提交到展示完成的总耗时为准。
- `review_text_length` 用于判断“太长/太短”反馈是否与正文长度相关。

### 6.3 `review_feedback_submitted`

```json
{
  "event": "review_feedback_submitted",
  "session_id": "uuid",
  "user_id": "string",
  "problem_id": "string",
  "problem_title": "string",
  "review_mode": "failed_verdict | stuck_bridge | independent_reflect | editorial_transfer",
  "client_ts": "iso_datetime",
  "server_ts": "iso_datetime",
  "app_version": "string",
  "student_feedback": "understood | neutral | confused",
  "bad_reason": "too_abstract | not_grounded | too_long | no_next_step | still_cant_apply | none",
  "followup_clicked": true,
  "followup_question_count": 1
}
```

前端建议文案：

`student_feedback`
- `看懂了`
- `一般`
- `没看懂`

`bad_reason`
- `太抽象`
- `不贴这道题`
- `太长`
- `看完还是不知道下一步`
- `说得对，但我不会用`

说明：
- 若 `student_feedback != confused`，`bad_reason` 可固定写 `none`。
- 若学生没有提交任何反馈，不强制补空事件。

---

## 7. 后端日志字段

### 7.1 `review_generated`

```json
{
  "event": "review_generated",
  "session_id": "uuid",
  "user_id": "string",
  "problem_id": "string",
  "problem_title": "string",
  "review_mode": "failed_verdict | stuck_bridge | independent_reflect | editorial_transfer",
  "completion_status": "unfinished | hinted | independent | editorial",
  "submission_result": "wa | tle | re | ce | ac | not_submitted | unknown",
  "has_code": true,
  "problem_context_length": 320,
  "bottleneck_text_length": 48,
  "review_json_ok": true,
  "review_fields_ok": true,
  "review_text_length": 268,
  "main_block_length": 31,
  "key_bridge_length": 42,
  "next_step_length": 18,
  "transfer_signal_length": 27,
  "model_name": "kimi-k2.5",
  "total_latency_ms": 11840,
  "server_ts": "iso_datetime"
}
```

说明：
- `review_json_ok` 与 `review_fields_ok` 是最关键的结构可用性指标。
- `main_block_length / key_bridge_length / next_step_length / transfer_signal_length` 用于后续定位“字段为空”“字段过短”“字段异常长”等问题。

### 7.2 推荐扩展字段

若后端接入成本可接受，建议补以下可选字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `has_problem_title` | bool | 是否有题目标题 |
| `has_problem_context` | bool | 是否有题目背景 |
| `mode_source` | enum | `explicit / inferred` |
| `streaming_used` | bool | 是否走了流式状态通道 |
| `error_code` | string | 失败时的结构化错误码 |

第一版没有这些字段也可以先上线。

---

## 8. 人工抽样复核

人工复核不做全量，只做抽样。

建议频率：
- 每天抽 `10-20` 条

建议来源：
- 各 mode 都要覆盖
- 优先抽学生反馈为 `confused`
- 再抽一部分 `understood` 作为对照组

### 8.1 复核表字段

```json
{
  "session_id": "uuid",
  "problem_id": "string",
  "review_mode": "string",
  "mode_correct": "correct | incorrect | unsure",
  "review_grounded": "grounded | mixed | vague",
  "student_can_move_next": "yes | no | unsure",
  "notes": "string"
}
```

字段解释：

- `mode_correct`
  - 路由是否分对
- `review_grounded`
  - 复盘是否贴题
- `student_can_move_next`
  - 看完后学生是否具备明确下一步
- `notes`
  - 一句自由备注，用于记录特殊失败模式

---

## 9. 看板指标口径

第一版看板只看 8 个核心指标。

### 9.1 生成成功率

```text
review_success_rate = review_generated / review_request_submitted
```

### 9.2 展示成功率

```text
review_show_rate = review_shown / review_generated
```

### 9.3 看懂率

```text
understood_rate = student_feedback == understood / review_feedback_submitted
```

### 9.4 没看懂率

```text
confused_rate = student_feedback == confused / review_feedback_submitted
```

### 9.5 追问率

```text
followup_rate = followup_clicked == true / review_shown
```

### 9.6 路由正确率

```text
mode_match_rate = mode_correct == correct / 人工复核样本数
```

### 9.7 贴题率

```text
grounded_rate = review_grounded == grounded / 人工复核样本数
```

### 9.8 可继续率

```text
can_move_next_rate = student_can_move_next == yes / 人工复核样本数
```

### 9.9 时延

使用：
- `latency_p50`
- `latency_p90`

来源：
- `review_generated.total_latency_ms`

---

## 10. 第一版看板分组建议

第一版只建议按 3 个维度分组：

1. `review_mode`
2. `has_code`
3. `student_feedback`

不建议一开始就按：
- 题号
- 年级
- 老师
- 班级

拆得太细会让样本量过小，噪音高于信号。

---

## 11. 第一周重点观察

第一周只盯 6 张图或 6 组数：

1. 各 mode 请求量
2. 各 mode `understood_rate`
3. 各 mode `followup_rate`
4. `bad_reason` 分布
5. `latency_p50 / latency_p90`
6. 人工复核里的 `mode_match_rate`

---

## 12. 开发接入顺序

建议按下面顺序推进：

### 第一步：先接后端日志

目标：
- 保证每条 review 至少有结构化生成记录。

原因：
- 后端日志最稳定，最容易先落。

### 第二步：再接前端反馈

目标：
- 收集学生是否看懂、是否追问。

原因：
- 这是上线后最值钱的真实用户信号。

### 第三步：再接人工复核表

目标：
- 验证 mode routing 是否真的分对。

原因：
- 人工复核成本更高，适合在前两步稳定后接入。

---

## 13. 非目标

本 spec 第一版不要求：

- 自动生成复杂经营报表
- 做教师端全量看板
- 对每条 review 做在线 rubric/gate 评分
- 直接估计学生长期掌握程度

这些能力可以在真实使用数据积累后再加。

---

## 14. 落地验收标准

上线前，至少满足以下 4 条：

1. 四个事件有统一 `session_id`
2. 后端能稳定产出 `review_generated`
3. 前端能采集学生反馈三档和差评原因
4. 每天能抽样复核 `10-20` 条并回填结果

若以上 4 条不能同时满足，不建议把“真实数据驱动迭代”作为下一阶段主策略。

---

## 15. 配套落地文档

为方便开发和教研分工，配套拆出三份执行文档：

- 前端接入清单：
  - `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_frontend_checklist.md`
- 后端接入清单：
  - `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_backend_checklist.md`
- 人工抽样复核 SOP：
  - `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_manual_review_sop.md`

进一步的派工文档：

- 前端任务单：
  - `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_frontend_tasks.md`
- 后端任务单：
  - `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_backend_tasks.md`
- 教研任务单：
  - `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_teaching_tasks.md`
