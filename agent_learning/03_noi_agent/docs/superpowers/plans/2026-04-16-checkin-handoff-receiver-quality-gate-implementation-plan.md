# Checkin Handoff Receiver Quality Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a receiver-side eval gate that verifies real checkin review output after AIChat handoff.

**Architecture:** Add a focused `evals/checkin` package with one runner module that owns case loading, schema validation, hard gate checks, generation via `review_engine.generate_review`, optional judge scoring, and report writing. Keep receiver eval logic separate from AIChat eval logic, but reuse the same command/report patterns and Kimi timeout conventions where helpful.

**Tech Stack:** Python stdlib, `unittest`, existing `review_engine.generate_review`, existing `evals.review.run_review_case_kimi_cli`, existing JSON/JSONL report conventions, shell-based `run_test.sh`.

---

## File Structure

Create or modify these files:

- Create: `agent_learning/03_noi_agent/docs/common/checkin_handoff_receiver_eval_cases_2026_04.json`
  - Owns the six v0 receiver eval cases.
- Create: `agent_learning/03_noi_agent/evals/checkin/__init__.py`
  - Makes `evals.checkin` importable.
- Create: `agent_learning/03_noi_agent/evals/checkin/run_handoff_receiver_eval.py`
  - Owns receiver case schema validation, hard gate, generation rows, judge prompt/result parsing, suite running, CLI, and Markdown report.
- Create: `agent_learning/03_noi_agent/test_checkin_handoff_receiver_eval_cases_unit.py`
  - Verifies case schema and v0 case set.
- Create: `agent_learning/03_noi_agent/test_checkin_handoff_receiver_eval_runner_unit.py`
  - Verifies hard gate, runner, judge, CLI, and report behavior.
- Modify: `agent_learning/03_noi_agent/run_test.sh`
  - Adds the two new unit test files and the new runner module to syntax compilation.
- Modify: `agent_learning/03_noi_agent/docs/common/current_validation_baseline.md`
  - Records final real receiver eval report path and result after real validation.

Boundary decisions:

- Do not modify `review_engine.py` in this plan unless real receiver eval exposes a generation-quality problem after the gate exists.
- Do not modify frontend files.
- Do not add knowledge-marker, mastery, HINA, DIF, or code-understanding quiz features.

---

### Task 1: Receiver Case Fixture And Schema Tests

**Files:**
- Create: `agent_learning/03_noi_agent/docs/common/checkin_handoff_receiver_eval_cases_2026_04.json`
- Create: `agent_learning/03_noi_agent/test_checkin_handoff_receiver_eval_cases_unit.py`

- [ ] **Step 1: Write the failing schema tests**

Create `test_checkin_handoff_receiver_eval_cases_unit.py`:

```python
import json
import unittest
from pathlib import Path


CASES_PATH = Path("docs/common/checkin_handoff_receiver_eval_cases_2026_04.json")
EXPECTED_CASE_IDS = [
    "recv_001_p3128_ac_unclear_lca",
    "recv_002_p3372_ac_unclear_lazy",
    "recv_003_p1434_ac_unclear_dp_state",
    "recv_004_p2678_repeated_stuck_check",
    "recv_005_p3128_repeated_stuck_lca",
    "recv_006_p2249_repeated_stuck_bound",
]
ALLOWED_RISK_TYPES = {"ac_unclear_in_aichat", "repeated_stuck_exit"}


class CheckinHandoffReceiverEvalCasesTests(unittest.TestCase):
    def load_cases(self) -> dict:
        return json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def test_receiver_cases_should_have_exact_v0_case_set(self):
        data = self.load_cases()
        self.assertEqual("checkin_handoff_receiver_quality", data["suite"])
        self.assertEqual(EXPECTED_CASE_IDS, [case["id"] for case in data["cases"]])

    def test_receiver_cases_should_have_required_schema(self):
        data = self.load_cases()
        for case in data["cases"]:
            with self.subTest(case_id=case["id"]):
                self.assertIn(case["risk_type"], ALLOWED_RISK_TYPES)
                for field in [
                    "problem_ref",
                    "problem_title",
                    "oj_source",
                    "problem_context",
                    "completion_status",
                    "submission_result",
                    "bottleneck_text",
                    "reflection",
                    "handoff_payload",
                    "expected_review_behavior",
                    "forbidden_review_behavior",
                ]:
                    self.assertIn(field, case)
                self.assertTrue(case["problem_ref"].strip())
                self.assertTrue(case["problem_title"].strip())
                self.assertTrue(case["bottleneck_text"].strip())
                payload = case["handoff_payload"]
                self.assertEqual("checkin_reflection", payload["handoff_type"])
                self.assertEqual("aichat", payload["source"])
                self.assertEqual(case["risk_type"], payload["risk_type"])
                self.assertEqual(case["problem_ref"], payload["problem_ref"])
                self.assertTrue(payload["last_user_message"].strip())
                self.assertTrue(payload["suggested_focus"].strip())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run schema tests to verify RED**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
python3 -m unittest test_checkin_handoff_receiver_eval_cases_unit -v
```

Expected: fail with `FileNotFoundError` because `checkin_handoff_receiver_eval_cases_2026_04.json` does not exist yet.

- [ ] **Step 3: Write the receiver case JSON**

Create `docs/common/checkin_handoff_receiver_eval_cases_2026_04.json` with this exact content:

