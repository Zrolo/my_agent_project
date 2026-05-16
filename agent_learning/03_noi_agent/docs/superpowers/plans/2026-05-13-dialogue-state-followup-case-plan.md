# Dialogue-State Follow-up Case Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a v3 dialogue-state held-out draft that adds follow-up tutoring turns, scaffold-followability labels, evidence quotes, confidence, and review workbooks without overwriting v2.

**Architecture:** Keep v2 as the real-problem source foundation. Add a separate v3 generator that transforms selected v2 rows into initial/follow-up dialogue-state rows with fixed prior AI scaffold context. Add a v3 validator and workbook exports so coach review can verify followability labels before any response-generation experiment.

**Tech Stack:** Python standard library, `openpyxl`, existing `evals.aichat` scripts, `unittest`, JSONL, XLSX.

---

## File Structure

- Create `evals/aichat/generate_dialogue_state_v3_50.py`
  - Reads `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`.
  - Writes `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`.
  - Writes `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`.
  - Writes bilingual generation reports.
  - Does not overwrite v2.

- Create `evals/aichat/validate_dialogue_state_v3_dataset.py`
  - Validates required v3 fields and followability evidence.
  - Reports context type, followability, expected tutor move, confidence, and low-confidence counts.

- Modify `evals/aichat/coach_labeling_schema_v2.py`
  - Adds optional dialogue-state columns so coach labeling workbooks can show v3 fields.

- Modify `evals/aichat/export_coach_seed_labeling_workbook_v2.py`
  - Carries v3 fields from JSONL into coach workbook rows when present.

- Modify `evals/aichat/export_coach_response_review_workbook_xlsx.py`
  - Ensures response-review workbooks can show `prior_ai_scaffold`, `student_reply_to_prior_scaffold`, `student_scaffold_followability`, and `expected_tutor_move` when present.

- Create `test_dialogue_state_v3_generation_unit.py`
  - Tests v3 generator behavior and non-overwrite guarantees.

- Create `test_dialogue_state_v3_validation_unit.py`
  - Tests v3 validation errors and summary distributions.

- Modify `test_coach_seed_labeling_v2_workbook_unit.py`
  - Tests optional v3 columns are exported.

- Modify `test_coach_response_review_xlsx_unit.py`
  - Tests optional v3 context columns are present in response review workbook.

- Create `docs/research/dialogue_state_v3_generation_report_20260513.zh.md`
- Create `docs/research/dialogue_state_v3_generation_report_20260513.md`
- Modify `docs/research/index.md`
  - Adds links to v3 reports after implementation.

---

## Task 1: Add v3 generator tests first

**Files:**
- Create: `test_dialogue_state_v3_generation_unit.py`
- Later Create: `evals/aichat/generate_dialogue_state_v3_50.py`

- [ ] **Step 1: Write failing tests for v3 generation**

Create `test_dialogue_state_v3_generation_unit.py`:

```python
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

from evals.aichat import generate_dialogue_state_v3_50


def _v2_case(idx: int, bucket: str = "predicate_check_semantics") -> dict:
    return {
        "case_id": f"heldout_v2_luogu_{idx:03d}",
        "id": f"heldout_v2_luogu_{idx:03d}",
        "category": bucket,
        "bridge_bucket": bucket,
        "bridge_bucket_zh": "判定条件/check",
        "problem_ref": f"luogu_p{1000 + idx}_{bucket}",
        "problem_source_platform": "luogu",
        "problem_source_id": f"P{1000 + idx}",
        "problem_source_url": f"https://www.luogu.com.cn/problem/P{1000 + idx}",
        "problem_statement": f"题目：样例题 {idx}\n题意摘录：给定若干数据，要求判断候选答案是否满足限制。",
        "problem_statement_public_summary": f"洛谷 P{1000 + idx}《样例题 {idx}》：判断候选答案是否满足限制。",
        "problem_statement_rights_note": "local review only",
        "problem_statement_access_level": "local_review_only",
        "problem_title": f"样例题 {idx}",
        "problem_tags": ["二分"],
        "student_message": "check 该判什么？",
        "student_message_length_bucket": "short",
        "problem_context": f"洛谷 P{1000 + idx}《样例题 {idx}》：判断候选答案是否满足限制。",
        "recent_dialogue": "N/A",
        "recent_dialogue_bucket": "none",
        "student_code_excerpt": "N/A",
        "student_known_state": "学生知道可能要判断候选值。",
        "missing_bridge": "缺少把候选值、限制和可行性方向对应起来的关系。",
        "allowed_help_level": "L2",
        "forbidden_content": ["no_complete_check_condition"],
        "success_criteria": ["回复让学生判断 true/false 的含义。"],
        "review_notes_for_coach": "draft",
        "reference_label_status": "draft_needs_coach_review",
        "primary_bridge_family": "predicate_check_bridge",
        "primary_bridge_subtype_id": "predicate.feasibility_truth_direction",
        "registered_focus_id": "check_truth_direction",
        "algorithm_topic_l1": "binary_search",
    }


class DialogueStateV3GenerationTests(unittest.TestCase):
    def test_build_dialogue_state_cases_adds_followup_fields(self):
        v2_rows = [_v2_case(i) for i in range(1, 51)]

        cases = generate_dialogue_state_v3_50.build_dialogue_state_cases(v2_rows)

        self.assertEqual(50, len(cases))
        self.assertEqual(50, len({row["case_id"] for row in cases}))
        self.assertTrue(all(row["case_id"].startswith("dialogue_v3_") for row in cases))
        self.assertTrue(any(row["turn_position"] == "followup" for row in cases))
        for row in cases:
            self.assertIn(row["turn_position"], {"initial", "followup"})
            self.assertIn("context_type", row)
            self.assertIn("fixed_recent_dialogue_source", row)
            if row["turn_position"] == "followup":
                self.assertIn(row["student_scaffold_followability"], {"F1", "F2", "F3", "F4"})
                self.assertIn(row["expected_tutor_move"], {"advance", "clarify", "micro_step", "prerequisite_repair", "safe_redirect"})
                self.assertIn(row["followability_label_confidence"], {"high", "medium", "low"})
                self.assertTrue(row["followability_evidence_quote"].strip())
                self.assertIn(row["followability_evidence_quote"], row["student_reply_to_prior_scaffold"])
                self.assertIn("AI：", row["recent_dialogue"])
                self.assertIn("学生：", row["recent_dialogue"])

    def test_default_distribution_is_followup_majority(self):
        v2_rows = [_v2_case(i) for i in range(1, 51)]

        cases = generate_dialogue_state_v3_50.build_dialogue_state_cases(v2_rows)
        context_counts = Counter(row["context_type"] for row in cases)
        followability_counts = Counter(row.get("student_scaffold_followability", "NA") for row in cases)

        self.assertEqual(10, context_counts["initial_question"])
        self.assertGreaterEqual(sum(count for context, count in context_counts.items() if context != "initial_question"), 40)
        self.assertEqual(7, followability_counts["F1"])
        self.assertEqual(8, followability_counts["F2"])
        self.assertEqual(7, followability_counts["F3"])
        self.assertEqual(5, followability_counts["F4"])

    def test_export_review_workbook_has_dialogue_state_columns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "dialogue_review.xlsx"
            cases = generate_dialogue_state_v3_50.build_dialogue_state_cases([_v2_case(i) for i in range(1, 51)])

            generate_dialogue_state_v3_50.export_dialogue_state_review_workbook(cases, output)
            workbook = load_workbook(output)

        self.assertIn("dialogue_state_review", workbook.sheetnames)
        sheet = workbook["dialogue_state_review"]
        headers = [sheet.cell(row=1, column=col).value for col in range(1, sheet.max_column + 1)]
        self.assertIn("上下文类型", headers)
        self.assertIn("学生跟随状态", headers)
        self.assertIn("上一轮 AI 脚手架", headers)
        self.assertIn("学生对脚手架的回答", headers)
        self.assertIn("跟随状态证据", headers)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest test_dialogue_state_v3_generation_unit.py
```

Expected: FAIL with `ImportError` or missing `generate_dialogue_state_v3_50`.

---

## Task 2: Implement v3 generator

**Files:**
- Create: `evals/aichat/generate_dialogue_state_v3_50.py`
- Test: `test_dialogue_state_v3_generation_unit.py`

- [ ] **Step 1: Create generator with constants and case builder**

Create `evals/aichat/generate_dialogue_state_v3_50.py`:

```python
"""Generate dialogue-state v3 held-out draft cases.

The v3 dataset extends Luogu-grounded v2 cases with fixed follow-up tutoring
contexts. It does not overwrite v2 and does not use historical online AI
replies as generation inputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


DEFAULT_SOURCE_JSONL = Path("docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl")
DEFAULT_OUTPUT_JSONL = Path("docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl")
DEFAULT_REVIEW_XLSX = Path("docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx")
DEFAULT_REPORT_JSON = Path("docs/research/dialogue_state_v3_generation_report_20260513.json")
DEFAULT_REPORT_ZH = Path("docs/research/dialogue_state_v3_generation_report_20260513.zh.md")
DEFAULT_REPORT_EN = Path("docs/research/dialogue_state_v3_generation_report_20260513.md")

CONTEXT_PLAN = (
    ["initial_question"] * 10
    + ["followup_after_correct_short_answer"] * 7
    + ["followup_after_partial_answer"] * 8
    + ["followup_after_wrong_answer"] * 7
    + ["followup_after_code_attempt"] * 10
    + ["followup_after_prerequisite_gap"] * 5
    + ["policy_direct_answer_special"] * 3
)

FOLLOWABILITY_BY_CONTEXT = {
    "initial_question": "",
    "followup_after_correct_short_answer": "F1",
    "followup_after_partial_answer": "F2",
    "followup_after_wrong_answer": "F3",
    "followup_after_code_attempt": "F2",
    "followup_after_prerequisite_gap": "F4",
    "policy_direct_answer_special": "F3",
}

EXPECTED_MOVE_BY_CONTEXT = {
    "initial_question": "clarify",
    "followup_after_correct_short_answer": "advance",
    "followup_after_partial_answer": "clarify",
    "followup_after_wrong_answer": "micro_step",
    "followup_after_code_attempt": "micro_step",
    "followup_after_prerequisite_gap": "prerequisite_repair",
    "policy_direct_answer_special": "safe_redirect",
}

FOLLOWUP_TEMPLATES = {
    "F1": {
        "prior_ai": "先看候选值变大时，限制是更容易满足还是更难满足？",
        "student_reply": "变大以后更难满足。",
        "evidence": "变大以后更难满足。",
        "confidence": "high",
        "uncertainty": "",
    },
    "F2": {
        "prior_ai": "你先说 true 是表示当前候选值可行，还是表示答案要去另一边找。",
        "student_reply": "应该是可行吧，但我不知道后面该往哪边。",
        "evidence": "应该是可行吧，但我不知道后面该往哪边。",
        "confidence": "high",
        "uncertainty": "",
    },
    "F3": {
        "prior_ai": "先说这一格对应处理到哪一步。",
        "student_reply": "是不是记录答案？我不太确定。",
        "evidence": "是不是记录答案？我不太确定。",
        "confidence": "medium",
        "uncertainty": "学生尝试回答但混淆了下标语义和值语义。",
    },
    "F4": {
        "prior_ai": "先看一个节点 [1,2]，如果整段加了 5，但还没往两个叶子递归，你觉得叶子现在真的改了吗？",
        "student_reply": "我不太懂节点和叶子是什么意思。",
        "evidence": "我不太懂节点和叶子是什么意思。",
        "confidence": "high",
        "uncertainty": "",
    },
    "policy": {
        "prior_ai": "完整代码先不直接给。你可以贴你现在最接近答案的一句思路或一段代码。",
        "student_reply": "我现在就想看完整思路和代码。",
        "evidence": "我现在就想看完整思路和代码。",
        "confidence": "high",
        "uncertainty": "",
    },
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _template_for_context(context_type: str) -> dict:
    if context_type == "policy_direct_answer_special":
        return FOLLOWUP_TEMPLATES["policy"]
    followability = FOLLOWABILITY_BY_CONTEXT.get(context_type, "")
    return FOLLOWUP_TEMPLATES.get(followability, {})


def _recent_dialogue_for_row(base: dict, context_type: str) -> tuple[str, dict]:
    if context_type == "initial_question":
        return base.get("recent_dialogue") or "N/A", {
            "prior_ai_scaffold": "",
            "student_reply_to_prior_scaffold": "",
            "followability_evidence_quote": "",
            "followability_label_confidence": "",
            "followability_uncertainty_reason": "",
        }
    template = _template_for_context(context_type)
    prior_ai = template["prior_ai"]
    student_reply = template["student_reply"]
    initial = base.get("student_message") or "这题我卡住了。"
    recent = f"学生：{initial}\nAI：{prior_ai}\n学生：{student_reply}"
    return recent, {
        "prior_ai_scaffold": prior_ai,
        "student_reply_to_prior_scaffold": student_reply,
        "followability_evidence_quote": template["evidence"],
        "followability_label_confidence": template["confidence"],
        "followability_uncertainty_reason": template["uncertainty"],
    }


def build_dialogue_state_cases(v2_rows: list[dict]) -> list[dict]:
    if len(v2_rows) < 50:
        raise ValueError(f"Need at least 50 v2 rows, got {len(v2_rows)}")
    rows = []
    for idx, (base, context_type) in enumerate(zip(v2_rows[:50], CONTEXT_PLAN), 1):
        recent_dialogue, followup_fields = _recent_dialogue_for_row(base, context_type)
        followability = FOLLOWABILITY_BY_CONTEXT[context_type]
        expected_move = EXPECTED_MOVE_BY_CONTEXT[context_type]
        row = dict(base)
        row.update(
            {
                "case_id": f"dialogue_v3_{idx:03d}",
                "id": f"dialogue_v3_{idx:03d}",
                "source_case_id": base.get("case_id", ""),
                "turn_position": "initial" if context_type == "initial_question" else "followup",
                "context_type": context_type,
                "student_scaffold_followability": followability,
                "expected_tutor_move": expected_move,
                "fixed_recent_dialogue_source": "synthetic_dialogue_state_v3",
                "recent_dialogue": recent_dialogue,
                "recent_dialogue_bucket": "none" if recent_dialogue.strip().upper() == "N/A" else "long",
                "reference_label_status": "draft_needs_coach_review",
                "case_generation_method": "dialogue-state synthetic-but-grounded from heldout v2 problem source",
            }
        )
        row.update(followup_fields)
        rows.append(row)
    return rows
```

- [ ] **Step 2: Add review workbook and report rendering**

Append to `evals/aichat/generate_dialogue_state_v3_50.py`:

```python
REVIEW_COLUMNS = [
    ("case_id", "样本编号"),
    ("source_case_id", "v2 来源样本"),
    ("context_type", "上下文类型"),
    ("turn_position", "轮次位置"),
    ("student_scaffold_followability", "学生跟随状态"),
    ("followability_label_confidence", "跟随状态置信度"),
    ("expected_tutor_move", "期望 Tutor 动作"),
    ("problem_source_id", "洛谷题号"),
    ("problem_title", "题目标题"),
    ("problem_source_url", "原题链接"),
    ("problem_statement", "必要题面"),
    ("student_message", "学生当前问题"),
    ("recent_dialogue", "固定近期对话"),
    ("prior_ai_scaffold", "上一轮 AI 脚手架"),
    ("student_reply_to_prior_scaffold", "学生对脚手架的回答"),
    ("followability_evidence_quote", "跟随状态证据"),
    ("followability_uncertainty_reason", "不确定原因"),
    ("missing_bridge", "目标 bridge"),
    ("forbidden_content", "禁止内容"),
    ("success_criteria", "成功标准"),
]


def _cell_value(value: object) -> str:
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value or "")


def export_dialogue_state_review_workbook(cases: list[dict], output_xlsx: Path) -> int:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "dialogue_state_review"
    sheet.append([label for _key, label in REVIEW_COLUMNS])
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="17324D")
        cell.fill = header_fill
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    for row in cases:
        sheet.append([_cell_value(row.get(key)) for key, _label in REVIEW_COLUMNS])
    for row_cells in sheet.iter_rows(min_row=2, max_row=sheet.max_row):
        for cell in row_cells:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    widths = {
        "A": 18, "B": 20, "C": 34, "D": 14, "E": 16, "F": 16, "G": 18,
        "H": 12, "I": 24, "J": 42, "K": 72, "L": 38, "M": 58,
        "N": 46, "O": 46, "P": 36, "Q": 36, "R": 46, "S": 36, "T": 44,
    }
    for col, width in widths.items():
        sheet.column_dimensions[col].width = width
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    output_xlsx.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_xlsx)
    return len(cases)


def build_report_payload(cases: list[dict], errors: list[dict], output_jsonl: Path, review_xlsx: Path) -> dict:
    return {
        "output_jsonl": str(output_jsonl),
        "review_xlsx": str(review_xlsx),
        "row_count": len(cases),
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
        "context_type_counts": dict(Counter(row["context_type"] for row in cases)),
        "turn_position_counts": dict(Counter(row["turn_position"] for row in cases)),
        "followability_counts": dict(Counter(row.get("student_scaffold_followability", "") or "NA" for row in cases)),
        "expected_tutor_move_counts": dict(Counter(row["expected_tutor_move"] for row in cases)),
        "followability_confidence_counts": dict(Counter(row.get("followability_label_confidence", "") or "NA" for row in cases)),
    }


def render_report_zh(payload: dict) -> str:
    return "\n".join(
        [
            "# Dialogue-State v3 50-case Generation Report",
            "",
            "本报告记录 dialogue-state v3 draft。该版本在 held-out v2 真实题源基础上加入固定后续辅导轮上下文和学生跟随状态标签。",
            "",
            f"- output_jsonl: `{payload['output_jsonl']}`",
            f"- review_xlsx: `{payload['review_xlsx']}`",
            f"- row_count: `{payload['row_count']}`",
            f"- ok: `{payload['ok']}`",
            "",
            "## 分布",
            "",
            f"- context_type_counts: `{payload['context_type_counts']}`",
            f"- turn_position_counts: `{payload['turn_position_counts']}`",
            f"- followability_counts: `{payload['followability_counts']}`",
            f"- expected_tutor_move_counts: `{payload['expected_tutor_move_counts']}`",
            f"- followability_confidence_counts: `{payload['followability_confidence_counts']}`",
            "",
            "## 边界",
            "",
            "- v3 不覆盖 v2。",
            "- prior AI scaffold 是固定 synthetic context，不来自任一被评测 baseline。",
            "- F1-F4 是 draft label，进入正式实验前需要教练复核和部分双标。",
        ]
    ) + "\n"


def render_report_en(payload: dict) -> str:
    return "\n".join(
        [
            "# Dialogue-State v3 50-case Generation Report",
            "",
            "This report records the dialogue-state v3 draft. It extends held-out v2 real problem sources with fixed follow-up tutoring contexts and scaffold-followability labels.",
            "",
            f"- output_jsonl: `{payload['output_jsonl']}`",
            f"- review_xlsx: `{payload['review_xlsx']}`",
            f"- row_count: `{payload['row_count']}`",
            f"- ok: `{payload['ok']}`",
            "",
            "## Distributions",
            "",
            f"- context_type_counts: `{payload['context_type_counts']}`",
            f"- turn_position_counts: `{payload['turn_position_counts']}`",
            f"- followability_counts: `{payload['followability_counts']}`",
            f"- expected_tutor_move_counts: `{payload['expected_tutor_move_counts']}`",
            f"- followability_confidence_counts: `{payload['followability_confidence_counts']}`",
            "",
            "## Boundaries",
            "",
            "- v3 does not overwrite v2.",
            "- prior AI scaffold context is fixed synthetic context and is not generated by any evaluated baseline.",
            "- F1-F4 labels are draft labels and require coach review plus partial double annotation before formal experiments.",
        ]
    ) + "\n"
```

- [ ] **Step 3: Add generation entrypoint**

Append:

```python
def generate_dataset(
    *,
    source_jsonl: Path = DEFAULT_SOURCE_JSONL,
    output_jsonl: Path = DEFAULT_OUTPUT_JSONL,
    review_xlsx: Path = DEFAULT_REVIEW_XLSX,
    report_json: Path = DEFAULT_REPORT_JSON,
    report_zh: Path = DEFAULT_REPORT_ZH,
    report_en: Path = DEFAULT_REPORT_EN,
) -> dict:
    v2_rows = read_jsonl(source_jsonl)
    cases = build_dialogue_state_cases(v2_rows)
    from evals.aichat import validate_dialogue_state_v3_dataset

    validation = validate_dialogue_state_v3_dataset.validate_dataset(cases)
    errors = validation["errors"]
    write_jsonl(cases, output_jsonl)
    export_dialogue_state_review_workbook(cases, review_xlsx)
    payload = build_report_payload(cases, errors, output_jsonl, review_xlsx)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_zh.write_text(render_report_zh(payload), encoding="utf-8")
    report_en.write_text(render_report_en(payload), encoding="utf-8")
    return payload


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-jsonl", type=Path, default=DEFAULT_SOURCE_JSONL)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--review-xlsx", type=Path, default=DEFAULT_REVIEW_XLSX)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-zh", type=Path, default=DEFAULT_REPORT_ZH)
    parser.add_argument("--report-en", type=Path, default=DEFAULT_REPORT_EN)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    payload = generate_dataset(
        source_jsonl=args.source_jsonl,
        output_jsonl=args.output_jsonl,
        review_xlsx=args.review_xlsx,
        report_json=args.report_json,
        report_zh=args.report_zh,
        report_en=args.report_en,
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run generator tests**

Run:

```bash
python3 -m unittest test_dialogue_state_v3_generation_unit.py
```

Expected: all tests pass after Task 3 validation module exists. If validation module is not yet created, the direct builder/export tests should pass but `generate_dataset` is not tested in this file.

---

## Task 3: Add v3 validator

**Files:**
- Create: `evals/aichat/validate_dialogue_state_v3_dataset.py`
- Create: `test_dialogue_state_v3_validation_unit.py`

- [ ] **Step 1: Write failing validation tests**

Create `test_dialogue_state_v3_validation_unit.py`:

```python
import unittest

from evals.aichat import validate_dialogue_state_v3_dataset


def _row(**overrides):
    row = {
        "case_id": "dialogue_v3_001",
        "turn_position": "followup",
        "context_type": "followup_after_partial_answer",
        "student_scaffold_followability": "F2",
        "followability_label_confidence": "high",
        "followability_evidence_quote": "应该是可行吧",
        "followability_uncertainty_reason": "",
        "prior_ai_scaffold": "true 表示什么？",
        "student_reply_to_prior_scaffold": "应该是可行吧，但不知道往哪边。",
        "expected_tutor_move": "clarify",
        "fixed_recent_dialogue_source": "synthetic_dialogue_state_v3",
        "recent_dialogue": "学生：check 是啥？\nAI：true 表示什么？\n学生：应该是可行吧，但不知道往哪边。",
        "reference_label_status": "draft_needs_coach_review",
    }
    row.update(overrides)
    return row


class DialogueStateV3ValidationTests(unittest.TestCase):
    def test_valid_followup_row_passes(self):
        result = validate_dialogue_state_v3_dataset.validate_dataset([_row()], expected_count=1)

        self.assertTrue(result["ok"])
        self.assertEqual([], result["errors"])
        self.assertEqual({"F2": 1}, result["followability_counts"])

    def test_rejects_missing_followability_evidence(self):
        result = validate_dialogue_state_v3_dataset.validate_dataset(
            [_row(followability_evidence_quote="")],
            expected_count=1,
        )

        self.assertFalse(result["ok"])
        self.assertIn("missing_followability_evidence_quote", {error["code"] for error in result["errors"]})

    def test_rejects_evidence_not_in_student_reply(self):
        result = validate_dialogue_state_v3_dataset.validate_dataset(
            [_row(followability_evidence_quote="另一个答案")],
            expected_count=1,
        )

        self.assertFalse(result["ok"])
        self.assertIn("evidence_quote_not_in_student_reply", {error["code"] for error in result["errors"]})

    def test_rejects_low_confidence_in_headline_mode(self):
        result = validate_dialogue_state_v3_dataset.validate_dataset(
            [_row(followability_label_confidence="low", followability_uncertainty_reason="学生回答太短。")],
            expected_count=1,
            allow_low_confidence_headline=False,
        )

        self.assertFalse(result["ok"])
        self.assertIn("low_confidence_followability_excluded_from_headline", {error["code"] for error in result["errors"]})

    def test_initial_question_must_not_have_followability_label(self):
        result = validate_dialogue_state_v3_dataset.validate_dataset(
            [
                _row(
                    turn_position="initial",
                    context_type="initial_question",
                    student_scaffold_followability="F1",
                    prior_ai_scaffold="",
                    student_reply_to_prior_scaffold="",
                    followability_evidence_quote="",
                    followability_label_confidence="",
                    recent_dialogue="N/A",
                    expected_tutor_move="clarify",
                )
            ],
            expected_count=1,
        )

        self.assertFalse(result["ok"])
        self.assertIn("initial_case_has_followability_label", {error["code"] for error in result["errors"]})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest test_dialogue_state_v3_validation_unit.py
