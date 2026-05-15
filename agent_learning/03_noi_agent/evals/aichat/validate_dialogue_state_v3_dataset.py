"""Validate dialogue-state v3 held-out draft datasets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


DEFAULT_DATASET_PATH = Path("docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl")
DEFAULT_OUTPUT_JSON = Path("docs/research/dialogue_state_v3_validation_report_20260513.json")

REQUIRED_FIELDS = [
    "case_id",
    "source_case_id",
    "category",
    "problem_ref",
    "problem_source_platform",
    "problem_source_id",
    "problem_source_url",
    "problem_statement",
    "problem_statement_public_summary",
    "problem_statement_rights_note",
    "problem_statement_access_level",
    "student_message",
    "problem_context",
    "recent_dialogue",
    "student_code_excerpt",
    "student_known_state",
    "missing_bridge",
    "allowed_help_level",
    "forbidden_content",
    "success_criteria",
    "reference_label_status",
    "turn_position",
    "context_type",
    "student_scaffold_followability",
    "followability_label_confidence",
    "followability_evidence_quote",
    "prior_ai_scaffold",
    "student_reply_to_prior_scaffold",
    "expected_tutor_move",
    "fixed_recent_dialogue_source",
]

TURN_POSITIONS = {"initial", "followup"}
CONTEXT_TYPES = {
    "initial_question",
    "followup_after_correct_short_answer",
    "followup_after_partial_answer",
    "followup_after_wrong_answer",
    "followup_after_code_attempt",
    "followup_after_prerequisite_gap",
    "policy_direct_answer_special",
}
FOLLOWABILITY = {"NA", "F1", "F2", "F3", "F4"}
CONFIDENCE = {"high", "medium", "low"}
EXPECTED_TUTOR_MOVES = {"advance", "clarify", "micro_step", "prerequisite_repair", "safe_redirect"}
LIST_FIELDS = ["forbidden_content", "success_criteria"]


def _load_jsonl(path: Path) -> tuple[list[dict], list[dict]]:
    rows = []
    errors = []
    if not path.exists():
        return [], [{"code": "file_not_found", "file": str(path)}]
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append({"code": "invalid_json", "line_number": line_number, "message": str(exc)})
            continue
        if not isinstance(row, dict):
            errors.append({"code": "row_not_object", "line_number": line_number})
            continue
        row["_line_number"] = line_number
        rows.append(row)
    return rows, errors


def _is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not value
    return False


def validate_dataset(dataset_path: Path = DEFAULT_DATASET_PATH, *, expected_count: int = 50) -> dict:
    dataset_path = Path(dataset_path)
    rows, errors = _load_jsonl(dataset_path)
    seen_case_ids = set()
    duplicate_case_ids = set()
    turn_position_counts = Counter()
    context_type_counts = Counter()
    followability_counts = Counter()
    expected_tutor_move_counts = Counter()
    confidence_counts = Counter()

    if len(rows) != expected_count:
        errors.append({"code": "unexpected_row_count", "expected_count": expected_count, "actual_count": len(rows)})

    for row in rows:
        line_number = row.get("_line_number")
        case_id = row.get("case_id")
        if isinstance(case_id, str) and case_id:
            if case_id in seen_case_ids:
                duplicate_case_ids.add(case_id)
            seen_case_ids.add(case_id)
        for field in REQUIRED_FIELDS:
            if field in {"followability_evidence_quote", "prior_ai_scaffold", "student_reply_to_prior_scaffold"}:
                continue
            if field not in row or _is_blank(row.get(field)):
                errors.append(
                    {
                        "code": "missing_required_field",
                        "line_number": line_number,
                        "case_id": case_id,
                        "field": field,
                    }
                )
        for field in LIST_FIELDS:
            value = row.get(field)
            if not isinstance(value, list) or not value:
                errors.append(
                    {
                        "code": "invalid_list_field",
                        "line_number": line_number,
                        "case_id": case_id,
                        "field": field,
                    }
                )

        turn_position = row.get("turn_position")
        context_type = row.get("context_type")
        followability = row.get("student_scaffold_followability")
        confidence = row.get("followability_label_confidence")
        expected_move = row.get("expected_tutor_move")
        turn_position_counts[turn_position] += 1
        context_type_counts[context_type] += 1
        followability_counts[followability] += 1
        confidence_counts[confidence] += 1
        expected_tutor_move_counts[expected_move] += 1

        if turn_position not in TURN_POSITIONS:
            errors.append({"code": "invalid_turn_position", "line_number": line_number, "case_id": case_id})
        if context_type not in CONTEXT_TYPES:
            errors.append({"code": "invalid_context_type", "line_number": line_number, "case_id": case_id})
        if followability not in FOLLOWABILITY:
            errors.append({"code": "invalid_followability", "line_number": line_number, "case_id": case_id})
        if confidence not in CONFIDENCE:
            errors.append({"code": "invalid_followability_confidence", "line_number": line_number, "case_id": case_id})
        if expected_move not in EXPECTED_TUTOR_MOVES:
            errors.append({"code": "invalid_expected_tutor_move", "line_number": line_number, "case_id": case_id})

        if turn_position == "initial":
            if followability != "NA":
                errors.append(
                    {
                        "code": "initial_followability_must_be_na",
                        "line_number": line_number,
                        "case_id": case_id,
                        "student_scaffold_followability": followability,
                    }
                )
        elif turn_position == "followup":
            evidence = str(row.get("followability_evidence_quote") or "").strip()
            reply = str(row.get("student_reply_to_prior_scaffold") or "")
            recent_dialogue = str(row.get("recent_dialogue") or "")
            prior_ai = str(row.get("prior_ai_scaffold") or "").strip()
            if not evidence:
                errors.append({"code": "missing_followability_evidence", "line_number": line_number, "case_id": case_id})
            elif evidence not in reply:
                errors.append(
                    {
                        "code": "followability_evidence_not_in_student_reply",
                        "line_number": line_number,
                        "case_id": case_id,
                    }
                )
            if not reply.strip():
                errors.append({"code": "missing_student_reply_to_prior_scaffold", "line_number": line_number, "case_id": case_id})
            if not prior_ai:
                errors.append({"code": "missing_prior_ai_scaffold", "line_number": line_number, "case_id": case_id})
            if "AI：" not in recent_dialogue or "学生：" not in recent_dialogue:
                errors.append({"code": "recent_dialogue_missing_roles", "line_number": line_number, "case_id": case_id})
            if followability == "NA":
                errors.append({"code": "followup_followability_must_not_be_na", "line_number": line_number, "case_id": case_id})

        if row.get("fixed_recent_dialogue_source") != "synthetic_dialogue_state_v3":
            errors.append({"code": "invalid_fixed_recent_dialogue_source", "line_number": line_number, "case_id": case_id})
        source_url = row.get("problem_source_url")
        if isinstance(source_url, str) and source_url and not source_url.startswith(("http://", "https://")):
            errors.append({"code": "invalid_problem_source_url", "line_number": line_number, "case_id": case_id})

    for case_id in sorted(duplicate_case_ids):
        errors.append({"code": "duplicate_case_id", "case_id": case_id})

    return {
        "dataset_path": str(dataset_path),
        "row_count": len(rows),
        "expected_count": expected_count,
        "turn_position_counts": {key: turn_position_counts.get(key, 0) for key in ["initial", "followup"]},
        "context_type_counts": dict(sorted(context_type_counts.items())),
        "followability_counts": {key: followability_counts.get(key, 0) for key in ["NA", "F1", "F2", "F3", "F4"]},
        "expected_tutor_move_counts": dict(sorted(expected_tutor_move_counts.items())),
        "followability_confidence_counts": dict(sorted(confidence_counts.items())),
        "low_confidence_count": confidence_counts.get("low", 0),
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate dialogue-state v3 held-out draft dataset.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--expected-count", type=int, default=50)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    report = validate_dataset(args.dataset, expected_count=args.expected_count)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
