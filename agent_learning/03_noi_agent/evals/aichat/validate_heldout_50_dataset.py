import argparse
import json
import re
from collections import Counter
from pathlib import Path


DEFAULT_DATASET_PATH = Path("docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl")
DEFAULT_OUTPUT_JSON = Path("docs/research/bridgebench_cp_heldout_v1_50_validation_report.json")
DEFAULT_MAX_NO_RECENT_DIALOGUE = 10
DEFAULT_MIN_LONG_RECENT_DIALOGUE = 15
DEFAULT_MIN_CODE_EXCERPT = 10
DEFAULT_MIN_STUDENT_MESSAGE_LENGTH_BUCKETS = {
    "short": 20,
    "medium_short": 15,
    "medium_long": 10,
    "long": 5,
}
DEFAULT_DEV_SEED_PATHS = [
    Path("docs/research/bridgebench_cp_seed_v1.jsonl"),
    Path("docs/research/bridgebench_cp_seed_v2_gold_20.jsonl"),
    Path("docs/research/coach_seed_labeling_v2_gold_20.jsonl"),
]

REQUIRED_FIELDS = [
    "case_id",
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
    "review_notes_for_coach",
    "reference_label_status",
]

PROBLEM_STATEMENT_ACCESS_LEVELS = {
    "local_review_only",
    "public_summary_only",
    "open_license",
    "original_link_only",
}

LIST_FIELDS = ["forbidden_content", "success_criteria"]
DRAFT_ALLOWED_STATUSES = {
    "draft_needs_coach_review",
    "coach_reference_pending",
    "needs_adjudication",
}
GOLD_STATUSES = {
    "adjudicated_gold",
    "single_coach_reference",
    "coach_gold",
}
FROZEN_REFERENCE_STATUSES = GOLD_STATUSES | {
    "adjudicated_reference",
    "coach_reference",
}


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
            errors.append(
                {
                    "code": "invalid_json",
                    "file": str(path),
                    "line_number": line_number,
                    "message": str(exc),
                }
            )
            continue
        if not isinstance(row, dict):
            errors.append(
                {
                    "code": "row_not_object",
                    "file": str(path),
                    "line_number": line_number,
                }
            )
            continue
        row["_line_number"] = line_number
        rows.append(row)
    return rows, errors


def _load_case_ids(paths: list[Path]) -> set[str]:
    ids = set()
    for path in paths:
        rows, _errors = _load_jsonl(path)
        for row in rows:
            case_id = row.get("case_id") or row.get("id")
            if isinstance(case_id, str) and case_id:
                ids.add(case_id)
    return ids


def _is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len(value) == 0
    return False


def _recent_dialogue_bucket(value: str) -> str:
    text = (value or "").strip()
    if not text or text.upper() == "N/A":
        return "none"
    role_lines = [
        line
        for line in text.splitlines()
        if line.strip().lower().startswith(("student:", "assistant:", "学生：", "教练：", "ai：", "assistant："))
    ]
    if len(role_lines) >= 4:
        return "long"
    return "short"


