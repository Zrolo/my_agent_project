#!/usr/bin/env python3
"""Validate the real-student 30-case second-coach focus review workbook.

This validator checks workbook structure, allowed Chinese dropdown values, and
privacy/reporting gates. It intentionally does not export raw student text,
full code, or full AIChat responses.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


REQUIRED_SHEETS = ["案例上下文", "二审评分", "隐私与报告门"]

REQUIRED_COLUMNS = {
    "二审评分": [
        "案例编号",
        "题目名称/匿名题号",
        "二审状态",
        "二审上下文是否足够",
        "二审是否同意AI预复核",
        "二审泄露标签",
        "二审总体质量（1-5）",
        "二审是否愿意给学生看",
        "二审复核信心",
        "二审是否需要裁决",
        "二审备注（中文）",
    ],
    "隐私与报告门": [
        "案例编号",
        "题目名称/匿名题号",
        "隐私复核状态",
        "知情/报告门",
        "二审公开边界备注",
    ],
    "案例上下文": [
        "案例编号",
        "题目名称/匿名题号",
        "题面匹配状态",
        "题面来源",
        "题面映射方式",
        "当前AIChat回复字段说明",
    ],
}

ALLOWED_VALUES = {
    "二审状态": {"待二审", "已二审", "仍需裁决", "因隐私风险排除", "因上下文不足排除"},
    "二审上下文是否足够": {"足够", "部分足够", "不足", "不清楚"},
    "二审是否同意AI预复核": {"同意", "部分同意", "不同意", "不适用"},
    "二审泄露标签": {"无泄露", "轻微关键桥泄露", "重大关键桥泄露", "答案或代码泄露", "上下文不足未判断"},
    "二审总体质量（1-5）": {"5", "4", "3", "2", "1", 5, 4, 3, 2, 1},
    "二审是否愿意给学生看": {"是", "边界", "否"},
    "二审复核信心": {"高", "中", "低"},
    "二审是否需要裁决": {"否", "是"},
    "隐私复核状态": {"待复核", "可内部复核", "需继续脱敏", "因隐私风险排除"},
    "知情/报告门": {"待完成", "可报告", "不可报告", "已退出"},
}

SCORING_REQUIRED_WHEN_REVIEWED = [
    "二审上下文是否足够",
    "二审是否同意AI预复核",
    "二审泄露标签",
    "二审总体质量（1-5）",
    "二审是否愿意给学生看",
    "二审复核信心",
    "二审是否需要裁决",
]


def normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_rows(ws: Any) -> tuple[list[str], list[dict[str, Any]]]:
    headers = [normalize(cell.value) for cell in ws[1]]
    rows: list[dict[str, Any]] = []
    for row_idx in range(2, ws.max_row + 1):
        row = {headers[col_idx - 1]: ws.cell(row=row_idx, column=col_idx).value for col_idx in range(1, len(headers) + 1)}
        if any(normalize(v) for v in row.values()):
            row["_row"] = row_idx
            rows.append(row)
    return headers, rows


def add_error(errors: list[str], sheet: str, row: int | None, message: str) -> None:
    loc = f"{sheet}"
    if row is not None:
        loc += f" row {row}"
    errors.append(f"{loc}: {message}")


def validate(path: Path, expected_rows: int, allow_pending: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    # Some user-edited workbooks omit worksheet dimension metadata; openpyxl's
    # read-only worksheets then expose max_row/max_column as None. The focus
    # review workbook is intentionally small, so normal mode is safer here.
    wb = load_workbook(path, read_only=False, data_only=True)
    for sheet in REQUIRED_SHEETS:
        if sheet not in wb.sheetnames:
            add_error(errors, sheet, None, "missing required sheet")

    if errors:
        return {"path": str(path), "errors": errors, "warnings": warnings}

    parsed: dict[str, tuple[list[str], list[dict[str, Any]]]] = {}
    for sheet in REQUIRED_SHEETS:
        headers, rows = read_rows(wb[sheet])
        parsed[sheet] = (headers, rows)
        for col in REQUIRED_COLUMNS[sheet]:
            if col not in headers:
                add_error(errors, sheet, None, f"missing required column: {col}")
        if len(rows) != expected_rows:
            add_error(errors, sheet, None, f"expected {expected_rows} data rows, found {len(rows)}")

    if errors:
        return {"path": str(path), "errors": errors, "warnings": warnings}

    context_rows = parsed["案例上下文"][1]
    scoring_rows = parsed["二审评分"][1]
    privacy_rows = parsed["隐私与报告门"][1]

    context_ids = {normalize(row["案例编号"]) for row in context_rows}
    scoring_ids = {normalize(row["案例编号"]) for row in scoring_rows}
    privacy_ids = {normalize(row["案例编号"]) for row in privacy_rows}
    if len(context_ids) != expected_rows or len(scoring_ids) != expected_rows or len(privacy_ids) != expected_rows:
        add_error(errors, "workbook", None, "case ids must be non-empty and unique in each sheet")
    if context_ids != scoring_ids or scoring_ids != privacy_ids:
        add_error(errors, "workbook", None, "case ids must match across 案例上下文 / 二审评分 / 隐私与报告门")

    for row in context_rows:
        role = normalize(row.get("当前AIChat回复字段说明"))
        if role != "线上已展示回复，观察项，非实验条件":
            add_error(errors, "案例上下文", row["_row"], "当前AIChat回复字段说明 must be 线上已展示回复，观察项，非实验条件")

    reviewed_counter: Counter[str] = Counter()
    for row in scoring_rows:
        row_idx = int(row["_row"])
        status = normalize(row.get("二审状态"))
        if not status:
            add_error(errors, "二审评分", row_idx, "二审状态 is required")
            continue
        if status not in ALLOWED_VALUES["二审状态"]:
            add_error(errors, "二审评分", row_idx, f"invalid 二审状态: {status}")
        reviewed_counter[status] += 1

        if status == "待二审" and not allow_pending:
            add_error(errors, "二审评分", row_idx, "二审状态 remains 待二审; use --allow-pending only for template smoke tests")
        if status in {"已二审", "仍需裁决"}:
            for col in SCORING_REQUIRED_WHEN_REVIEWED:
                if not normalize(row.get(col)):
                    add_error(errors, "二审评分", row_idx, f"{col} is required when 二审状态={status}")

        for col, allowed in ALLOWED_VALUES.items():
            if col not in row:
                continue
            value = row.get(col)
            if normalize(value) and value not in allowed and normalize(value) not in {normalize(v) for v in allowed}:
                add_error(errors, "二审评分", row_idx, f"invalid {col}: {value}")

    privacy_by_case = {normalize(row["案例编号"]): row for row in privacy_rows}
    for case_id, row in privacy_by_case.items():
        row_idx = int(row["_row"])
        privacy_status = normalize(row.get("隐私复核状态"))
        reporting_gate = normalize(row.get("知情/报告门"))
        for col in ["隐私复核状态", "知情/报告门"]:
            value = normalize(row.get(col))
            if not value:
                add_error(errors, "隐私与报告门", row_idx, f"{col} is required")
            elif value not in {normalize(v) for v in ALLOWED_VALUES[col]}:
                add_error(errors, "隐私与报告门", row_idx, f"invalid {col}: {value}")

        if reporting_gate == "可报告" and privacy_status != "可内部复核":
            add_error(errors, "隐私与报告门", row_idx, "知情/报告门=可报告 requires 隐私复核状态=可内部复核")
        if privacy_status == "因隐私风险排除" and reporting_gate == "可报告":
            add_error(errors, "隐私与报告门", row_idx, "privacy-risk excluded rows cannot be 可报告")

    reportable_rows = sum(
        1
        for row in privacy_rows
        if normalize(row.get("隐私复核状态")) == "可内部复核" and normalize(row.get("知情/报告门")) == "可报告"
    )

    return {
        "path": str(path),
        "expected_rows": expected_rows,
        "allow_pending": allow_pending,
        "sheet_names": wb.sheetnames,
        "review_status_counts": dict(reviewed_counter),
        "reportable_rows_after_gate": reportable_rows,
        "errors": errors,
        "warnings": warnings,
        "boundary": "Validator checks structure and gates only; it does not make AI labels human evidence or publish case-level content.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--expected-rows", type=int, default=9)
    parser.add_argument("--allow-pending", action="store_true", help="Use only for blank template smoke tests.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = validate(args.workbook, args.expected_rows, args.allow_pending)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