```json
{
  "version": "2026-04",
  "suite": "checkin_handoff_receiver_quality",
  "rubric": {
    "hard_gate": [
      "no complete code",
      "no complete DP state definition",
      "no complete P3128 tree-difference formula",
      "no complete check(mid) semantics",
      "no lazy full mechanism leak",
      "no A/B answer-shaped bridge leakage",
      "no live AIChat continuation"
    ],
    "llm_judge": [
      "Behaves as checkin_reflection, not ordinary AIChat",
      "For AC-but-unclear, verifies one understanding point without reteaching the full solution",
      "For repeated-stuck, splits one bridge with a small example or concrete reflection step",
      "Keeps the response concrete to the problem and student's stated bottleneck",
      "Does not leak complete state, transition, check function, formula, or code"
    ]
  },
  "cases": [
    {
      "id": "recv_001_p3128_ac_unclear_lca",
      "risk_type": "ac_unclear_in_aichat",
      "problem_ref": "P3128",
      "problem_title": "P3128 [USACO15DEC] Max Flow P",
      "oj_source": "luogu",
      "problem_context": "给一棵 N 个节点的树和 K 条运输路径，每条路径从 u 到 v。求所有路径经过次数最多的点。学生已用 LCA 和树上差分 AC。",
      "completion_status": "independent",
      "submission_result": "accepted",
      "bottleneck_text": "我 AC 了，但说不清为什么 LCA 附近要额外处理，感觉只是照着公式写过了。",
      "reflection": "我知道端点要加，但公共祖先那里为什么不能直接跟端点一样处理，我讲不顺。",
      "student_code": "cnt[u]++; cnt[v]++; cnt[lca]--; cnt[parent[lca]]--;",
      "handoff_payload": {
        "handoff_type": "checkin_reflection",
        "source": "aichat",
        "risk_type": "ac_unclear_in_aichat",
        "problem_ref": "P3128",
        "last_user_message": "我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。",
        "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。"
      },
      "expected_review_behavior": [
        "围绕 LCA 附近的处理验证理解",
        "不在复盘里直接重写完整树差分公式"
      ],
      "forbidden_review_behavior": [
        "完整写出端点、LCA、parent(LCA) 的全部加减公式",
        "给出完整 AC 代码"
      ]
    },
    {
      "id": "recv_002_p3372_ac_unclear_lazy",
      "risk_type": "ac_unclear_in_aichat",
      "problem_ref": "P3372",
      "problem_title": "P3372 【模板】线段树 1",
      "oj_source": "luogu",
      "problem_context": "支持区间加和区间求和。学生已 AC，但对 lazy 标记表示什么、什么时候下传不稳。",
      "completion_status": "independent",
      "submission_result": "accepted",
      "bottleneck_text": "我代码过了，但 lazy 到底是没来得及改，还是已经改完只是没下传，我说不清。",
      "reflection": "我能写 pushdown，但不确定父节点、子节点和 lazy 各自保存的含义。",
      "student_code": "tree[p] += k * (r - l + 1); lazy[p] += k;",
      "handoff_payload": {
        "handoff_type": "checkin_reflection",
        "source": "aichat",
        "risk_type": "ac_unclear_in_aichat",
        "problem_ref": "P3372",
        "last_user_message": "线段树 AC 了，但是 lazy 是什么我好像只是背下来了。",
        "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。"
      },
      "expected_review_behavior": [
        "验证父节点值、子节点值、lazy 标记三者的局部含义",
        "不完整展开 pushdown 模板"
      ],
      "forbidden_review_behavior": [
        "直接完整定义 lazy 并展开整个 pushdown 机制",
        "给出线段树完整代码"
      ]
    },
    {
      "id": "recv_003_p1434_ac_unclear_dp_state",
      "risk_type": "ac_unclear_in_aichat",
      "problem_ref": "P1434",
      "problem_title": "P1434 [SHOI2002] 滑雪",
      "oj_source": "luogu",
      "problem_context": "给定高度矩阵，只能从高处滑到相邻低处，求最长滑行路径。学生已 AC，但不确定 DP 状态方向。",
      "completion_status": "independent",
      "submission_result": "accepted",
      "bottleneck_text": "我 AC 了，但 dp 的方向我其实靠试出来的，说不清它为什么这样定义。",
      "reflection": "我知道有记忆化搜索，但不知道从一个格子看还是从终点看更自然。",
      "student_code": "int dfs(int x,int y){ if(dp[x][y]) return dp[x][y]; }",
      "handoff_payload": {
        "handoff_type": "checkin_reflection",
        "source": "aichat",
        "risk_type": "ac_unclear_in_aichat",
        "problem_ref": "P1434",
        "last_user_message": "P1434 过了，但状态方向我还是有点蒙。",
        "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。"
      },
      "expected_review_behavior": [
        "验证学生能用边界格子解释状态方向",
        "不直接给完整 dp[x][y] 状态定义"
      ],
      "forbidden_review_behavior": [
        "dp[x][y] 表示从 x,y 出发的最长路",
        "完整写出状态定义和转移"
      ]
    },
    {
      "id": "recv_004_p2678_repeated_stuck_check",
      "risk_type": "repeated_stuck_exit",
      "problem_ref": "P2678",
      "problem_title": "P2678 [NOIP2015 提高组] 跳石头",
      "oj_source": "luogu",
      "problem_context": "河道长度 L，中间有 n 块石头，最多移走 m 块。求移走后最短跳跃距离的最大值。学生在 AIChat 连续说不清 check(mid)。",
      "completion_status": "unfinished",
      "submission_result": "not_submitted",
      "bottleneck_text": "我还是说不清 check(mid) 到底在检查什么，每次讲到移石头就混了。",
      "reflection": "我试过拿 mid 当答案，但不知道扫描石头时什么时候计数。",
      "student_code": "",
      "handoff_payload": {
        "handoff_type": "checkin_reflection",
        "source": "aichat",
        "risk_type": "repeated_stuck_exit",
        "problem_ref": "P2678",
        "last_user_message": "我还是说不清 check(mid) 到底检查什么。",
        "suggested_focus": "用小例子拆开当前卡住的桥，记录卡点和已尝试路径。"
      },
      "expected_review_behavior": [
        "用一个很小的石头序列拆 check 的局部行为",
        "不把完整 check 语义写成答案"
      ],
      "forbidden_review_behavior": [
        "完整写出 check(mid) 函数",
        "用 A/B 选项把正确 check 语义夹进去"
      ]
    },
    {
      "id": "recv_005_p3128_repeated_stuck_lca",
      "risk_type": "repeated_stuck_exit",
      "problem_ref": "P3128",
      "problem_title": "P3128 [USACO15DEC] Max Flow P",
      "oj_source": "luogu",
      "problem_context": "给一棵树和多条路径，要求统计路径经过次数最多的点。学生反复卡在一条路径对公共祖先附近贡献的理解。",
      "completion_status": "unfinished",
      "submission_result": "wa",
      "bottleneck_text": "我还是想不出来为什么 LCA 那里要处理，我画链也会算重。",
      "reflection": "我试过只给 u 和 v 加标记，再从下往上累加，但 LCA 附近数量不对。",
      "student_code": "cnt[u]++; cnt[v]++;",
      "handoff_payload": {
        "handoff_type": "checkin_reflection",
        "source": "aichat",
        "risk_type": "repeated_stuck_exit",
        "problem_ref": "P3128",
        "last_user_message": "我还是想不出来为什么 LCA 那里要处理。",
        "suggested_focus": "用小例子拆开当前卡住的桥，记录卡点和已尝试路径。"
      },
      "expected_review_behavior": [
        "用 3-5 个点的小树或链记录一次路径贡献",
        "不完整给出树差分公式"
      ],
      "forbidden_review_behavior": [
        "完整写出端点、LCA、parent(LCA) 的全部加减公式",
        "A/B 选项中一个选项是完整正确桥梁"
      ]
    },
    {
      "id": "recv_006_p2249_repeated_stuck_bound",
      "risk_type": "repeated_stuck_exit",
      "problem_ref": "P2249",
      "problem_title": "P2249 【深基13.例1】查找",
      "oj_source": "luogu",
      "problem_context": "给定非降序数组，多次查询某个数第一次出现的位置。学生反复卡在二分边界和候选保留。",
      "completion_status": "unfinished",
      "submission_result": "wa",
      "bottleneck_text": "我还是不懂 a[mid] >= x 的时候为什么不能直接丢掉 mid。",
      "reflection": "我试过 r = mid - 1，但样例里第一个位置会被跳过去。",
      "student_code": "while(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }",
      "handoff_payload": {
        "handoff_type": "checkin_reflection",
        "source": "aichat",
        "risk_type": "repeated_stuck_exit",
        "problem_ref": "P2249",
        "last_user_message": "我还是不懂 a[mid] >= x 的时候为什么不能直接丢掉 mid。",
        "suggested_focus": "用小例子拆开当前卡住的桥，记录卡点和已尝试路径。"
      },
      "expected_review_behavior": [
        "用一个小数组拆候选区间如何保留 mid",
        "不直接给出完整二分模板"
      ],
      "forbidden_review_behavior": [
        "完整给出二分模板代码",
        "只说继续想想而没有复盘定位"
      ]
    }
  ]
}
```

- [ ] **Step 4: Run schema tests to verify GREEN**

Run:

```bash
python3 -m unittest test_checkin_handoff_receiver_eval_cases_unit -v
```

Expected: pass with 2 tests.

- [ ] **Step 5: Commit**

```bash
git add docs/common/checkin_handoff_receiver_eval_cases_2026_04.json test_checkin_handoff_receiver_eval_cases_unit.py
git commit -m "Add checkin handoff receiver eval cases"
```

---

### Task 2: Hard Gate Tests And Implementation

**Files:**
- Create: `agent_learning/03_noi_agent/evals/checkin/__init__.py`
- Create: `agent_learning/03_noi_agent/evals/checkin/run_handoff_receiver_eval.py`
- Create: `agent_learning/03_noi_agent/test_checkin_handoff_receiver_eval_runner_unit.py`

- [ ] **Step 1: Write failing hard gate tests**

