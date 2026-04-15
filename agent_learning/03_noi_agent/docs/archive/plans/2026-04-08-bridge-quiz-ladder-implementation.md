# Bridge Quiz Ladder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为讲解型补救增加第三轮 `final_micro_confirm`，并把三轮 quiz 的终局语义与 `mastery_status` 对齐。

**Architecture:** 保持现有 `main / followup / remedy` 学习流不大改，只在讲解型 remedy 的收尾路径上插入一个最终最小确认题。前端只新增一个新 `next_state` 分支，后端复用现有 `QUIZ_ROLE_REMEDY` 终局逻辑。

**Tech Stack:** FastAPI, SQLite, vanilla JS, unittest, Node test runner

---

### Task 1: 先写学习流回归测试

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_learning_flow_api_integration.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`

- [ ] **Step 1: 写一个失败中的集成测试，覆盖“讲解型 remedy 后先出 final micro-confirm，再终局”**

测试要覆盖：
- `POST /api/reviews/{id}/remedy` with `dynamic_bridge_help` 返回 `mode=explain`
- `POST /api/reviews/{id}/remedy/resolve` with `resolved` 不再直接 resolved，而是返回一个 quiz
- 该 quiz 正确提交后，最终 `mastery_status = assisted_success`

- [ ] **Step 2: 跑该测试，确认当前实现失败**

Run: `python3 -m unittest -v test_learning_flow_api_integration.py`
Expected: 现有 `test_a_route_from_checkin_to_remedy_resolve` 或新增测试失败，因为当前 `remedy/resolve` 直接返回 `resolved`

- [ ] **Step 3: 补一个 API 层单测，确保新的 `next_state` 和 quiz 序列化稳定**

覆盖：
- `remedy/resolve` 返回：
  - `learning_status = quiz_in_progress`
  - `next_state = final_micro_confirm`
  - `quiz.quiz_role = remedy`
  - `quiz.round = 3`

- [ ] **Step 4: 跑 API 单测，确认也先失败**

Run: `python3 -m unittest -v test_review_async_api_unit.py`
Expected: 新断言失败

### Task 2: 后端接入 final micro-confirm

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`

- [ ] **Step 1: 在 `remedy_resolve_endpoint` 里改“resolved”分支**

行为改成：
- 不再直接 `finalize_review_terminal_state(..., resolved)`
- 先调用 `generate_bridge_quiz(..., quiz_role=QUIZ_ROLE_REMEDY)`
- 如果成功，创建 round=3、role=`remedy` 的 quiz，返回：
  - `ok = True`
  - `learning_status = quiz_in_progress`
  - `next_state = final_micro_confirm`
  - `quiz = serialize_quiz(...)`

- [ ] **Step 2: 为无法稳定出 final micro-confirm 的情况保留保守 fallback**

如果 `generate_bridge_quiz(..., remedy)` 返回非 `quiz`：
- 沿用当前老行为，直接 `resolved`
- 保持现有终局逻辑不崩

- [ ] **Step 3: 保持现有 round 语义**

创建 final quiz 时：
- `round = MAX_SCAFFOLD_ROUNDS`
- `quiz_role = QUIZ_ROLE_REMEDY`
- `target_bridge` 继续沿用当前 review 的桥

- [ ] **Step 4: 跑后端测试并确认通过**

Run:
- `python3 -m unittest -v test_learning_flow_api_integration.py`
- `python3 -m unittest -v test_review_async_api_unit.py`

Expected: 全通过

### Task 3: 前端接 final micro-confirm

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

- [ ] **Step 1: 调整讲解型 remedy 的 CTA**

把解释卡里的 `我懂了` 改成更贴当前行为的文案，例如：
- `我来试最后一题`

避免点击后突然出现 quiz 的心智落差。

- [ ] **Step 2: 在 `resolveRemedy()` 里接 `next_state = final_micro_confirm`**

收到该状态时：
- 渲染一个轻量成功过渡文案
- 紧接 `renderQuizCard(data.quiz, reviewId)`

不要直接把容器替换成 resolved 结束态。

- [ ] **Step 3: 保持其他状态兼容**

`resolveRemedy()` 仍需兼容：
- `resolved`
- `needs_teacher_followup`

- [ ] **Step 4: 跑前端测试与语法检查**

Run:
- `node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

### Task 4: 补前端/回归测试

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs` (如需 badge 文案验证)
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_checkin_review_ui.mjs`

- [ ] **Step 1: 增加前端状态测试**

覆盖：
- `resolveRemedy` 收到 `final_micro_confirm` 后会渲染 quiz
- 不会错误落到 resolved 结束态

- [ ] **Step 2: 跑 Node 测试**

Run:
- `node --test /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_checkin_review_ui.mjs /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`

### Task 5: 终局回归

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/specs/2026-04-08-three-round-scaffold-ladder-design.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/specs/2026-04-08-bridge-quiz-ladder-design.md`

- [ ] **Step 1: 文档对齐最终行为**

明确写入：
- 讲解型 remedy 后先出 `final_micro_confirm`
- 第 3 轮 quiz 无论对错都终局

- [ ] **Step 2: 跑默认回归**

Run: `bash /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh`
Expected: 全绿
