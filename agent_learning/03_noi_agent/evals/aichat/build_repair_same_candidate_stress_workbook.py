"""Build a same-candidate Repair stress-review workbook.

This script is offline-only. It reads existing response-generation JSONL files,
selects rows where Repair was actually applied, and writes a blind before/after
review template. It does not call any model, change prompts, or alter main
experiment labels.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Iterable

try:
    from openpyxl import Workbook
except ImportError:  # pragma: no cover - optional dependency.
    Workbook = None  # type: ignore[assignment]


DEFAULT_MAIN_JSONL = Path(
    "evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/combined_dev_ablation.jsonl"
)
DEFAULT_DBOX_JSONL = Path(
    "evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/combined_dev_ablation.jsonl"
)
DEFAULT_AUDIT_JSONL = Path("docs/research/dialogue_state_v3_50_context_readiness_audit_20260515.jsonl")
DEFAULT_OUTPUT_CSV = Path(
    "evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/"
    "repair_same_candidate_stress_candidate_list_20260517.csv"
)
DEFAULT_OUTPUT_XLSX = Path(
    "evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/"
    "repair_same_candidate_stress_workbook_template_20260517.xlsx"
)

REVIEW_FIELDS = [
    "before_overall_quality_score",
    "before_would_show_to_student",
    "before_leakage_label",
    "before_student_response_burden",
    "after_overall_quality_score",
    "after_would_show_to_student",
    "after_leakage_label",
    "after_student_response_burden",
    "after_too_vague",
    "review_notes",
]


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def _audit_map(path: Path) -> dict[str, dict]:
    return {str(row.get("case_id")): row for row in _read_jsonl(path)}


def _repair_instruction(row: dict) -> str:
    repair_result = row.get("repair_result") or {}
    removed = repair_result.get("removed_elements") or []
    notes = str(repair_result.get("repair_notes") or "").strip()
    if notes and removed:
        return notes + " Removed: " + "; ".join(str(item) for item in removed)
    if notes:
        return notes
    return str(row.get("repair_instructions") or "").strip()


def _safe_action(row: dict, *, post: bool = False) -> str:
    key = "post_repair_leakage_judge" if post else "initial_leakage_judge"
    judge = row.get(key) or row.get("leakage_judge") or {}
    return str(judge.get("safe_action") or row.get("safe_action") or "").strip()


def _leakage_level(row: dict, *, post: bool = False) -> str:
    key = "post_repair_leakage_judge" if post else "initial_leakage_judge"
    judge = row.get(key) or row.get("leakage_judge") or {}
    return str(judge.get("leakage_level") or row.get("leakage_level") or "").strip()


def _risk_reason(row: dict) -> str:
    judge = row.get("initial_leakage_judge") or row.get("leakage_judge") or {}
    return str(judge.get("risk_reason") or judge.get("reason") or "").strip()


def collect_repair_rows(
    paths: Iterable[Path],
    *,
    audit: dict[str, dict],
    sample_limit: int | None,
    seed: int,
) -> list[dict]:
    collected: list[dict] = []
    for path in paths:
        for row in _read_jsonl(path):
            if not row.get("repair_applied"):
                continue
            case_id = str(row.get("case_id") or "")
            audit_row = audit.get(case_id, {})
            repair_result = row.get("repair_result") or {}
            original = str(row.get("candidate_response_text") or "").strip()
            repaired = str(repair_result.get("repaired_response") or row.get("final_response_text") or "").strip()
            if not case_id or not original or not repaired:
                continue
            collected.append(
                {
                    "case_id": case_id,
                    "slice": audit_row.get("recommended_use") or "",
                    "bridge_bucket": audit_row.get("bridge_bucket") or row.get("bridge_bucket") or "",
                    "source_condition": row.get("condition_id") or "",
                    "source_run": path.parent.name,
                    "initial_safe_action": _safe_action(row, post=False),
                    "initial_leakage_level": _leakage_level(row, post=False),
                    "repair_instruction": _repair_instruction(row),
                    "post_repair_safe_action": _safe_action(row, post=True),
                    "post_repair_leakage_level": _leakage_level(row, post=True),
                    "repair_still_leaks": str(bool(repair_result.get("still_needs_leakage_check"))),
                    "student_message": row.get("student_message") or "",
                    "risk_reason": _risk_reason(row),
                    "original_candidate": original,
                    "repair_output": repaired,
                }
            )

    collected.sort(
        key=lambda item: (
            item.get("source_condition") != "bridge_contract_compact_guard_repair",
            item.get("slice") != "main_scaffold_eval",
            item.get("case_id"),
            item.get("source_condition"),
        )
    )
    if sample_limit is not None and len(collected) > sample_limit:
        rng = random.Random(seed)
        selected = collected[:]
        rng.shuffle(selected)
        selected = selected[:sample_limit]
        selected.sort(key=lambda item: (item.get("case_id"), item.get("source_condition")))
        collected = selected

    for index, item in enumerate(collected, 1):
        item["stress_id"] = f"repair_same_candidate_{index:03d}"
        for field in REVIEW_FIELDS:
            item.setdefault(field, "")
    return collected


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "stress_id",
        "case_id",
        "slice",
        "bridge_bucket",
        "source_condition",
        "source_run",
        "initial_safe_action",
        "initial_leakage_level",
        "repair_instruction",
        "post_repair_safe_action",
        "post_repair_leakage_level",
        "repair_still_leaks",
        "student_message",
        "risk_reason",
        "original_candidate",
        "repair_output",
        *REVIEW_FIELDS,
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_xlsx(rows: list[dict], path: Path) -> None:
    if Workbook is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "repair_same_candidate"
    fieldnames = list(rows[0].keys()) if rows else ["stress_id"]
    sheet.append(fieldnames)
    for row in rows:
        sheet.append([row.get(field, "") for field in fieldnames])
    sheet.freeze_panes = "A2"
    workbook.save(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-jsonl", type=Path, default=DEFAULT_MAIN_JSONL)
    parser.add_argument("--dbox-jsonl", type=Path, default=DEFAULT_DBOX_JSONL)
    parser.add_argument("--audit-jsonl", type=Path, default=DEFAULT_AUDIT_JSONL)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-xlsx", type=Path, default=DEFAULT_OUTPUT_XLSX)
    parser.add_argument("--sample-limit", type=int, default=None)
    parser.add_argument("--seed", type=int, default=20260517)
    args = parser.parse_args(argv)

    rows = collect_repair_rows(
        [args.main_jsonl, args.dbox_jsonl],
        audit=_audit_map(args.audit_jsonl),
        sample_limit=args.sample_limit,
        seed=args.seed,
    )
    write_csv(rows, args.output_csv)
    write_xlsx(rows, args.output_xlsx)
    print(f"Wrote {len(rows)} repair stress rows to {args.output_csv}")
    if Workbook is not None:
        print(f"Wrote workbook to {args.output_xlsx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