Create `test_checkin_handoff_receiver_eval_runner_unit.py` with these tests:

```python
import json
import tempfile
import unittest
from pathlib import Path

from evals.checkin import run_handoff_receiver_eval


class CheckinHandoffReceiverHardGateTests(unittest.TestCase):
    def case(self, case_id="recv_001_p3128_ac_unclear_lca", problem_ref="P3128", risk_type="ac_unclear_in_aichat"):
        return {
            "id": case_id,
            "risk_type": risk_type,
            "problem_ref": problem_ref,
            "problem_title": problem_ref,
            "oj_source": "luogu",
            "problem_context": "context",
            "completion_status": "independent",
            "submission_result": "accepted",
            "bottleneck_text": "这个卡点文字长度足够用于校验。",
            "reflection": "我已经试过手推。",
            "student_code": "",
            "handoff_payload": {
                "handoff_type": "checkin_reflection",
                "source": "aichat",
                "risk_type": risk_type,
                "problem_ref": problem_ref,
                "last_user_message": "我 AC 了但不懂。",
                "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。",
            },
            "expected_review_behavior": [],
            "forbidden_review_behavior": [],
        }

    def assertFailure(self, case, response_text, expected_failure):
        result = run_handoff_receiver_eval.evaluate_hard_response(case, response_text)
        self.assertFalse(result["passed"])
        self.assertIn(expected_failure, result["failures"])

    def test_hard_gate_flags_complete_code(self):
        response = "```cpp\n#include <bits/stdc++.h>\nint main(){return 0;}\n```"
        self.assertFailure(self.case(problem_ref="P2249"), response, "complete_code")

    def test_hard_gate_flags_three_code_like_lines_without_include(self):
        response = "for(int i=1;i<=n;i++){\n  if(a[i]>=x) ans=i;\n  return ans;\n}"
        self.assertFailure(self.case(problem_ref="P2249"), response, "complete_code")

    def test_hard_gate_flags_dp_state_definition(self):
        response = "这里 dp[x][y] = 从 (x,y) 出发能滑到的最长路径。"
        self.assertFailure(self.case(problem_ref="P1434"), response, "dp_state_definition")

    def test_hard_gate_flags_p3128_complete_formula_only_when_all_four_parts_appear(self):
        response = "完整公式是 cnt[u]++，cnt[v]++，cnt[lca]--，cnt[parent[lca]]--。"
        self.assertFailure(self.case(problem_ref="P3128"), response, "tree_difference_formula")

    def test_hard_gate_allows_partial_p3128_formula(self):
        result = run_handoff_receiver_eval.evaluate_hard_response(
            self.case(problem_ref="P3128"),
            "我们先只看端点：cnt[u]++ 这一项代表路径从 u 进入记录。",
        )
        self.assertTrue(result["passed"], result["failures"])

    def test_hard_gate_ignores_question_line_for_p3128_formula(self):
        result = run_handoff_receiver_eval.evaluate_hard_response(
            self.case(problem_ref="P3128"),
            "如果你写 cnt[u]++，cnt[v]++，cnt[lca]--，cnt[parent[lca]]--，这四处分别会抵消谁？",
        )
        self.assertTrue(result["passed"], result["failures"])

    def test_hard_gate_flags_complete_check_mid_leak(self):
        response = "check(mid) 就是扫描石头，判断每步至少 mid 时需要移走几块。"
        self.assertFailure(self.case(problem_ref="P2678", risk_type="repeated_stuck_exit"), response, "check_mid_complete_semantics")

    def test_hard_gate_flags_lazy_full_mechanism(self):
        response = "lazy 就是还没下传的区间增量，pushdown 时下传到左右儿子并更新子节点。"
        self.assertFailure(self.case(problem_ref="P3372"), response, "lazy_full_mechanism")

    def test_hard_gate_flags_ab_answer_shaped_dp_option(self):
        response = "A: dp[x][y] = 从(x,y)出发的最长路径;\nB: dp[x][y] = 到达(x,y)的最长路径;"
        self.assertFailure(self.case(problem_ref="P1434"), response, "ab_answer_leak")

    def test_hard_gate_flags_ab_answer_shaped_check_option(self):
        response = "A: check(mid) 扫描石头，判断每步至少 mid 时移走几块。\nB: check(mid) 找最短的一跳。"
        self.assertFailure(self.case(problem_ref="P2678", risk_type="repeated_stuck_exit"), response, "ab_answer_leak")

    def test_hard_gate_flags_live_aichat_continuation_at_start(self):
        response = "你先回答我：这个变量代表节点还是边？然后我继续提示。"
        self.assertFailure(self.case(problem_ref="P3128"), response, "live_aichat_continuation")

    def test_hard_gate_allows_short_question_after_receiver_positioning(self):
        response = "这次复盘先记录一个点：你卡在公共祖先附近的抵消。\n我们只看一条 1-2-3 的链。\nLCA 算几次？"
        result = run_handoff_receiver_eval.evaluate_hard_response(self.case(problem_ref="P3128"), response)
        self.assertTrue(result["passed"], result["failures"])
```

- [ ] **Step 2: Run hard gate tests to verify RED**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
python3 -m unittest test_checkin_handoff_receiver_eval_runner_unit.CheckinHandoffReceiverHardGateTests -v
```

Expected: import error because `evals.checkin.run_handoff_receiver_eval` does not exist.

- [ ] **Step 3: Create package and minimal hard gate implementation**

Create an empty package file:

```python
# evals/checkin/__init__.py
```

Create `evals/checkin/run_handoff_receiver_eval.py` with this implementation:

