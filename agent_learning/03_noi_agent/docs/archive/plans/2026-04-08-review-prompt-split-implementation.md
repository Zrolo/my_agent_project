# Review Prompt Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把当前单个 review prompt 拆成 `normal_review_prompt / clarify_prompt / remedy_prompt` 三类职责明确的 prompt，同时保持前后端协议和 deterministic fallback 稳定。

**Architecture:** 保留第一轮 `generate_review(...)` 的 5 段结构化复盘链路，只把“证据不足的澄清式支架”和“第一轮失败后的解释型补救”从当前 deterministic 文案里升级成独立 prompt。运行时继续由代码负责分流和停止条件，prompt 只负责当前这一轮怎么教。

**Tech Stack:** Python, FastAPI, vanilla JS, unittest, Node test runner

---

### Task 1: 先用失败测试钉住 prompt 拆分接口

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 为 `clarify_prompt` 写失败测试，要求它明确禁止直接讲题**

新增测试，断言新的 `_build_clarify_system_prompt()` 至少包含这些核心约束：

```python
    def test_build_clarify_system_prompt_should_forbid_direct_teaching(self):
        prompt = review_engine._build_clarify_system_prompt()
        self.assertIn("禁止直接讲题", prompt)
        self.assertIn("帮助学生把问题说清楚", prompt)
        self.assertIn("题目要求你求什么", prompt)
        self.assertIn("你试到哪一步", prompt)
```

- [ ] **Step 2: 为 `remedy_prompt` 写失败测试，要求它只缩小一步、不重复第一轮**

新增测试，断言新的 `_build_remedy_system_prompt()` 至少包含这些规则：

```python
    def test_build_remedy_system_prompt_should_require_smaller_step_not_repetition(self):
        prompt = review_engine._build_remedy_system_prompt(review_engine.REMEDY_ACTION_DYNAMIC)
        self.assertIn("不重复第一轮复盘", prompt)
        self.assertIn("只把桥缩小一步", prompt)
        self.assertIn("换一种表示方式", prompt)
        self.assertIn("只能给一个最小动作", prompt)
```

- [ ] **Step 3: 为 `generate_remedy_explanation(...)` 写失败测试，钉住 insufficient -> clarify 路由**

新增测试，mock `_call_llm` 返回 JSON，断言：

```python
    def test_generate_remedy_explanation_should_use_clarify_prompt_for_insufficient(self):
        review_context = {
            "error_layer": "insufficient",
            "bottleneck_text": "我不会这题",
            "main_block": "你还没把具体卡点说清楚。",
        }
        fake_json = '{"remedy_text":"先把题目目标说清楚。","micro_action":"先用一句话说这题要求你求什么。"}'
        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})) as mocked_call:
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertEqual("先把题目目标说清楚。", payload["remedy_text"])
        messages = mocked_call.call_args.args[0]
        self.assertIn("帮助学生把问题说清楚", messages[0]["content"])
```

- [ ] **Step 4: 为 `generate_remedy_explanation(...)` 写失败测试，钉住非 insufficient -> remedy 路由**

新增测试，mock `_call_llm` 返回 JSON，断言：

```python
    def test_generate_remedy_explanation_should_use_remedy_prompt_for_non_insufficient(self):
        review_context = {
            "error_layer": "modeling",
            "bottleneck_text": "我不知道状态该怎么定义。",
            "main_block": "你卡在状态含义没站稳。",
            "key_bridge": "先把每个状态表示的对象写清楚。",
            "next_step": "先写每个状态表示什么。",
        }
        fake_json = '{"remedy_text":"先把状态缩成一维来看。","micro_action":"先说 dp[i] 表示什么。"}'
        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})) as mocked_call:
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertEqual("先把状态缩成一维来看。", payload["remedy_text"])
        messages = mocked_call.call_args.args[0]
        self.assertIn("不重复第一轮复盘", messages[0]["content"])
```

