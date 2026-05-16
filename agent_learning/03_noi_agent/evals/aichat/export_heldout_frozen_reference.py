"""Export reviewed held-out coach labels into a frozen reference JSONL.

This tool does not invent labels. It merges the held-out draft task rows with
Coach A's completed v2 workbook rows and fails if any draft case lacks a
`review_status=labeled` reference row.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.aichat.coach_labeling_schema_v2 import extract_option_id
from evals.aichat.export_coach_v2_gold_jsonl import build_gold_row
from evals.aichat.validate_coach_workbook_v2 import load_csv_rows, load_xlsx_rows


DEFAULT_DRAFT_JSONL = Path("docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl")
DEFAULT_COACH_A_WORKBOOK = Path("docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx")
DEFAULT_OUTPUT_JSONL = Path("docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl")

FROZEN_REFERENCE_STATUSES = {
    "coach_reference",
    "adjudicated_reference",
    "single_coach_reference",
    "coach_gold",
    "adjudicated_gold",
}

ADJUDICATED_STATUSES = {"adjudicated_reference", "adjudicated_gold"}


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid_json:{path}:{line_number}:{exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"row_not_object:{path}:{line_number}")
        rows.append(row)
    return rows


def _load_workbook_rows(path: Path) -> list[dict]:
    if path.suffix.lower() == ".xlsx":
        return load_xlsx_rows(path)
    return load_csv_rows(path)


def _case_id(row: dict) -> str:
    return str(row.get("case_id") or row.get("id") or "").strip()


def _join_values(value: object) -> str:
    if isinstance(value, list):
        return ";".join(str(item).strip() for item in value if str(item).strip())
    return str(value or "").strip()


def _merged_forbidden_content(gold: dict, fallback: object) -> list[str]:
    forbidden = []
    for field in ("general_forbidden_content", "bridge_specific_forbidden_content"):
        value = gold.get(field)
        if isinstance(value, list):
            forbidden.extend(str(item).strip() for item in value if str(item).strip())
        elif isinstance(value, str) and value.strip():
            forbidden.append(value.strip())
    if forbidden:
        return forbidden
    if isinstance(fallback, list):
        return [str(item).strip() for item in fallback if str(item).strip()]
    if isinstance(fallback, str) and fallback.strip():
        return [fallback.strip()]
    return []


def _needs_new_focus(gold: dict) -> bool:
    focus_status = str(gold.get("focus_match_status") or "").strip()
    focus_id = str(gold.get("registered_focus_id") or "").strip()
    return focus_status == "needs_new_focus" or focus_id in {"", "unknown", "not_applicable"}


def _reference_metadata(reference_status: str) -> dict:
    return {
        "label_reference_type": reference_status,
        "label_adjudication_status": "adjudicated" if reference_status in ADJUDICATED_STATUSES else "raw",
        "is_adjudicated_gold": reference_status in ADJUDICATED_STATUSES,
    }


def build_frozen_row(draft_row: dict, coach_row: dict, *, reference_status: str) -> dict:
    gold = build_gold_row(coach_row)
    gold.update(_reference_metadata(reference_status))
    forbidden_content = _merged_forbidden_content(gold, draft_row.get("forbidden_content"))

    frozen = dict(draft_row)
    frozen["reference_label_status"] = reference_status
    frozen["missing_bridge"] = gold.get("missing_bridge_instance") or frozen.get("missing_bridge", "")
    frozen["allowed_help_level"] = gold.get("max_scaffold_level") or frozen.get("allowed_help_level", "")
    frozen["forbidden_content"] = forbidden_content
    frozen["coach_v2_gold"] = gold
    frozen["gold_student_state"] = gold.get("student_problem_solving_state", "")
    frozen["gold_bridge_family"] = gold.get("primary_bridge_family", "")
    frozen["gold_known_focus"] = gold.get("registered_focus_id", "")
    frozen["gold_help_seeking_type"] = _join_values(gold.get("help_seeking_type"))
    frozen["gold_missing_link"] = gold.get("missing_bridge_instance", "")
    frozen["gold_allowed_help_level"] = gold.get("max_scaffold_level", "")
    frozen["gold_forbidden_completion"] = _join_values(forbidden_content)
    frozen["needs_new_focus"] = _needs_new_focus(gold)
    return frozen


def _labeled_rows_by_case_id(rows: list[dict]) -> dict[str, dict]:
    labeled = {}
    duplicate_ids = []
    for row in rows:
        if extract_option_id(row.get("review_status")) != "labeled":
            continue
        case_id = _case_id(row)
        if not case_id:
            continue
        if case_id in labeled:
            duplicate_ids.append(case_id)
        labeled[case_id] = row
    if duplicate_ids:
        raise ValueError("duplicate_labeled_reference:" + ",".join(sorted(set(duplicate_ids))))
    return labeled


def export_frozen_reference(
    *,
    draft_jsonl: Path = DEFAULT_DRAFT_JSONL,
    coach_a_workbook: Path = DEFAULT_COACH_A_WORKBOOK,
    output_jsonl: Path = DEFAULT_OUTPUT_JSONL,
    reference_status: str = "coach_reference",
) -> dict:
    if reference_status not in FROZEN_REFERENCE_STATUSES:
        raise ValueError(f"unsupported_reference_status:{reference_status}")

    draft_rows = _read_jsonl(Path(draft_jsonl))
    coach_rows = _load_workbook_rows(Path(coach_a_workbook))
    labeled_by_id = _labeled_rows_by_case_id(coach_rows)

    frozen_rows = []
    missing_labeled = []
    draft_ids = set()
    for draft_row in draft_rows:
        case_id = _case_id(draft_row)
        if not case_id:
            raise ValueError("draft_case_id_missing")
        draft_ids.add(case_id)
        coach_row = labeled_by_id.get(case_id)
        if coach_row is None:
            missing_labeled.append(case_id)
            continue
        frozen_rows.append(build_frozen_row(draft_row, coach_row, reference_status=reference_status))

    unexpected_labeled = sorted(set(labeled_by_id) - draft_ids)
    if missing_labeled or unexpected_labeled:
        payload = {
            "code": "missing_labeled_reference",
            "missing_labeled_case_ids": missing_labeled,
            "unexpected_labeled_case_ids": unexpected_labeled,
        }
        raise ValueError(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    output_jsonl = Path(output_jsonl)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    output_jsonl.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in frozen_rows) + ("\n" if frozen_rows else ""),
        encoding="utf-8",
    )
    return {
        "draft_jsonl": str(draft_jsonl),
        "coach_a_workbook": str(coach_a_workbook),
        "output_jsonl": str(output_jsonl),
        "row_count": len(frozen_rows),
        "reference_status": reference_status,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export frozen held-out reference JSONL from a reviewed coach workbook.")
    parser.add_argument("--draft-jsonl", type=Path, default=DEFAULT_DRAFT_JSONL)
    parser.add_argument("--coach-a-workbook", type=Path, default=DEFAULT_COACH_A_WORKBOOK)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument(
        "--reference-status",
        default="coach_reference",
        choices=sorted(FROZEN_REFERENCE_STATUSES),
        help="Frozen status to write after review/adjudication.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        summary = export_frozen_reference(
            draft_jsonl=args.draft_jsonl,
            coach_a_workbook=args.coach_a_workbook,
            output_jsonl=args.output_jsonl,
            reference_status=args.reference_status,
        )
    except ValueError as exc:
        try:
            payload = json.loads(str(exc))
            if not isinstance(payload, dict):
                payload = {"message": str(exc)}
        except json.JSONDecodeError:
            payload = {"message": str(exc)}
        payload.setdefault("code", "export_failed")
        payload["ok"] = False
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    summary["ok"] = True
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