```python
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Callable

import review_engine
from evals.review import run_review_case_kimi_cli


DEFAULT_CASES_PATH = Path("docs/common/checkin_handoff_receiver_eval_cases_2026_04.json")
DEFAULT_OUTPUT_DIR = Path("evals/checkin/reports/receiver_latest")
ALLOWED_RISK_TYPES = {"ac_unclear_in_aichat", "repeated_stuck_exit"}
JudgeFn = Callable[[str], str]


def _compact_ws(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def _non_question_lines(text: str) -> list[str]:
    lines = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.endswith("?") or stripped.endswith("？"):
            continue
        lines.append(stripped)
    return lines


def _has_complete_code(text: str) -> bool:
    if re.search(r"#include\s*<", text) or re.search(r"\bint\s+main\s*\(", text):
        return True
    code_like = 0
    for line in (text or "").splitlines():
        stripped = line.strip()
        if re.search(r"(\{|\}|;|\bfor\s*\(|\bwhile\s*\(|\bif\s*\(|\breturn\b|\w+\s*=|\w+\s*\[.+?\])", stripped):
            code_like += 1
    return code_like >= 3


def _has_dp_state_definition(text: str) -> bool:
    pattern = (
        r"dp\s*\[\s*[a-zA-Z]\w*\s*\]\s*\[\s*[a-zA-Z]\w*\s*\]\s*"
        r"(?:=|表示|代表|定义为)\s*"
        r"[^。！？\n]{0,40}"
        r"(?:从\s*\(?\s*[a-zA-Z]\w*\s*,\s*[a-zA-Z]\w*\s*\)?\s*出发|出发)"
        r"[^。！？\n]{0,40}"
        r"(?:最长路|最长路径)"
    )
    return re.search(pattern, text or "", re.IGNORECASE) is not None


def _has_tree_difference_formula(text: str) -> bool:
    normalized = _compact_ws("\n".join(_non_question_lines(text)))
    endpoint_u = re.search(r"(?:cnt|diff|s|d)?\[\s*u\s*\]\+\+", normalized, re.IGNORECASE)
    endpoint_v = re.search(r"(?:cnt|diff|s|d)?\[\s*v\s*\]\+\+", normalized, re.IGNORECASE)
    lca_dec = re.search(r"(?:cnt|diff|s|d)?\[\s*lca\s*\](?:--|-=1)", normalized, re.IGNORECASE)
    parent_lca_dec = re.search(
        r"(?:cnt|diff|s|d)?\[\s*(?:parent|fa|father|p)\s*\[\s*lca\s*\]\s*\](?:--|-=1)",
        normalized,
        re.IGNORECASE,
    )
    return bool(endpoint_u and endpoint_v and lca_dec and parent_lca_dec)


CHECK_FULL_WORDS = ["每步至少", "移走几块", "能否达到", "扫描石头"]


def _has_complete_check_mid(text: str) -> bool:
    for line in (text or "").splitlines():
        if re.search(r"check\s*\(?\s*mid\s*\)?", line, re.IGNORECASE) and any(word in line for word in CHECK_FULL_WORDS):
            return True
    return False


def _has_lazy_full_mechanism(text: str) -> bool:
    normalized = text or ""
    defines_lazy = re.search(r"lazy\s*(?:就是|表示|代表|=|定义为)", normalized, re.IGNORECASE)
    propagation = re.search(r"(pushdown|下传到左右儿子|更新子节点|传给左右儿子)", normalized, re.IGNORECASE)
    return bool(defines_lazy and propagation)


def _has_ab_answer_leak(text: str) -> bool:
    lines = (text or "").splitlines()
    has_ab_shape = bool(re.search(r"(^|\n)\s*(?:-?\s*)A[:：.、]", text or "")) and bool(
        re.search(r"(^|\n)\s*(?:-?\s*)B[:：.、]", text or "")
    )
    has_inline_shape = "是不是" in (text or "") and "还是" in (text or "")
    if not (has_ab_shape or has_inline_shape):
        return False
    for line in lines:
        option = re.sub(r"^\s*-?\s*[AB][:：.、]\s*", "", line.strip(), flags=re.IGNORECASE)
        if re.search(r"dp\s*\[.+?\]\s*\[.+?\]\s*=", option) and (line.rstrip().endswith(";") or line != option):
            return True
        if re.search(r"check\s*\(?\s*mid\s*\)?", option, re.IGNORECASE) and any(word in option for word in CHECK_FULL_WORDS):
            return True
    return False


LIVE_AICHAT_PATTERNS = ["我们继续在 AIChat", "你先回答我", "然后我继续提示"]


def _chinese_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text or ""))


def _line_has_receiver_positioning(line: str) -> bool:
    return any(word in line for word in ["复盘", "记录", "卡", "这次", "小例子", "先看", "我们只看", "题目"])


def _has_live_aichat_continuation(text: str) -> bool:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    for index, line in enumerate(lines):
        if any(pattern in line for pattern in LIVE_AICHAT_PATTERNS):
            if line.endswith(("?", "？")) and _chinese_len(line) <= 20:
                prior_positioning = sum(1 for prior in lines[:index] if _line_has_receiver_positioning(prior))
                if prior_positioning >= 2:
                    continue
            return True
    return False


def evaluate_hard_response(case: dict, response_text: str) -> dict:
    failures = []
    if _has_complete_code(response_text):
        failures.append("complete_code")
    if _has_dp_state_definition(response_text):
        failures.append("dp_state_definition")
    if str(case.get("problem_ref", "")).upper() == "P3128" and _has_tree_difference_formula(response_text):
        failures.append("tree_difference_formula")
    if str(case.get("problem_ref", "")).upper() == "P2678" and _has_complete_check_mid(response_text):
        failures.append("check_mid_complete_semantics")
    if str(case.get("problem_ref", "")).upper() == "P3372" and _has_lazy_full_mechanism(response_text):
        failures.append("lazy_full_mechanism")
    if _has_ab_answer_leak(response_text):
        failures.append("ab_answer_leak")
    if _has_live_aichat_continuation(response_text):
        failures.append("live_aichat_continuation")
    return {
        "case_id": case["id"],
        "passed": not failures,
        "failures": failures,
        "response_chars": len(response_text or ""),
    }
```

- [ ] **Step 4: Run hard gate tests to verify GREEN**

Run:

```bash
python3 -m unittest test_checkin_handoff_receiver_eval_runner_unit.CheckinHandoffReceiverHardGateTests -v
```

Expected: all hard gate tests pass.

- [ ] **Step 5: Commit**

```bash
git add evals/checkin/__init__.py evals/checkin/run_handoff_receiver_eval.py test_checkin_handoff_receiver_eval_runner_unit.py
git commit -m "Add checkin receiver hard gate"
```

---

### Task 3: Runner Generation, Re-Evaluation, And Report

**Files:**
- Modify: `agent_learning/03_noi_agent/evals/checkin/run_handoff_receiver_eval.py`
- Modify: `agent_learning/03_noi_agent/test_checkin_handoff_receiver_eval_runner_unit.py`

- [ ] **Step 1: Add failing runner tests**

Append this test class to `test_checkin_handoff_receiver_eval_runner_unit.py`:

```python
class CheckinHandoffReceiverRunnerTests(unittest.TestCase):
    def write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def cases_data(self):
        case = CheckinHandoffReceiverHardGateTests().case()
        return {"version": "test", "suite": "checkin_handoff_receiver_quality", "rubric": {"llm_judge": []}, "cases": [case]}

    def fake_review_ok(self, **kwargs):
        return {
            "ok": True,
            "kind": "success",
            "review": {
                "diagnosis": "这次复盘先定位 LCA 附近的抵消点。",
                "problem_focus": "LCA 附近贡献为什么要抵消",
                "key_bridge": "先用一条短链看公共祖先被统计几次。",
                "guided_walkthrough": "1. 画 1-2-3。2. 标一条 1 到 3 的路径。3. 看节点 2 被累加几次。",
                "try_now": "只解释节点 2 在这条路径里被算了几次。",
                "next_action": "用短链复述 LCA 附近的抵消。",
            },
            "telemetry": {"model": "fake"},
        }

    def test_validate_cases_should_reject_mismatched_risk_type(self):
        data = self.cases_data()
        data["cases"][0]["handoff_payload"]["risk_type"] = "repeated_stuck_exit"
        with self.assertRaisesRegex(ValueError, "handoff_payload.risk_type"):
            run_handoff_receiver_eval.validate_cases(data)

    def test_generate_response_rows_should_call_generate_review_with_handoff_payload(self):
        captured = {}

        def fake_generate_review(**kwargs):
            captured.update(kwargs)
            return self.fake_review_ok(**kwargs)

        rows = run_handoff_receiver_eval.generate_response_rows(self.cases_data(), generate_review_fn=fake_generate_review)

        self.assertEqual(1, len(rows))
        self.assertEqual("recv_001_p3128_ac_unclear_lca", rows[0]["case_id"])
        self.assertIn("这次复盘先定位", rows[0]["response_text"])
        self.assertEqual("ac_unclear_in_aichat", captured["handoff_payload"]["risk_type"])
        self.assertEqual("P3128 [USACO15DEC] Max Flow P", captured["problem_title"])

    def test_generate_response_rows_should_capture_generation_failure(self):
        def fake_generate_review(**kwargs):
            return {"ok": False, "kind": "llm_unavailable", "message": "model down"}

        rows = run_handoff_receiver_eval.generate_response_rows(self.cases_data(), generate_review_fn=fake_generate_review)

        self.assertEqual("generation_failed:model down", rows[0]["error"])
        self.assertEqual("", rows[0]["response_text"])

    def test_run_suite_should_write_responses_summary_and_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            output_dir = tmp / "report"
            self.write_json(cases_path, self.cases_data())

            summary = run_handoff_receiver_eval.run_suite(
                cases_path=cases_path,
                output_dir=output_dir,
                generate_review_fn=self.fake_review_ok,
            )

            self.assertEqual(1, summary["hard_summary"]["passed_case_count"])
            self.assertTrue((output_dir / "responses.jsonl").exists())
            self.assertTrue((output_dir / "hard_summary.json").exists())
            self.assertTrue((output_dir / "suite_summary.json").exists())
            self.assertIn("Checkin Handoff Receiver Eval Report", (output_dir / "report.md").read_text(encoding="utf-8"))

    def test_run_suite_should_re_evaluate_existing_responses_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            responses_path = tmp / "responses.jsonl"
            output_dir = tmp / "report"
            self.write_json(cases_path, self.cases_data())
            responses_path.write_text(
                json.dumps(
                    {
                        "case_id": "recv_001_p3128_ac_unclear_lca",
                        "response_text": "这次复盘先定位 LCA 附近的抵消点。",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            summary = run_handoff_receiver_eval.run_suite(
                cases_path=cases_path,
                responses_path=responses_path,
                output_dir=output_dir,
            )

            self.assertEqual(1, summary["hard_summary"]["passed_case_count"])
```

