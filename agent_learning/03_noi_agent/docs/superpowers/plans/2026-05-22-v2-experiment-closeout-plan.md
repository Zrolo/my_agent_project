# CP-MissingBridgeBench v2 Experiment Closeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a v2 closeout pipeline that validates the completed 100-case / 700-response coach review, recomputes existing v2 summaries, adds closeout-level stratified/failure/reliability summaries, and writes a versioned evidence freeze manifest.

**Architecture:** Reuse the existing v2 workbook validator and batched-review analyzer as the source of truth for row parsing and main metrics. Add one focused closeout script that consumes the analyzer output plus case metadata, writes privacy-safe aggregate reports, and records hashes and evidence boundaries. Keep all private review material in a private local directory or user-provided local paths; public docs receive only aggregate summaries and manifests.

**Tech Stack:** Python 3, standard library (`csv`, `json`, `hashlib`, `collections`, `pathlib`), existing `openpyxl` workbook validators, existing `evals.aichat.analyze_dev_ablation_review` metric helpers, `pytest`/`unittest` style tests already used under `evals/aichat/tests`.

---

### File Structure

**Create**
- `evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py`  
  Consumes existing analysis outputs and metadata, generates closeout JSON/Markdown reports and freeze manifest.
- `evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py`  
  Unit tests for closeout helpers using synthetic rows only.
- `docs/research/cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md`  
  Generated aggregate closeout report.
- `docs/research/cp_missingbridgebench_v2_experiment_closeout_summary_20260522.json`  
  Generated machine-readable closeout summary.
- `docs/research/cp_missingbridgebench_v2_evidence_freeze_manifest_20260522.json`  
  Generated evidence freeze manifest.

**Reuse**
- `evals/aichat/validate_cp_missingbridgebench_v2_batched_coach_review.py`  
  Existing structural validator for the 10-batch coach-review workbook.
- `evals/aichat/analyze_cp_missingbridgebench_v2_batched_review.py`  
  Existing analyzer for workbook flattening, key merge, system summaries, and paired comparisons.
- `evals/aichat/export_cp_missingbridgebench_v2_batched_review_to_csv.py`  
  Existing private flattening helper.
- `evals/aichat/analyze_dev_ablation_review.py`  
  Existing metric functions reused by the analyzer.

**Do not modify**
- dialogue-state v3 result scripts and tables.
- production AIChat, prompt, active-mode, quota, migration, or runtime files.
- a private local directory contents except for generated private closeout outputs.

---

### Task 1: Add Unit Tests for Closeout Helpers

**Files:**
- Create: `evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py`
- Test target created in Task 2: `evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py`

- [ ] **Step 1: Write the failing tests**

Create `evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py` with this content:

```python
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def load_module(relative_path: str, module_name: str):
    script_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class V2CloseoutHelperTest(unittest.TestCase):
    def setUp(self) -> None:
        self.closeout = load_module(
            "evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py",
            "v2_closeout",
        )

    def test_slug_maps_known_designs_to_reader_labels(self):
        self.assertEqual(
            self.closeout.reader_label("dbox_inspired_guard"),
            "DBox-inspired + Guard",
        )
        self.assertEqual(
            self.closeout.reader_label("bridge_contract_compact_guard_repair"),
            "Bridge Contract + Guard/Repair",
        )

    def test_main_summary_extracts_core_metrics(self):
        payload = {
            "row_count": 700,
            "case_count": 100,
            "system_summary": {
                "dbox_inspired_guard": {
                    "n": 100,
                    "overall_quality_mean": 4.23,
                    "student_ready_pass_count": 72,
                    "student_ready_safe_pass_count": 54,
                    "major_or_answer_leakage_count": 1,
                    "answer_leakage_count": 0,
                    "student_response_burden_low_count": 69,
                    "student_response_burden_medium_count": 30,
                    "student_response_burden_high_count": 1,
                    "scaffold_sufficiency_mean": 1.89,
                }
            },
        }
        summary = self.closeout.extract_main_results(payload)
        row = summary["designs"][0]
        self.assertEqual(row["design_id"], "dbox_inspired_guard")
        self.assertEqual(row["design_label"], "DBox-inspired + Guard")
        self.assertEqual(row["overall_quality_mean"], 4.23)
        self.assertEqual(row["student_ready_count"], 72)
        self.assertEqual(row["safe_ready_count"], 54)
        self.assertEqual(row["major_plus_answer_leakage_count"], 1)
        self.assertEqual(row["burden_low_medium_high"], "69/30/1")

    def test_extract_required_pairwise_comparisons(self):
        payload = {
            "paired_comparisons": {
                "bridge_contract_compact_guard__vs__dbox_inspired_guard": {
                    "paired_cases": 100,
                    "mean_diff": -0.41,
                    "wins": 18,
                    "ties": 45,
                    "losses": 37,
                    "bootstrap_ci95": [-0.63, -0.19],
                }
            }
        }
        comparisons = self.closeout.extract_required_pairwise(payload)
        self.assertEqual(len(comparisons), 1)
        item = comparisons[0]
        self.assertEqual(item["comparison"], "Bridge Contract + Guard - DBox-inspired + Guard")
        self.assertEqual(item["delta_overall"], -0.41)
        self.assertEqual(item["w_t_l"], "18/45/37")

    def test_manifest_hashes_existing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifact.txt"
            path.write_text("stable evidence\n", encoding="utf-8")
            manifest = self.closeout.build_freeze_manifest(
                input_paths=[path],
                output_paths=[],
                closeout_summary={"case_count": 100, "row_count": 700},
                evidence_role="v2 benchmark closeout",
                freeze_date="2026-05-22",
            )
        self.assertEqual(manifest["freeze_date"], "2026-05-22")
        self.assertEqual(manifest["closeout_summary"]["case_count"], 100)
        self.assertEqual(len(manifest["inputs"]), 1)
        self.assertEqual(manifest["inputs"][0]["sha256"], "9cb58c678e175227332bb72bcb5fd33cc0697338383c8463414c6305de3063d7")

    def test_report_does_not_include_private_paths_by_default(self):
        closeout_summary = {
            "case_count": 100,
            "row_count": 700,
            "main_results": {
                "designs": [
                    {
                        "design_label": "DBox-inspired + Guard",
                        "n": 100,
                        "overall_quality_mean": 4.23,
                        "student_ready_count": 72,
                        "safe_ready_count": 54,
                        "major_plus_answer_leakage_count": 1,
                        "answer_leakage_count": 0,
                        "burden_low_medium_high": "69/30/1",
                    }
                ]
            },
            "required_pairwise": [],
            "privacy_boundary": "Aggregate-only public reporting.",
        }
        report = self.closeout.render_closeout_report_zh(closeout_summary)
        self.assertIn("DBox-inspired + Guard", report)
        self.assertNotIn("<private_local_dir>", report)
        self.assertNotIn("<restricted_material_marker>", report)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails because the script is missing**

Run:

```bash
python -m pytest evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py -q
```

Expected: FAIL during module loading with `FileNotFoundError` for `evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py`.

- [ ] **Step 3: Commit only the failing test**

```bash
git add evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py
git commit -m "test: add v2 closeout helper tests"
```

---

### Task 2: Implement the v2 Closeout Script

**Files:**
- Create: `evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py`
- Test: `evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py`

- [ ] **Step 1: Create the closeout script**

Create `evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py` with this content:

```python
#!/usr/bin/env python3
"""Close out CP-MissingBridgeBench v2 100-case / 700-response review evidence.

This script consumes existing private analyzer outputs and writes aggregate-only
closeout reports plus a freeze manifest. It does not recompute dialogue-state v3
main tables, modify production AIChat, or expose raw student text.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


DESIGN_LABELS = {
    "enhanced_prompt_only_clean": "Prompt-only",
    "codehelp_codeaid_clean": "No-direct-solution help",
    "dbox_inspired_clean": "DBox-inspired",
    "dbox_inspired_guard": "DBox-inspired + Guard",
    "bridge_guided_dbox_style_guard": "Bridge-guided DBox-style + Guard",
    "bridge_contract_compact_guard": "Bridge Contract + Guard",
    "bridge_contract_compact_guard_repair": "Bridge Contract + Guard/Repair",
}

DESIGN_ORDER = [
    "enhanced_prompt_only_clean",
    "codehelp_codeaid_clean",
    "dbox_inspired_clean",
    "dbox_inspired_guard",
    "bridge_guided_dbox_style_guard",
    "bridge_contract_compact_guard",
    "bridge_contract_compact_guard_repair",
]

REQUIRED_PAIRS = [
    ("bridge_contract_compact_guard", "dbox_inspired_guard"),
    ("bridge_guided_dbox_style_guard", "dbox_inspired_guard"),
    ("bridge_contract_compact_guard_repair", "dbox_inspired_guard"),
    ("bridge_contract_compact_guard_repair", "bridge_contract_compact_guard"),
    ("dbox_inspired_guard", "dbox_inspired_clean"),
    ("enhanced_prompt_only_clean", "dbox_inspired_guard"),
    ("codehelp_codeaid_clean", "dbox_inspired_guard"),
]

PUBLIC_PRIVACY_BOUNDARY = (
    "Aggregate-only reporting. Public outputs must not include raw student text, "
    "full student code, complete AIChat responses, real identity fields, hash salts, "
    "or reversible mappings."
)


def reader_label(design_id: str) -> str:
    return DESIGN_LABELS.get(design_id, design_id)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path: Path) -> dict:
    exists = path.exists()
    return {
        "path": str(path),
        "exists": exists,
        "bytes": path.stat().st_size if exists else None,
        "sha256": sha256_file(path) if exists else None,
    }


def extract_main_results(payload: dict) -> dict:
    system_summary = payload.get("system_summary") or {}
    rows = []
    for design_id in DESIGN_ORDER:
        item = system_summary.get(design_id) or {}
        if not item:
            continue
        rows.append(
            {
                "design_id": design_id,
                "design_label": reader_label(design_id),
                "n": item.get("n", 0),
                "overall_quality_mean": item.get("overall_quality_mean", 0.0),
                "student_ready_count": item.get("student_ready_pass_count", 0),
                "safe_ready_count": item.get("student_ready_safe_pass_count", 0),
                "major_plus_answer_leakage_count": item.get("major_or_answer_leakage_count", 0),
                "answer_leakage_count": item.get("answer_leakage_count", 0),
                "scaffold_sufficiency_mean": item.get("scaffold_sufficiency_mean", 0.0),
                "burden_low_medium_high": (
                    f"{item.get('student_response_burden_low_count', 0)}/"
                    f"{item.get('student_response_burden_medium_count', 0)}/"
                    f"{item.get('student_response_burden_high_count', 0)}"
                ),
            }
        )
    return {"designs": rows}


def extract_required_pairwise(payload: dict) -> list[dict]:
    comparisons = payload.get("paired_comparisons") or {}
    output = []
    for left, right in REQUIRED_PAIRS:
        key = f"{left}__vs__{right}"
        if key not in comparisons:
            continue
        item = comparisons[key]
        output.append(
            {
                "comparison": f"{reader_label(left)} - {reader_label(right)}",
                "left_design_id": left,
                "right_design_id": right,
                "paired_cases": item.get("paired_cases", 0),
                "delta_overall": item.get("mean_diff", 0.0),
                "w_t_l": f"{item.get('wins', 0)}/{item.get('ties', 0)}/{item.get('losses', 0)}",
                "ci95": item.get("bootstrap_ci95", [0.0, 0.0]),
            }
        )
    return output


def summarize_case_metadata(rows: Iterable[dict[str, str]]) -> dict:
    rows = list(rows)
    if not rows:
        return {
            "row_count": 0,
            "context_sufficiency_counts": {},
            "reasoning_focus_counts": {},
            "help_seeking_context_counts": {},
        }

    def first_value(row: dict[str, str], keys: list[str]) -> str:
        for key in keys:
            value = str(row.get(key) or "").strip()
            if value:
                return value
        return ""

    context_counts = Counter(first_value(row, ["context_sufficiency", "context_sufficiency_light"]) for row in rows)
    reasoning_counts = Counter(first_value(row, ["reasoning_focus", "rough_bridge_family", "coach_missing_bridge_family"]) for row in rows)
    help_counts = Counter(first_value(row, ["help_seeking_context", "help_seeking_type"]) for row in rows)
    return {
        "row_count": len(rows),
        "context_sufficiency_counts": dict(sorted(context_counts.items())),
        "reasoning_focus_counts": dict(sorted(reasoning_counts.items())),
        "help_seeking_context_counts": dict(sorted(help_counts.items())),
    }


def summarize_failure_modes(labels_rows: Iterable[dict[str, str]]) -> dict:
    rows = list(labels_rows)
    by_design = defaultdict(Counter)
    discussion_by_design = Counter()
    notes_by_design = Counter()
    major_rows = []
    for row in rows:
        design_id = str(row.get("condition_id") or row.get("system") or "")
        leakage = str(row.get("leakage_label") or "")
        burden = str(row.get("student_response_burden") or "")
        show = str(row.get("would_show_to_student") or "")
        if leakage:
            by_design[design_id][f"leakage:{leakage}"] += 1
        if burden:
            by_design[design_id][f"burden:{burden}"] += 1
        if show:
            by_design[design_id][f"show:{show}"] += 1
        if str(row.get("needs_discussion") or "") == "yes":
            discussion_by_design[design_id] += 1
        if str(row.get("notes") or "").strip():
            notes_by_design[design_id] += 1
        if leakage in {"major_bridge_leakage", "answer_leakage"}:
            major_rows.append(
                {
                    "case_id": str(row.get("case_id") or ""),
                    "design_id": design_id,
                    "design_label": reader_label(design_id),
                    "leakage_label": leakage,
                    "overall_quality_score": row.get("overall_quality_score", 0),
                    "would_show_to_student": show,
                }
            )
    return {
        "counts_by_design": {reader_label(key): dict(value) for key, value in sorted(by_design.items())},
        "needs_discussion_by_design": {reader_label(key): value for key, value in sorted(discussion_by_design.items())},
        "notes_count_by_design": {reader_label(key): value for key, value in sorted(notes_by_design.items())},
        "major_or_answer_rows_no_private_text": major_rows,
    }


def build_review_reliability(validation: dict | None, second_review_summary: dict | None) -> dict:
    validation = validation or {}
    return {
        "primary_review_rows": validation.get("completed_rows", validation.get("total_rows", 0)),
        "primary_validation_passed": validation.get("passed"),
        "completed_rows_missing_required_fields": validation.get("completed_rows_missing_required_fields", 0),
        "second_review_summary": second_review_summary or {
            "status": "not_linked_in_closeout_run",
            "interpretation": "Report as single-coach expert review unless a second-review artifact is provided.",
        },
        "authority_boundary": (
            "Coach review is treated as expert review evidence, not final gold. "
            "Second review or adjudication, when linked, is a bounded reliability check."
        ),
    }


def build_freeze_manifest(
    *,
    input_paths: list[Path],
    output_paths: list[Path],
    closeout_summary: dict,
    evidence_role: str,
    freeze_date: str,
) -> dict:
    return {
        "manifest_id": f"cp_missingbridgebench_v2_evidence_freeze_{freeze_date.replace('-', '')}",
        "freeze_date": freeze_date,
        "evidence_role": evidence_role,
        "closeout_summary": {
            "case_count": closeout_summary.get("case_count"),
            "row_count": closeout_summary.get("row_count"),
            "privacy_boundary": closeout_summary.get("privacy_boundary", PUBLIC_PRIVACY_BOUNDARY),
        },
        "inputs": [artifact_record(path) for path in input_paths],
        "outputs": [artifact_record(path) for path in output_paths],
        "do_not_release": [
            "raw student text",
            "full student code",
            "complete AIChat responses",
            "identity fields",
            "hash salts",
            "reversible mappings",
            "private workbooks",
        ],
        "result_boundary": (
            "v2 closeout evidence; does not recompute or modify dialogue-state v3 main results; "
            "does not modify online AIChat; does not establish learning outcomes."
        ),
    }


def render_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def render_closeout_report_zh(closeout_summary: dict) -> str:
    main_rows = [
        [
            row["design_label"],
            row["n"],
            row["overall_quality_mean"],
            row["student_ready_count"],
            row["safe_ready_count"],
            row["major_plus_answer_leakage_count"],
            row["answer_leakage_count"],
            row["burden_low_medium_high"],
        ]
        for row in closeout_summary.get("main_results", {}).get("designs", [])
    ]
    pair_rows = [
        [
            row["comparison"],
            row["paired_cases"],
            row["delta_overall"],
            row["w_t_l"],
            row["ci95"],
        ]
        for row in closeout_summary.get("required_pairwise", [])
    ]
    metadata = closeout_summary.get("case_metadata_summary") or {}
    reliability = closeout_summary.get("human_review_reliability") or {}
    return "\n\n".join(
        [
            "# CP-MissingBridgeBench v2 实验收尾报告（aggregate）",
            "本报告只汇总 v2 100-case / 700-response 人审实验的 aggregate 结果；不公开学生原文、完整代码、完整 AIChat 回复、真实身份、hash salt 或可逆映射。",
            f"- case count: {closeout_summary.get('case_count')}\n- response rows: {closeout_summary.get('row_count')}\n- evidence role: {closeout_summary.get('evidence_role')}",
            "## 主结果摘要",
            render_table(
                [
                    "design",
                    "n",
                    "overall",
                    "student-ready",
                    "safe-ready",
                    "major+answer",
                    "answer",
                    "burden low/medium/high",
                ],
                main_rows,
            ),
            "## 关键配对比较",
            render_table(["comparison", "cases", "Δ overall", "W/T/L", "CI95"], pair_rows),
            "## 样本结构摘要",
            "```json\n" + json.dumps(metadata, ensure_ascii=False, indent=2) + "\n```",
            "## 人审可靠性边界",
            "```json\n" + json.dumps(reliability, ensure_ascii=False, indent=2) + "\n```",
            "## 解释边界",
            "- v2 closeout 不修改 dialogue-state v3 主结果。\n"
            "- v2 closeout 不证明线上部署效果或学习效果。\n"
            "- 如果 DBox-inspired + Guard 在 v2 中领先，应直接报告为强 baseline，而不是改写成 Bridge Contract 方法胜利。\n"
            "- Bridge Contract / Repair 变体应作为被评估设计和失败分析对象报告，除非结果支持更强 claim。",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-summary-json", type=Path, required=True)
    parser.add_argument("--labels-jsonl", type=Path)
    parser.add_argument("--validation-json", type=Path)
    parser.add_argument("--case-metadata-csv", type=Path)
    parser.add_argument("--second-review-summary-json", type=Path)
    parser.add_argument("--input-artifact", action="append", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--freeze-date", default="2026-05-22")
    args = parser.parse_args()

    payload = read_json(args.analysis_summary_json)
    validation = read_json(args.validation_json) if args.validation_json and args.validation_json.exists() else {}
    metadata_rows = read_csv_rows(args.case_metadata_csv) if args.case_metadata_csv and args.case_metadata_csv.exists() else []
    second_review = (
        read_json(args.second_review_summary_json)
        if args.second_review_summary_json and args.second_review_summary_json.exists()
        else None
    )
    labels_rows = []
    if args.labels_jsonl and args.labels_jsonl.exists():
        labels_rows = [
            json.loads(line)
            for line in args.labels_jsonl.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    closeout_summary = {
        "case_count": payload.get("case_count"),
        "row_count": payload.get("row_count"),
        "evidence_role": "v2 benchmark/evaluation closeout; not dialogue-state v3 main result",
        "privacy_boundary": PUBLIC_PRIVACY_BOUNDARY,
        "main_results": extract_main_results(payload),
        "required_pairwise": extract_required_pairwise(payload),
        "case_metadata_summary": summarize_case_metadata(metadata_rows),
        "failure_mode_summary": summarize_failure_modes(labels_rows),
        "human_review_reliability": build_review_reliability(validation, second_review),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "cp_missingbridgebench_v2_experiment_closeout_summary_20260522.json"
    report_path = args.output_dir / "cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md"
    manifest_path = args.output_dir / "cp_missingbridgebench_v2_evidence_freeze_manifest_20260522.json"

    summary_path.write_text(json.dumps(closeout_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_closeout_report_zh(closeout_summary) + "\n", encoding="utf-8")

    input_paths = [args.analysis_summary_json]
    if args.validation_json:
        input_paths.append(args.validation_json)
    if args.case_metadata_csv:
        input_paths.append(args.case_metadata_csv)
    if args.labels_jsonl:
        input_paths.append(args.labels_jsonl)
    input_paths.extend(args.input_artifact)

    manifest = build_freeze_manifest(
        input_paths=input_paths,
        output_paths=[summary_path, report_path],
        closeout_summary=closeout_summary,
        evidence_role=closeout_summary["evidence_role"],
        freeze_date=args.freeze_date,
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str(summary_path), "report": str(report_path), "manifest": str(manifest_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the helper tests**

Run:

```bash
python -m pytest evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py -q
```

Expected: PASS.

- [ ] **Step 3: Commit the passing implementation**

```bash
git add evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py
git commit -m "feat: add v2 experiment closeout script"
```

---

### Task 3: Run Existing Main Analysis on the Completed By-Case Workbook

**Files:**
- Read local workbook: `<private_review_workbook>`
- Read key CSV: `<private_key_csv>`
- Write private analysis outputs under: `<private_closeout_dir>/`

- [ ] **Step 1: Confirm the local workbook and key file exist**

Run:

```bash
test -f <private_review_workbook>
test -f <private_key_csv>
```

Expected: both commands exit with status 0 and print nothing.

- [ ] **Step 2: Confirm this is the 50-case-style by-case workbook**

Run:

```bash
.venv/bin/python - <<'PY'
from openpyxl import load_workbook
p = '<private_review_workbook>'
wb = load_workbook(p, read_only=True, data_only=True)
print('sheet_count', len(wb.sheetnames))
print('has_blind_sheet', '盲评表' in wb.sheetnames)
print('by_case_sheets', sum(1 for name in wb.sheetnames if name.startswith('题')))
ws = wb['盲评表']
print('blind_sheet_rows', ws.max_row)
print('blind_sheet_cols', ws.max_column)
PY
```

Expected: `has_blind_sheet True`, `by_case_sheets 100`, and `blind_sheet_rows 702`. Do not run the old `validate_cp_missingbridgebench_v2_batched_coach_review.py` here because that validator expects `批次01` to `批次10`, while this workbook uses `盲评表` plus one sheet per case.

- [ ] **Step 3: Run the existing by-case workbook analyzer**

Run:

```bash
.venv/bin/python evals/aichat/analyze_dev_ablation_review.py \
  --review-xlsx <private_review_workbook> \
  --key-csv <private_key_csv> \
  --output-labels-jsonl <private_closeout_dir>/analysis_from_bycase_review/coach_response_review_labels_v2_100case_7design.jsonl \
  --output-json <private_closeout_dir>/analysis_from_bycase_review/coach_response_review_analysis_v2_100case_7design.summary.json \
  --output-md-zh <private_closeout_dir>/analysis_from_bycase_review/coach_response_review_analysis_v2_100case_7design.zh.md \
  --output-md <private_closeout_dir>/analysis_from_bycase_review/coach_response_review_analysis_v2_100case_7design.md \
  --system-set dialogue_state_v3_main
```

Expected: printed paths for `labels`, `summary`, `zh report`, and `en report`.

- [ ] **Step 4: Inspect the generated summary for key v2 counts**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
path = Path('<private_closeout_dir>/analysis_from_bycase_review/coach_response_review_analysis_v2_100case_7design.summary.json')
payload = json.loads(path.read_text(encoding='utf-8'))
print(payload['case_count'], payload['row_count'])
for key in ['dbox_inspired_guard', 'bridge_contract_compact_guard', 'bridge_contract_compact_guard_repair']:
    item = payload['system_summary'][key]
    print(key, item['overall_quality_mean'], item['student_ready_pass_count'], item['student_ready_safe_pass_count'], item['major_or_answer_leakage_count'])
PY
```

Expected: first line `100 700`; printed design rows should match the reviewed v2 result direction, with `dbox_inspired_guard` leading on the main aggregate metrics if the current workbook matches the status record.

- [ ] **Step 5: Commit no private outputs**

Run:

```bash
git status --short <private_local_dir>
```

Expected: private outputs are not staged and should remain outside public commit scope.

---

### Task 4: Generate Closeout Report and Freeze Manifest

**Files:**
- Read private summary: `<private_closeout_dir>/analysis_from_bycase_review/coach_response_review_analysis_v2_100case_7design.summary.json`
- Read private labels: `<private_closeout_dir>/analysis_from_bycase_review/coach_response_review_labels_v2_100case_7design.jsonl`
- Read case metadata: `docs/research/cp_missingbridgebench_v2_100case_source_selection_manifest_v2_2_all_sufficient_20260521.csv`
- Write public aggregate outputs under: `docs/research/`

- [ ] **Step 1: Run the closeout script**

Run:

```bash
python evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py \
  --analysis-summary-json <private_closeout_dir>/analysis_from_bycase_review/coach_response_review_analysis_v2_100case_7design.summary.json \
  --labels-jsonl <private_closeout_dir>/analysis_from_bycase_review/coach_response_review_labels_v2_100case_7design.jsonl \
  --case-metadata-csv docs/research/cp_missingbridgebench_v2_100case_source_selection_manifest_v2_2_all_sufficient_20260521.csv \
  --input-artifact <private_review_workbook> \
  --input-artifact <private_key_csv> \
  --output-dir docs/research \
  --freeze-date 2026-05-22
```

Expected: JSON printed with paths:

```json
{
  "summary": "docs/research/cp_missingbridgebench_v2_experiment_closeout_summary_20260522.json",
  "report": "docs/research/cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md",
  "manifest": "docs/research/cp_missingbridgebench_v2_evidence_freeze_manifest_20260522.json"
}
```

- [ ] **Step 2: Run privacy grep on public outputs**

Run:

```bash
rg -n "<restricted-material-marker-pattern>|<private-download-path-pattern>|\\<private_local_dir>" \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_summary_20260522.json \
  docs/research/cp_missingbridgebench_v2_evidence_freeze_manifest_20260522.json
```

Expected: no matches. The manifest records private input artifacts with redacted path labels, not full private paths.

- [ ] **Step 3: Verify closeout report states the benchmark/evaluation boundary**

Run:

```bash
rg -n "不修改 dialogue-state v3|DBox-inspired \\+ Guard|Bridge Contract|线上部署效果|学习效果" \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md
```

Expected: matches show the report frames v2 as closeout evidence, not method victory, not online deployment, and not learning-effect evidence.

- [ ] **Step 4: Commit public aggregate outputs and the closeout script**

```bash
git add \
  evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py \
  evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_summary_20260522.json \
  docs/research/cp_missingbridgebench_v2_evidence_freeze_manifest_20260522.json
git commit -m "Add v2 experiment closeout evidence package"
```

---

### Task 5: Add a Human-Review Reliability Addendum if Second-Review Artifacts Are Linked

**Files:**
- Read existing optional summaries:
  - `docs/research/cp_missingbridgebench_v2_100case_second_coach_focus_selection_summary_20260521.json`
  - `docs/research/cp_missingbridgebench_v2_100case_second_review_focus_packet_audit_20260521.zh.md`
- Modify generated aggregate report only if the optional artifacts can be summarized without private case text.

- [ ] **Step 1: Check optional second-review files**

Run:

```bash
test -f docs/research/cp_missingbridgebench_v2_100case_second_coach_focus_selection_summary_20260521.json
test -f docs/research/cp_missingbridgebench_v2_100case_second_review_focus_packet_audit_20260521.zh.md
```

Expected: both commands exit with status 0 if second-review planning artifacts exist.

- [ ] **Step 2: Extract aggregate second-review status**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
path = Path('docs/research/cp_missingbridgebench_v2_100case_second_coach_focus_selection_summary_20260521.json')
data = json.loads(path.read_text(encoding='utf-8'))
print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
PY
```

Expected: output contains aggregate selection counts only. If it contains case-level private text, do not copy it into the public closeout report.

- [ ] **Step 3: Create a small second-review summary JSON when safe**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
source = Path('docs/research/cp_missingbridgebench_v2_100case_second_coach_focus_selection_summary_20260521.json')
target = Path('docs/research/cp_missingbridgebench_v2_second_review_aggregate_summary_20260522.json')
data = json.loads(source.read_text(encoding='utf-8'))
safe = {
    'source': str(source),
    'status': 'selection_artifact_present',
    'aggregate_summary': data,
    'authority_boundary': 'Second-review artifacts are targeted reliability support, not final gold.'
}
target.write_text(json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True) + '\\n', encoding='utf-8')
print(target)
PY
```

Expected: path printed and JSON contains no raw student text, full code, or full response text.

- [ ] **Step 4: Rerun closeout script with second-review summary**

Run:

```bash
python evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py \
  --analysis-summary-json <private_closeout_dir>/analysis_from_bycase_review/coach_response_review_analysis_v2_100case_7design.summary.json \
  --labels-jsonl <private_closeout_dir>/analysis_from_bycase_review/coach_response_review_labels_v2_100case_7design.jsonl \
  --case-metadata-csv docs/research/cp_missingbridgebench_v2_100case_source_selection_manifest_v2_2_all_sufficient_20260521.csv \
  --second-review-summary-json docs/research/cp_missingbridgebench_v2_second_review_aggregate_summary_20260522.json \
  --input-artifact <private_review_workbook> \
  --input-artifact <private_key_csv> \
  --output-dir docs/research \
  --freeze-date 2026-05-22
```

Expected: closeout report and manifest are regenerated with the second-review aggregate boundary included.

- [ ] **Step 5: Commit the second-review aggregate summary**

```bash
git add \
  docs/research/cp_missingbridgebench_v2_second_review_aggregate_summary_20260522.json \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_summary_20260522.json \
  docs/research/cp_missingbridgebench_v2_evidence_freeze_manifest_20260522.json
git commit -m "Document v2 second-review aggregate boundary"
```

---

### Task 6: Final Verification Before Reporting Complete

**Files:**
- Verify: `evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py`
- Verify: `evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py`
- Verify: generated closeout docs under `docs/research/`

- [ ] **Step 1: Run unit tests**

Run:

```bash
python -m pytest evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py -q
```

Expected: PASS.

- [ ] **Step 2: Run syntax check for touched Python files**

Run:

```bash
python -m py_compile \
  evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py \
  evals/aichat/tests/test_closeout_cp_missingbridgebench_v2_experiment.py
```

Expected: exits with status 0 and prints nothing.

- [ ] **Step 3: Check no dialogue-state v3 main result files were modified in this implementation**

Run:

```bash
git diff --name-only HEAD~3..HEAD | rg "dialogue_state_v3|paper_submission_manuscript|run_bridge_offline_eval|run_dev_ablation_suite" || true
```

Expected: no matched files from this closeout implementation, except pre-existing unrelated dirty worktree files that were not staged in closeout commits.

- [ ] **Step 4: Check public outputs do not contain unsafe claims**

Run:

```bash
rg -n "method victory|outperforms all|significantly dominates|<unsafe-claim-pattern>" \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md \
  docs/research/cp_missingbridgebench_v2_experiment_closeout_summary_20260522.json \
  docs/research/cp_missingbridgebench_v2_evidence_freeze_manifest_20260522.json || true
```

Expected: no unsafe claim matches.

- [ ] **Step 5: Show final git status**

Run:

```bash
git status --short
```

Expected: closeout files are committed. The repository may still show pre-existing unrelated dirty files from earlier work; do not stage or revert them.
