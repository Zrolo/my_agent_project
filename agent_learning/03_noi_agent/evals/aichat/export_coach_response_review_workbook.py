import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import TextIO


DEFAULT_INPUT_PATH = Path("evals/aichat/bridge_offline_eval_results.jsonl")
DEFAULT_OUTPUT_PATH = Path("docs/research/coach_response_review_workbook_v1.csv")
DEFAULT_KEY_PATH = Path("docs/research/coach_response_review_workbook_v1.key.csv")

REVIEW_COLUMNS = [
    "case_id",
    "anonymized_response_id",
    "problem_ref",
    "student_message",
    "problem_context",
    "recent_dialogue",
    "response_text",
    "coach_bridge_identification_score",
    "coach_groundedness_score",
    "coach_scaffold_appropriateness_score",
    "coach_bridge_leakage_control_score",
    "coach_next_step_clarity_score",
    "coach_single_focus_coherence_score",
    "coach_bridge_oriented_micro_example_score",
    "coach_micro_example_applicability",
    "coach_leakage_label",
    "coach_preference_rank",
    "coach_overall_quality_score",
    "coach_would_show_to_student",
    "coach_reviewer_confidence",
    "coach_needs_discussion",
    "coach_notes",
    "review_status",
]

KEY_COLUMNS = [
    "anonymized_response_id",
    "case_id",
    "tutor_mode",
    "guard_mode",
    "pipeline_mode",
    "tutor_model_provider",
    "chat_thinking_mode",
    "final_response_source",
    "repair_applied",
    "blocked",
]


def load_result_rows(path: Path = DEFAULT_INPUT_PATH) -> list[dict]:
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def _context_from_row(row: dict, key: str) -> str:
    value = row.get(key)
    if value:
        return str(value)
    seed = row.get("seed") or row.get("input") or {}
    if isinstance(seed, dict):
        return str(seed.get(key) or "")
    return ""


def _response_text(row: dict) -> str:
    if row.get("final_response_text"):
        return str(row["final_response_text"])
    tutor_response = row.get("tutor_response") or {}
    return str(tutor_response.get("response_text") or row.get("candidate_response_text") or "")


def _anonymized_id(row: dict, ordinal: int, *, id_salt: str = "") -> str:
    case_id = str(row.get("case_id") or row.get("id") or ordinal)
    raw = "|".join(
        [
            id_salt,
            case_id,
            str(row.get("tutor_mode") or ""),
            str(row.get("guard_mode") or ""),
            str(row.get("pipeline_mode") or ""),
            str(row.get("final_response_source") or ""),
            str(ordinal),
        ]
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10]
    return f"resp_{digest}"


def build_review_rows(
    result_rows: list[dict],
    *,
    shuffle_seed: int = 17,
    id_salt: str = "",
) -> tuple[list[dict], list[dict]]:
    paired_rows = []
    for ordinal, row in enumerate(result_rows, 1):
        response_text = _response_text(row)
        if not response_text.strip():
            continue
        anonymized_id = _anonymized_id(row, ordinal, id_salt=id_salt)
        review_row = {
            "case_id": row.get("case_id") or row.get("id") or "",
            "anonymized_response_id": anonymized_id,
            "problem_ref": row.get("problem_ref", ""),
            "student_message": _context_from_row(row, "student_message"),
            "problem_context": _context_from_row(row, "problem_context"),
            "recent_dialogue": _context_from_row(row, "recent_dialogue"),
            "response_text": response_text,
            "coach_bridge_identification_score": "",
            "coach_groundedness_score": "",
            "coach_scaffold_appropriateness_score": "",
            "coach_bridge_leakage_control_score": "",
            "coach_next_step_clarity_score": "",
            "coach_single_focus_coherence_score": "",
            "coach_bridge_oriented_micro_example_score": "",
            "coach_micro_example_applicability": "",
            "coach_leakage_label": "",
            "coach_preference_rank": "",
            "coach_overall_quality_score": "",
            "coach_would_show_to_student": "",
            "coach_reviewer_confidence": "",
            "coach_needs_discussion": "",
            "coach_notes": "",
            "review_status": "unlabeled",
        }
        models = row.get("models") or {}
        key_row = {
            "anonymized_response_id": anonymized_id,
            "case_id": review_row["case_id"],
            "tutor_mode": row.get("tutor_mode") or models.get("tutor_mode") or "",
            "guard_mode": row.get("guard_mode") or models.get("guard_mode") or "",
            "pipeline_mode": row.get("pipeline_mode") or models.get("pipeline_mode") or "",
            "tutor_model_provider": models.get("tutor_model_provider") or "",
            "chat_thinking_mode": models.get("chat_thinking_mode") or "",
            "final_response_source": row.get("final_response_source") or "",
            "repair_applied": str(bool(row.get("repair_applied", False))).lower(),
            "blocked": str(bool(row.get("blocked", False))).lower(),
        }
        paired_rows.append((review_row, key_row))

    rng = random.Random(shuffle_seed)
    rng.shuffle(paired_rows)
    return [item[0] for item in paired_rows], [item[1] for item in paired_rows]


def write_review_csv(output: TextIO, rows: list[dict]) -> None:
    writer = csv.DictWriter(output, fieldnames=REVIEW_COLUMNS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def write_key_csv(output: TextIO, rows: list[dict]) -> None:
    writer = csv.DictWriter(output, fieldnames=KEY_COLUMNS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def export_response_review_workbook(
    *,
    input_jsonl: Path = DEFAULT_INPUT_PATH,
    output_csv: Path = DEFAULT_OUTPUT_PATH,
    key_csv: Path = DEFAULT_KEY_PATH,
    shuffle_seed: int = 17,
    id_salt: str = "",
) -> int:
    review_rows, key_rows = build_review_rows(
        load_result_rows(input_jsonl),
        shuffle_seed=shuffle_seed,
        id_salt=id_salt,
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    key_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        write_review_csv(f, review_rows)
    with key_csv.open("w", encoding="utf-8-sig", newline="") as f:
        write_key_csv(f, key_rows)
    return len(review_rows)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export blind coach response-review workbook from offline eval JSONL.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--key-csv", type=Path, default=DEFAULT_KEY_PATH)
    parser.add_argument("--shuffle-seed", type=int, default=17)
    parser.add_argument(
        "--id-salt",
        default="",
        help="Optional experiment/run id included in anonymized response ids to avoid cross-run collisions.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    row_count = export_response_review_workbook(
        input_jsonl=args.input_jsonl,
        output_csv=args.output_csv,
        key_csv=args.key_csv,
        shuffle_seed=args.shuffle_seed,
        id_salt=args.id_salt,
    )
    print(
        json.dumps(
            {"output_csv": str(args.output_csv), "key_csv": str(args.key_csv), "row_count": row_count},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
