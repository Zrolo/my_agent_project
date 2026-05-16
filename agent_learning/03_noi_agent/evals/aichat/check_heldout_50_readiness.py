"""Summarize whether the 50-case held-out package is ready for the main run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.aichat.coach_labeling_schema_v2 import extract_option_id
from evals.aichat.validate_coach_workbook_v2 import load_csv_rows, load_xlsx_rows
from evals.aichat.validate_heldout_50_dataset import validate_dataset


DEFAULT_DRAFT_JSONL = Path("docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl")
DEFAULT_COACH_A_WORKBOOK = Path("docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx")
DEFAULT_COACH_B_WORKBOOK = Path("docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx")
DEFAULT_FROZEN_JSONL = Path("docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl")
DEFAULT_OUTPUT_JSON = Path("docs/research/heldout_50_readiness_20260513.json")


def _load_workbook_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    if path.suffix.lower() == ".xlsx":
        return load_xlsx_rows(path)
    return load_csv_rows(path)


def _case_id(row: dict) -> str:
    return str(row.get("case_id") or row.get("id") or "").strip()


def _workbook_status(path: Path) -> dict:
    rows = _load_workbook_rows(path)
    labeled_case_ids = []
    needs_discussion_case_ids = []
    unlabeled_case_ids = []
    for row in rows:
        case_id = _case_id(row)
        if not case_id:
            continue
        status = extract_option_id(row.get("review_status"))
        if status == "labeled":
            labeled_case_ids.append(case_id)
        elif status == "needs_discussion":
            needs_discussion_case_ids.append(case_id)
        else:
            unlabeled_case_ids.append(case_id)
    return {
        "path": str(path),
        "exists": path.exists(),
        "row_count": len(rows),
        "labeled_count": len(labeled_case_ids),
        "needs_discussion_count": len(needs_discussion_case_ids),
        "unlabeled_count": len(unlabeled_case_ids),
        "labeled_case_ids": labeled_case_ids,
        "needs_discussion_case_ids": needs_discussion_case_ids,
        "unlabeled_case_ids": unlabeled_case_ids,
    }


def _append_blocker(blocking_reasons: list[str], condition: bool, reason: str) -> None:
    if condition:
        blocking_reasons.append(reason)


def check_readiness(
    *,
    draft_jsonl: Path = DEFAULT_DRAFT_JSONL,
    coach_a_workbook: Path = DEFAULT_COACH_A_WORKBOOK,
    coach_b_workbook: Path = DEFAULT_COACH_B_WORKBOOK,
    frozen_jsonl: Path = DEFAULT_FROZEN_JSONL,
    expected_count: int = 50,
    expected_coach_b_overlap: int = 20,
) -> dict:
    draft_validation = validate_dataset(Path(draft_jsonl), expected_count=expected_count)
    coach_a = _workbook_status(Path(coach_a_workbook))
    coach_b = _workbook_status(Path(coach_b_workbook))

    frozen_jsonl = Path(frozen_jsonl)
    frozen_exists = frozen_jsonl.exists()
    if frozen_exists:
        frozen_preflight = validate_dataset(
            frozen_jsonl,
            expected_count=expected_count,
            require_frozen_status=True,
        )
    else:
        frozen_preflight = {
            "ok": False,
            "error_count": 1,
            "errors": [{"code": "file_not_found", "file": str(frozen_jsonl)}],
        }

    blocking_reasons: list[str] = []
    _append_blocker(blocking_reasons, not draft_validation.get("ok"), "draft_validation_failed")
    _append_blocker(blocking_reasons, coach_a["labeled_count"] < expected_count, "coach_a_incomplete")
    _append_blocker(
        blocking_reasons,
        coach_b["labeled_count"] < expected_coach_b_overlap,
        "coach_b_overlap_incomplete",
    )
    _append_blocker(blocking_reasons, not frozen_exists, "frozen_jsonl_missing")
    _append_blocker(
        blocking_reasons,
        frozen_exists and not frozen_preflight.get("ok"),
        "frozen_formal_preflight_failed",
    )

    return {
        "draft_jsonl": str(draft_jsonl),
        "coach_a_workbook": str(coach_a_workbook),
        "coach_b_workbook": str(coach_b_workbook),
        "frozen_jsonl": str(frozen_jsonl),
        "expected_count": expected_count,
        "expected_coach_b_overlap": expected_coach_b_overlap,
        "draft_validation_ok": bool(draft_validation.get("ok")),
        "draft_validation": draft_validation,
        "coach_a": coach_a,
        "coach_b": coach_b,
        "frozen_dataset": {
            "path": str(frozen_jsonl),
            "exists": frozen_exists,
            "formal_preflight_ok": bool(frozen_preflight.get("ok")),
            "formal_preflight": frozen_preflight,
        },
        "blocking_reasons": blocking_reasons,
        "ready_for_main_experiment": not blocking_reasons,
    }


def _fmt_bool(value: bool) -> str:
    return "pass" if value else "blocked"


def render_report_zh(payload: dict) -> str:
    coach_a = payload["coach_a"]
    coach_b = payload["coach_b"]
    frozen = payload["frozen_dataset"]
    lines = [
        "# Held-out 50 Readiness Report",
        "",
        "本报告汇总 50-case held-out 从草稿到正式主实验前的当前状态。它不是实验结果，只是发车门禁。",
        "",
        "## 总结",
        "",
        f"- ready_for_main_experiment: `{payload['ready_for_main_experiment']}`",
        f"- blocking_reasons: {', '.join(f'`{item}`' for item in payload['blocking_reasons']) if payload['blocking_reasons'] else 'none'}",
        "",
        "## 状态表",
        "",
        "| 项 | 状态 | 备注 |",
        "|---|---|---|",
        f"| draft validation | {_fmt_bool(payload['draft_validation_ok'])} | `{payload['draft_jsonl']}` |",
        f"| Coach A labeled | {_fmt_bool(coach_a['labeled_count'] >= payload['expected_count'])} | {coach_a['labeled_count']} / {payload['expected_count']} |",
        f"| Coach B overlap labeled | {_fmt_bool(coach_b['labeled_count'] >= payload['expected_coach_b_overlap'])} | {coach_b['labeled_count']} / {payload['expected_coach_b_overlap']} |",
        f"| frozen JSONL exists | {_fmt_bool(frozen['exists'])} | `{frozen['path']}` |",
        f"| frozen formal preflight | {_fmt_bool(frozen['formal_preflight_ok'])} | require frozen reference status |",
        "",
        "## 下一步",
        "",
    ]
    if payload["ready_for_main_experiment"]:
        lines.append("- 可以按 heldout_main runbook 启动正式 400-row 主实验。")
    else:
        lines.extend(
            [
                "- 补齐 Coach A 全量标注；",
                "- 补齐 Coach B overlap 复标；",
                "- 计算 agreement 并裁决分歧；",
                "- 导出 frozen reference JSONL；",
                "- 重新运行 formal preflight，直到无 blocker。",
            ]
        )
    return "\n".join(lines) + "\n"


def render_report_en(payload: dict) -> str:
    coach_a = payload["coach_a"]
    coach_b = payload["coach_b"]
    frozen = payload["frozen_dataset"]
    lines = [
        "# Held-out 50 Readiness Report",
        "",
        "This report summarizes the current status of the 50-case held-out package before the formal main experiment. It is not an experiment result; it is a launch gate.",
        "",
        "## Summary",
        "",
        f"- ready_for_main_experiment: `{payload['ready_for_main_experiment']}`",
        f"- blocking_reasons: {', '.join(f'`{item}`' for item in payload['blocking_reasons']) if payload['blocking_reasons'] else 'none'}",
        "",
        "## Status Table",
        "",
        "| Item | Status | Notes |",
        "|---|---|---|",
        f"| draft validation | {_fmt_bool(payload['draft_validation_ok'])} | `{payload['draft_jsonl']}` |",
        f"| Coach A labeled | {_fmt_bool(coach_a['labeled_count'] >= payload['expected_count'])} | {coach_a['labeled_count']} / {payload['expected_count']} |",
        f"| Coach B overlap labeled | {_fmt_bool(coach_b['labeled_count'] >= payload['expected_coach_b_overlap'])} | {coach_b['labeled_count']} / {payload['expected_coach_b_overlap']} |",
        f"| frozen JSONL exists | {_fmt_bool(frozen['exists'])} | `{frozen['path']}` |",
        f"| frozen formal preflight | {_fmt_bool(frozen['formal_preflight_ok'])} | require frozen reference status |",
        "",
        "## Next Steps",
        "",
    ]
    if payload["ready_for_main_experiment"]:
        lines.append("- Start the formal 400-row main experiment using the heldout_main runbook.")
    else:
        lines.extend(
            [
                "- Complete Coach A full labeling.",
                "- Complete Coach B overlap labeling.",
                "- Compute agreement and adjudicate disagreements.",
                "- Export the frozen reference JSONL.",
                "- Rerun formal preflight until there are no blockers.",
            ]
        )
    return "\n".join(lines) + "\n"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check readiness for the 50-case held-out main experiment.")
    parser.add_argument("--draft-jsonl", type=Path, default=DEFAULT_DRAFT_JSONL)
    parser.add_argument("--coach-a-workbook", type=Path, default=DEFAULT_COACH_A_WORKBOOK)
    parser.add_argument("--coach-b-workbook", type=Path, default=DEFAULT_COACH_B_WORKBOOK)
    parser.add_argument("--frozen-jsonl", type=Path, default=DEFAULT_FROZEN_JSONL)
    parser.add_argument("--expected-count", type=int, default=50)
    parser.add_argument("--expected-coach-b-overlap", type=int, default=20)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md-zh", type=Path)
    parser.add_argument("--output-md", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    payload = check_readiness(
        draft_jsonl=args.draft_jsonl,
        coach_a_workbook=args.coach_a_workbook,
        coach_b_workbook=args.coach_b_workbook,
        frozen_jsonl=args.frozen_jsonl,
        expected_count=args.expected_count,
        expected_coach_b_overlap=args.expected_coach_b_overlap,
    )
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    if args.output_md_zh:
        args.output_md_zh.parent.mkdir(parents=True, exist_ok=True)
        args.output_md_zh.write_text(render_report_zh(payload), encoding="utf-8")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_report_en(payload), encoding="utf-8")
    output = stdout or sys.stdout
    output.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
