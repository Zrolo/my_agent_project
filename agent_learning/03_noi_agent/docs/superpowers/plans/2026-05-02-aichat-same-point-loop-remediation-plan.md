# AIChat Same-Point Loop Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent AIChat from endlessly asking questions when a student is stuck on the same small point; provide half-step scaffolding or localized teaching, and only offer review/checkin when understanding evidence exists.

**Architecture:** Extend the existing AIChat control plane rather than adding a new LLM call. Reuse current progress and stuck-signal helpers, add a small same-point loop detector and an understanding-evidence gate, then route to existing tutor actions (`give_micro_scaffold`, `give_micro_example`, `offer_checkin_reflection`).

**Tech Stack:** Python, unittest/pytest, existing `noi_agent.py` runtime policy tests.

---

### Task 1: Add Regression Tests

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_runtime_policy_unit.py`

- [ ] Add tests for:
  - 2-3 turn same-point stuck loop routes to `give_micro_scaffold`.
  - Repeated evidence-seeking plus frustration routes to `give_micro_scaffold`.
  - First-turn vague ask does not route to `give_micro_scaffold`.
  - New reasoning progress does not trigger loop protection.
  - 4+ turns stuck without understanding evidence routes to `give_micro_example`, not checkin.
  - 4+ turns stuck with understanding evidence routes to `offer_checkin_reflection`.

- [ ] Run focused tests and verify the new tests fail for the expected behavior gaps.

### Task 2: Implement Loop Detection And Evidence Gate

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`

- [ ] Add evidence-seeking and frustration keyword helpers.
- [ ] Add `_has_same_small_gap_loop(messages) -> tuple[bool, str]`.
- [ ] Add `_has_understanding_evidence(messages) -> bool`, reusing `evaluate_understanding_evidence` and existing progress/debug signals.
- [ ] Update `_select_tutor_control`:
  - State 2 loop -> `give_micro_scaffold`.
  - State 3 4+ stuck without evidence -> `give_micro_example`.
  - State 4 4+ stuck with evidence -> `offer_checkin_reflection`.
- [ ] Update allowed-help text for `give_micro_scaffold` and state-3 `give_micro_example`.

### Task 3: Update Judge Prompt Guidance

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/aichat_pedagogical_judge_v2_system_prompt.md`

- [ ] Add same-point loop guidance under `give_micro_scaffold`.
- [ ] Do not change judge schema or add actions.

### Task 4: Verify

**Commands:**
- `.venv/bin/python -m pytest test_aichat_runtime_policy_unit.py -q`
- `.venv/bin/python -m pytest test_prompt_smoke.py test_aichat_runtime_policy_unit.py -q`
- `.venv/bin/python -c "from noi_agent import analyze_student_turn; print('ok')"`

**Expected:** All targeted and smoke tests pass, with no changes to frontend, chat routing, or deployment files.
