#!/usr/bin/env python3
"""Validate Chinese coach-facing 5-case real-student review forms.

This validator is intentionally separate from the dialogue-state v3 main
experiment. It only checks the local/pilot coach-review form shape and gates;
it does not recompute main tables or alter online AIChat behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_INPUT = Path(".local_private/real_student_online_5case_coach_review_packet_cn_v2_20260520.csv")
DEFAULT_SCHEMA = Path("docs/research/real_student_online_5case_coach_review_cn_schema_v2.json")
DEFAULT_EXPECTED_ROWS = 5

OPTIONALLY_EMPTY_FIELDS = {
    "近期对话（已脱敏，可空）",
    "学生代码片段（已脱敏，可空）",
    "上下文是否足够",
    "识别当前缺失桥是否准确（0/1/2）",
    "回复是否基于当前材料（0/1/2）",
    "脚手架是否合适（0/1/2）",
    "是否控制关键桥泄露（0/1/2）",
    "下一步是否清楚（0/1/2）",
    "是否单焦点连贯（0/1/2）",
    "微例是否围绕桥梁（0/1/2/不适用）",
    "微例适用性",
    "泄露标签",
    "总体质量（1-5）",
    "是否愿意给学生看",
    "学生回答负担",
    "复核信心",
    "是否需要讨论",
    "缺失桥家族（中文）",
    "当前缺失桥实例（中文简述）",
    "禁止直接说出的内容（中文）",
    "可以提示到什么程度（中文）",
    "期望学生下一步（中文）",
    "是否匹配现有taxonomy",
    "新桥候选（如无填“无”）",
    "观察到的下一轮进展",
    "是否同意AI预标注",
    "是否需要裁决",
    "教练备注（中文）",
}

FIFTY_CASE_REQUIRED_WHEN_REVIEWED = {
    "识别当前缺失桥是否准确（0/1/2）",
    "回复是否基于当前材料（0/1/2）",
    "脚手架是否合适（0/1/2）",
    "是否控制关键桥泄露（0/1/2）",
    "下一步是否清楚（0/1/2）",
    "是否单焦点连贯（0/1/2）",
    "微例是否围绕桥梁（0/1/2/不适用）",
    "微例适用性",
    "泄露标签",
    "总体质量（1-5）",
    "是否愿意给学生看",
    "学生回答负担",
    "复核信心",
    "是否需要讨论",
}

PILOT_REQUIRED_WHEN_CONTEXT_AVAILABLE = {
    "缺失桥家族（中文）",
    "当前缺失桥实例（中文简述）",
    "禁止直接说出的内容（中文）",
    "可以提示到什么程度（中文）",
    "期望学生下一步（中文）",
    "是否匹配现有taxonomy",
    "新桥候选（如无填“无”）",
    "观察到的下一轮进展",
    "是否同意AI预标注",
    "是否需要裁决",
}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(rows: list[dict[str, str]], header: list[str], schema: dict, expected_rows: int) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    required = list(schema.get("required", []))
    properties = schema.get("properties", {})

    missing_columns = [field for field in required if field not in header]
    extra_columns = [field for field in header if field not in properties]
    if missing_columns:
        errors.append(f"缺少必需列: {', '.join(missing_columns)}")
    if extra_columns:
        errors.append(f"存在 schema 外的列: {', '.join(extra_columns)}")

    if len(rows) != expected_rows:
        errors.append(f"应有 {expected_rows} 行教练复核记录，实际为 {len(rows)} 行")

    enum_by_field = {
        field: set(spec.get("enum", []))
        for field, spec in properties.items()
        if isinstance(spec, dict) and spec.get("enum")
    }

    seen_candidate_ids: dict[str, int] = {}
    reviewed_rows = 0
    reportable_after_consent = 0

    for index, row in enumerate(rows, start=2):
        row_id = _clean(row.get("候选轮次编号")) or f"第{index}行"
        if row_id in seen_candidate_ids:
            errors.append(f"{row_id}: 候选轮次编号重复，首次出现在第 {seen_candidate_ids[row_id]} 行")
        else:
            seen_candidate_ids[row_id] = index

        for field in required:
            if field in OPTIONALLY_EMPTY_FIELDS:
                continue
            if not _clean(row.get(field)):
                errors.append(f"{row_id}: 必填字段“{field}”为空")

        for field, allowed in enum_by_field.items():
            value = _clean(row.get(field))
            if value not in allowed:
                errors.append(f"{row_id}: “{field}”取值无效: {value!r}; 可选值={sorted(allowed)}")

        if _clean(row.get("知情/报告门")) != "可报告":
            warnings.append(f"{row_id}: 知情/报告门未标为“可报告”，不能作为公开 deep-pilot evidence")
        else:
            reportable_after_consent += 1

        review_status = _clean(row.get("复核状态"))
        if review_status == "已复核":
            reviewed_rows += 1
            if _clean(row.get("隐私复核状态")) != "可内部复核":
                errors.append(f"{row_id}: 已复核行要求“隐私复核状态=可内部复核”")
            context = _clean(row.get("上下文是否足够"))
            if context not in {"足够", "部分足够", "不足", "不清楚"}:
                errors.append(f"{row_id}: 已复核行必须填写“上下文是否足够”")

            for field in FIFTY_CASE_REQUIRED_WHEN_REVIEWED:
                if not _clean(row.get(field)):
                    errors.append(f"{row_id}: 已复核行必须填写 50-case 对齐评分字段“{field}”")

            if context in {"足够", "部分足够"}:
                for field in PILOT_REQUIRED_WHEN_CONTEXT_AVAILABLE:
                    if not _clean(row.get(field)):
                        errors.append(f"{row_id}: 上下文为“{context}”时必须填写“{field}”")
            elif context in {"不足", "不清楚"}:
                if _clean(row.get("泄露标签")) != "上下文不足未判断":
                    errors.append(f"{row_id}: 上下文不足/不清楚时，“泄露标签”应为“上下文不足未判断”")

    return {
        "ok": not errors,
        "total_rows": len(rows),
        "expected_rows": expected_rows,
        "reviewed_rows_count": reviewed_rows,
        "reportable_after_consent_count": reportable_after_consent,
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验中文教练可填 5-case real-student 复核表。")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--expected-rows", type=int, default=DEFAULT_EXPECTED_ROWS)
    parser.add_argument("--output-json", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    header, rows = read_csv(args.input)
    schema = read_schema(args.schema)
    result = validate(rows, header, schema, args.expected_rows)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output_json:
        args.output_json.write_text(text + "\n", encoding="utf-8")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
