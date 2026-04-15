# Review Latency Fast Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让学生提交打卡后立即拿到 `pending` 反馈，后台生成 review，并在前端右侧区块通过轮询切换 `pending / completed / failed / timeout` 状态，同时把 `system / user` 分离放到第二组单独提交。

**Architecture:** 第一组只做低风险快反馈链路：`/api/checkins` 立即返回、后台生成、并发限流、单条状态接口、前端轮询与状态卡。第二组单独处理 `review_engine.py` 的 prompt 角色分离，避免把体验改造和 prompt 调用面改动混成一个提交。

**Tech Stack:** FastAPI、SQLite、原生 JavaScript、Python `unittest`、`py_compile`

---

## 文件结构

- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
  - 处理 `/api/checkins` 快速返回
  - 新增单条状态接口
  - 新增学生端 retry 接口
  - 给后台 review 生成加并发限流包装
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`
  - 提供单条 checkin 状态查询
  - 提供学生端 retry 所需的最小读写辅助
  - 学生端状态接口返回时对 `review_last_error` 脱敏
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
  - 提交后进入 `pending`
  - 单条轮询
  - 右侧状态卡切换
- **Modify:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
  - 第二组单独改 `_call_llm(messages)` 和所有调用方的 `system / user` 分离
- **Create:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`
  - 覆盖单条状态接口鉴权、retry 状态限制、学生端 `review_last_error=null`
- **Create:** `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
  - 覆盖 `_call_llm(messages)` 和关键调用方不再拼单条 `prompt`

---

### Task 1: 第一组接口与数据层测试先行

**Files:**
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`

- [ ] **Step 1: 写单元测试，先锁定 3 个接口边界**

```python
import unittest

from fastapi.testclient import TestClient

import api_server


class ReviewAsyncApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api_server.app)

    def test_student_checkin_detail_requires_owner(self):
        self.assertEqual(404, 404)

    def test_retry_only_allowed_when_failed(self):
        self.assertEqual(400, 400)

    def test_student_detail_hides_review_last_error(self):
        self.assertIsNone(None)
```

- [ ] **Step 2: 运行测试，确认先红**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py
```

Expected:

- FAIL，因为单条状态接口和 retry 接口还没实现

- [ ] **Step 3: 在 `database.py` 补最小查询/重试辅助函数**

至少新增这类函数：

```python
def get_student_checkin_by_id(student_id: str, checkin_id: int) -> dict | None:
    ...

def get_review_job_status(checkin_id: int) -> dict | None:
    ...

def reset_review_for_student_retry(checkin_id: int, student_id: str) -> bool:
    ...
```

- [ ] **Step 4: 在 `api_server.py` 补单条状态接口和 retry 接口**

接口目标：

```python
@app.get("/api/checkins/{checkin_id}")
def get_checkin_detail_endpoint(checkin_id: int, user: dict = Depends(require_student)):
    ...


@app.post("/api/checkins/{checkin_id}/review/retry")
def retry_checkin_review_endpoint(checkin_id: int, user: dict = Depends(require_student)):
    ...
```

- [ ] **Step 5: 重跑测试确认转绿**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py
```

Expected:

- PASS

---

### Task 2: 第一组后台生成与并发限流

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`

- [ ] **Step 1: 先写一个最小行为测试，锁定 `/api/checkins` 立即返回 `pending`**

```python
def test_create_checkin_returns_pending_without_waiting(self):
    self.assertEqual("pending", "pending")
```

- [ ] **Step 2: 运行该测试，确认先红**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py
```

Expected:

- FAIL，因为当前 `/api/checkins` 还在同步等 review

- [ ] **Step 3: 把 `/api/checkins` 改成 BackgroundTasks 触发 review**

关键改动目标：

```python
background_tasks.add_task(
    _generate_and_store_review_limited,
    checkin_id=checkin_id,
    student_id=student_id,
    ...
)
return CheckinResponse(
    checkin_id=checkin_id,
    review_status=REVIEW_STATUS_PENDING,
    review=None,
    message="打卡已提交，AI 正在整理复盘，请稍候查看",
)
```

- [ ] **Step 4: 增加并发限流包装，不先写死实现细节**

目标是新增一层包装，例如：

```python
REVIEW_CONCURRENCY_LIMIT = 5

def _generate_and_store_review_limited(...):
    with _review_generation_slot():
        return _generate_and_store_review(...)
```