- [ ] **Step 2: Run runner tests to verify RED**

Run:

```bash
python3 -m unittest test_checkin_handoff_receiver_eval_runner_unit.CheckinHandoffReceiverRunnerTests -v
```

Expected: failures for missing `validate_cases`, `generate_response_rows`, and `run_suite`.

- [ ] **Step 3: Implement case loading, validation, generation, hard summary, and report**

Append these functions to `evals/checkin/run_handoff_receiver_eval.py`:

```python
def load_cases(cases_path: Path = DEFAULT_CASES_PATH) -> dict:
    return json.loads(cases_path.read_text(encoding="utf-8"))


def load_responses(responses_path: Path) -> dict[str, str]:
    responses = {}
    for line_no, line in enumerate(responses_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        case_id = row.get("case_id") or row.get("id")
        response_text = row.get("response_text") or row.get("response") or row.get("text")
        if not case_id:
            raise ValueError(f"responses_jsonl line {line_no} missing case_id")
        if response_text is None:
            raise ValueError(f"responses_jsonl line {line_no} missing response_text")
        responses[str(case_id)] = str(response_text)
    return responses


def validate_cases(cases_data: dict) -> None:
    if cases_data.get("suite") != "checkin_handoff_receiver_quality":
        raise ValueError("suite must be checkin_handoff_receiver_quality")
    for case in cases_data.get("cases", []):
        case_id = case.get("id", "<missing id>")
        for field in ["id", "risk_type", "problem_ref", "problem_title", "oj_source", "problem_context", "completion_status", "submission_result", "bottleneck_text", "reflection", "handoff_payload"]:
            if field not in case:
                raise ValueError(f"{case_id} missing {field}")
        if case["risk_type"] not in ALLOWED_RISK_TYPES:
            raise ValueError(f"{case_id} invalid risk_type: {case['risk_type']}")
        payload = case["handoff_payload"]
        if payload.get("handoff_type") != "checkin_reflection":
            raise ValueError(f"{case_id} handoff_payload.handoff_type must be checkin_reflection")
        if payload.get("source") != "aichat":
            raise ValueError(f"{case_id} handoff_payload.source must be aichat")
        if payload.get("risk_type") != case["risk_type"]:
            raise ValueError(f"{case_id} handoff_payload.risk_type must match risk_type")
        for field in ["problem_ref", "problem_title", "bottleneck_text"]:
            if not str(case.get(field, "")).strip():
                raise ValueError(f"{case_id} {field} must be non-empty")
        if not str(payload.get("suggested_focus", "")).strip():
            raise ValueError(f"{case_id} handoff_payload.suggested_focus must be non-empty")


def _review_to_text(review: dict) -> str:
    fields = ["diagnosis", "problem_focus", "main_block", "key_bridge", "visual_hint", "guided_walkthrough", "try_now", "next_action", "transfer_signal"]
    return "\n".join(str(review.get(field, "")).strip() for field in fields if str(review.get(field, "")).strip())


def generate_response_rows(cases_data: dict, generate_review_fn=review_engine.generate_review, limit: int | None = None, progress_stream=None) -> list[dict]:
    validate_cases(cases_data)
    cases = cases_data.get("cases", [])
    if limit is not None:
        cases = cases[:limit]
    rows = []
    total = len(cases)
    for index, case in enumerate(cases, 1):
        case_id = case["id"]
        if progress_stream is not None:
            progress_stream.write(f"CASE_START index={index} total={total} case_id={case_id}\n")
            progress_stream.flush()
        row = {"case_id": case_id, "problem_ref": case.get("problem_ref", ""), "risk_type": case.get("risk_type", "")}
        try:
            result = generate_review_fn(
                problem_title=case["problem_title"],
                oj_source=case["oj_source"],
                completion_status=case["completion_status"],
                bottleneck_text=case["bottleneck_text"],
                error_types=case.get("error_types") or ["未说明"],
                reflection=case.get("reflection", ""),
                problem_context=case.get("problem_context", ""),
                problem_tags=case.get("problem_tags") or [],
                chat_context_summary=case.get("chat_context_summary") or case["handoff_payload"].get("suggested_focus", ""),
                submission_result=case.get("submission_result"),
                student_code=case.get("student_code", ""),
                handoff_payload=case["handoff_payload"],
            )
            if not result.get("ok"):
                message = result.get("message") or result.get("kind") or "unknown"
                row.update({"response_text": "", "error": f"generation_failed:{message}"})
                if progress_stream is not None:
                    progress_stream.write(f"CASE_ERROR index={index} total={total} case_id={case_id} error=generation_failed\n")
                    progress_stream.flush()
            else:
                row.update({"response_text": _review_to_text(result.get("review") or {}), "error": ""})
                if progress_stream is not None:
                    progress_stream.write(f"CASE_DONE index={index} total={total} case_id={case_id}\n")
                    progress_stream.flush()
        except Exception as exc:
            row.update({"response_text": "", "error": f"generation_failed:{exc}"})
            if progress_stream is not None:
                progress_stream.write(f"CASE_ERROR index={index} total={total} case_id={case_id} error={str(exc)[:120]}\n")
                progress_stream.flush()
        rows.append(row)
    return rows


def write_response_rows(output_path: Path, rows: list[dict]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def evaluate_hard_responses(cases_data: dict, responses: dict[str, str]) -> dict:
    validate_cases(cases_data)
    results = []
    for case in cases_data.get("cases", []):
        case_id = case["id"]
        if case_id not in responses:
            results.append({"case_id": case_id, "passed": False, "failures": ["missing_response"], "response_chars": 0})
            continue
        results.append(evaluate_hard_response(case, responses[case_id]))
    case_count = len(results)
    failed_case_count = sum(1 for result in results if not result["passed"])
    passed_case_count = case_count - failed_case_count
    return {
        "case_count": case_count,
        "passed_case_count": passed_case_count,
        "failed_case_count": failed_case_count,
        "pass_rate": round(passed_case_count / case_count, 3) if case_count else 0.0,
        "results": results,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_markdown_report(hard_summary: dict, judge_summary: dict | None = None, responses_path: Path | None = None) -> str:
    lines = ["# Checkin Handoff Receiver Eval Report", ""]
    if responses_path:
        lines.extend(["## Inputs", "", f"- responses: `{responses_path}`", ""])
    lines.extend([
        "## Hard Gate",
        "",
        f"- Cases: {hard_summary.get('case_count', 0)}",
        f"- Passed: {hard_summary.get('passed_case_count', 0)}",
        f"- Failed: {hard_summary.get('failed_case_count', 0)}",
        f"- Hard gate pass rate: {_pct(hard_summary.get('pass_rate', 0.0))}",
        "",
    ])
    failures = [result for result in hard_summary.get("results", []) if not result.get("passed")]
    if failures:
        lines.extend(["### Hard Gate Failures", ""])
        for result in failures:
            lines.append(f"- `{result.get('case_id')}`: {', '.join(result.get('failures', [])) or 'unknown'}")
        lines.append("")
    if judge_summary is None:
        lines.extend(["## Judge Gate", "", "- Not run.", ""])
    else:
        lines.extend([
            "## Judge Gate",
            "",
            f"- Cases: {judge_summary.get('case_count', 0)}",
            f"- Judge coverage: {judge_summary.get('coverage', 'unknown')} ({judge_summary.get('case_count', 0)}/{judge_summary.get('total_case_count', 0)} cases)",
            f"- Passed: {judge_summary.get('passed_case_count', 0)}",
            f"- Failed: {judge_summary.get('failed_case_count', 0)}",
            f"- Judge pass rate: {_pct(judge_summary.get('pass_rate', 0.0))}",
            f"- Average judge score: {judge_summary.get('average_score', 0.0)} / 3",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _limit_cases_data(cases_data: dict, limit: int | None) -> dict:
    if limit is None:
        return cases_data
    limited = dict(cases_data)
    limited["cases"] = list(cases_data.get("cases", []))[:limit]
    return limited


def _validate_judge_coverage(with_judge: bool, raw_case_count: int, eval_case_count: int, allow_judge_smoke: bool) -> None:
    if with_judge and eval_case_count < raw_case_count and not allow_judge_smoke:
        raise ValueError(
            f"limited judge smoke is disabled by default: judging {eval_case_count}/{raw_case_count} cases. "
            "Run without --limit for full judge coverage, or pass --allow-judge-smoke for an explicit smoke check."
        )


def run_suite(
    cases_path: Path = DEFAULT_CASES_PATH,
    responses_path: Path | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    with_judge: bool = False,
    generate_review_fn=review_engine.generate_review,
    judge_fn: JudgeFn = run_review_case_kimi_cli._run_kimi_cli,
    limit: int | None = None,
    allow_judge_smoke: bool = False,
    progress_stream=None,
    judge_timeout_seconds: int | None = None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_cases_data = load_cases(cases_path)
    validate_cases(raw_cases_data)
    cases_data = _limit_cases_data(raw_cases_data, limit)
    _validate_judge_coverage(with_judge, len(raw_cases_data.get("cases", [])), len(cases_data.get("cases", [])), allow_judge_smoke)
    eval_cases_path = cases_path
    if limit is not None:
        eval_cases_path = output_dir / "cases.limited.json"
        _write_json(eval_cases_path, cases_data)

    if responses_path is None:
        responses_path = output_dir / "responses.jsonl"
        rows = generate_response_rows(cases_data, generate_review_fn=generate_review_fn, progress_stream=progress_stream)
        write_response_rows(responses_path, rows)

    hard_summary = evaluate_hard_responses(cases_data, load_responses(responses_path))
    _write_json(output_dir / "hard_summary.json", hard_summary)

    judge_summary = None
    summary = {
        "cases_path": str(eval_cases_path),
        "responses_path": str(responses_path),
        "output_dir": str(output_dir),
        "with_judge": with_judge,
        "judge_coverage": "not_run",
        "hard_summary": hard_summary,
        "judge_summary": judge_summary,
    }
    _write_json(output_dir / "suite_summary.json", summary)
    (output_dir / "report.md").write_text(build_markdown_report(hard_summary, judge_summary=judge_summary, responses_path=responses_path), encoding="utf-8")
    return summary
```

