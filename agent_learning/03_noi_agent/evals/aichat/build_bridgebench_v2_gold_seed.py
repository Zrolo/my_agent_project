import argparse
import json
from pathlib import Path


DEFAULT_SEED_JSONL = Path("docs/research/bridgebench_cp_seed_v1.jsonl")
DEFAULT_GOLD_JSONL = Path("docs/research/coach_seed_labeling_v2_gold_20.jsonl")
DEFAULT_OUTPUT_JSONL = Path("docs/research/bridgebench_cp_seed_v2_gold_20.jsonl")


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _first(values: object) -> str:
    if isinstance(values, list):
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""
    if isinstance(values, str):
        return values.strip()
    return ""


def _join_values(values: object) -> str:
    if isinstance(values, list):
        return "；".join(str(value).strip() for value in values if str(value).strip())
    if isinstance(values, str):
        return values.strip()
    return ""


def _forbidden_completion_from_gold(gold_row: dict) -> str:
    bridge_specific = _join_values(gold_row.get("bridge_specific_forbidden_content"))
    general = _join_values(gold_row.get("general_forbidden_content"))
    if bridge_specific and general:
        return f"{bridge_specific}；{general}"
    return bridge_specific or general


def _promoted_focus_id(gold_row: dict) -> str:
    registered_focus_id = str(gold_row.get("registered_focus_id") or "").strip()
    new_focus_candidate = str(gold_row.get("new_focus_candidate") or "").strip()
    if registered_focus_id and registered_focus_id != "unknown":
        return registered_focus_id
    if new_focus_candidate:
        return new_focus_candidate
    return registered_focus_id


def _needs_new_focus(gold_row: dict) -> bool:
    if _promoted_focus_id(gold_row) and _promoted_focus_id(gold_row) != str(gold_row.get("registered_focus_id") or "").strip():
        return False
    if gold_row.get("focus_match_status") == "needs_new_focus":
        return True
    if gold_row.get("new_focus_candidate") and gold_row.get("registered_focus_id") in {"", "unknown"}:
        return True
    return False


def build_legacy_seed_row(seed_row: dict, gold_row: dict) -> dict:
    merged = dict(seed_row)
    merged.update(
        {
            "gold_student_state": gold_row.get("student_problem_solving_state", ""),
            "gold_bridge_family": gold_row.get("primary_bridge_family", ""),
            "gold_known_focus": _promoted_focus_id(gold_row),
            "gold_help_seeking_type": _first(gold_row.get("help_seeking_type")),
            "gold_missing_link": gold_row.get("missing_bridge_instance", ""),
            "gold_allowed_help_level": gold_row.get("max_scaffold_level", ""),
            "gold_forbidden_completion": _forbidden_completion_from_gold(gold_row),
            "needs_new_focus": _needs_new_focus(gold_row),
            "coach_v2_gold": gold_row,
        }
    )
    if gold_row.get("new_focus_candidate"):
        merged["new_focus_candidate"] = gold_row["new_focus_candidate"]
    return merged


def merge_seed_rows_with_v2_gold(seed_rows: list[dict], gold_rows: list[dict], output_path: Path) -> int:
    gold_by_case_id = {row.get("case_id"): row for row in gold_rows if row.get("case_id")}
    merged_rows = [
        build_legacy_seed_row(seed_row, gold_by_case_id[seed_row["id"]])
        for seed_row in seed_rows
        if seed_row.get("id") in gold_by_case_id
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in merged_rows) + ("\n" if merged_rows else ""),
        encoding="utf-8",
    )
    return len(merged_rows)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge coach v2 gold labels into BridgeBench seed rows.")
    parser.add_argument("--seed-jsonl", type=Path, default=DEFAULT_SEED_JSONL)
    parser.add_argument("--gold-jsonl", type=Path, default=DEFAULT_GOLD_JSONL)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    row_count = merge_seed_rows_with_v2_gold(
        load_jsonl(args.seed_jsonl),
        load_jsonl(args.gold_jsonl),
        args.output_jsonl,
    )
    print(
        json.dumps(
            {
                "seed_jsonl": str(args.seed_jsonl),
                "gold_jsonl": str(args.gold_jsonl),
                "output_jsonl": str(args.output_jsonl),
                "row_count": row_count,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
