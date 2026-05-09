import argparse
import csv
import json
import sys
from pathlib import Path
from typing import TextIO


DEFAULT_WORKBOOK_PATH = Path("docs/research/coach_seed_labeling_workbook_v1.csv")
DEFAULT_FOCUS_REGISTRY_PATH = Path("docs/research/focus_registry_v1.json")

PROBLEM_SOLVING_STATES = {
    "text_comprehension_blocked",
    "problem_representation_unclear",
    "strategy_generation_blocked",
    "strategy_misconception",
    "strategy_application_gap",
    "implementation_execution_gap",
    "debugging_verification_gap",
    "reflection_transfer_gap",
}

BRIDGE_FAMILIES = {
    "representation_bridge",
    "transition_bridge",
    "predicate_bridge",
    "modeling_bridge",
    "selection_bridge",
    "aggregation_bridge",
    "ordering_bridge",
    "mapping_bridge",
    "boundary_bridge",
    "complexity_bridge",
    "unknown_bridge",
}

HELP_SEEKING_TYPES = {
    "instrumental_help",
    "executive_help",
    "help_avoidance",
    "unclear",
}

HELP_LEVELS = {"L1", "L2", "L3"}

HELP_FORMS = {
    "guiding_question",
    "question",
    "hint",
    "micro_example",
    "counterexample",
    "constraint_probe",
    "debug_evidence_request",
    "local_code_hint",
    "code_diagnosis",
    "checklist",
    "partial_trace",
    "visual_table",
    "ascii_diagram",
    "pseudocode_skeleton",
    "summary",
    "summary_and_next_step",
    "understanding_check",
    "reflection_prompt",
}

REVIEW_STATUSES = {"unlabeled", "labeled", "needs_discussion", "review_seed_gold"}


def load_focus_ids(path: Path = DEFAULT_FOCUS_REGISTRY_PATH) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    focuses = data.get("focuses", data) if isinstance(data, dict) else data
    if not isinstance(focuses, list):
        raise ValueError(f"Focus registry must be a list or contain focuses: {path}")
    focus_ids = set()
    for item in focuses:
        if isinstance(item, str):
            focus_ids.add(item)
        elif isinstance(item, dict) and item.get("focus_id"):
            focus_ids.add(str(item["focus_id"]))
    return focus_ids


def load_workbook_rows(path: Path = DEFAULT_WORKBOOK_PATH) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _split_multivalue(value: str) -> list[str]:
    normalized = (value or "").replace("，", ";").replace(",", ";")
    return [item.strip() for item in normalized.split(";") if item.strip()]


def _add_error(errors: list[dict], row_number: int, case_id: str, field: str, value: str, message: str) -> None:
    errors.append(
        {
            "row_number": row_number,
            "case_id": case_id,
            "field": field,
            "value": value,
            "message": message,
        }
    )


def _validate_enum(
    errors: list[dict],
    *,
    row_number: int,
    case_id: str,
    row: dict,
    field: str,
    allowed: set[str],
) -> None:
    value = (row.get(field) or "").strip()
    if value and value not in allowed:
        _add_error(errors, row_number, case_id, field, value, f"Must be one of {sorted(allowed)}.")


def validate_rows(rows: list[dict], *, focus_ids: set[str]) -> list[dict]:
    errors: list[dict] = []
    for index, row in enumerate(rows, 2):
        case_id = row.get("case_id") or ""
        _validate_enum(
            errors,
            row_number=index,
            case_id=case_id,
            row=row,
            field="coach_problem_solving_state",
            allowed=PROBLEM_SOLVING_STATES,
        )
        _validate_enum(
            errors,
            row_number=index,
            case_id=case_id,
            row=row,
            field="coach_bridge_family",
            allowed=BRIDGE_FAMILIES,
        )
        _validate_enum(
            errors,
            row_number=index,
            case_id=case_id,
            row=row,
            field="coach_secondary_bridge_family",
            allowed=BRIDGE_FAMILIES,
        )
        _validate_enum(
            errors,
            row_number=index,
            case_id=case_id,
            row=row,
            field="coach_help_seeking_type",
            allowed=HELP_SEEKING_TYPES,
        )
        _validate_enum(
            errors,
            row_number=index,
            case_id=case_id,
            row=row,
            field="coach_allowed_help_level",
            allowed=HELP_LEVELS,
        )
        _validate_enum(
            errors,
            row_number=index,
            case_id=case_id,
            row=row,
            field="review_status",
            allowed=REVIEW_STATUSES,
        )

        known_focus = (row.get("coach_known_focus") or "").strip()
        if known_focus and known_focus != "unknown" and known_focus not in focus_ids:
            _add_error(
                errors,
                index,
                case_id,
                "coach_known_focus",
                known_focus,
                "Must be unknown or a focus_id from focus_registry_v1.json.",
            )

        for help_form in _split_multivalue(row.get("coach_help_forms") or ""):
            if help_form not in HELP_FORMS:
                _add_error(
                    errors,
                    index,
                    case_id,
                    "coach_help_forms",
                    help_form,
                    f"Each help form must be one of {sorted(HELP_FORMS)}.",
                )

        needs_new_focus = (row.get("coach_needs_new_focus") or "").strip().lower()
        if needs_new_focus and needs_new_focus not in {"true", "false"}:
            _add_error(
                errors,
                index,
                case_id,
                "coach_needs_new_focus",
                needs_new_focus,
                "Must be true or false.",
            )

        confidence = (row.get("coach_confidence") or "").strip()
        if confidence:
            try:
                value = int(confidence)
            except ValueError:
                value = -1
            if value < 1 or value > 5:
                _add_error(errors, index, case_id, "coach_confidence", confidence, "Must be an integer from 1 to 5.")
    return errors


def validate_workbook(input_csv: Path, focus_registry: Path) -> dict:
    rows = load_workbook_rows(input_csv)
    errors = validate_rows(rows, focus_ids=load_focus_ids(focus_registry))
    return {
        "input_csv": str(input_csv),
        "row_count": len(rows),
        "error_count": len(errors),
        "errors": errors,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate coach seed labeling workbook enum fields.")
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_WORKBOOK_PATH)
    parser.add_argument("--focus-registry", type=Path, default=DEFAULT_FOCUS_REGISTRY_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    report = validate_workbook(args.input_csv, args.focus_registry)
    output = stdout or sys.stdout
    output.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0 if report["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
