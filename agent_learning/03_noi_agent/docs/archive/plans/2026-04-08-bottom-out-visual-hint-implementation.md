# Bottom-Out Prompt And Visual Hint Ladder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a third-round `bottom_out_prompt` plus optional `visual_hint` support across first-, second-, and third-round scaffolds without introducing a fourth round.

**Architecture:** Keep the learning-state machine in code and keep prompt responsibility single-purpose. Persist `visual_hint` in canonical review storage, route explanation generations by round (`clarify` / `remedy` / `bottom_out`), and render text-based mini diagrams in both student and teacher views.

**Tech Stack:** Python, FastAPI, SQLite, vanilla JS, Node test runner, unittest

---

### File Map

**Backend prompt / flow**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`

**Frontend render**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/review_family_ui.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/teacher_manual_review_ui.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css`

**Tests**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`

### Task 1: Lock Backend Tests For New Prompt Contracts

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: Write failing tests for `visual_hint` extraction and `bottom_out` routing**

Add tests covering:

```python
def test_build_review_system_prompt_should_request_optional_visual_hint(self):
    prompt = review_engine._build_normal_review_system_prompt(mode="stuck_bridge")
    self.assertIn("visual_hint", prompt)

def test_generate_remedy_explanation_should_use_bottom_out_prompt_after_prior_remedy(self):
    review_context = {
        "problem_title": "P2195 HXY造公园",
        "review_mode": "stuck_bridge",
        "error_layer": "bridge",
        "problem_focus": "你卡在新最长路候选怎么产生",
        "key_bridge": "新最长路只会来自三类候选",
        "guided_walkthrough": "1. 先看左边 2. 再看右边 3. 最后看新边",
        "try_now": "如果经过新边，左边这一端该接什么点？",
        "target_bridge": "新最长路候选来源",
        "remedy_count": 1,
    }
    with patch.object(review_engine, "_call_llm", return_value=json.dumps({
        "remedy_text": "先只看左边这部分。",
        "visual_hint": "左边: A-B-C\\n右边: D-E\\n新边: C-D",
        "micro_action": "现在只回答：左边这一端该接什么点？",
    })) as mock_call:
        payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)
    self.assertIn("visual_hint", payload)
    system_prompt = mock_call.call_args.kwargs["system_prompt"]
    self.assertIn("bottom_out", system_prompt.lower())
```

- [ ] **Step 2: Run focused unittest to verify RED**

Run:
```bash
python3 -m unittest -v test_review_engine_messages_unit.py
```

Expected:
- FAIL on missing `visual_hint` assertions and missing bottom-out routing/assertions

### Task 2: Lock Persistence And API Shape For `visual_hint`

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`

- [ ] **Step 1: Write failing API tests for `visual_hint` in stored reviews**

Add assertions to the existing review persistence test:

```python
self.assertEqual("左边: A-B-C", stored["visual_hint"])
self.assertEqual(stored["visual_hint"], payload["review"]["visual_hint"])
```

Add a new remedy API test for explanation payload:

```python
self.assertIn("visual_hint", remedy_response.json())
self.assertIn("C-D", remedy_response.json()["visual_hint"])
```

- [ ] **Step 2: Run focused unittest to verify RED**

Run:
```bash
python3 -m unittest -v test_review_async_api_unit.py
```

Expected:
- FAIL because DB/API do not persist or return `visual_hint`

### Task 3: Lock Learning-Flow Behavior For Third-Round Bottom-Out

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py`

- [ ] **Step 1: Write failing integration test for second explanation remedy -> bottom-out**

Add a flow test like:

```python
def test_c_second_explanation_remedy_uses_bottom_out_and_returns_visual_hint(self):
    # arrange a review already at remedy_count = 1
    # call /api/reviews/{id}/remedy with action_type=dynamic_bridge_help
    # mock LLM payload with remedy_text + visual_hint + micro_action
    # assert response includes visual_hint
    # assert remedy_count increments
```

- [ ] **Step 2: Run focused unittest to verify RED**

Run:
```bash
python3 -m unittest -v test_learning_flow_api_integration.py
```

Expected:
- FAIL because round-aware bottom-out behavior is not implemented yet

### Task 4: Lock Frontend Rendering For `visual_hint`

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`

- [ ] **Step 1: Write failing frontend tests for field order and labels**

Add tests asserting:

```js
assert.deepEqual(
  reviewFieldOrder('failure_diagnosis'),
  ['problem_focus', 'key_bridge', 'visual_hint', 'guided_walkthrough', 'try_now', 'transfer_signal']
)

assert.equal(reviewFieldLabel('visual_hint'), '看图想一想')
```

Add teacher helper expectations for the same ordering/label.