- [ ] **Step 4: Run runner tests to verify GREEN**

Run:

```bash
python3 -m unittest test_checkin_handoff_receiver_eval_runner_unit.CheckinHandoffReceiverRunnerTests -v
```

Expected: all runner tests pass.

- [ ] **Step 5: Commit**

```bash
git add evals/checkin/run_handoff_receiver_eval.py test_checkin_handoff_receiver_eval_runner_unit.py
git commit -m "Add checkin receiver eval runner"
```

---

### Task 4: Judge Gate And CLI

**Files:**
- Modify: `agent_learning/03_noi_agent/evals/checkin/run_handoff_receiver_eval.py`
- Modify: `agent_learning/03_noi_agent/test_checkin_handoff_receiver_eval_runner_unit.py`

- [ ] **Step 1: Add failing judge and CLI tests**

Append this test class to `test_checkin_handoff_receiver_eval_runner_unit.py`:

```python
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from unittest.mock import patch


class CheckinHandoffReceiverJudgeTests(unittest.TestCase):
    def cases_data(self):
        case = CheckinHandoffReceiverHardGateTests().case()
        case["expected_review_behavior"] = ["验证一个理解点"]
        case["forbidden_review_behavior"] = ["完整树差分公式"]
        return {"version": "test", "suite": "checkin_handoff_receiver_quality", "rubric": {"llm_judge": ["按 checkin_reflection 评审"]}, "cases": [case]}

    def test_build_judge_prompt_should_include_receiver_contract(self):
        prompt = run_handoff_receiver_eval.build_judge_prompt(
            self.cases_data()["cases"][0],
            "这次复盘先定位 LCA 附近的抵消点。",
            self.cases_data()["rubric"],
        )
        self.assertIn("checkin_reflection", prompt)
        self.assertIn("不是普通 AIChat", prompt)
        self.assertIn("AC-but-unclear", prompt)
        self.assertIn("完整树差分公式", prompt)

    def test_evaluate_judge_should_emit_progress_and_score(self):
        progress = StringIO()
        summary = run_handoff_receiver_eval.evaluate_judge(
            self.cases_data(),
            {"recv_001_p3128_ac_unclear_lca": "这次复盘先定位 LCA 附近的抵消点。"},
            judge_fn=lambda prompt: '{"pass": true, "score": 3, "reasons": ["ok"], "failed_criteria": []}',
            progress_stream=progress,
        )
        self.assertEqual(1, summary["passed_case_count"])
        self.assertIn("JUDGE_START index=1 total=1 case_id=recv_001_p3128_ac_unclear_lca", progress.getvalue())
        self.assertIn("JUDGE_DONE index=1 total=1 case_id=recv_001_p3128_ac_unclear_lca score=3 passed=True ok=True", progress.getvalue())

    def test_run_suite_should_run_judge_and_apply_timeout(self):
        captured_timeout = []
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            output_dir = tmp / "report"
            cases_path.write_text(json.dumps(self.cases_data(), ensure_ascii=False), encoding="utf-8")

            def fake_review(**kwargs):
                return CheckinHandoffReceiverRunnerTests().fake_review_ok(**kwargs)

            def fake_judge(prompt):
                captured_timeout.append(os.environ.get("REVIEW_EVAL_KIMI_TIMEOUT_SECONDS"))
                return '{"pass": true, "score": 3, "reasons": ["ok"], "failed_criteria": []}'

            summary = run_handoff_receiver_eval.run_suite(
                cases_path=cases_path,
                output_dir=output_dir,
                with_judge=True,
                generate_review_fn=fake_review,
                judge_fn=fake_judge,
                judge_timeout_seconds=12,
            )

            self.assertEqual(1, summary["judge_summary"]["passed_case_count"])
            self.assertTrue((output_dir / "judge_summary.json").exists())
            self.assertIn("Judge pass rate: 100.0%", (output_dir / "report.md").read_text(encoding="utf-8"))

        self.assertEqual(["12"], captured_timeout)

    def test_main_should_return_clear_error_for_limited_judge_without_smoke(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_data = self.cases_data()
            cases_data["cases"].append({**cases_data["cases"][0], "id": "recv_second"})
            cases_path = tmp / "cases.json"
            cases_path.write_text(json.dumps(cases_data, ensure_ascii=False), encoding="utf-8")
            stderr = StringIO()
            with redirect_stderr(stderr), redirect_stdout(StringIO()):
                exit_code = run_handoff_receiver_eval.main(
                    ["--cases", str(cases_path), "--output-dir", str(tmp / "out"), "--with-judge", "--limit", "1"]
                )
        self.assertEqual(2, exit_code)
        self.assertIn("limited judge smoke", stderr.getvalue())
```