- [ ] **Step 5: 为 fallback 写失败测试，确保 LLM 失败时仍返回 deterministic 文案**

新增测试，断言 LLM 失败时不会抛异常，且仍保留现有字段形状：

```python
    def test_generate_remedy_explanation_should_fallback_when_llm_fails(self):
        review_context = {
            "error_layer": "modeling",
            "bottleneck_text": "我不知道状态怎么定义。",
            "main_block": "你卡在状态没站稳。",
            "next_step": "先写状态含义。",
        }
        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertEqual("explain", payload["remedy_type"])
        self.assertTrue(payload["remedy_text"])
        self.assertTrue(payload["micro_action"])
```

- [ ] **Step 6: 跑聚焦单测，确认先红灯**

Run:
`python3 -m unittest -v test_review_engine_messages_unit.py`

Expected:
- 新增的 clarify/remedy 测试失败
- 失败原因是 builder 不存在或 routing 仍是 deterministic

### Task 2: 在 `review_engine.py` 里拆 prompt builder

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`

- [ ] **Step 1: 保持第一轮 review builder，不直接打散现有 `generate_review(...)`**

只做命名级清理，新增一个轻包装：

```python
def _build_normal_review_system_prompt(mode: str = "independent_reflect") -> str:
    return _build_review_system_prompt(mode=mode)
```

让后续 routing 可以显式区分第一轮和其他轮次，而不影响现有调用。

- [ ] **Step 2: 新增 `clarify_prompt` 的 system/user builder**

在 `review_engine.py` 新增：

```python
def _build_clarify_system_prompt() -> str:
    return \"\"\"你是 NOI 教练。当前任务不是讲题，而是帮助学生把问题说清楚。
如果证据不足，禁止直接讲题、禁止猜方法、禁止展开完整题解。
你只做两件事：
1. 说明当前为什么还不能稳定复盘
2. 给一个最小澄清问题

只输出 JSON：
{
  "remedy_text": "string",
  "micro_action": "string"
}

要求：
- remedy_text 必须说明当前缺少哪类证据
- micro_action 只能问一个问题
- 优先围绕：题目要求求什么 / 试到哪一步 / 具体卡在哪一层
\"\"\".strip()


def _build_clarify_user_prompt(review_context: dict, remedy_action: str) -> str:
    return "\\n".join([
        f"题目：{review_context.get('problem_title', '')}",
        f"题目摘要：{_compact_text(review_context.get('problem_context', ''), 180)}",
        f"学生卡点：{_compact_text(review_context.get('bottleneck_text', ''), 120)}",
        f"当前 error_layer：{review_context.get('error_layer', 'insufficient')}",
        f"补救动作：{remedy_action}",
    ]).strip()
```

- [ ] **Step 3: 新增 `remedy_prompt` 的 system/user builder**

在 `review_engine.py` 新增：

```python
def _build_remedy_system_prompt(remedy_action: str) -> str:
    return f\"\"\"你是 NOI 教练。当前任务是第一轮没过后的解释型补救。
禁止重复第一轮复盘，禁止重讲整题，禁止直接给完整答案。
你只能把当前桥缩小一步，或换一种表示方式，或纠正一个具体误解。
当前补救动作：{remedy_action}

只输出 JSON：
{{
  "remedy_text": "string",
  "micro_action": "string"
}}

要求：
- remedy_text 只服务当前这一小步
- micro_action 只能给一个一步内可回答或执行的小动作
\"\"\".strip()


def _build_remedy_user_prompt(review_context: dict, remedy_action: str) -> str:
    return "\\n".join([
        f"题目：{review_context.get('problem_title', '')}",
        f"核心卡点：{_compact_text(review_context.get('bottleneck_text', ''), 120)}",
        f"problem_focus：{review_context.get('problem_focus') or review_context.get('main_block', '')}",
        f"key_bridge：{review_context.get('key_bridge', '')}",
        f"try_now：{review_context.get('try_now') or review_context.get('next_step', '')}",
        f"补救动作：{remedy_action}",
    ]).strip()
