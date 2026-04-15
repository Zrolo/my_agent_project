# Review 上线观测前端任务单

这份任务单面向前端开发，目标是把上线观测埋点接到现有学生端流程里。

关联文档：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_spec.md`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_frontend_checklist.md`

---

## 1. 当前代码接入点

### 1.1 提交打卡入口

文件：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

函数：
- `submitCheckin()`

位置：
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js:2034`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/static\/app.js#L2034)

作用：
- 收集学生输入
- 调用 `POST /api/checkins`
- 构造本地 `draftItem`
- 根据返回结果进入 pending 或 completed 流程

这里是 `review_request_submitted` 的最佳接入点。

### 1.2 review 展示完成

文件：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

函数：
- `subscribeCheckinReviewStream(...)`
- `pollCheckinReviewStatus(...)`

关键位置：
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js:1200`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/static\/app.js#L1200)
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js:1283`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/static\/app.js#L1283)

作用：
- SSE 收到 `review_ready`
- 或轮询拿到 `review_status === completed`
- 然后刷新工作区

这里是 `review_shown` 的最佳接入点。

### 1.3 学生反馈入口

当前状态：
- 现有页面已有 quiz 自评按钮，但还没有针对 review 本身的“看懂/没看懂”反馈事件。

建议落点：
- 在 review 工作区渲染完成后，新增一组 review 反馈按钮
- 按钮点击后发 `review_feedback_submitted`

推荐挂载区域：
- `renderActiveCheckinWorkspace(item)` 渲染出的 review 右侧区域
- 文件位置可从 [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js:522`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/static\/app.js#L522) 一带往下看 `renderActiveCheckinWorkspace`

---

## 2. 任务拆分

### 任务 F1：接 `review_request_submitted`

目标：
- 学生点击提交并成功发出 `/api/checkins` 请求后，发一条埋点事件。

改动位置：
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js:2114`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/static\/app.js#L2114)

验收：
- 每次提交成功都有事件
- `session_id`、`problem_title`、`review_mode`、`has_code`、长度字段齐全

### 任务 F2：接 `review_shown`

目标：
- review 真正展示到学生界面时发一条埋点事件。

改动位置：
- SSE 成功路径：
  - [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js:1200`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/static\/app.js#L1200)
- 轮询成功路径：
  - [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js:1283`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/static\/app.js#L1283)

验收：
- 无论 SSE 还是轮询完成，最终都只发一次 `review_shown`
- `latency_ms` 不为空

### 任务 F3：新增 review 反馈 UI

目标：
- 在 review 区域新增：
  - `看懂了`
  - `一般`
  - `没看懂`
- 若点 `没看懂`，再出现差评原因二级选项

改动位置：
- `renderActiveCheckinWorkspace(item)` 所在区域
- 建议新增一个单独的 `renderReviewFeedbackPanel(item)`，避免把主渲染函数继续做大

验收：
- 学生能完成一次 feedback 提交
- `bad_reason` 只在 `confused` 时出现

### 任务 F4：接 `review_feedback_submitted`

目标：
- review 反馈提交时发送事件

依赖：
- 先完成 F3

验收：
- 三档反馈都能上报
- `followup_clicked` 与 `followup_question_count` 字段有值

---

## 3. 前端建议实现顺序

1. F1
2. F2
3. F3
4. F4

---

## 4. 前端联调验收

上线前至少确认：

1. 一次正常 review 流程包含：
   - `review_request_submitted`
   - `review_shown`
2. 学生点反馈后包含：
   - `review_feedback_submitted`
3. 同一条 session 的三个事件 `session_id` 一致
4. SSE 和轮询都不会重复上报 `review_shown`
