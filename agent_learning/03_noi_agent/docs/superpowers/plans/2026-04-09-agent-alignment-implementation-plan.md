# AGENT Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align `AGENT.md` with the project's actual current structure, routing model, and harness files without introducing new product rules.

**Architecture:** Keep this change documentation-only and narrowly scoped. Update the top-level workflow rules in `AGENT.md`, then sync the specific long-term rule mismatches in `docs/harness/project_invariants.md` so the repo no longer contains two conflicting sources of truth.

**Tech Stack:** Markdown docs, existing harness conventions

---

### Task 1: Fix AGENT startup and workflow references

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/AGENT.md`

- [ ] **Step 1: Identify stale references that conflict with current repo state**

Check and correct:
- `lessons.md` hard dependency
- missing/obsolete workflow tool names
- outdated student routing description
- outdated version governance file names

- [ ] **Step 2: Update AGENT.md with minimal, current rules**

Apply these content changes:
- keep startup reads to existing harness files only
- replace the `lessons.md` requirement with current harness review guidance
- update student route guidance to match `/app/chat`, `/app/checkin`, `/app/history`, `/app/history/:id`
- update version governance references to the current consolidated file
- keep the “重大改动先方案再实现” rule intact

- [ ] **Step 3: Read the file once for contradictions**

Check that:
- no rule points to a missing file
- no rule conflicts with current route structure
- no rule reintroduces archived doc names

### Task 2: Sync long-term project invariants that AGENT depends on

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/project_invariants.md`

- [ ] **Step 1: Update student information architecture rules**

Adjust the student routing section so it reflects the current page contract:
- `AI 解答`
- `打卡复盘`
- `历史打卡`
- history detail can be addressed by dedicated in-app route

- [ ] **Step 2: Update version governance references**

Replace references to:
- `version_policy.md`
- `version_plan.md`

with the current consolidated governance document:
- `docs/common/version_governance.md`

- [ ] **Step 3: Read the file once for consistency**

Check that:
- long-term rules still describe the current project
- no archived file names remain
- AGENT and invariants now agree on route semantics

### Task 3: Final verification and status sync

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`

- [ ] **Step 1: Verify the exact changed files render as clean Markdown**

Run:
```bash
python3 -m py_compile /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py
```

Expected:
- command succeeds; this is only a quick smoke check that the repo environment is still healthy after doc-only edits

- [ ] **Step 2: Update active work item with this doc-alignment round**

Add a brief note under current risk / next step that:
- AGENT and harness route rules were synchronized
- the next product work should continue on review / knowledge-card quality rather than doc drift

- [ ] **Step 3: Summarize changed files and impact**

Confirm the final changed set is limited to:
- `AGENT.md`
- `docs/harness/project_invariants.md`
- `docs/harness/active_work_item.md`
- this implementation plan file