```

- [ ] **Step 4: 新增 remedy payload 解析 helper**

在 `review_engine.py` 新增一个最小 parser：

```python
def _parse_remedy_explanation_payload(content: str) -> dict | None:
    try:
        parsed = json.loads(content)
    except Exception:
        return None
    remedy_text = str(parsed.get("remedy_text", "")).strip()
    micro_action = str(parsed.get("micro_action", "")).strip()
    if not remedy_text or not micro_action:
        return None
    return {
        "remedy_text": remedy_text[:400],
        "micro_action": micro_action[:160],
    }
```

### Task 3: 用新 prompt 改造 `generate_remedy_explanation(...)`

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`

- [ ] **Step 1: 提取当前 deterministic 逻辑为 fallback helper**

把当前 `generate_remedy_explanation(...)` 的正文抽成：

```python
def _generate_remedy_explanation_fallback(review_context: dict, remedy_action: str) -> dict:
    ...
```

要求：
- 返回值保持完全兼容：
  - `remedy_type`
  - `remedy_action`
  - `remedy_text`
  - `micro_action`

- [ ] **Step 2: 在 `generate_remedy_explanation(...)` 里接 clarify/remedy prompt 路由**

目标逻辑：

```python
def generate_remedy_explanation(review_context: dict, remedy_action: str) -> dict:
    error_layer = review_context.get("error_layer", "insufficient")
    if error_layer == "insufficient":
        messages = [
            {"role": "system", "content": _build_clarify_system_prompt()},
            {"role": "user", "content": _build_clarify_user_prompt(review_context, remedy_action)},
        ]
    else:
        messages = [
            {"role": "system", "content": _build_remedy_system_prompt(remedy_action)},
            {"role": "user", "content": _build_remedy_user_prompt(review_context, remedy_action)},
        ]

    ok, content, _telemetry = _call_llm(messages)
    if ok:
        parsed = _parse_remedy_explanation_payload(content)
        if parsed:
            return {
                "remedy_type": "explain",
                "remedy_action": remedy_action,
                **parsed,
            }

    return _generate_remedy_explanation_fallback(review_context, remedy_action)
```

- [ ] **Step 3: 保持 API 和前端完全不感知本次重构**

检查并保证：
- `/api/reviews/{review_id}/remedy` 仍收到同样字段
- `static/app.js` 不需要改协议
- 单轮失败时前端体验保持一致，只是文案来源从 deterministic 变成 prompt + fallback

- [ ] **Step 4: 跑聚焦单测并确认转绿**

Run:
`python3 -m unittest -v test_review_engine_messages_unit.py`

Expected:
- clarify/remedy 新测试全部通过
- 原 review prompt 测试继续通过

### Task 4: 用 API 回归确认 learning flow 没被 prompt split 打断

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py` (仅在需要时补最小覆盖)

- [ ] **Step 1: 补一个 API 层回归，确保 remedy endpoint 仍返回兼容字段**

如果现有测试没有直接覆盖 `/api/reviews/{id}/remedy` 的 payload，就新增：

```python
    def test_remedy_endpoint_keeps_payload_shape_after_prompt_split(self):
        ...
        self.assertEqual("explain", body["mode"])
        self.assertTrue(body["remedy_text"])
        self.assertTrue(body["micro_action"])
```

- [ ] **Step 2: 跑 Python 后端回归**

Run:
`python3 -m unittest -v test_review_async_api_unit.py test_review_engine_messages_unit.py`

Expected:
- 全通过

### Task 5: 默认绿灯与文档收尾

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/specs/2026-04-08-review-prompt-split-design.md` (如实现细节与 spec 有必要微调)

- [ ] **Step 1: 跑默认回归入口**

Run:
`bash /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh`

Expected:
- 默认测试入口全绿

- [ ] **Step 2: 如实现中有必要，把 spec 里关于 fallback 与 builder 命名的小差异补齐**

只做最小文档同步，不扩 scope。