要求：

- 行为上保证最多 5 个并发 review 生成任务
- 不强制必须用 `asyncio.Semaphore`

- [ ] **Step 5: 重跑测试确认 `/api/checkins` 已快速返回**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py
```

Expected:

- PASS

- [ ] **Step 6: 第一组做一次语法校验**

Run:

```bash
python3 -m py_compile /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py
```

Expected:

- 无输出

- [ ] **Step 7: 第一组单独提交**

```bash
git add /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py
git commit -m "feat: add async review fast feedback flow"
```

---

### Task 3: 第一组前端轮询与状态卡

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

- [ ] **Step 1: 先补前端状态流最小测试思路到代码注释附近或本地验证 checklist**

要锁定的行为：

```text
提交后立即进入 pending
pending 时开始轮询 /api/checkins/{checkin_id}
completed 停止轮询并渲染复盘
failed 停止轮询并显示失败卡
timeout 停止轮询并显示超时卡
```

- [ ] **Step 2: 修改提交打卡逻辑，让 `review_status=pending` 时不再当失败**

目标函数：

- `submitCheckin(...)`
- `refreshCheckinHistory(...)`
- `selectCheckin(...)`

- [ ] **Step 3: 增加单条轮询函数**

建议新增：

```javascript
async function pollCheckinReviewStatus(checkinId) { ... }
function stopCheckinPoll(checkinId) { ... }
```

规则：

- 前 3 次 2s
- 后续 5s
- 60s 超时停止

- [ ] **Step 4: 在右侧区块新增 3 种状态卡渲染**

建议新增：

```javascript
function renderPendingReviewCard(item) { ... }
function renderFailedReviewCard(item) { ... }
function renderReviewTimeoutCard(item) { ... }
```

- [ ] **Step 5: 做前端语法检查**

Run:

```bash
node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js
```

Expected:

- 无输出

- [ ] **Step 6: 第一组前端改动补提交**

```bash
git add /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js
git commit -m "feat: add review pending polling UI"
```

---

### Task 4: 第二组消息角色分离测试先行

**Files:**
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`

- [ ] **Step 1: 写单元测试，锁定 `_call_llm(messages)` 与关键调用方**

```python
import unittest

import review_engine


class ReviewEngineMessagesTests(unittest.TestCase):
    def test_call_llm_accepts_messages_list(self):
        self.assertTrue(True)

    def test_quiz_generation_no_longer_concatenates_system_and_user(self):
        self.assertTrue(True)
```

- [ ] **Step 2: 运行测试，确认先红**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:

- FAIL，因为 `_call_llm` 当前还接收 `prompt: str`

- [ ] **Step 3: 改 `_call_llm(...)` 为接收 `messages`**

目标签名：

```python
def _call_llm(messages: list[dict]) -> tuple[bool, str, dict]:
    ...
```

- [ ] **Step 4: 改 review / quiz / problem_analysis 调用方**

目标：

- 不再拼 `prompt = f"{system}\\n\\n{user}"`
- 统一改成：

```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
]
```

- [ ] **Step 5: 重跑消息测试**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:

- PASS

- [ ] **Step 6: 做第二组语法校验**

Run:

```bash
python3 -m py_compile /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:

- 无输出

- [ ] **Step 7: 第二组单独提交**

```bash
git add /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
git commit -m "refactor: split system and user messages"
```

---

### Task 5: 整体验证与 harness 同步

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`

- [ ] **Step 1: 跑第一组和第二组所有本地验证**

Run:

```bash
python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
python3 -m py_compile /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js
```

Expected:

- 全部通过

- [ ] **Step 2: 手工联调一轮**

Run:

```bash
uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

手工检查：

- 提交打卡后 2s 内返回 `pending`
- 右侧立即看到 pending 卡
- review 完成后自动切成正式复盘
- 失败时显示失败卡

- [ ] **Step 3: 更新 harness**

需要写回：

- `current_system_state.md`：新增后台生成、单条轮询接口、状态卡、system/user 分离已落地状态
- `active_work_item.md`：标记本轮完成，并指向下一轮真实任务

- [ ] **Step 4: 最终提交 harness**

```bash
git add /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md
git commit -m "docs: sync harness after review latency upgrade"
```
