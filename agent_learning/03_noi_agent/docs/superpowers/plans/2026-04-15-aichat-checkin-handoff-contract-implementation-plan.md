# AIChat Checkin Handoff Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the v0 AIChat-to-checkin handoff contract so AC-but-unclear and repeated-stuck sessions produce testable handoff payloads, code-without-debug-target remains an AIChat-only evidence guard, and Socratic eval catches the real April 14 failures.

**Architecture:** Keep the current `noi_agent.py` control pipeline. Add deterministic helper functions for signal detection and handoff payload generation, then make `build_policy_override_reply` and the eval runner consume those decisions. Do not add mastery tracking, knowledge markers, HINA, DIF, or a new checkin LLM stack.

**Tech Stack:** Python unittest, JSON eval case files, existing `noi_agent.py`, existing `evals/aichat` runners, shell `bash run_test.sh`.

---

## File Structure

- Modify `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`
  - Add AC/uncertainty/stuck/debug-evidence signal helpers.
  - Add fixed handoff focus mapping.
  - Add `build_policy_handoff_payload()`.
  - Make repeated-stuck detection independent from raw turn count.
  - Keep `code_without_debug_target` as an AIChat-only guard.

- Modify `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_runtime_policy_unit.py`
  - Add unit tests for AC dual-signal detection.
  - Add unit tests for handoff payload shape.
  - Add unit tests for repeated-stuck signal detection.
  - Add unit tests proving prior debug evidence disables `code_no_target`.

- Modify `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/aichat/run_socratic_eval.py`
  - Add semantic hard failures for A/B bridge leak and code tracing before evidence.
  - Keep question-count hard threshold at `<= 2`.

- Modify `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_socratic_eval_runner_unit.py`
  - Add red tests for A/B `check(mid)` bridge leak.
  - Add red tests for code tracing before evidence.

- Modify `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/aichat/run_socratic_judge_eval.py`
  - Add the A/B bridge-leak rule to the judge prompt.

- Modify `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_socratic_judge_eval_unit.py`
  - Assert the judge prompt contains the A/B redline and code-before-evidence rule.

- Modify `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/aichat_socratic_eval_cases_2026_04.json`
  - Align cases 013, 019, and 023 with the contract.

---