- [ ] **Step 2: Run judge tests to verify RED**

Run:

```bash
python3 -m unittest test_checkin_handoff_receiver_eval_runner_unit.CheckinHandoffReceiverJudgeTests -v
```

Expected: failures for missing `build_judge_prompt`, `evaluate_judge`, and `main`.

- [ ] **Step 3: Implement judge helpers and CLI**

Add or update these functions in `evals/checkin/run_handoff_receiver_eval.py`:

```python
def build_judge_prompt(case: dict, response_text: str, rubric: dict) -> str:
    criteria_lines = "\n".join(f"{idx}. {item}" for idx, item in enumerate(rubric.get("llm_judge", []), 1))
    expected_lines = "\n".join(f"- {item}" for item in case.get("expected_review_behavior", []))
    forbidden_lines = "\n".join(f"- {item}" for item in case.get("forbidden_review_behavior", []))
    payload = json.dumps(case.get("handoff_payload", {}), ensure_ascii=False)
    return "\n".join(
        [
            "你是打卡复盘接收侧质量评委。请判断 NOI 学习系统的复盘输出是否符合 AIChat handoff 后的 checkin_reflection 行为。",
            "只输出 JSON，不要输出 Markdown。",
            "",
            "输出格式：",
            '{"pass": true|false, "score": 0-3, "reasons": ["...", "..."], "failed_criteria": ["...", "..."]}',
            "",
            "评分含义：",
            "3 = 明确按 checkin_reflection 接住学生；只验证一个理解点或拆一个桥；贴题；没有泄露完整桥。",
            "2 = 安全但偏泛，或者像普通复盘，receiver-specific 价值不足。",
            "1 = 没泄题，但没有形成有效理解验证或卡点拆解。",
            "0 = 泄露完整解法、完整代码、完整公式、完整状态、完整 check，或继续普通 AIChat 式追问。",
            "",
            "关键边界：",
            "- 这是 checkin_reflection，不是普通 AIChat。",
            "- Checkin 可以比 AIChat 更结构化，也可以给一个 3-5 节点或小输入例子。",
            "- AC-but-unclear 的目标是验证理解，不是重讲完整题解。",
            "- repeated-stuck 的目标是拆一个卡点，不是给完整路线。",
            "- 缺少复盘定位、卡点记录、理解验证或小例子属于 judge 扣分，不属于 hard gate。",
            "- 仍禁止完整状态、完整转移、完整 check 函数、完整树差分公式和完整代码。",
            "",
            "通用评审标准：",
            criteria_lines or "- 是否像 checkin receiver\n- 是否贴题\n- 是否只推进一个理解点或卡点桥",
            "",
            f"case_id: {case.get('id', '')}",
            f"risk_type: {case.get('risk_type', '')}",
            f"problem_ref: {case.get('problem_ref', '')}",
            f"problem_context: {case.get('problem_context', '')}",
            f"bottleneck_text: {case.get('bottleneck_text', '')}",
            f"reflection: {case.get('reflection', '')}",
            f"handoff_payload: {payload}",
            "",
            "该 case 的期望行为：",
            expected_lines or "- 无",
            "",
            "该 case 的禁止行为：",
            forbidden_lines or "- 无",
            "",
            "复盘实际输出：",
            response_text,
        ]
    )


def extract_judge_result(output: str) -> dict:
    cleaned = run_review_case_kimi_cli._strip_json_fence(output or "")
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return {"ok": False, "pass": False, "score": 0, "reasons": [f"invalid_json: {exc}"], "failed_criteria": ["invalid_json"], "raw_output": cleaned[:1000]}
    score = parsed.get("score")
    passed = parsed.get("pass")
    if not isinstance(passed, bool) or not isinstance(score, int) or score < 0 or score > 3:
        return {"ok": False, "pass": False, "score": 0, "reasons": ["invalid_schema"], "failed_criteria": ["invalid_schema"], "raw_output": cleaned[:1000]}
    reasons = parsed.get("reasons") or []
    failed_criteria = parsed.get("failed_criteria") or []
    return {
        "ok": True,
        "pass": passed,
        "score": score,
        "reasons": [str(reason) for reason in (reasons if isinstance(reasons, list) else [reasons])],
        "failed_criteria": [str(item) for item in (failed_criteria if isinstance(failed_criteria, list) else [failed_criteria])],
    }


def judge_response(case: dict, response_text: str, rubric: dict, judge_fn: JudgeFn = run_review_case_kimi_cli._run_kimi_cli) -> dict:
    try:
        return extract_judge_result(judge_fn(build_judge_prompt(case, response_text, rubric)))
    except Exception as exc:
        return {"ok": False, "pass": False, "score": 0, "reasons": [f"judge_failed: {exc}"], "failed_criteria": ["judge_failed"]}


def _write_progress(progress_stream, event: str, **fields) -> None:
    if progress_stream is None:
        return
    progress_stream.write(" ".join([event] + [f"{key}={value}" for key, value in fields.items()]) + "\n")
    progress_stream.flush()


def evaluate_judge(cases_data: dict, responses: dict[str, str], judge_fn: JudgeFn = run_review_case_kimi_cli._run_kimi_cli, progress_stream=None) -> dict:
    validate_cases(cases_data)
    rubric = cases_data.get("rubric", {})
    results = []
    cases = cases_data.get("cases", [])
    total = len(cases)
    for index, case in enumerate(cases, 1):
        case_id = case["id"]
        _write_progress(progress_stream, "JUDGE_START", index=index, total=total, case_id=case_id)
        response_text = responses.get(case_id)
        if response_text is None:
            judged = {"ok": False, "pass": False, "score": 0, "reasons": ["missing_response"], "failed_criteria": ["missing_response"]}
        else:
            judged = judge_response(case, response_text, rubric, judge_fn=judge_fn)
        passed = bool(judged["ok"] and judged["pass"] and judged["score"] >= 3)
        result = {"case_id": case_id, "passed": passed, "score": judged["score"], "ok": judged["ok"], "reasons": judged["reasons"], "failed_criteria": judged["failed_criteria"]}
        results.append(result)
        _write_progress(progress_stream, "JUDGE_DONE", index=index, total=total, case_id=case_id, score=result["score"], passed=result["passed"], ok=result["ok"])
    case_count = len(results)
    passed_case_count = sum(1 for result in results if result["passed"])
    return {
        "case_count": case_count,
        "passed_case_count": passed_case_count,
        "failed_case_count": case_count - passed_case_count,
        "pass_rate": round(passed_case_count / case_count, 3) if case_count else 0.0,
        "average_score": round(sum(result["score"] for result in results) / case_count, 3) if case_count else 0.0,
        "results": results,
    }
```

Update `run_suite` so the `with_judge` block becomes:

```python
    judge_summary = None
    if with_judge:
        previous_timeout = os.environ.get("REVIEW_EVAL_KIMI_TIMEOUT_SECONDS")
        if judge_timeout_seconds is not None:
            os.environ["REVIEW_EVAL_KIMI_TIMEOUT_SECONDS"] = str(judge_timeout_seconds)
        try:
            judge_summary = evaluate_judge(cases_data, load_responses(responses_path), judge_fn=judge_fn, progress_stream=progress_stream)
        finally:
            if judge_timeout_seconds is not None:
                if previous_timeout is None:
                    os.environ.pop("REVIEW_EVAL_KIMI_TIMEOUT_SECONDS", None)
                else:
                    os.environ["REVIEW_EVAL_KIMI_TIMEOUT_SECONDS"] = previous_timeout
        judge_summary["coverage"] = "smoke" if len(cases_data.get("cases", [])) < len(raw_cases_data.get("cases", [])) else "full"
        judge_summary["total_case_count"] = len(raw_cases_data.get("cases", []))
        _write_json(output_dir / "judge_summary.json", judge_summary)
```

