# Review 上线观测前端接入清单

这份清单给前端开发使用，目标是把 review 上线观测的用户侧埋点接完整。

关联文档：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_spec.md`

---

## 1. 目标

前端侧需要完成三件事：

1. 在学生提交 review 请求时打点。
2. 在 review 实际展示给学生时打点。
3. 在学生反馈“看懂/没看懂”以及追问时打点。

第一版不要求前端自己计算复杂指标，只要求稳定发送结构化事件。

---

## 2. 需要接入的事件

### 2.1 `review_request_submitted`

触发时机：
- 学生点击提交，并且请求已成功发出后。

必填字段：

```json
{
  "event": "review_request_submitted",
  "session_id": "uuid",
  "user_id": "string",
  "problem_id": "string",
  "problem_title": "string",
  "review_mode": "failed_verdict | stuck_bridge | independent_reflect | editorial_transfer",
  "client_ts": "iso_datetime",
  "app_version": "string",
  "has_code": true,
  "problem_context_length": 320,
  "bottleneck_text_length": 48
}
```

实现要点：
- `session_id` 与一次 checkin / 一次 review 会话 1:1 对应，必须能串起后续所有事件。
- 如果 `problem_id` 不存在，可以传空字符串，但字段必须保留。
- `problem_context_length` 和 `bottleneck_text_length` 按字符数统计即可。

### 2.2 `review_shown`

触发时机：
- review 已成功渲染到学生可见界面后。

必填字段：

```json
{
  "event": "review_shown",
  "session_id": "uuid",
  "user_id": "string",
  "problem_id": "string",
  "problem_title": "string",
  "review_mode": "failed_verdict | stuck_bridge | independent_reflect | editorial_transfer",
  "client_ts": "iso_datetime",
  "app_version": "string",
  "latency_ms": 12345,
  "review_text_length": 268
}
```

实现要点：
- `latency_ms` 以前端从提交到展示完成的总耗时为准。
- `review_text_length` 建议按四个学生端字段拼接后的总长度统计。

### 2.3 `review_feedback_submitted`

触发时机：
- 学生点击反馈按钮。
- 学生提交追问。

必填字段：

```json
{
  "event": "review_feedback_submitted",
  "session_id": "uuid",
  "user_id": "string",
  "problem_id": "string",
  "problem_title": "string",
  "review_mode": "failed_verdict | stuck_bridge | independent_reflect | editorial_transfer",
  "client_ts": "iso_datetime",
  "app_version": "string",
  "student_feedback": "understood | neutral | confused",
  "bad_reason": "too_abstract | not_grounded | too_long | no_next_step | still_cant_apply | none",
  "followup_clicked": true,
  "followup_question_count": 1
}
```

实现要点：
- 没看懂时才展示 `bad_reason` 二级选项。
- 若学生点击“看懂了”或“一般”，`bad_reason` 固定传 `none`。
- `followup_question_count` 第一版只需统计当前 session 下学生追加提问的次数。

---

## 3. 建议交互文案

### 3.1 学生理解反馈

- `看懂了`
- `一般`
- `没看懂`

### 3.2 差评原因

- `太抽象`
- `不贴这道题`
- `太长`
- `看完还是不知道下一步`
- `说得对，但我不会用`

---

## 4. 接入顺序

建议前端按下面顺序实现：

1. 先接 `review_request_submitted`
2. 再接 `review_shown`
3. 最后接 `review_feedback_submitted`

原因：
- 这样可以先打通基础漏斗，再补用户反馈层。

---

## 5. 联调验收

前端联调完成后，至少确认：

1. 一次正常 review 会产生：
   - `review_request_submitted`
   - `review_shown`
2. 学生点击反馈后会产生：
   - `review_feedback_submitted`
3. 三个事件的 `session_id` 一致
4. `latency_ms` 不为空
5. `student_feedback` 和 `bad_reason` 枚举值符合 spec

---

## 6. 前端不负责的内容

第一版前端不负责：

- 判断 `mode` 是否分对
- 计算 `mode_match_rate`
- 做复杂聚合报表
- 在线 rubric / gate 判分

这些由后端日志和人工复核承担。