def _role_lines(value: str) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    for raw_line in str(value or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "：" in line:
            role, content = line.split("：", 1)
        elif ":" in line:
            role, content = line.split(":", 1)
        else:
            continue
        role_key = role.strip().lower()
        if role_key in {"student", "user", "学生"}:
            lines.append(("student", content.strip()))
        elif role_key in {"assistant", "ai", "教练", "老师"}:
            lines.append(("assistant", content.strip()))
    return lines


def _text_bigrams(value: str) -> set[str]:
    compact = "".join(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", str(value or "")))
    if len(compact) < 2:
        return set(compact)
    return {compact[index : index + 2] for index in range(len(compact) - 1)}


def _text_similarity(left: str, right: str) -> float:
    left_bigrams = _text_bigrams(left)
    right_bigrams = _text_bigrams(right)
    if not left_bigrams or not right_bigrams:
        return 0.0
    return len(left_bigrams & right_bigrams) / len(left_bigrams | right_bigrams)


def _recent_dialogue_alignment(row: dict) -> dict:
    recent_dialogue = str(row.get("recent_dialogue") or "").strip()
    if not recent_dialogue or recent_dialogue.upper() == "N/A":
        return {"status": "no_recent_dialogue"}
    role_lines = _role_lines(recent_dialogue)
    if not role_lines:
        return {"status": "unparseable_recent_dialogue"}
    last_role, last_content = role_lines[-1]
    if last_role != "student":
        return {"status": "aligned_prior_context_ends_with_assistant"}
    student_message = str(row.get("student_message") or "").strip()
    similarity = _text_similarity(last_content, student_message)
    if similarity >= 0.45 or last_content in student_message or student_message in last_content:
        return {
            "status": "aligned_last_student_matches_current",
            "last_student_turn": last_content,
            "similarity": round(similarity, 4),
        }
    return {
        "status": "recent_dialogue_last_student_mismatch",
        "last_student_turn": last_content,
        "student_message": student_message,
        "similarity": round(similarity, 4),
    }


def _code_excerpt_bucket(value: str) -> str:
    text = (value or "").strip()
    if not text or text.upper() in {"N/A", "NA", "NONE"}:
        return "none"
    return "present"


def _student_message_length_bucket(value: str) -> str:
    length = len("".join(str(value or "").split()))
    if length <= 30:
        return "short"
    if length <= 70:
        return "medium_short"
    if length <= 140:
        return "medium_long"
    return "long"


def validate_dataset(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    *,
    expected_count: int = 50,
    dev_seed_paths: list[Path] | None = None,
    max_no_recent_dialogue: int | None = None,
    min_long_recent_dialogue: int | None = None,
    min_code_excerpt: int | None = None,
    min_student_message_length_buckets: dict[str, int] | None = None,
    require_frozen_status: bool = False,
) -> dict:
    dataset_path = Path(dataset_path)
    dev_seed_paths = [Path(path) for path in (dev_seed_paths or [])]
    rows, errors = _load_jsonl(dataset_path)
    dev_case_ids = _load_case_ids(dev_seed_paths) if dev_seed_paths else set()

    if len(rows) != expected_count:
        errors.append(
            {
                "code": "unexpected_row_count",
                "expected_count": expected_count,
                "actual_count": len(rows),
            }
        )

    seen_case_ids = set()
    duplicate_case_ids = set()
    category_counts = Counter()
    problem_source_platform_counts = Counter()
    problem_statement_access_level_counts = Counter()
    recent_dialogue_distribution = Counter()
    recent_dialogue_alignment_distribution = Counter()
    student_code_excerpt_distribution = Counter()
    student_message_length_distribution = Counter()

    for row in rows:
        line_number = row.get("_line_number")
        case_id = row.get("case_id")
        if isinstance(case_id, str) and case_id:
            if case_id in seen_case_ids:
                duplicate_case_ids.add(case_id)
            seen_case_ids.add(case_id)
        category = row.get("category")
        if isinstance(category, str) and category:
            category_counts[category] += 1
        problem_source_platform = row.get("problem_source_platform")
        if isinstance(problem_source_platform, str) and problem_source_platform.strip():
            problem_source_platform_counts[problem_source_platform.strip()] += 1
        problem_statement_access_level = row.get("problem_statement_access_level")
        if isinstance(problem_statement_access_level, str) and problem_statement_access_level.strip():
            problem_statement_access_level_counts[problem_statement_access_level.strip()] += 1
        recent_dialogue_distribution[_recent_dialogue_bucket(row.get("recent_dialogue") or "")] += 1
        alignment = _recent_dialogue_alignment(row)
        recent_dialogue_alignment_distribution[alignment["status"]] += 1
        if alignment["status"] in {
            "recent_dialogue_last_student_mismatch",
            "unparseable_recent_dialogue",
        }:
            errors.append(
                {
                    "code": alignment["status"],
                    "line_number": line_number,
                    "case_id": case_id,
                    **{
                        key: value
                        for key, value in alignment.items()
                        if key != "status"
                    },
                }
            )
        student_code_excerpt_distribution[_code_excerpt_bucket(row.get("student_code_excerpt") or "")] += 1
        student_message_length_distribution[
            _student_message_length_bucket(row.get("student_message") or "")
        ] += 1

        for field in REQUIRED_FIELDS:
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
            if field in row and (
                not isinstance(value, list)
                or not value
                or any(not isinstance(item, str) or not item.strip() for item in value)
            ):
                errors.append(
                    {
                        "code": "invalid_list_field",
                        "line_number": line_number,
                        "case_id": case_id,
                        "field": field,
                    }
                )

        source_url = row.get("problem_source_url")
        if isinstance(source_url, str) and source_url.strip() and not source_url.startswith(("https://", "http://")):
            errors.append(
                {
                    "code": "invalid_problem_source_url",
                    "line_number": line_number,
                    "case_id": case_id,
                    "problem_source_url": source_url,
                }
            )

        if (
            isinstance(problem_statement_access_level, str)
            and problem_statement_access_level.strip()
            and problem_statement_access_level not in PROBLEM_STATEMENT_ACCESS_LEVELS
        ):
            errors.append(
                {
                    "code": "invalid_problem_statement_access_level",
                    "line_number": line_number,
                    "case_id": case_id,
                    "problem_statement_access_level": problem_statement_access_level,
                    "allowed_values": sorted(PROBLEM_STATEMENT_ACCESS_LEVELS),
                }
            )

        status = row.get("reference_label_status")
        if require_frozen_status:
            if status not in FROZEN_REFERENCE_STATUSES:
                errors.append(
                    {
                        "code": "frozen_status_required",
                        "line_number": line_number,
                        "case_id": case_id,
                        "reference_label_status": status,
                    }
                )
        elif status in FROZEN_REFERENCE_STATUSES or status not in DRAFT_ALLOWED_STATUSES:
            errors.append(
                {
                    "code": "gold_status_not_allowed",
                    "line_number": line_number,
                    "case_id": case_id,
                    "reference_label_status": status,
                }
            )

        if case_id in dev_case_ids:
            errors.append(
                {
                    "code": "case_id_overlaps_dev_seed",
                    "line_number": line_number,
                    "case_id": case_id,
                }
            )

    for case_id in sorted(duplicate_case_ids):
        errors.append({"code": "duplicate_case_id", "case_id": case_id})

    if (
        max_no_recent_dialogue is not None
        and recent_dialogue_distribution.get("none", 0) > max_no_recent_dialogue
    ):
        errors.append(
            {
                "code": "too_many_no_recent_dialogue",
                "max_allowed": max_no_recent_dialogue,
                "actual_count": recent_dialogue_distribution.get("none", 0),
            }
        )
    if (
        min_long_recent_dialogue is not None
        and recent_dialogue_distribution.get("long", 0) < min_long_recent_dialogue
    ):
        errors.append(
            {
                "code": "too_few_long_recent_dialogue",
                "min_required": min_long_recent_dialogue,
                "actual_count": recent_dialogue_distribution.get("long", 0),
            }
        )
    if (
        min_code_excerpt is not None
        and student_code_excerpt_distribution.get("present", 0) < min_code_excerpt
    ):
        errors.append(
            {
                "code": "too_few_code_excerpts",
                "min_required": min_code_excerpt,
                "actual_count": student_code_excerpt_distribution.get("present", 0),
            }
        )
    for bucket, min_required in (min_student_message_length_buckets or {}).items():
        actual_count = student_message_length_distribution.get(bucket, 0)
        if actual_count < min_required:
            errors.append(
                {
                    "code": "too_few_student_message_length_bucket",
                    "bucket": bucket,
                    "min_required": min_required,
                    "actual_count": actual_count,
                }
            )

    return {
        "dataset_path": str(dataset_path),
        "row_count": len(rows),
        "expected_count": expected_count,
        "category_counts": dict(sorted(category_counts.items())),
        "problem_source_platform_counts": dict(sorted(problem_source_platform_counts.items())),
        "problem_statement_access_level_counts": dict(sorted(problem_statement_access_level_counts.items())),
        "recent_dialogue_distribution": {
            "none": recent_dialogue_distribution.get("none", 0),
            "short": recent_dialogue_distribution.get("short", 0),
            "long": recent_dialogue_distribution.get("long", 0),
        },
        "recent_dialogue_alignment_distribution": dict(sorted(recent_dialogue_alignment_distribution.items())),
        "student_code_excerpt_distribution": {
            "none": student_code_excerpt_distribution.get("none", 0),
            "present": student_code_excerpt_distribution.get("present", 0),
        },
        "student_message_length_distribution": {
            "short": student_message_length_distribution.get("short", 0),
            "medium_short": student_message_length_distribution.get("medium_short", 0),
            "medium_long": student_message_length_distribution.get("medium_long", 0),
            "long": student_message_length_distribution.get("long", 0),
        },
        "dev_seed_paths": [str(path) for path in dev_seed_paths],
        "dev_seed_case_id_count": len(dev_case_ids),
        "require_frozen_status": require_frozen_status,
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Research v1 50-case held-out draft dataset.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--expected-count", type=int, default=50)
    parser.add_argument("--max-no-recent-dialogue", type=int, default=DEFAULT_MAX_NO_RECENT_DIALOGUE)
    parser.add_argument("--min-long-recent-dialogue", type=int, default=DEFAULT_MIN_LONG_RECENT_DIALOGUE)
    parser.add_argument("--min-code-excerpt", type=int, default=DEFAULT_MIN_CODE_EXCERPT)
    parser.add_argument("--min-short-student-message", type=int, default=DEFAULT_MIN_STUDENT_MESSAGE_LENGTH_BUCKETS["short"])
    parser.add_argument(
        "--min-medium-short-student-message",
        type=int,
        default=DEFAULT_MIN_STUDENT_MESSAGE_LENGTH_BUCKETS["medium_short"],
    )
    parser.add_argument(
        "--min-medium-long-student-message",
        type=int,
        default=DEFAULT_MIN_STUDENT_MESSAGE_LENGTH_BUCKETS["medium_long"],
    )
    parser.add_argument("--min-long-student-message", type=int, default=DEFAULT_MIN_STUDENT_MESSAGE_LENGTH_BUCKETS["long"])
    parser.add_argument(
        "--require-frozen-status",
        action="store_true",
        help="Require reference_label_status to be adjudicated/coach reference for formal held-out launch.",
    )
    parser.add_argument("--dev-seed", type=Path, action="append", default=None)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    dev_seed_paths = args.dev_seed if args.dev_seed is not None else DEFAULT_DEV_SEED_PATHS
    result = validate_dataset(
        args.dataset,
        expected_count=args.expected_count,
        dev_seed_paths=dev_seed_paths,
        max_no_recent_dialogue=args.max_no_recent_dialogue,
        min_long_recent_dialogue=args.min_long_recent_dialogue,
        min_code_excerpt=args.min_code_excerpt,
        min_student_message_length_buckets={
            "short": args.min_short_student_message,
            "medium_short": args.min_medium_short_student_message,
            "medium_long": args.min_medium_long_student_message,
            "long": args.min_long_student_message,
        },
        require_frozen_status=args.require_frozen_status,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
