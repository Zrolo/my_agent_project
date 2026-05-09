import argparse
import json
from pathlib import Path


EXACT_FIELDS = [
    "student_problem_solving_state",
    "primary_bridge_family",
    "registered_focus_id",
    "max_scaffold_level",
    "leakage_risk",
]


def load_jsonl_by_case_id(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        row = json.loads(line)
        case_id = row.get("case_id")
        if not case_id:
            raise ValueError(f"Missing case_id at {path}:{line_number}")
        rows[str(case_id)] = row
    return rows


def _clean(value: object) -> str:
    return str(value or "").strip()


def _ratio(count: int, total: int) -> float | None:
    if total <= 0:
        return None
    return round(count / total, 3)


def _exact_agreement(paired_rows: list[tuple[dict, dict]], field: str) -> float | None:
    comparable = [(a, b) for a, b in paired_rows if _clean(a.get(field)) or _clean(b.get(field))]
    if not comparable:
        return None
    matches = sum(1 for a, b in comparable if _clean(a.get(field)) == _clean(b.get(field)))
    return _ratio(matches, len(comparable))


def _bridge_family_values(row: dict) -> set[str]:
    return {
        value
        for value in (
            _clean(row.get("primary_bridge_family")),
            _clean(row.get("secondary_bridge_family")),
        )
        if value
    }


def _focus_values(row: dict) -> set[str]:
    return {
        value
        for value in (
            _clean(row.get("registered_focus_id")),
            _clean(row.get("secondary_registered_focus_id")),
        )
        if value and value not in {"unknown", "not_applicable"}
    }


def _set_overlap_agreement(paired_rows: list[tuple[dict, dict]], value_fn) -> float | None:
    comparable = [(value_fn(a), value_fn(b)) for a, b in paired_rows if value_fn(a) or value_fn(b)]
    if not comparable:
        return None
    matches = sum(1 for a_values, b_values in comparable if bool(a_values & b_values))
    return _ratio(matches, len(comparable))


def _needs_adjudication(a: dict, b: dict) -> bool:
    if _clean(a.get("student_problem_solving_state")) != _clean(b.get("student_problem_solving_state")):
        return True
    if not (_bridge_family_values(a) & _bridge_family_values(b)):
        return True
    a_focus = _focus_values(a)
    b_focus = _focus_values(b)
    if (a_focus or b_focus) and not (a_focus & b_focus):
        return True
    if _clean(a.get("max_scaffold_level")) != _clean(b.get("max_scaffold_level")):
        return True
    return False


def summarize_agreement(annotator_a_jsonl: Path, annotator_b_jsonl: Path) -> dict:
    a_rows = load_jsonl_by_case_id(annotator_a_jsonl)
    b_rows = load_jsonl_by_case_id(annotator_b_jsonl)
    paired_case_ids = sorted(set(a_rows) & set(b_rows))
    paired_rows = [(a_rows[case_id], b_rows[case_id]) for case_id in paired_case_ids]
    exact = {field: _exact_agreement(paired_rows, field) for field in EXACT_FIELDS}
    relaxed = {
        "bridge_family_primary_or_secondary": _set_overlap_agreement(paired_rows, _bridge_family_values),
        "focus_primary_or_secondary": _set_overlap_agreement(paired_rows, _focus_values),
    }
    needs_adjudication = [
        case_id
        for case_id in paired_case_ids
        if _needs_adjudication(a_rows[case_id], b_rows[case_id])
    ]
    return {
        "annotator_a_jsonl": str(annotator_a_jsonl),
        "annotator_b_jsonl": str(annotator_b_jsonl),
        "annotator_a_count": len(a_rows),
        "annotator_b_count": len(b_rows),
        "paired_count": len(paired_case_ids),
        "unpaired_a_case_ids": sorted(set(a_rows) - set(b_rows)),
        "unpaired_b_case_ids": sorted(set(b_rows) - set(a_rows)),
        "exact_agreement": exact,
        "relaxed_agreement": relaxed,
        "needs_adjudication_count": len(needs_adjudication),
        "needs_adjudication_case_ids": needs_adjudication,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize agreement between two coach v2 JSONL label files.")
    parser.add_argument("--annotator-a-jsonl", type=Path, required=True)
    parser.add_argument("--annotator-b-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    summary = summarize_agreement(args.annotator_a_jsonl, args.annotator_b_jsonl)
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