```

Expected: FAIL because module is missing.

- [ ] **Step 3: Implement validator**

Create `evals/aichat/validate_dialogue_state_v3_dataset.py`:

```python
"""Validate dialogue-state v3 held-out draft rows."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

FOLLOWABILITY = {"F1", "F2", "F3", "F4"}
CONFIDENCE = {"high", "medium", "low"}
EXPECTED_MOVES = {"advance", "clarify", "micro_step", "prerequisite_repair", "safe_redirect"}
CONTEXT_TYPES = {
    "initial_question",
    "followup_after_correct_short_answer",
    "followup_after_partial_answer",
    "followup_after_wrong_answer",
    "followup_after_code_attempt",
    "followup_after_prerequisite_gap",
    "policy_direct_answer_special",
}


def _blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate_dataset(
    rows: list[dict],
    *,
    expected_count: int | None = 50,
    allow_low_confidence_headline: bool = True,
) -> dict:
    errors = []
    case_ids = Counter(str(row.get("case_id") or "") for row in rows)
    context_counts = Counter(str(row.get("context_type") or "") for row in rows)
    turn_counts = Counter(str(row.get("turn_position") or "") for row in rows)
    followability_counts = Counter(str(row.get("student_scaffold_followability") or "NA") for row in rows)
    confidence_counts = Counter(str(row.get("followability_label_confidence") or "NA") for row in rows)
    move_counts = Counter(str(row.get("expected_tutor_move") or "") for row in rows)

    if expected_count is not None and len(rows) != expected_count:
        errors.append({"code": "unexpected_row_count", "expected": expected_count, "actual": len(rows)})

    for idx, row in enumerate(rows, 1):
        case_id = row.get("case_id")
        context_type = row.get("context_type")
        turn_position = row.get("turn_position")
        if context_type not in CONTEXT_TYPES:
            errors.append({"code": "invalid_context_type", "row": idx, "case_id": case_id, "context_type": context_type})
        if turn_position not in {"initial", "followup"}:
            errors.append({"code": "invalid_turn_position", "row": idx, "case_id": case_id, "turn_position": turn_position})
        if row.get("expected_tutor_move") not in EXPECTED_MOVES:
            errors.append({"code": "invalid_expected_tutor_move", "row": idx, "case_id": case_id, "expected_tutor_move": row.get("expected_tutor_move")})
        if row.get("fixed_recent_dialogue_source") != "synthetic_dialogue_state_v3":
            errors.append({"code": "invalid_fixed_recent_dialogue_source", "row": idx, "case_id": case_id})
        if row.get("reference_label_status") != "draft_needs_coach_review":
            errors.append({"code": "invalid_reference_label_status", "row": idx, "case_id": case_id})

        if turn_position == "initial":
            if row.get("student_scaffold_followability"):
                errors.append({"code": "initial_case_has_followability_label", "row": idx, "case_id": case_id})
            continue

        followability = row.get("student_scaffold_followability")
        confidence = row.get("followability_label_confidence")
        evidence = row.get("followability_evidence_quote") or ""
        student_reply = row.get("student_reply_to_prior_scaffold") or ""
        if followability not in FOLLOWABILITY:
            errors.append({"code": "invalid_student_scaffold_followability", "row": idx, "case_id": case_id, "value": followability})
        if confidence not in CONFIDENCE:
            errors.append({"code": "invalid_followability_label_confidence", "row": idx, "case_id": case_id, "value": confidence})
        if _blank(row.get("prior_ai_scaffold")):
            errors.append({"code": "missing_prior_ai_scaffold", "row": idx, "case_id": case_id})
        if _blank(student_reply):
            errors.append({"code": "missing_student_reply_to_prior_scaffold", "row": idx, "case_id": case_id})
        if _blank(evidence):
            errors.append({"code": "missing_followability_evidence_quote", "row": idx, "case_id": case_id})
        elif evidence not in student_reply:
            errors.append({"code": "evidence_quote_not_in_student_reply", "row": idx, "case_id": case_id})
        if confidence == "low" and not row.get("followability_uncertainty_reason"):
            errors.append({"code": "low_confidence_missing_uncertainty_reason", "row": idx, "case_id": case_id})
        if confidence == "low" and not allow_low_confidence_headline:
            errors.append({"code": "low_confidence_followability_excluded_from_headline", "row": idx, "case_id": case_id})

    for case_id, count in case_ids.items():
        if case_id and count > 1:
            errors.append({"code": "duplicate_case_id", "case_id": case_id})

    return {
        "row_count": len(rows),
        "expected_count": expected_count,
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
        "context_type_counts": dict(context_counts),
        "turn_position_counts": dict(turn_counts),
        "followability_counts": dict(followability_counts),
        "followability_confidence_counts": dict(confidence_counts),
        "expected_tutor_move_counts": dict(move_counts),
    }


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--expected-count", type=int, default=50)
    parser.add_argument("--strict-headline", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    result = validate_dataset(
        _read_jsonl(args.dataset),
        expected_count=args.expected_count,
        allow_low_confidence_headline=not args.strict_headline,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run validation tests**

Run:

```bash
python3 -m unittest test_dialogue_state_v3_validation_unit.py
```

Expected: all tests pass.

---

## Task 4: Wire optional v3 fields into coach labeling workbook

**Files:**
- Modify: `evals/aichat/coach_labeling_schema_v2.py`
- Modify: `evals/aichat/export_coach_seed_labeling_workbook_v2.py`
- Modify: `test_coach_seed_labeling_v2_workbook_unit.py`

- [ ] **Step 1: Add failing workbook test**

Append to `test_coach_seed_labeling_v2_workbook_unit.py`:

```python
    def test_workbook_includes_dialogue_state_v3_fields_when_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_jsonl = Path(tmpdir) / "dialogue_v3.jsonl"
            output_xlsx = Path(tmpdir) / "dialogue_v3.xlsx"
            row = {
                **self._minimal_seed_row(),
                "turn_position": "followup",
                "context_type": "followup_after_partial_answer",
                "student_scaffold_followability": "F2",
                "followability_label_confidence": "high",
                "followability_evidence_quote": "应该是可行吧",
                "followability_uncertainty_reason": "",
                "prior_ai_scaffold": "true 表示什么？",
                "student_reply_to_prior_scaffold": "应该是可行吧，但不知道往哪边。",
                "expected_tutor_move": "clarify",
            }
            input_jsonl.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")

            export_coach_seed_labeling_workbook_v2.export_workbook(input_jsonl, output_xlsx)
            workbook = load_workbook(output_xlsx)
            sheet = workbook["标注表"]
            machine_headers = [sheet.cell(row=1, column=col).value for col in range(1, sheet.max_column + 1)]

        self.assertIn("student_scaffold_followability", machine_headers)
        self.assertIn("followability_evidence_quote", machine_headers)
        self.assertIn("expected_tutor_move", machine_headers)
```

If this test cannot use `self._minimal_seed_row()` because the test class has no helper, create a local minimal row by copying the existing test’s row construction pattern.

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest test_coach_seed_labeling_v2_workbook_unit.py
```

Expected: FAIL because v3 fields are missing from workbook schema.

- [ ] **Step 3: Add v3 columns to schema**

In `evals/aichat/coach_labeling_schema_v2.py`, add optional input columns near `recent_dialogue`:

```python
DIALOGUE_STATE_INPUT_COLUMNS = [
    "turn_position",
    "context_type",
    "student_scaffold_followability",
    "followability_label_confidence",
    "followability_evidence_quote",
    "followability_uncertainty_reason",
    "prior_ai_scaffold",
    "student_reply_to_prior_scaffold",
    "expected_tutor_move",
]
```

Extend the exported column list by inserting these after `recent_dialogue` if the file currently uses a static list. Add Chinese headers:

```python
"turn_position": "轮次位置",
"context_type": "上下文类型",
"student_scaffold_followability": "学生跟随状态",
"followability_label_confidence": "跟随状态置信度",
"followability_evidence_quote": "跟随状态证据",
"followability_uncertainty_reason": "不确定原因",
"prior_ai_scaffold": "上一轮 AI 脚手架",
"student_reply_to_prior_scaffold": "学生对脚手架的回答",
"expected_tutor_move": "期望 Tutor 动作",
```

- [ ] **Step 4: Carry v3 fields through normalizer**

In `evals/aichat/export_coach_seed_labeling_workbook_v2.py`, update `_normalize_seed_row`:

```python
for field in [
    "turn_position",
    "context_type",
    "student_scaffold_followability",
    "followability_label_confidence",
    "followability_evidence_quote",
    "followability_uncertainty_reason",
    "prior_ai_scaffold",
    "student_reply_to_prior_scaffold",
    "expected_tutor_move",
]:
    normalized[field] = row.get(field) or ""
```

- [ ] **Step 5: Run workbook tests**

Run:

```bash
python3 -m unittest test_coach_seed_labeling_v2_workbook_unit.py
```

Expected: all tests pass.

---

## Task 5: Wire optional v3 context into response review workbook

**Files:**
- Modify: `evals/aichat/export_coach_response_review_workbook_xlsx.py`
- Modify: `test_coach_response_review_xlsx_unit.py`

- [ ] **Step 1: Add failing response workbook test**

Append to `test_coach_response_review_xlsx_unit.py`:

```python
    def test_response_review_workbook_includes_dialogue_state_context(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_jsonl = Path(tmpdir) / "responses.jsonl"
            output_xlsx = Path(tmpdir) / "review.xlsx"
            row = {
                "case_id": "dialogue_v3_001",
                "anonymized_response_id": "resp_001",
                "problem_ref": "luogu_p1001",
                "problem_context": "题面摘要",
                "recent_dialogue": "学生：check 是啥？\nAI：true 表示什么？\n学生：应该是可行吧。",
                "student_message": "应该是可行吧，但不知道往哪边。",
                "response_text": "先确认 true 的含义，再看候选值变大时可行性怎么变化。",
                "prior_ai_scaffold": "true 表示什么？",
                "student_reply_to_prior_scaffold": "应该是可行吧。",
                "student_scaffold_followability": "F2",
                "expected_tutor_move": "clarify",
            }
            input_jsonl.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")

            export_coach_response_review_workbook_xlsx.export_workbook(input_jsonl, output_xlsx)
            workbook = load_workbook(output_xlsx)
            sheet = workbook.active
            headers = [sheet.cell(row=1, column=col).value for col in range(1, sheet.max_column + 1)]

        self.assertIn("上一轮 AI 脚手架", headers)
        self.assertIn("学生对脚手架的回答", headers)
        self.assertIn("学生跟随状态", headers)
        self.assertIn("期望 Tutor 动作", headers)
```

Adjust function names if existing tests use a different public API.

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest test_coach_response_review_xlsx_unit.py
```

Expected: FAIL because v3 context columns are not exported.

- [ ] **Step 3: Add optional columns**

In `evals/aichat/export_coach_response_review_workbook_xlsx.py`, add optional v3 context fields after `recent_dialogue`:

```python
DIALOGUE_STATE_REVIEW_FIELDS = [
    ("prior_ai_scaffold", "上一轮 AI 脚手架"),
    ("student_reply_to_prior_scaffold", "学生对脚手架的回答"),
    ("student_scaffold_followability", "学生跟随状态"),
    ("expected_tutor_move", "期望 Tutor 动作"),
]
```

If the workbook uses a static `CONTEXT_COLUMNS`, insert these columns there. If it dynamically maps field headers, add these entries to the header map and ensure row extraction includes them.

- [ ] **Step 4: Run response workbook tests**

Run:

```bash
python3 -m unittest test_coach_response_review_xlsx_unit.py
```

Expected: all tests pass.

---

## Task 6: Generate v3 draft and reports

**Files:**
- Generate: `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- Generate: `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- Generate: `docs/research/dialogue_state_v3_generation_report_20260513.json`
- Generate: `docs/research/dialogue_state_v3_generation_report_20260513.zh.md`
- Generate: `docs/research/dialogue_state_v3_generation_report_20260513.md`
- Generate: `docs/research/dialogue_state_v3_validation_report_20260513.json`

- [ ] **Step 1: Run v3 generator**

Run:

```bash
python3 -m evals.aichat.generate_dialogue_state_v3_50
```

Expected: JSON output with `"row_count": 50` and `"ok": true`.

- [ ] **Step 2: Run v3 validator**

Run:

```bash
python3 -m evals.aichat.validate_dialogue_state_v3_dataset \
  --dataset docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl \
  --output-json docs/research/dialogue_state_v3_validation_report_20260513.json \
  --expected-count 50
```

Expected: `"ok": true`.

- [ ] **Step 3: Export coach labeling workbook for v3**

Run:

```bash
python3 -m evals.aichat.export_coach_seed_labeling_workbook_v2 \
  --seed-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl \
  --output-xlsx docs/research/coach_seed_labeling_workbook_dialogue_state_v3_50_coach_a_full.zh.xlsx
```

Expected: workbook row count 50 and v3 columns visible.

---

## Task 7: Update research index

**Files:**
- Modify: `docs/research/index.md`

- [ ] **Step 1: Add report links**

In `docs/research/index.md`, under Annotation / held-out dataset docs, add:

```markdown
- [dialogue_state_v3_generation_report_20260513.zh.md](dialogue_state_v3_generation_report_20260513.zh.md): 中文 dialogue-state v3 50-case 生成报告，记录 follow-up tutoring turn、学生跟随状态 F1-F4 和期望 Tutor 动作分布。
- [dialogue_state_v3_generation_report_20260513.md](dialogue_state_v3_generation_report_20260513.md): English generation report for the dialogue-state v3 50-case draft.
```

- [ ] **Step 2: Run bilingual docs validation**

Run:

```bash
python3 -m evals.aichat.validate_research_bilingual_docs --output-json docs/research/bilingual_docs_validation_report.json
```

Expected: `unpaired_count: 0`.

---

## Task 8: Final verification

**Files:**
- All files touched above.

- [ ] **Step 1: Run targeted unit tests**

Run:

```bash
python3 -m unittest \
  test_dialogue_state_v3_generation_unit.py \
  test_dialogue_state_v3_validation_unit.py \
  test_coach_seed_labeling_v2_workbook_unit.py \
  test_coach_response_review_xlsx_unit.py
```

Expected: all tests pass.

- [ ] **Step 2: Run existing held-out tests**

Run:

```bash
python3 -m unittest \
  test_luogu_heldout_v2_generation_unit.py \
  test_heldout_50_dataset_unit.py \
  test_heldout_source_completion_unit.py
```

Expected: all tests pass.

- [ ] **Step 3: Inspect generated v3 distributions**

Run:

```bash
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path
rows = [json.loads(line) for line in Path("docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
print("row_count", len(rows))
print("context_type", Counter(row["context_type"] for row in rows))
print("followability", Counter(row.get("student_scaffold_followability", "") or "NA" for row in rows))
print("moves", Counter(row["expected_tutor_move"] for row in rows))
print("sample_followup")
for row in rows:
    if row["turn_position"] == "followup":
        print(row["case_id"], row["context_type"], row["student_scaffold_followability"])
        print(row["recent_dialogue"])
        break
PY
```

Expected:

```text
row_count 50
context_type includes initial_question: 10
followability includes F1: 6, F2: 19, F3: 10, F4: 5, NA: 10
sample_followup shows fixed student/AI/student context
```

- [ ] **Step 4: Do not push automatically**

Do not commit or push unless the user explicitly asks. Report generated files, verification commands, and remaining review steps.
