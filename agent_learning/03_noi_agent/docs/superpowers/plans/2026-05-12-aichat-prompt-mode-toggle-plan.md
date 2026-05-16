# AIChat Prompt Mode Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a student-facing AIChat answer-style switch where `简洁提示` maps to the current production prompt and `教练引导` maps to an enhanced prompt-only guidance layer.

**Architecture:** Keep model selection and answer style independent. The frontend sends `chat_model_provider` for `快速/专业` and `aichat_prompt_mode` for `简洁提示/教练引导`; the backend defaults missing/unknown prompt mode to `current_system` and appends an enhanced guidance block only for `enhanced_prompt_only_clean`.

**Tech Stack:** FastAPI/Pydantic backend, existing `noi_agent.chat()` pipeline, Vue student chat page, Python `unittest`, Node built-in test runner.

---

### Task 1: Backend Contract And Chat Prompt Mode

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_prompt_mode_unit.py`

- [ ] **Step 1: Write failing backend tests**

Add tests that assert:

```python
def test_chat_endpoint_passes_prompt_mode_to_chat():
    # POST /chat with aichat_prompt_mode="enhanced_prompt_only_clean"
    # should call api_server.chat(..., aichat_prompt_mode="enhanced_prompt_only_clean")
    # and return the same prompt mode in ChatResponse.
```

```python
def test_enhanced_prompt_mode_appends_guidance_block_to_system_prompt():
    # noi_agent.chat(..., aichat_prompt_mode="enhanced_prompt_only_clean")
    # should send a system prompt containing "增强教练引导模式" and "不要直接补完整关键桥".
```

Run:

```bash
python3 -m unittest test_aichat_prompt_mode_unit.py
```

Expected: tests fail because `aichat_prompt_mode` is not yet accepted or passed.

- [ ] **Step 2: Implement minimal backend support**

Add:

```python
AIChatPromptMode = Literal["current_system", "enhanced_prompt_only_clean"]
```

Add request/response field:

```python
aichat_prompt_mode: str = Field(default="current_system", description="AIChat 回答方式")
```

Pass the normalized prompt mode into `chat(...)`.

In `noi_agent.chat`, accept:

```python
aichat_prompt_mode: str | None = None
```

If mode is `enhanced_prompt_only_clean`, append a short system guidance block to the existing current prompt. Default and unknown values keep the current prompt unchanged.

- [ ] **Step 3: Verify backend tests pass**

Run:

```bash
python3 -m unittest test_aichat_prompt_mode_unit.py test_aichat_model_switch_unit.py test_aichat_trace_latency_unit.py
```

Expected: all pass.

### Task 2: Frontend Answer-Style Switch

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/pages/student/ChatPage.vue`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_student_entry_ui.mjs`

- [ ] **Step 1: Write failing frontend test**

Add assertions that `ChatPage.vue` contains:

```javascript
const CHAT_PROMPT_MODE_STORAGE_KEY = 'noi-agent-chat-prompt-mode';
```

and that the chat payload includes:

```javascript
aichat_prompt_mode: selectedChatPromptMode.value
```

Run:

```bash
node --test test_student_entry_ui.mjs
```

Expected: fails because the UI switch and payload field do not exist.

- [ ] **Step 2: Implement UI switch**

Add local storage state:

```javascript
const CHAT_PROMPT_MODE_STORAGE_KEY = 'noi-agent-chat-prompt-mode';
const CHAT_PROMPT_MODE_OPTIONS = [
  { value: 'current_system', label: '简洁提示', description: '沿用当前回答方式，适合小问题和局部确认。' },
  { value: 'enhanced_prompt_only_clean', label: '教练引导', description: '更偏启发提问和小例子，适合真正卡住时使用。' },
];
const selectedChatPromptMode = ref(window.localStorage.getItem(CHAT_PROMPT_MODE_STORAGE_KEY) || 'current_system');
```

Add segmented buttons near the model selector with label:

```text
回答方式：简洁提示 / 教练引导
```

Add `aichat_prompt_mode: selectedChatPromptMode.value` to `sendChat(...)`.

- [ ] **Step 3: Verify frontend tests pass**

Run:

```bash
node --test test_student_entry_ui.mjs
```

Expected: pass.

### Task 3: Combined Verification

**Files:**
- No new files.

- [ ] **Step 1: Run targeted tests**

Run:

```bash
python3 -m unittest test_aichat_prompt_mode_unit.py test_aichat_model_switch_unit.py test_aichat_trace_latency_unit.py
node --test test_student_entry_ui.mjs
```

Expected: all pass.

- [ ] **Step 2: Inspect changed files**

Run:

```bash
git diff -- api_server.py noi_agent.py frontend/src/pages/student/ChatPage.vue test_aichat_prompt_mode_unit.py test_student_entry_ui.mjs docs/superpowers/plans/2026-05-12-aichat-prompt-mode-toggle-plan.md
```

Expected: only the prompt mode toggle, tests, and this plan changed.
