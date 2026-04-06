# Review 上线观测后端接入清单

这份清单给后端开发使用，目标是保证每条 review 都有结构化生成日志，且能和前端反馈、人工复核对齐。

关联文档：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_spec.md`

---

## 1. 目标

后端侧第一版只做两件事：

1. 为每次成功生成的 review 写结构化日志。
2. 用统一的 `session_id` 串起前后端和人工复核。
   `session_id` 第一阶段与一次 checkin / 一次 review 会话 1:1 对应。

后端不是第一版看板的实现方，但必须提供足够稳定的底层字段。

---

## 2. 需要接入的事件

### 2.1 `review_generated`

触发时机：
- review JSON 解析成功，且学生端核心字段齐全后记录。

必填字段：

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

---

## 3. 字段实现说明

### 3.1 必须稳定的字段

#### `session_id`
- 必须唯一。
- 必须能和前端事件、人工复核一一对齐。

#### `review_mode`
- 使用实际进入 review prompt 的 mode。
- 不要记录“候选 mode”或“默认 mode”。

#### `review_json_ok`
- 只表示输出是否是合法 JSON。

#### `review_fields_ok`
- 只表示学生端核心字段是否齐：
  - `main_block`
  - `key_bridge`
  - `next_step`
  - `transfer_signal`

#### `total_latency_ms`
- 从后端收到生成请求到 review 结构完成可返回为止。
- 不能混用前端展示耗时。

### 3.2 建议补充但非阻塞字段

若接入成本可接受，建议同步补：

```json
{
  "has_problem_title": true,
  "has_problem_context": true,
  "mode_source": "explicit | inferred",
  "streaming_used": true,
  "error_code": "string"
}
```

这些字段第一版不是上线阻塞项，但后续排查会很有价值。

---

## 4. 推荐日志形态

建议统一写 JSON Line，每条一行，便于后续导入分析。

示例：

```json
{"event":"review_generated","session_id":"abc","review_mode":"independent_reflect","review_json_ok":true,"review_fields_ok":true,"total_latency_ms":11840}
```

不建议第一版就拆复杂表结构，先保证日志稳定和字段一致。

---

## 5. 联调验收

后端接入完成后，至少确认：

1. 每次成功生成 review 都有一条 `review_generated`
2. `session_id` 与前端上报一致
3. `review_mode` 与实际 prompt 路由一致
4. `review_json_ok / review_fields_ok / total_latency_ms` 不为空
5. `main_block_length / key_bridge_length / next_step_length / transfer_signal_length` 有值

---

## 6. 后端不负责的内容

第一版后端不负责：

- 学生“看懂/没看懂”的按钮交互
- 差评原因采集
- 人工标注界面
- 最终看板展示

这些由前端和复核流程承担。
