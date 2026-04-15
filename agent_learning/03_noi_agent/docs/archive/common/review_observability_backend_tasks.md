# Review 上线观测后端任务单

这份任务单面向后端开发，目标是把 review 主链路的结构化观测接到现有 API 和数据层里。

关联文档：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_spec.md`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_backend_checklist.md`

---

## 1. 当前代码接入点

### 1.1 checkin 创建入口

文件：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`

接口：
- `POST /api/checkins`

位置：
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py:1307`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/api_server.py#L1307)

作用：
- 校验学生输入
- 创建 checkin
- 启动 review 生成线程

这个接口是 `session_id` 串联和请求级元数据入库的第一接入点。
第一阶段默认 `session_id` 与一次 checkin / 一次 review 会话 1:1 对应。

### 1.2 review 生成主链

文件：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`

函数：
- `_generate_and_store_review(...)`

位置：
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py:940`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/api_server.py#L940)

作用：
- 调用 `generate_review`
- 记录 runtime status
- 写 `review_sessions`
- 写最终 `reviews`

这里是 `review_generated` 的最佳接入点。

### 1.3 SSE 状态流

文件：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`

接口：
- `GET /api/checkins/{checkin_id}/stream`

位置：
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py:1458`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/api_server.py#L1458)

作用：
- 输出 `status / review_ready / error / review_chunk / keepalive`

第一版不要求把线上埋点直接塞进 SSE，但这个接口会影响前端 `review_shown` 的触发时机。

### 1.4 数据层

文件：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`

关键函数：
- `create_checkin(...)`
  - [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py:378`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/database.py#L378)
- `create_review_session(...)`
  - [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py:812`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/database.py#L812)
- `create_pending_review(...)`
  - [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py:1066`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/database.py#L1066)

作用：
- 持久化输入
- 持久化 review 生成时延和模型信息
- 持久化 review 状态

---

## 2. 任务拆分

### 任务 B1：确定 `session_id` 来源并贯通

目标：
- 明确 `session_id` 由谁生成
- 保证 `POST /api/checkins`、`review_generated` 日志、前端事件、人工复核能用同一标识对齐

建议：
- 若当前学生端已有 `sessionId`，优先允许前端显式上传
- 后端可在缺失时补生成，但必须回传

### 任务 B2：补 `review_generated` 结构化日志

目标：
- 在 `_generate_and_store_review(...)` 中，当 review JSON 成功且四字段齐全后，记录一条结构化日志或入库事件

推荐接入点：
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py:980`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/api_server.py#L980)
- [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py:1005`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/api_server.py#L1005)

验收：
- 每次成功 review 都有一条 `review_generated`
- `review_mode / review_json_ok / review_fields_ok / total_latency_ms` 齐全

### 任务 B3：补输入侧元数据持久化

目标：
- 确保 `has_code / problem_context_length / bottleneck_text_length / completion_status / submission_result` 可稳定提取

推荐接入点：
- checkin 创建时：
  - [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py:1377`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/api_server.py#L1377)
- 持久化函数：
  - [`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py:378`](\/Users\/kongyouli\/Downloads\/my_agent_project\/agent_learning\/03_noi_agent\/database.py#L378)

### 任务 B4：决定日志落点

目标：
- 第一版明确使用哪种形态记录 `review_generated`

推荐优先级：
1. JSON Line 文件
2. SQLite 新表
3. 外部埋点平台

建议：
- 第一版优先选 JSON Line 或 SQLite，先保证稳定可读

---

## 3. 后端建议实现顺序

1. B1
2. B2
3. B3
4. B4

---

## 4. 后端联调验收

上线前至少确认：

1. 每次成功 review 都有 `review_generated`
2. `session_id` 可与前端事件对齐
3. `review_json_ok / review_fields_ok / total_latency_ms` 不为空
4. `review_mode` 与实际 prompt 路由一致