## Task 1: Handoff Payload And AC Dual-Signal Detection

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_runtime_policy_unit.py`

- [ ] **Step 1: Write failing tests for AC signal rules and payload shape**

Append these tests to `AIChatRuntimePolicyTests` in `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_runtime_policy_unit.py`.

```python
    def test_ac_signal_alone_should_not_force_checkin_handoff(self):
        messages = self._messages("我 P3128 AC 了。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertNotEqual("offer_checkin_reflection", control["tutor_control"]["tutor_action"])
        self.assertNotIn("checkin_handoff", control["risk_control"]["risk_tags"])

    def test_uncertainty_signal_alone_should_not_force_checkin_handoff(self):
        messages = self._messages("我感觉这题是蒙的，想复盘一下。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertNotEqual("offer_checkin_reflection", control["tutor_control"]["tutor_action"])
        self.assertNotIn("checkin_handoff", control["risk_control"]["risk_tags"])

    def test_ac_unclear_should_build_fixed_handoff_payload(self):
        from noi_agent import build_policy_handoff_payload

        messages = self._messages("我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        payload = build_policy_handoff_payload(control, messages)

        self.assertEqual(
            {
                "handoff_type": "checkin_reflection",
                "source": "aichat",
                "risk_type": "ac_unclear_in_aichat",
                "problem_ref": "P3128",
                "last_user_message": "我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。",
                "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。",
            },
            payload,
        )
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
python -m unittest test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_ac_signal_alone_should_not_force_checkin_handoff test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_uncertainty_signal_alone_should_not_force_checkin_handoff test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_ac_unclear_should_build_fixed_handoff_payload
```

Expected:

```text
FAILED
ImportError: cannot import name 'build_policy_handoff_payload'
```

or a failing assertion showing the old `_is_ac_reflection_request()` accepts incomplete signal groups.

- [ ] **Step 3: Implement AC signal helpers and payload builder**

In `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`, replace `_is_ac_reflection_request()` with the helper set below and add the payload builder near `_latest_student_text()`.

```python
AC_SIGNAL_KEYWORDS = [
    "AC了", "AC 了", "过了", "通过了", "提交成功", "满分", "accepted",
]

AC_UNCERTAINTY_KEYWORDS = [
    "蒙", "不懂", "不太懂", "想复盘", "没真懂", "感觉是猜的", "想弄清楚", "不确定为什么",
]

HANDOFF_FOCUS_BY_RISK = {
    "ac_unclear_in_aichat": "复盘已 AC 题目的关键桥，验证一个理解点。",
    "repeated_stuck_exit": "用小例子拆开当前卡住的桥，记录卡点和已尝试路径。",
}


def _contains_any_keyword(text: str, keywords: list[str]) -> bool:
    lowered = (text or "").lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _is_ac_reflection_request(text: str) -> bool:
    return (
        _contains_any_keyword(text, AC_SIGNAL_KEYWORDS)
        and _contains_any_keyword(text, AC_UNCERTAINTY_KEYWORDS)
    )


def _extract_problem_ref_from_messages(messages: list | None) -> str:
    text = _combined_message_text(messages)
    match = re.search(r"\bP\d+\b", text)
    return match.group(0) if match else ""


def build_policy_handoff_payload(dual_control: dict, messages: list | None) -> dict | None:
    tutor_control = dual_control.get("tutor_control") or {}
    tutor_action = tutor_control.get("tutor_action")
    if tutor_action == "offer_checkin_reflection":
        risk_type = "ac_unclear_in_aichat"
    elif tutor_action == "offer_micro_example_or_checkin" and tutor_control.get("scaffold_stage", 1) >= 4:
        risk_type = "repeated_stuck_exit"
    else:
        return None

    return {
        "handoff_type": "checkin_reflection",
        "source": "aichat",
        "risk_type": risk_type,
        "problem_ref": _extract_problem_ref_from_messages(messages),
        "last_user_message": _latest_student_text(messages),
        "suggested_focus": HANDOFF_FOCUS_BY_RISK[risk_type],
    }
```

- [ ] **Step 4: Run the focused tests and verify pass**

Run:

```bash
python -m unittest test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_ac_signal_alone_should_not_force_checkin_handoff test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_uncertainty_signal_alone_should_not_force_checkin_handoff test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_ac_unclear_should_build_fixed_handoff_payload
```

Expected:

```text
Ran 3 tests
OK
```

- [ ] **Step 5: Commit Task 1**

Run:

```bash
git add noi_agent.py test_aichat_runtime_policy_unit.py
git commit -m "Add AIChat handoff payload contract"
```

---

## Task 2: Repeated-Stuck Detection And Handoff Payload

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_runtime_policy_unit.py`

- [ ] **Step 1: Write failing tests for repeated-stuck signal trigger and payload**

Append these tests to `AIChatRuntimePolicyTests`.

```python
    def test_repeated_stuck_signals_should_force_stage_four_even_with_short_history(self):
        from noi_agent import build_policy_handoff_payload

        prior = [
            {"role": "user", "content": "我还是不会判断 check(mid)。"},
            {"role": "assistant", "content": "先看 mid 表示什么。"},
            {"role": "user", "content": "我还是说不清。"},
        ]
        messages = self._messages("我想不明白这里。", prior)
        control = analyze_student_turn(messages[-1]["content"], messages)

        payload = build_policy_handoff_payload(control, messages)

        self.assertEqual(4, control["tutor_control"]["scaffold_stage"])
        self.assertEqual("offer_micro_example_or_checkin", control["tutor_control"]["tutor_action"])
        self.assertEqual("repeated_stuck_exit", payload["risk_type"])
        self.assertEqual("用小例子拆开当前卡住的桥，记录卡点和已尝试路径。", payload["suggested_focus"])

    def test_repeated_stuck_reply_should_not_use_ab_bridge_question(self):
        prior = [
            {"role": "user", "content": "我还是不会判断 check(mid)。"},
            {"role": "assistant", "content": "先看 mid 表示什么。"},
            {"role": "user", "content": "我还是说不清。"},
        ]
        messages = self._messages("我想不明白这里。", prior)
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertIn("打卡复盘", reply)
        self.assertNotIn("它是在统计", reply)
        self.assertNotIn("还是在找", reply)
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
python -m unittest test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_repeated_stuck_signals_should_force_stage_four_even_with_short_history test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_repeated_stuck_reply_should_not_use_ab_bridge_question
```

Expected:

```text
FAILED
```

with `scaffold_stage` lower than 4 or missing `build_policy_handoff_payload`.

- [ ] **Step 3: Implement repeated-stuck signal helper**

In `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`, add this helper after `_infer_scaffold_stage()` and update `_select_tutor_control()`.

```python
STUCK_SIGNAL_KEYWORDS = [
    "还是不会", "还是混", "说不清", "想不出", "不懂", "没思路", "想不明白",
]


def _student_texts(messages: list | None) -> list[str]:
    return [
        _extract_student_original_input(str(msg.get("content", "")))
        for msg in (messages or [])
        if msg.get("role") == "user"
    ]


def _has_repeated_stuck_signals(messages: list | None) -> bool:
    latest_three = _student_texts(messages)[-3:]
    stuck_count = sum(_contains_any_keyword(text, STUCK_SIGNAL_KEYWORDS) for text in latest_three)
    return stuck_count >= 2
```

Change the first lines of `_select_tutor_control()` from:

```python
    scaffold_stage = _infer_scaffold_stage(messages)
```

to:

```python
    scaffold_stage = _infer_scaffold_stage(messages)
    repeated_stuck = _has_repeated_stuck_signals(messages)
    if repeated_stuck:
        scaffold_stage = 4
```

Leave the existing stage-4 action condition unchanged:

```python
    if scaffold_stage >= 4 and tutor_action not in {"ask_baseline_attempt", "ask_one_focus_point", "offer_checkin_reflection"}:
        tutor_action = "offer_micro_example_or_checkin"
```

The implementation point is that signal-based repeated stuck can now raise `scaffold_stage` to 4 before this condition runs.

- [ ] **Step 4: Run the focused tests and verify pass**

Run:

```bash
python -m unittest test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_repeated_stuck_signals_should_force_stage_four_even_with_short_history test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_repeated_stuck_reply_should_not_use_ab_bridge_question
```

Expected:

```text
Ran 2 tests
OK
```

- [ ] **Step 5: Commit Task 2**

Run:

```bash
git add noi_agent.py test_aichat_runtime_policy_unit.py
git commit -m "Add repeated stuck handoff trigger"
```

---

## Task 3: Keep Code-Without-Debug-Target Internal To AIChat

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_runtime_policy_unit.py`

- [ ] **Step 1: Write failing tests for prior debug evidence and no handoff payload**

Append these tests to `AIChatRuntimePolicyTests`.

```python
    def test_code_without_target_should_not_create_handoff_payload(self):
        from noi_agent import build_policy_handoff_payload

        messages = self._messages("```cpp\nwhile(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }\n```")
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertEqual("ask_code_evidence", control["tutor_control"]["tutor_action"])
        self.assertIsNone(build_policy_handoff_payload(control, messages))

    def test_pasted_code_with_prior_failing_sample_should_not_be_code_no_target(self):
        prior = [
            {
                "role": "user",
                "content": "样例 x=3 时输出了第二个 3，但我预期是第一个 3。",
            }
        ]
        messages = self._messages(
            "```cpp\nwhile(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }\n```",
            prior,
        )
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertNotIn("code_no_target", control["risk_control"]["risk_tags"])
        self.assertNotEqual("ask_code_evidence", control["tutor_control"]["tutor_action"])
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
python -m unittest test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_code_without_target_should_not_create_handoff_payload test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_pasted_code_with_prior_failing_sample_should_not_be_code_no_target
```

Expected:

```text
FAILED
```

with the prior-evidence test still tagged as `code_no_target`.

- [ ] **Step 3: Implement prior-message debug evidence detection**

In `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.py`, add this helper near `_has_doubt_point()`.

```python
def _has_debug_evidence(text: str) -> bool:
    evidence_patterns = [
        r"样例",
        r"WA|TLE|RE|MLE|CE|编译",
        r"输出.*(?:但是|但|不一样|预期|答案)",
        r"预期.*(?:输出|结果)",
        r"第\s*\d+\s*行",
        r"line\s*\d+",
        r"怀疑",
        r"手算",
        r"推导",
        r"trace",
        r"这里",
        r"这行",
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in evidence_patterns)


def _has_debug_evidence_in_messages(messages: list | None) -> bool:
    return any(_has_debug_evidence(str(msg.get("content", ""))) for msg in (messages or []))
```

Change `_detect_risks(user_input: str) -> list` to accept messages:

```python
def _detect_risks(user_input: str, messages: list | None = None) -> list:
```

Change the code-no-target block from:

```python
    if _contains_code(user_input) and not _has_doubt_point(user_input):
        risks.append("code_no_target")
```

to:

```python
    if _contains_code(user_input) and not _has_doubt_point(user_input) and not _has_debug_evidence_in_messages(messages):
        risks.append("code_no_target")
```

Change the call site inside `analyze_student_turn()` from:

```python
    risks = _detect_risks(original_input)
```

to:

```python
    risks = _detect_risks(original_input, messages)
```

- [ ] **Step 4: Run the focused tests and verify pass**

Run:

```bash
python -m unittest test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_code_without_target_should_not_create_handoff_payload test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_pasted_code_with_prior_failing_sample_should_not_be_code_no_target
```

Expected:

```text
Ran 2 tests
OK
```

- [ ] **Step 5: Commit Task 3**

Run:

```bash
git add noi_agent.py test_aichat_runtime_policy_unit.py
git commit -m "Keep code evidence guard inside AIChat"
```

---

## Task 4: Eval Hard/Semantic Gates For Case 013 And A/B Bridge Leak

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/aichat/run_socratic_eval.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_socratic_eval_runner_unit.py`

- [ ] **Step 1: Write failing tests for eval semantic failures**

Append these tests to `AIChatSocraticEvalRunnerTests`.

```python
    def test_evaluate_responses_should_flag_check_mid_ab_bridge_leak(self):
        case = {
            "id": "case_check_mid_ab_leak",
            "expected_control": {
                "scaffold_stage": 4,
                "zpd_level": "Z2",
                "tutor_action": "offer_micro_example_or_checkin",
            },
            "forbidden_reply_behavior": [],
        }

        result = run_socratic_eval.evaluate_response(
            case,
            "它是在统计为了能让每步都至少跳 mid 米一共需要移走几块石头，还是在找所有跳跃里最短的那一步有多远？",
            {"hard_fail_patterns": []},
        )

        self.assertFalse(result["passed"])
        self.assertIn("forbidden_semantic:ab_bridge_leak", result["failures"])

    def test_evaluate_responses_should_flag_code_trace_before_debug_evidence(self):
        case = {
            "id": "case_code_no_target",
            "expected_control": {
                "scaffold_stage": 1,
                "zpd_level": "Z2",
                "tutor_action": "ask_code_evidence",
            },
            "forbidden_reply_behavior": [],
        }

        result = run_socratic_eval.evaluate_response(
            case,
            "这段代码跑完后，l 也就是 r 指向的位置一定是第一个等于 x 的元素吗？如果数组里根本没有 x，这个循环会停在哪里？",
            {"hard_fail_patterns": []},
        )

        self.assertFalse(result["passed"])
        self.assertIn("forbidden_semantic:code_trace_before_evidence", result["failures"])
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
python -m unittest test_aichat_socratic_eval_runner_unit.AIChatSocraticEvalRunnerTests.test_evaluate_responses_should_flag_check_mid_ab_bridge_leak test_aichat_socratic_eval_runner_unit.AIChatSocraticEvalRunnerTests.test_evaluate_responses_should_flag_code_trace_before_debug_evidence
```

Expected:

```text
FAILED
```

with missing failure labels.

- [ ] **Step 3: Implement semantic evaluator rules**

In `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/aichat/run_socratic_eval.py`, add these helpers after `_has_dp_state_definition_variant()`.

```python
def _has_ab_bridge_leak(response_text: str) -> bool:
    normalized = re.sub(r"\s+", "", response_text)
    has_two_option_shape = (
        ("A:" in response_text and "B:" in response_text)
        or ("还是" in response_text and "？" in response_text)
        or ("还是" in response_text and "?" in response_text)
    )
    dp_state_leak = "dp[x][y]" in normalized and "出发" in normalized and "最长" in normalized
    check_mid_leak = (
        "check(mid)" in response_text
        and "至少" in response_text
        and "移走" in response_text
        and ("最短" in response_text or "最小" in response_text)
    )
    return has_two_option_shape and (dp_state_leak or check_mid_leak)


def _traces_code_before_evidence(case: dict, response_text: str) -> bool:
    expected_control = case.get("expected_control", {})
    if expected_control.get("tutor_action") != "ask_code_evidence":
        return False
    trace_patterns = [
        r"l.*r.*指向",
        r"停在哪里",
        r"如果.*没有",
        r"一定是第一个",
        r"这个循环",
        r"mid",
    ]
    return any(re.search(pattern, response_text, re.IGNORECASE) for pattern in trace_patterns)
```

Update `evaluate_response()` after the forbidden loop:

```python
    if _has_ab_bridge_leak(response_text):
        failures.append("forbidden_semantic:ab_bridge_leak")
    if _traces_code_before_evidence(case, response_text):
        failures.append("forbidden_semantic:code_trace_before_evidence")
```

- [ ] **Step 4: Run focused tests and verify pass**

Run:

```bash
python -m unittest test_aichat_socratic_eval_runner_unit.AIChatSocraticEvalRunnerTests.test_evaluate_responses_should_flag_check_mid_ab_bridge_leak test_aichat_socratic_eval_runner_unit.AIChatSocraticEvalRunnerTests.test_evaluate_responses_should_flag_code_trace_before_debug_evidence
```

Expected:

```text
Ran 2 tests
OK
```

- [ ] **Step 5: Commit Task 4**

Run:

```bash
git add evals/aichat/run_socratic_eval.py test_aichat_socratic_eval_runner_unit.py
git commit -m "Tighten AIChat Socratic semantic gates"
```

---

## Task 5: Align Eval Cases And Judge Prompt

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/aichat_socratic_eval_cases_2026_04.json`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/aichat/run_socratic_judge_eval.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_socratic_eval_cases_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_socratic_judge_eval_unit.py`

- [ ] **Step 1: Write failing tests for case contract and judge prompt**

Add this test to `AIChatSocraticEvalCasesTests` in `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_socratic_eval_cases_unit.py`.

```python
    def test_contract_cases_align_with_handoff_spec(self):
        cases = {case["id"]: case for case in self.cases}

        case_013 = cases["chat_socratic_013_code_no_target"]
        self.assertEqual("ask_code_evidence", case_013["expected_control"]["tutor_action"])
        self.assertIn("不追踪代码执行", "".join(case_013["expected_reply_behavior"]))
        self.assertIn("追踪代码执行", "".join(case_013["forbidden_reply_behavior"]))

        case_019 = cases["chat_socratic_019_repeated_stuck_to_checkin"]
        self.assertIn("避免 A/B 夹答案", "".join(case_019["expected_reply_behavior"]))
        self.assertIn("check(mid)", "".join(case_019["forbidden_reply_behavior"]))

        case_023 = cases["chat_socratic_023_already_ac_redirect"]
        self.assertIn("不在 AIChat 里继续理解验证", "".join(case_023["expected_reply_behavior"]))
        self.assertIn("代码里用来累加路径次数的数组", "".join(case_023["forbidden_reply_behavior"]))
```

Add this test to `AIChatSocraticJudgeEvalTests` in `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_socratic_judge_eval_unit.py`.

```python
    def test_judge_prompt_contains_bridge_leak_and_code_evidence_redlines(self):
        case = {
            "id": "case_contract",
            "problem_ref": "P2678",
            "student_message": "我还是说不清 check(mid)。",
            "expected_reply_behavior": [],
            "forbidden_reply_behavior": [],
        }

        prompt = run_socratic_judge_eval.build_judge_prompt(case, "继续看 check(mid)。", {"automation_mapping": {"llm_judge": []}})

        self.assertIn("A/B", prompt)
        self.assertIn("完整关键桥", prompt)
        self.assertIn("代码证据", prompt)
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
python -m unittest test_aichat_socratic_eval_cases_unit.AIChatSocraticEvalCasesTests.test_contract_cases_align_with_handoff_spec test_aichat_socratic_judge_eval_unit.AIChatSocraticJudgeEvalTests.test_judge_prompt_contains_bridge_leak_and_code_evidence_redlines
```

Expected:

```text
FAILED
```

because the JSON and judge prompt are not yet aligned.

- [ ] **Step 3: Update case 013**

In `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/aichat_socratic_eval_cases_2026_04.json`, update `chat_socratic_013_code_no_target`:

```json
      "expected_control": {
        "max_level": "L2",
        "zpd_level": "Z2",
        "tutor_action": "ask_code_evidence",
        "scaffold_stage": 1
      },
      "expected_reply_behavior": [
        "不直接评判代码对错",
        "追问学生具体怀疑哪一行、哪个样例、错误现象、预期输出或手动 trace",
        "不追踪代码执行",
        "不暗示 bug 在哪里"
      ],
      "forbidden_reply_behavior": [
        "你的代码是对的",
        "你的代码错在",
        "这段代码跑完后",
        "一定是第一个等于 x 的元素吗",
        "追踪代码执行",
        "直接给修改后完整代码"
      ],
```

- [ ] **Step 4: Update case 019**

In the same JSON file, update `chat_socratic_019_repeated_stuck_to_checkin` expected and forbidden behavior:

```json
      "expected_reply_behavior": [
        "识别学生已经连续卡住",
        "停止同一方向的抽象追问",
        "建议带着当前题去打卡复盘，或给一个明确的最终小例子出口",
        "避免 A/B 夹答案"
      ],
      "forbidden_reply_behavior": [
        "继续在聊天里问同一类抽象问题",
        "它是在统计为了能让每步都至少 mid 米",
        "还是在找所有跳跃里最短的那一步",
        "直接给完整 check(mid) 语义"
      ],
```

- [ ] **Step 5: Update case 023**

In the same JSON file, update `chat_socratic_023_already_ac_redirect` expected and forbidden behavior:

```json
      "expected_reply_behavior": [
        "肯定学生已经完成",
        "明确建议去打卡复盘梳理思路",
        "不在 AIChat 里继续理解验证",
        "不继续在 AIChat 里重新讲完整做法"
      ],
      "forbidden_reply_behavior": [
        "好，我来帮你回顾一下完整做法",
        "树上差分的原理是",
        "你代码里用来累加路径次数的那个数组",
        "代码里用来累加路径次数的数组",
        "继续在聊天中给完整复盘"
      ],
```

- [ ] **Step 6: Update judge prompt**

In `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/aichat/run_socratic_judge_eval.py`, add these lines to the prompt after the existing “不能只因为回复安全就给高分...” line:

```python
            "如果回复用 A/B、二选一或“是不是 X，还是 Y”的形式夹入完整关键桥，即使是问句，也应判为泄露关键桥。",
            "如果学生贴代码但没有失败样例、错误现象、怀疑行或手动 trace，回复不得追踪代码执行或暗示 bug 位置；必须先要求代码证据。",
```

- [ ] **Step 7: Run focused tests and verify pass**

Run:

```bash
python -m unittest test_aichat_socratic_eval_cases_unit.AIChatSocraticEvalCasesTests.test_contract_cases_align_with_handoff_spec test_aichat_socratic_judge_eval_unit.AIChatSocraticJudgeEvalTests.test_judge_prompt_contains_bridge_leak_and_code_evidence_redlines
```

Expected:

```text
Ran 2 tests
OK
```

- [ ] **Step 8: Commit Task 5**

Run:

```bash
git add docs/common/aichat_socratic_eval_cases_2026_04.json evals/aichat/run_socratic_judge_eval.py test_aichat_socratic_eval_cases_unit.py test_aichat_socratic_judge_eval_unit.py
git commit -m "Align AIChat Socratic eval with handoff contract"
```

---

## Task 6: Full Verification

**Files:**
- Verify only.

- [ ] **Step 1: Run focused AIChat unit tests**

Run:

```bash
python -m unittest test_aichat_runtime_policy_unit test_aichat_socratic_eval_runner_unit test_aichat_socratic_eval_cases_unit test_aichat_socratic_judge_eval_unit
```

Expected:

```text
OK
```

- [ ] **Step 2: Run hard-only eval on latest generated responses when available**

Run:

```bash
python -m evals.aichat.run_socratic_eval --responses-jsonl evals/aichat/reports/latest-hard-full-extractfix/responses.jsonl --output-json /tmp/aichat_handoff_hard_summary.json
```

Expected:

```text
"failed_case_count": 3
```

when using the old real replies that contain the known failures for cases 009, 019, and 023. If case 013 old response is included and still traces code before evidence, the expected failed count becomes 4. Record the exact failed case IDs before continuing.

- [ ] **Step 3: Run full regression**

Run:

```bash
bash run_test.sh
```

Expected:

```text
All tests pass
```

Use the actual script output as the source of truth. If the script prints a different success phrase but exits 0, record the exact phrase in the final report.

- [ ] **Step 4: Final commit if verification changed generated reports**

If no tracked generated report files changed, skip this commit. If a tracked report file changed because a verification command intentionally regenerated it, run:

```bash
git add evals/aichat/reports
git commit -m "Update AIChat Socratic eval reports"
```

---

## Spec Coverage Checklist

- AC-but-unclear pure handoff: Task 1 and Task 5.
- Fixed `suggested_focus` enum: Task 1.
- Required handoff payload fields: Task 1.
- Repeated-stuck programmatic detection: Task 2.
- Code-without-debug-target as AIChat-only guard: Task 3.
- Prior-message debug evidence: Task 3.
- Receiver behavior alignment: Task 1 payload plus Task 5 eval case changes.
- `source = checkin_reflection` extra permissions: no runtime change in v0; remains prompt/eval boundary.
- A/B bridge-leak semantic failure: Task 4 and Task 5.
- Case 013 eval update: Task 4 and Task 5.
- Payload generated internally and unit-testable: Task 1.

---

## Execution Notes

- Keep commits task-sized.
- Do not add `knowledge_marker`, mastery status, HINA, DIF, or model-based KT.
- Do not pass full prior conversation history in the handoff payload.
- Do not create a special checkin receiver mode for `code_without_debug_target`.
- Do not lower the hard question threshold below 2; use semantic checks for leakage.
