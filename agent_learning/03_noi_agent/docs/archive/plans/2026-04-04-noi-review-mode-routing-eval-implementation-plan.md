# NOI Review Mode Routing And Eval Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `review` 建立 submission_result 归一化、mode 路由、prompt supplement 和 promptfoo 评测基线，并用真实样例对比验证改动收益。

**Architecture:** 保持现有 `review` JSON schema、解析链、guard 链和 LLM 调用链不变，只在 `generate_review(...)` 入口和 `system_prompt` 构造层增加 mode-aware routing。评测侧通过 `promptfoo + exec provider` 调用真实 `generate_review(...)`，用真实打卡记录生成 baseline 与对比集。

**Tech Stack:** Python, unittest, Promptfoo, JSONL, existing `review_engine.py`

---

### Task 1: 锁定 review mode 路由入口

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`

- [ ] **Step 1: 写失败测试，覆盖 submission_result 归一化和 mode 路由**

```python
def test_detect_review_mode_prefers_failed_verdict_for_wa_with_spaces(self):
    mode = review_engine._detect_review_mode("unfinished", " WA ")
    self.assertEqual(mode, "failed_verdict")

def test_detect_review_mode_maps_editorial_before_independent(self):
    mode = review_engine._detect_review_mode("editorial", "unknown")
    self.assertEqual(mode, "editorial_transfer")

def test_detect_review_mode_maps_unfinished_to_stuck_bridge(self):
    mode = review_engine._detect_review_mode("unfinished", "not_submitted")
    self.assertEqual(mode, "stuck_bridge")

def test_detect_review_mode_defaults_to_independent_reflect(self):
    mode = review_engine._detect_review_mode("independent", "unknown")
    self.assertEqual(mode, "independent_reflect")
```

- [ ] **Step 2: 只跑新测试，确认先红**

Run:
`python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

Expected:
包含 `_detect_review_mode` 缺失或断言失败。

- [ ] **Step 3: 在 review_engine.py 增加 `_detect_review_mode(...)` 和 submission_result 归一化**

```python
def _detect_review_mode(completion_status: str, submission_result: str | None) -> str:
    submission_result = (submission_result or "unknown").strip().lower()
    if submission_result in {"wa", "tle", "re", "ce"}:
        return "failed_verdict"
    if completion_status == "editorial":
        return "editorial_transfer"
    if completion_status in {"unfinished", "hinted"}:
        return "stuck_bridge"
    return "independent_reflect"
```

并在 `generate_review(...)` 开头加入：

```python
submission_result = (submission_result or "unknown").strip().lower()
```

- [ ] **Step 4: 重新跑单测，确认转绿**

Run:
`python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

Expected:
PASS

### Task 2: system prompt 增加 mode supplement

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`

- [ ] **Step 1: 写失败测试，锁定 4 种 mode 会带不同 supplement**

```python
def test_build_review_system_prompt_should_append_failed_verdict_supplement(self):
    prompt = review_engine._build_review_system_prompt("failed_verdict")
    self.assertIn("WA/TLE/RE/CE", prompt)
    self.assertIn("具体出错位置或逻辑", prompt)

def test_build_review_system_prompt_should_append_stuck_bridge_supplement(self):
    prompt = review_engine._build_review_system_prompt("stuck_bridge")
    self.assertIn("学生卡住了", prompt)
    self.assertIn("不能只写\"不会建模\"", prompt)

def test_build_review_system_prompt_should_append_editorial_transfer_supplement(self):
    prompt = review_engine._build_review_system_prompt("editorial_transfer")
    self.assertIn("学生看了题解", prompt)
    self.assertIn("为什么这个方法能解决这道题", prompt)

def test_build_review_system_prompt_should_append_independent_reflect_supplement(self):
    prompt = review_engine._build_review_system_prompt("independent_reflect")
    self.assertIn("学生独立完成", prompt)
    self.assertIn("更难的变形", prompt)
```

- [ ] **Step 2: 跑测试，确认先红**

Run:
`python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

Expected:
新增断言失败。

- [ ] **Step 3: 改 `_build_review_system_prompt(mode=...)`，保留骨架，末尾拼 supplement**

实现要求：
- base prompt 原有字段、规则、长度控制不删
- 只在末尾拼 `supplements[mode]`
- 默认 mode 为 `independent_reflect`

- [ ] **Step 4: 在 `generate_review(...)` 中接入 mode**

把：

```python
system_prompt = _build_review_system_prompt()
```

改成：

```python
mode = _detect_review_mode(completion_status, submission_result)
system_prompt = _build_review_system_prompt(mode=mode)
```

- [ ] **Step 5: 重新跑单测**

Run:
`python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_focus_unit.py`

Expected:
PASS

### Task 3: 建立 review eval 骨架

**Files:**
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/cases.jsonl`
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_case.py`
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.yaml`