Update summary assignment after judge:

```python
    summary = {
        "cases_path": str(eval_cases_path),
        "responses_path": str(responses_path),
        "output_dir": str(output_dir),
        "with_judge": with_judge,
        "judge_coverage": "not_run" if not with_judge else judge_summary["coverage"],
        "hard_summary": hard_summary,
        "judge_summary": judge_summary,
    }
```

Add CLI helpers:

```python
def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run checkin handoff receiver quality eval.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--responses-jsonl", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--with-judge", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--allow-judge-smoke", action="store_true")
    parser.add_argument("--judge-timeout-seconds", type=int)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        summary = run_suite(
            cases_path=args.cases,
            responses_path=args.responses_jsonl,
            output_dir=args.output_dir,
            with_judge=args.with_judge,
            limit=args.limit,
            allow_judge_smoke=args.allow_judge_smoke,
            progress_stream=sys.stderr,
            judge_timeout_seconds=args.judge_timeout_seconds,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output_dir": summary["output_dir"], "report": str(Path(summary["output_dir"]) / "report.md")}, ensure_ascii=False))
    hard_failed = summary["hard_summary"]["failed_case_count"] > 0
    judge_failed = bool(summary["judge_summary"] and summary["judge_summary"]["failed_case_count"] > 0)
    return 1 if hard_failed or judge_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run judge tests to verify GREEN**

Run:

```bash
python3 -m unittest test_checkin_handoff_receiver_eval_runner_unit.CheckinHandoffReceiverJudgeTests -v
```

Expected: all judge tests pass.

- [ ] **Step 5: Run all receiver unit tests**

Run:

```bash
python3 -m unittest test_checkin_handoff_receiver_eval_cases_unit test_checkin_handoff_receiver_eval_runner_unit -v
```

Expected: all receiver eval tests pass.

- [ ] **Step 6: Commit**

```bash
git add evals/checkin/run_handoff_receiver_eval.py test_checkin_handoff_receiver_eval_runner_unit.py
git commit -m "Add judge support for checkin receiver eval"
```

---

### Task 5: Run Test Integration

**Files:**
- Modify: `agent_learning/03_noi_agent/run_test.sh`

- [ ] **Step 1: Write the failing integration expectation manually**

Run the current syntax compilation command with the new module added manually:

```bash
python3 -m py_compile evals/checkin/run_handoff_receiver_eval.py
```

Expected: pass after Tasks 2-4.

Run the current full backend unit selection with the new tests added manually:

```bash
python3 -m unittest \
  test_checkin_handoff_receiver_eval_cases_unit.py \
  test_checkin_handoff_receiver_eval_runner_unit.py
```

Expected: pass.

- [ ] **Step 2: Modify `run_test.sh`**

In the `[1/7] Python 语法检查...` line, append:

```bash
evals/checkin/run_handoff_receiver_eval.py
```

In the `[2/7] 核心后端回归...` unittest list, append:

```bash
  test_checkin_handoff_receiver_eval_cases_unit.py \
  test_checkin_handoff_receiver_eval_runner_unit.py \
```

- [ ] **Step 3: Run full regression**

Run:

```bash
bash run_test.sh
```

Expected:

- Python syntax check passes.
- Core backend regression includes the new tests.
- Vite build passes.
- Frontend Node tests pass.
- Frontend syntax check passes.

- [ ] **Step 4: Commit**

```bash
git add run_test.sh
git commit -m "Include checkin receiver eval in regression"
```

---

### Task 6: Real Receiver Eval And Baseline Update

**Files:**
- Modify: `agent_learning/03_noi_agent/docs/common/current_validation_baseline.md`

- [ ] **Step 1: Run real receiver smoke without judge**

Run:

```bash
python3 -m evals.checkin.run_handoff_receiver_eval \
  --output-dir evals/checkin/reports/receiver_20260416_smoke \
  --limit 2
```

Expected:

- Exit code 0.
- `evals/checkin/reports/receiver_20260416_smoke/report.md` exists.
- Hard gate cases: 2.
- Hard gate failed: 0.

- [ ] **Step 2: Run real full receiver hard gate**

Run:

```bash
python3 -m evals.checkin.run_handoff_receiver_eval \
  --output-dir evals/checkin/reports/receiver_20260416_full_hard
```

Expected:

- Exit code 0.
- Hard gate cases: 6.
- Hard gate failed: 0.

If hard gate fails, inspect `responses.jsonl` and `hard_summary.json`. Fix only if the failure is a real implementation bug or prompt leak. If the failure is a bad hard-gate approximation, tighten the hard gate test and implementation before rerunning.

- [ ] **Step 3: Run real full receiver judge**

Run:

```bash
python3 -m evals.checkin.run_handoff_receiver_eval \
  --responses-jsonl evals/checkin/reports/receiver_20260416_full_hard/responses.jsonl \
  --output-dir evals/checkin/reports/receiver_20260416_full_judge_t90 \
  --with-judge \
  --judge-timeout-seconds 90
```

Expected:

- Exit code 0 if all six judge cases pass.
- If exit code 1, inspect `judge_summary.json`.
- No case may score 0 or 1 for v0 release.
- Score 2 requires manual review and a decision: tune prompt, tune case expectation, or accept as known limitation in the baseline.

- [ ] **Step 4: Update validation baseline**

Append a dated section to `docs/common/current_validation_baseline.md`:

```markdown
## 2026-04-16 Checkin Handoff Receiver Quality Gate

- Spec: `docs/superpowers/specs/2026-04-16-checkin-handoff-receiver-quality-gate-design.md`
- Plan: `docs/superpowers/plans/2026-04-16-checkin-handoff-receiver-quality-gate-implementation-plan.md`
- Hard report: `evals/checkin/reports/receiver_20260416_full_hard/report.md`
- Judge report: `evals/checkin/reports/receiver_20260416_full_judge_t90/report.md`
- Expected result: hard gate 6/6, judge gate has no 0/1 scores.
- Scope: receiver-side generated checkin review after AIChat handoff only.
```

If judge gate is 6/6, replace the expected result line with the actual result:

```markdown
- Result: hard gate 6/6, judge gate 6/6, average judge score X / 3.
```

- [ ] **Step 5: Run final regression**

Run:

```bash
bash run_test.sh
```

Expected: full regression passes.

- [ ] **Step 6: Commit**

```bash
git add docs/common/current_validation_baseline.md evals/checkin/reports/receiver_20260416_full_hard evals/checkin/reports/receiver_20260416_full_judge_t90
git commit -m "Record checkin receiver eval baseline"
```

If report directories are ignored by git, commit only the baseline doc and leave generated reports untracked or ignored according to repository policy.

---

## Final Verification

Run these commands before marking implementation complete:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
python3 -m unittest test_checkin_handoff_receiver_eval_cases_unit test_checkin_handoff_receiver_eval_runner_unit -v
python3 -m evals.checkin.run_handoff_receiver_eval --output-dir evals/checkin/reports/receiver_20260416_full_hard
bash run_test.sh
git status --short
```

Expected:

- Receiver unit tests pass.
- Real receiver hard gate exits 0.
- Full regression exits 0.
- Git status is clean after final commit.

Do not claim v0 complete if any generated checkin receiver case has hard gate failure or judge score 0/1.
