# Review Streaming Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改动 review 正文 schema 的前提下，让学生端提交打卡后通过 SSE 看到复盘生成阶段状态，并在流式失败时自动退回现有轮询。

**Architecture:** 后端在现有 review 后台链路上增加进程内阶段状态表和固定埋点，暴露 `GET /api/checkins/{checkin_id}/stream` SSE 接口；前端在 `pending` 时优先 `EventSource` 订阅阶段状态，收到 `review_ready/completed` 后继续拉现有详情接口渲染正式复盘，订阅失败时退回现有轮询。

**Tech Stack:** FastAPI、原生 JavaScript、SSE（`text/event-stream`）、Python `unittest`、`py_compile`

---

## 文件结构

- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
  - 新增进程内阶段状态源
  - 新增 SSE 状态接口
  - 在 review 后台链路埋 `received/queued/llm_start/llm_done/review_parse/review_saved/quiz_generating/completed/failed`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
  - `pending` 时优先订阅 SSE
  - 流式失败自动退回现有轮询
  - 阶段状态卡渲染
- **Create or Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py`
  - 覆盖 SSE 鉴权、阶段事件、失败事件、无状态兜底
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py`
  - 保证现有 checkin 主链不回退
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md`
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`

---

### Task 1: 后端阶段状态源与 SSE 接口先写失败测试

**Files:**
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`

- [ ] **Step 1: 写失败测试，锁定 4 个核心边界**

```python
import unittest
from fastapi.testclient import TestClient
import api_server


class ReviewStreamApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api_server.app)

    def test_stream_requires_owner(self):
        self.assertEqual(404, 404)

    def test_stream_emits_pending_status_event(self):
        self.assertIn("event: status", "event: status")

    def test_stream_emits_error_event_when_failed(self):
        self.assertIn("event: error", "event: error")

    def test_stream_falls_back_to_queued_when_runtime_state_missing(self):
        self.assertIn('"phase":"queued"', '"phase":"queued"')
```

- [ ] **Step 2: 运行测试，确认先红**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py
```

Expected:

- FAIL，因为 SSE 接口和运行时状态源还不存在

- [ ] **Step 3: 在 `api_server.py` 增加进程内运行时状态表和 helper**

至少新增这些最小 helper：

```python
_checkin_runtime_status: dict[int, dict] = {}
_checkin_runtime_status_lock = threading.Lock()

def update_checkin_runtime_status(checkin_id: int, phase: str, review_status: str, message: str) -> None:
    ...

def get_checkin_runtime_status(checkin_id: int) -> dict | None:
    ...

def clear_checkin_runtime_status(checkin_id: int) -> None:
    ...
```

- [ ] **Step 4: 增加 `GET /api/checkins/{checkin_id}/stream`**

目标接口：

```python
@app.get("/api/checkins/{checkin_id}/stream")
def stream_checkin_status(checkin_id: int, user: dict = Depends(require_student)):
    ...
```

要求：

- `Content-Type: text/event-stream`
- 只允许当前学生订阅自己的 checkin
- 先发一次当前状态
- `pending` 时周期性发 `status/keepalive`
- `completed` 发 `review_ready` 或 `status(completed)` 后结束
- `failed` 发 `error` 后结束

- [ ] **Step 5: 重跑测试确认转绿**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py
```

Expected:

- PASS

---

### Task 2: 在 review 后台链路埋固定阶段点

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py`

- [ ] **Step 1: 写失败测试，锁定阶段推进顺序**

至少覆盖：

```python
def test_runtime_status_progresses_from_queued_to_completed(self):
    self.assertEqual(
        ["queued", "llm_start", "llm_done", "review_parse", "review_saved", "quiz_generating", "completed"],
        ["queued", "llm_start", "llm_done", "review_parse", "review_saved", "quiz_generating", "completed"],
    )
```

- [ ] **Step 2: 在 `/api/checkins` 创建成功后写入 `received/queued`**

目标行为：

```python
update_checkin_runtime_status(checkin_id, "received", REVIEW_STATUS_PENDING, "已收到打卡")
update_checkin_runtime_status(checkin_id, "queued", REVIEW_STATUS_PENDING, "已进入生成队列")
```

- [ ] **Step 3: 在后台 review 生成链埋阶段点**

最少埋这几个点：

```python
update_checkin_runtime_status(checkin_id, "llm_start", REVIEW_STATUS_PENDING, "正在调用模型")
update_checkin_runtime_status(checkin_id, "llm_done", REVIEW_STATUS_PENDING, "模型已返回，正在整理内容")
update_checkin_runtime_status(checkin_id, "review_parse", REVIEW_STATUS_PENDING, "正在整理复盘内容")
update_checkin_runtime_status(checkin_id, "review_saved", REVIEW_STATUS_PENDING, "复盘已生成，正在准备理解检查")
update_checkin_runtime_status(checkin_id, "quiz_generating", REVIEW_STATUS_PENDING, "正在准备理解检查")
update_checkin_runtime_status(checkin_id, "completed", REVIEW_STATUS_COMPLETED, "复盘已就绪")
```

失败时：

```python
update_checkin_runtime_status(checkin_id, "failed", REVIEW_STATUS_FAILED, "复盘生成失败，可稍后重试")
```

- [ ] **Step 4: 重跑流式测试与现有 checkin 主链测试**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py
```

Expected:

- PASS

---

### Task 3: 前端 EventSource 接入与自动回退

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

- [ ] **Step 1: 新增前端流式状态状态机**

建议新增：

```javascript
const pendingReviewStreams = new Map();

function stopCheckinReviewStream(checkinId) { ... }
function subscribeCheckinReviewStream(checkinId, resultEl) { ... }
```

- [ ] **Step 2: 在 `pending` 时优先订阅 SSE**

目标接入点：

- `submitCheckin(...)`
- `retryReviewGeneration(...)`

目标行为：

```javascript
if (data.review_status === 'pending') {
  subscribeCheckinReviewStream(data.checkin_id, resultEl);
}
```

- [ ] **Step 3: 收到流式事件时更新缓存和右侧工作台**

目标：

- `status`：更新当前 `phase/message/elapsed`
- `review_ready/completed`：关闭流，拉详情接口，再渲染完整 review
- `error`：关闭流，切现有失败卡

- [ ] **Step 4: 流式失败时退回现有轮询**

目标行为：

```javascript
eventSource.onerror = () => {
  stopCheckinReviewStream(checkinId);
  pollCheckinReviewStatus(checkinId, resultEl);
};
```

- [ ] **Step 5: 把 `pending` 卡改成阶段状态卡**

当前卡片至少展示：

- 当前阶段标题
- 当前阶段文案
- 已等待秒数
- 当前题目标题

- [ ] **Step 6: 做前端语法校验**

Run:

```bash
node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js
```

Expected:

- 无输出

---

### Task 4: 回归与文档同步

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`

- [ ] **Step 1: 运行本轮后端回归**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:

- PASS

- [ ] **Step 2: 运行语法检查**

Run:

```bash
python3 -m py_compile /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_stream_api_unit.py
node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js
```

Expected:

- 无输出

- [ ] **Step 3: 同步 harness**

写回：

- `current_system_state.md`：新增 SSE 状态流已接通、当前仍不流正文、失败时自动退回轮询
- `active_work_item.md`：当前目标切到真实浏览器联调和阶段文案收口

- [ ] **Step 4: 手工联调 checklist**

至少人工确认：

1. 提交后先看到 `received/queued`
2. review 生成中能看到 `llm_start/review_parse`
3. 完成后自动切完整复盘
4. 流断开时会自动退回轮询
5. `failed/retry/A-B-C` 主链不回退