- [ ] **Step 1: 写 `run_review_case.py`**

```python
import json
import sys

sys.path.insert(0, "/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent")

from review_engine import generate_review


def run(case: dict) -> dict:
    inp = case["input"]
    result = generate_review(
        problem_title=inp["problem_title"],
        oj_source=inp.get("oj_source", ""),
        completion_status=inp["completion_status"],
        bottleneck_text=inp["bottleneck_text"],
        error_types=inp.get("error_types", []),
        submission_result=inp.get("submission_result"),
        reflection=inp.get("reflection"),
        problem_context=inp.get("problem_context"),
        problem_tags=inp.get("problem_tags"),
        student_code=inp.get("student_code"),
    )
    if not result["ok"]:
        return {"error": result["message"]}
    return result["review"]


if __name__ == "__main__":
    case = json.loads(sys.stdin.read())
    print(json.dumps(run(case), ensure_ascii=False))
```

- [ ] **Step 2: 写 `promptfoo.yaml`**

要求：
- 使用 `exec:python /Users/.../evals/review/run_review_case.py`
- 针对 `cases.jsonl` 的每条样例运行
- 断言包含：
  - is-json
  - 四字段非空
  - llm-rubric 4 条，阈值 3

- [ ] **Step 3: 创建空白 `cases.jsonl` 结构并写入首批样例**

每行一条 JSON：

```json
{"id":"failed_001","mode":"failed_verdict","input":{"problem_title":"...","oj_source":"洛谷","completion_status":"unfinished","bottleneck_text":"...","error_types":["..."],"submission_result":"wa"},"notes":"..."}
```

### Task 4: 从真实打卡记录抽取 baseline cases

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/cases.jsonl`
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/export_cases.py`

- [ ] **Step 1: 写导出脚本，从真实已完成打卡里筛样例**

脚本职责：
- 连接 `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/noi_agent.db`
- 从 `checkins` / `reviews` 相关表里筛 `review_status=completed`
- 优先选 `main_block/key_bridge/next_step/transfer_signal` 非空的样例
- 按 4 个 mode 目标各抽 5-7 条

- [ ] **Step 2: 运行导出脚本并人工检查 `cases.jsonl`**

Run:
`python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/export_cases.py`

Expected:
生成 20-30 条 JSONL。

- [ ] **Step 3: 修正少量坏样例**

要求：
- 去掉明显重复
- 去掉 review 质量明显空泛的记录
- 保证四类 mode 都有覆盖

### Task 5: 安装并运行 promptfoo baseline

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.yaml`
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/README.md`

- [ ] **Step 1: 安装 promptfoo**

Run:
`cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent && npx promptfoo@latest --version`

Expected:
输出 promptfoo 版本号。

- [ ] **Step 2: 跑 baseline**

Run:
`cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent && npx promptfoo@latest eval -c /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.yaml`

Expected:
生成 baseline 结果。

- [ ] **Step 3: 记录三个数字**

记录：
- JSON 合法率
- 四字段非空率
- llm-rubric 平均分

把结果写进 `README.md`。

### Task 6: 跑 mode 路由版本对比并同步文档

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/README.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`

- [ ] **Step 1: 再跑一轮 eval，记录 mode 路由版本结果**

Run:
`cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent && npx promptfoo@latest eval -c /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.yaml`

Expected:
输出对比结果。

- [ ] **Step 2: 在 README 写 baseline vs mode route 对比**

必须写：
- 三个指标的 baseline
- 三个指标的 mode route 版本
- 是否满足“至少一个上升，且没有整体退化”

- [ ] **Step 3: 同步 harness**

要求：
- `current_system_state.md` 写明本轮只做 prompt routing + eval，不动 schema/guard/SSE
- `active_work_item.md` 写明下一步是根据评测结果决定是否继续 prompt family 深化

- [ ] **Step 4: 完整验证**

Run:
`python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_focus_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression.py`

Run:
`python3 -m py_compile /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_case.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/export_cases.py`

Expected:
全部通过。
