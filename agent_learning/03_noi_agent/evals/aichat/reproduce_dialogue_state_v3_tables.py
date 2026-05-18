"""Reproduce dialogue-state v3 evidence tables from machine-readable artifacts.

This script is intentionally offline-only. It does not call an LLM, create new
experimental conditions, or touch the online AIChat active path. It recomputes
paper-facing summaries from checked-in JSONL/CSV/JSON evidence files.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:  # Support direct `python evals/aichat/...py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.aichat import summarize_llm_grader_calibration
from evals.aichat import summarize_repair_same_candidate_stress

MAIN_HUMAN_REVIEW_DIR = Path(
    "evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review"
)
DBOX_FAIRNESS_DIR = Path(
    "evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review"
)
CASE_SLICE_JSONL = Path(
    "docs/research/dialogue_state_v3_50_context_readiness_audit_20260515.jsonl"
)

LABEL_FILES = {
    "coach_A_only": MAIN_HUMAN_REVIEW_DIR
    / "dialogue_state_v3_main_coach_A_round1_labels_20260517.jsonl",
    "coach_B_only": MAIN_HUMAN_REVIEW_DIR
    / "dialogue_state_v3_main_coach_B_round1_labels_20260517.jsonl",
    "priority60_adjudicated_plus_coachA": MAIN_HUMAN_REVIEW_DIR
    / "dialogue_state_v3_main_priority60_adjudicated_plus_coachA_labels_20260517.jsonl",
    "priority60_adjudicated_plus_coachB": MAIN_HUMAN_REVIEW_DIR
    / "dialogue_state_v3_main_priority60_adjudicated_plus_coachB_labels_20260517.jsonl",
}

LLM_PREDICTION_FILES = {
    "priority60_adjudicated_deepseek": Path(
        "docs/research/llm_grader_calibration_predictions_priority60_adjudicated_deepseek_20260518.jsonl"
    ),
    "adj_coachA_sample20_deepseek": Path(
        "docs/research/llm_grader_calibration_predictions_adj_coachA_sample20_deepseek_20260518.jsonl"
    ),
    "adj_coachB_sample20_deepseek": Path(
        "docs/research/llm_grader_calibration_predictions_adj_coachB_sample20_deepseek_20260518.jsonl"
    ),
}

PAIRED_UNCERTAINTY_JSON = (
    MAIN_HUMAN_REVIEW_DIR
    / "dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.json"
)
REPAIR_SUMMARY_JSON = (
    MAIN_HUMAN_REVIEW_DIR / "repair_same_candidate_stress_summary_20260517.json"
)
REPAIR_CANDIDATE_CSV = (
    MAIN_HUMAN_REVIEW_DIR / "repair_same_candidate_stress_candidate_list_20260517.csv"
)
REPAIR_KEY_CSV = (
    MAIN_HUMAN_REVIEW_DIR / "repair_same_candidate_stress_blind_review_key_20260517.csv"
)
DBOX_FAIRNESS_SUMMARY_JSON = (
    DBOX_FAIRNESS_DIR / "dbox_guard_repair_fairness_comparison_summary_20260517.json"
)

CONDITION_ORDER = [
    "enhanced_prompt_only_clean",
    "codehelp_codeaid_clean",
    "dbox_inspired_clean",
    "dbox_inspired_guard",
    "bridge_guided_dbox_style_guard",
    "bridge_contract_compact_guard",
    "bridge_contract_compact_guard_repair",
]

SLICE_ORDER = [
    "main_scaffold_eval",
    "main_eval_with_caution",
    "clarification_safety_slice",
    "policy_safety_slice",
]

PAIRWISE_COMPARISONS = [
    ("bridge_contract_compact_guard_repair", "dbox_inspired_guard"),
    ("bridge_contract_compact_guard_repair", "bridge_contract_compact_guard"),
    ("bridge_contract_compact_guard_repair", "dbox_inspired_clean"),
    ("dbox_inspired_guard", "dbox_inspired_clean"),
    ("codehelp_codeaid_clean", "enhanced_prompt_only_clean"),
    ("bridge_contract_compact_guard", "dbox_inspired_guard"),
]

CRITICAL_LEAKAGE = {"major_bridge_leakage", "answer_leakage"}
BURDEN_VALUES = ["low", "medium", "high"]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = raw_line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_true(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"true", "yes", "1"}


def _slice_map(root: Path) -> dict[str, str]:
    return {
        row["case_id"]: row["recommended_use"]
        for row in _read_jsonl(root / CASE_SLICE_JSONL)
        if row.get("case_id") and row.get("recommended_use")
    }


def _group_labels(
    rows: list[dict[str, Any]], slices: dict[str, str]
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        case_id = str(row.get("case_id") or "")
        condition = str(row.get("condition_id") or "")
        case_slice = slices.get(case_id)
        if case_slice and condition:
            grouped[case_slice][condition].append(row)
    return grouped


def _summarize_condition(rows: list[dict[str, Any]]) -> dict[str, Any]:
    overall_values = [
        value
        for row in rows
        if (value := _as_float(row.get("overall_quality_score"))) is not None
    ]
    burden = Counter(str(row.get("student_response_burden") or "") for row in rows)
    scaffold_values = []
    for row in rows:
        scores = row.get("scores") or {}
        value = _as_float(scores.get("scaffold_sufficiency"))
        if value is not None:
            scaffold_values.append(value)
    leakage = Counter(str(row.get("leakage_label") or "") for row in rows)
    return {
        "n": len(rows),
        "overall": (
            sum(overall_values) / len(overall_values) if overall_values else None
        ),
        "student_ready": sum(
            1
            for row in rows
            if _is_true(row.get("student_ready_simple_after_adjudication"))
        ),
        "safe_ready": sum(
            1
            for row in rows
            if _is_true(row.get("safe_ready_simple_after_adjudication"))
        ),
        "show_yes": sum(
            1 for row in rows if str(row.get("would_show_to_student") or "") == "yes"
        ),
        "show_no": sum(
            1 for row in rows if str(row.get("would_show_to_student") or "") == "no"
        ),
        "no_leakage": leakage.get("no_leakage", 0),
        "minor": leakage.get("minor_bridge_leakage", 0),
        "major_answer": sum(leakage.get(label, 0) for label in CRITICAL_LEAKAGE),
        "scaffold_avg": (
            sum(scaffold_values) / len(scaffold_values) if scaffold_values else None
        ),
        "burden": {value: burden.get(value, 0) for value in BURDEN_VALUES},
        "adjudicated_rows": sum(
            1 for row in rows if "adjudicated" in str(row.get("label_source") or "")
        ),
    }


def reproduce_main_tables(
    root: Path,
) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    slices = _slice_map(root)
    output: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    for scenario, rel_path in LABEL_FILES.items():
        grouped = _group_labels(_read_jsonl(root / rel_path), slices)
        for case_slice in SLICE_ORDER:
            output.setdefault(case_slice, {})[scenario] = {}
            for condition in CONDITION_ORDER:
                output[case_slice][scenario][condition] = _summarize_condition(
                    grouped.get(case_slice, {}).get(condition, [])
                )
    return output


def _index_by_case_condition(
    rows: list[dict[str, Any]], slices: dict[str, str], case_slice: str
) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row.get("case_id") or ""), str(row.get("condition_id") or "")): row
        for row in rows
        if slices.get(str(row.get("case_id") or "")) == case_slice
    }


def _safe_ready(row: dict[str, Any] | None) -> bool:
    return bool(row and _is_true(row.get("safe_ready_simple_after_adjudication")))


def _major_answer(row: dict[str, Any] | None) -> bool:
    return bool(row and str(row.get("leakage_label") or "") in CRITICAL_LEAKAGE)


def _overall(row: dict[str, Any] | None) -> float | None:
    if not row:
        return None
    return _as_float(row.get("overall_quality_score"))


def _paired_lookup(root: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    data = _read_json(root / PAIRED_UNCERTAINTY_JSON)
    return {
        (item["scenario"], item["first"], item["second"]): item
        for item in data.get("stats", [])
    }


def reproduce_pairwise(root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    slices = _slice_map(root)
    paired_reference = _paired_lookup(root)
    output: dict[str, dict[str, dict[str, Any]]] = {}
    for scenario, rel_path in LABEL_FILES.items():
        rows = _read_jsonl(root / rel_path)
        by_case_condition = _index_by_case_condition(rows, slices, "main_scaffold_eval")
        case_ids = sorted(
            {
                case_id
                for case_id, case_slice in slices.items()
                if case_slice == "main_scaffold_eval"
            }
        )
        scenario_output: dict[str, dict[str, Any]] = {}
        for first, second in PAIRWISE_COMPARISONS:
            deltas: list[float] = []
            wins = ties = losses = 0
            safe_ready_delta = 0
            major_answer_delta = 0
            for case_id in case_ids:
                first_row = by_case_condition.get((case_id, first))
                second_row = by_case_condition.get((case_id, second))
                first_overall = _overall(first_row)
                second_overall = _overall(second_row)
                if first_overall is None or second_overall is None:
                    continue
                delta = first_overall - second_overall
                deltas.append(delta)
                if delta > 0:
                    wins += 1
                elif delta < 0:
                    losses += 1
                else:
                    ties += 1
                safe_ready_delta += int(_safe_ready(first_row)) - int(
                    _safe_ready(second_row)
                )
                major_answer_delta += int(_major_answer(first_row)) - int(
                    _major_answer(second_row)
                )
            reference = paired_reference.get((scenario, first, second), {})
            scenario_output[f"{first}__vs__{second}"] = {
                "n": len(deltas),
                "win_tie_loss": {"win": wins, "tie": ties, "loss": losses},
                "mean_delta_overall": sum(deltas) / len(deltas) if deltas else None,
                "bootstrap_ci95_low": reference.get("bootstrap_ci95_low"),
                "bootstrap_ci95_high": reference.get("bootstrap_ci95_high"),
                "sign_flip_permutation_p": reference.get("sign_flip_permutation_p"),
                "safe_ready_delta": safe_ready_delta,
                "major_answer_delta": major_answer_delta,
            }
        output[scenario] = scenario_output
    return output


def reproduce_sensitivity(root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    output: dict[str, dict[str, dict[str, Any]]] = {}
    for scenario, rel_path in LABEL_FILES.items():
        rows = _read_jsonl(root / rel_path)
        by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_condition[str(row.get("condition_id") or "")].append(row)
        output[scenario] = {
            condition: _summarize_condition(by_condition.get(condition, []))
            for condition in CONDITION_ORDER
        }
        for condition, summary in output[scenario].items():
            condition_rows = by_condition.get(condition, [])
            summary["rank1"] = sum(
                1
                for row in condition_rows
                if _as_float(row.get("preference_rank")) == 1.0
            )
    return output


def reproduce_repair_summary(root: Path) -> dict[str, Any]:
    candidate_rows = summarize_repair_same_candidate_stress.read_rows(
        root / REPAIR_CANDIDATE_CSV
    )
    normalized_rows = summarize_repair_same_candidate_stress.normalize_blind_rows(
        candidate_rows,
        summarize_repair_same_candidate_stress.read_key(root / REPAIR_KEY_CSV),
    )
    summary = summarize_repair_same_candidate_stress.summarize(normalized_rows)
    if summary.get("labeled_pairs"):
        summary["evidence_source"] = "candidate_or_blinded_rows"
        return summary
    fallback = _read_json(root / REPAIR_SUMMARY_JSON)
    fallback["evidence_source"] = "checked_in_machine_summary_json"
    return fallback


def reproduce_dbox_fairness(root: Path) -> dict[str, Any]:
    return _read_json(root / DBOX_FAIRNESS_SUMMARY_JSON)


def reproduce_llm_metrics(root: Path) -> dict[str, dict[str, Any]]:
    output = {}
    for view, rel_path in LLM_PREDICTION_FILES.items():
        rows = _read_jsonl(root / rel_path)
        output[view] = summarize_llm_grader_calibration.summarize(rows)
    return output


def reproduce(root: Path | str = Path(".")) -> dict[str, Any]:
    root_path = Path(root)
    return {
        "metadata": {
            "project": "CP-MissingBridgeBench",
            "evidence_package": "dialogue_state_v3",
            "checkpoint": "dbbbd5c",
            "headline_slice": "main_scaffold_eval",
            "status": "formal_human_review_evidence_candidate_not_final_gold",
        },
        "main_paper_ready_tables": reproduce_main_tables(root_path),
        "pairwise": reproduce_pairwise(root_path),
        "sensitivity": reproduce_sensitivity(root_path),
        "repair_same_candidate_summary": reproduce_repair_summary(root_path),
        "dbox_fairness_addon": reproduce_dbox_fairness(root_path),
        "llm_grader_calibration": reproduce_llm_metrics(root_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args(argv)

    bundle = reproduce(args.root)
    text = json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote reproduced dialogue-state v3 evidence bundle: {args.output_json}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