- [ ] **Step 2: Run focused Node tests to verify RED**

Run:
```bash
node --test test_review_family_ui.mjs test_teacher_manual_review_ui.mjs
```

Expected:
- FAIL on missing `visual_hint` field handling

### Task 5: Implement Backend Prompt Builders And Parsers

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: Add `visual_hint` to first-round review contract**

Implement in the normal review prompt and parse/backfill pipeline:

```python
visual_hint
- 可选字段
- 只在有必要时输出
- 用文本化小图、小表或小分类框帮助学生看清当前桥里的对象和关系
- 禁止输出大段讲义
```

Also update:
- JSON extraction
- canonical normalization
- text fallback parsing
- deterministic backfill defaults

- [ ] **Step 2: Add bottom-out prompt builders**

Implement:

```python
def _build_bottom_out_system_prompt(remedy_action: str) -> str:
    ...

def _build_bottom_out_user_prompt(review_context: dict, remedy_action: str) -> str:
    ...
```

Prompt requirements:
- current-problem worked example
- junior-high-readable language
- optional `visual_hint`
- single `micro_action`
- no full-solution dump

- [ ] **Step 3: Route `generate_remedy_explanation()` by round**

Use:
- `insufficient` -> clarify
- non-insufficient and `remedy_count <= 0` -> remedy
- non-insufficient and `remedy_count >= 1` -> bottom-out

- [ ] **Step 4: Update fallback for bottom-out**

Ensure `_generate_remedy_explanation_fallback(...)` can emit:

```python
{
    "remedy_text": "...",
    "visual_hint": "...",
    "micro_action": "..."
}
```

- [ ] **Step 5: Run focused backend tests to verify GREEN**

Run:
```bash
python3 -m unittest -v test_review_engine_messages_unit.py
```

Expected:
- PASS

### Task 6: Persist And Return `visual_hint`

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`

- [ ] **Step 1: Add DB migration and canonical persistence**

Add migration entry:

```python
("visual_hint", "ALTER TABLE reviews ADD COLUMN visual_hint TEXT")
```

Thread `visual_hint` through:
- `create_review(...)`
- `get_review_by_checkin(...)`
- teacher sample loaders
- review detail/list queries

- [ ] **Step 2: Add API serialization**

Ensure review payloads expose:

```python
"visual_hint": row["visual_hint"] or ""
```

- [ ] **Step 3: Run focused API tests to verify GREEN**

Run:
```bash
python3 -m unittest -v test_review_async_api_unit.py
```

Expected:
- PASS

### Task 7: Render `visual_hint` In Student And Teacher UI

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/review_family_ui.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/teacher_manual_review_ui.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`

- [ ] **Step 1: Add field order and labels**

Insert `visual_hint` between `key_bridge` and `guided_walkthrough`.

Use label:

```js
visual_hint: '看图想一想'
```

- [ ] **Step 2: Render review `visual_hint` as a preformatted mini-diagram block**

Student review/history and teacher sample cards should render:

```html
<pre class="review-visual-hint">...</pre>
```

only when `visual_hint` exists.

- [ ] **Step 3: Render remedy / bottom-out `visual_hint`**

In remedy cards, add a small preformatted visual block before `micro_action`.

- [ ] **Step 4: Add styles**

Add compact monospace styling for:
- review visual hints
- remedy visual hints

Keep them lighter than main prose.

- [ ] **Step 5: Run focused frontend tests to verify GREEN**

Run:
```bash
node --test test_review_family_ui.mjs test_teacher_manual_review_ui.mjs
node --check static/app.js static/review_family_ui.js static/teacher_manual_review_ui.js
```

Expected:
- PASS

### Task 8: Verify End-To-End Learning Flow

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py`

- [ ] **Step 1: Verify round ladder behavior**

Run:
```bash
python3 -m unittest -v test_learning_flow_api_integration.py
```

Expected:
- PASS
- second explanation remedy uses bottom-out
- `visual_hint` returned when present
- final micro confirm still appears after third-round explanation resolve

### Task 9: Run Full Regression

**Files:**
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh`

- [ ] **Step 1: Run Python compile check**

Run:
```bash
python3 -m py_compile /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py
```

Expected:
- no output

- [ ] **Step 2: Run default regression**

Run:
```bash
bash /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh
```

Expected:
- all backend suites pass
- all frontend Node suites pass
- exit code 0

- [ ] **Step 3: Commit**

```bash
git add /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/review_family_ui.js \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/teacher_manual_review_ui.js \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/specs/2026-04-08-bottom-out-visual-hint-design.md \
        /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/plans/2026-04-08-bottom-out-visual-hint-implementation.md
git commit -m "feat: add bottom-out prompt and visual hint ladder"
```
