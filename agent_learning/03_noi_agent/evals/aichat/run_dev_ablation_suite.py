"""Run the Research v1 development ablation suite.

This script wraps the shared offline runner so the 10-20 case development
ablation uses one reproducible command instead of ad hoc per-baseline runs.
It is offline-only and does not change online AIChat behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from evals.aichat.export_coach_response_review_workbook import export_response_review_workbook
from evals.aichat.export_coach_response_review_workbook_xlsx import export_xlsx
from evals.aichat.run_bridge_offline_eval import (
    load_seed_rows,
    run_bridge_offline_eval_rows,
    write_result_rows,
)
from evals.aichat.summarize_bridge_offline_eval import summarize_bridge_offline_results, write_summary_files


DEFAULT_INPUT_JSONL = Path("docs/research/bridgebench_cp_seed_v2_gold_20.jsonl")
DEFAULT_OUTPUT_DIR = Path("evals/aichat/ad_hoc_runs/dev_ablation_20260511")

DEFAULT_CONDITIONS = [
    {
        "condition_id": "enhanced_prompt_only_clean",
        "tutor_mode": "enhanced_prompt_only",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "socratic_no_answer_clean",
        "tutor_mode": "socratic_no_answer_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "codehelp_codeaid_clean",
        "tutor_mode": "codehelp_codeaid_no_direct_solution_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_clean",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_guard",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_inspired_expert_decision_clean",
        "tutor_mode": "bridge_inspired_expert_decision_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "single_llm_structured_clean",
        "tutor_mode": "single_llm_structured",
        "pipeline_mode": "tutor_only",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "single_llm_structured_guard",
        "tutor_mode": "single_llm_structured",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_clean",
        "tutor_mode": "bridge_contract",
        "pipeline_mode": "tutor_only",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_guard",
        "tutor_mode": "bridge_contract",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_guard_repair",
        "tutor_mode": "bridge_contract",
        "pipeline_mode": "tutor_plus_guard_plus_repair",
        "guard_mode": "predicted",
    },
]

EDF_CORE_CONDITIONS = [
    {
        "condition_id": "enhanced_prompt_only_clean",
        "tutor_mode": "enhanced_prompt_only",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_guard",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "edf_inspired_clean",
        "tutor_mode": "edf_inspired_adaptive_scaffolding_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "edf_inspired_guard",
        "tutor_mode": "edf_inspired_adaptive_scaffolding_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_guard",
        "tutor_mode": "bridge_contract",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_guard_repair",
        "tutor_mode": "bridge_contract",
        "pipeline_mode": "tutor_plus_guard_plus_repair",
        "guard_mode": "predicted",
    },
]

PROMPT_COMPRESSION_CONDITIONS = [
    {
        "condition_id": "dbox_inspired_guard",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_guard",
        "tutor_mode": "bridge_contract",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_compact_guard",
        "tutor_mode": "bridge_contract_compact",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_minimal_guard",
        "tutor_mode": "bridge_contract_minimal",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
]

DBOX_BRIDGE_HYBRID_CONDITIONS = [
    {
        "condition_id": "enhanced_prompt_only_clean",
        "tutor_mode": "enhanced_prompt_only",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_clean",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_guard",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_compact_guard",
        "tutor_mode": "bridge_contract_compact",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_guided_dbox_style_guard",
        "tutor_mode": "bridge_guided_dbox_style_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
]

GUARD_REPAIR_FAIRNESS_ADDON_CONDITIONS = [
    {
        "condition_id": "enhanced_prompt_only_guard",
        "tutor_mode": "enhanced_prompt_only",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "enhanced_prompt_only_guard_repair",
        "tutor_mode": "enhanced_prompt_only",
        "pipeline_mode": "tutor_plus_guard_plus_repair",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_guard_repair",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard_plus_repair",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_compact_clean",
        "tutor_mode": "bridge_contract_compact",
        "pipeline_mode": "tutor_only",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_compact_guard_repair",
        "tutor_mode": "bridge_contract_compact",
        "pipeline_mode": "tutor_plus_guard_plus_repair",
        "guard_mode": "predicted",
    },
]

DIALOGUE_STATE_V3_MAIN_CONDITIONS = [
    {
        "condition_id": "enhanced_prompt_only_clean",
        "tutor_mode": "enhanced_prompt_only",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "codehelp_codeaid_clean",
        "tutor_mode": "codehelp_codeaid_no_direct_solution_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_clean",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_guard",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_guided_dbox_style_guard",
        "tutor_mode": "bridge_guided_dbox_style_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_compact_guard",
        "tutor_mode": "bridge_contract_compact",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_compact_guard_repair",
        "tutor_mode": "bridge_contract_compact",
        "pipeline_mode": "tutor_plus_guard_plus_repair",
        "guard_mode": "predicted",
    },
]

DIALOGUE_STATE_V3_REPAIR_FAIRNESS_ADDON_CONDITIONS = [
    {
        "condition_id": "dbox_inspired_guard_repair",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard_plus_repair",
        "guard_mode": "predicted",
    },
]

HELDOUT_MAIN_CONDITIONS = [
    {
        "condition_id": "current_system_deployment",
        "tutor_mode": "current_system",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "enhanced_prompt_only_clean",
        "tutor_mode": "enhanced_prompt_only",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "codehelp_codeaid_clean",
        "tutor_mode": "codehelp_codeaid_no_direct_solution_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "dbox_inspired_guard",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_inspired_expert_decision_clean",
        "tutor_mode": "bridge_inspired_expert_decision_tutor",
        "pipeline_mode": "tutor_only_no_diagnosis",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "single_llm_structured_guard",
        "tutor_mode": "single_llm_structured",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_guard",
        "tutor_mode": "bridge_contract",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    },
    {
        "condition_id": "bridge_contract_guard_repair",
        "tutor_mode": "bridge_contract",
        "pipeline_mode": "tutor_plus_guard_plus_repair",
        "guard_mode": "predicted",
    },
]

SAFE_SCAFFOLD_APPENDIX_CONDITION = {
    "condition_id": "bridge_contract_safe_scaffold",
    "tutor_mode": "bridge_contract",
    "pipeline_mode": "deterministic_safe_scaffold",
    "guard_mode": "predicted",
}


def build_conditions(
    *,
    condition_set: str = "default",
    include_safe_scaffold: bool = False,
) -> list[dict]:
    if condition_set == "default":
        source_conditions = DEFAULT_CONDITIONS
    elif condition_set == "edf_core":
        source_conditions = EDF_CORE_CONDITIONS
    elif condition_set == "prompt_compression":
        source_conditions = PROMPT_COMPRESSION_CONDITIONS
    elif condition_set == "dbox_bridge_hybrid":
        source_conditions = DBOX_BRIDGE_HYBRID_CONDITIONS
    elif condition_set == "guard_repair_fairness_addon":
        source_conditions = GUARD_REPAIR_FAIRNESS_ADDON_CONDITIONS
    elif condition_set == "dialogue_state_v3_main":
        source_conditions = DIALOGUE_STATE_V3_MAIN_CONDITIONS
    elif condition_set == "dialogue_state_v3_repair_fairness_addon":
        source_conditions = DIALOGUE_STATE_V3_REPAIR_FAIRNESS_ADDON_CONDITIONS
    elif condition_set == "heldout_main":
        source_conditions = HELDOUT_MAIN_CONDITIONS
    elif condition_set == "custom":
        source_conditions = []
    else:
        raise ValueError(f"Unsupported condition_set: {condition_set}")
    conditions = [dict(condition) for condition in source_conditions]
    if include_safe_scaffold:
        conditions.append(dict(SAFE_SCAFFOLD_APPENDIX_CONDITION))
    return conditions


def build_default_conditions(*, include_safe_scaffold: bool = False) -> list[dict]:
    return build_conditions(condition_set="default", include_safe_scaffold=include_safe_scaffold)


def _normalize_filter_ids(values: list[str] | None) -> list[str]:
    if not values:
        return []
    normalized: list[str] = []
    for value in values:
        for item in str(value).split(","):
            item = item.strip()
            if item:
                normalized.append(item)
    return normalized


def _seed_case_id(row: dict, fallback_index: int) -> str:
    return str(row.get("id") or row.get("case_id") or f"case_{fallback_index}")


def filter_rows_by_case_ids(rows: list[dict], case_ids: list[str] | None) -> list[dict]:
    requested = _normalize_filter_ids(case_ids)
    if not requested:
        return rows
    available = {_seed_case_id(row, index) for index, row in enumerate(rows, 1)}
    missing = [case_id for case_id in requested if case_id not in available]
    if missing:
        raise ValueError(f"Unknown case_id(s): {', '.join(missing)}")
    requested_set = set(requested)
    return [row for index, row in enumerate(rows, 1) if _seed_case_id(row, index) in requested_set]


def filter_conditions_by_ids(conditions: list[dict], condition_ids: list[str] | None) -> list[dict]:
    requested = _normalize_filter_ids(condition_ids)
    if not requested:
        return conditions
    available = {str(condition.get("condition_id") or "") for condition in conditions}
    missing = [condition_id for condition_id in requested if condition_id not in available]
    if missing:
        raise ValueError(f"Unknown condition_id(s): {', '.join(missing)}")
    requested_set = set(requested)
    return [condition for condition in conditions if str(condition.get("condition_id") or "") in requested_set]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def _run_condition(rows: list[dict], condition: dict, **kwargs) -> list[dict]:
    return run_bridge_offline_eval_rows(
        rows,
        tutor_mode=condition["tutor_mode"],
        pipeline_mode=condition["pipeline_mode"],
        guard_mode=condition.get("guard_mode", "predicted"),
        judge_provider=kwargs["judge_provider"],
        chat_model_provider=kwargs["chat_model_provider"],
        chat_thinking_mode=kwargs.get("chat_thinking_mode"),
        max_retries=kwargs["max_retries"],
        progress_stream=kwargs.get("progress_stream"),
    )


def run_dev_ablation_suite(
    *,
    input_jsonl: Path = DEFAULT_INPUT_JSONL,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    conditions: list[dict] | None = None,
    condition_set: str = "default",
    condition_ids: list[str] | None = None,
    case_ids: list[str] | None = None,
    limit: int | None = None,
    chat_model_provider: str | None = "deepseek_flash",
    judge_provider: str = "deepseek",
    chat_thinking_mode: str | None = None,
    max_retries: int = 0,
    include_safe_scaffold: bool = False,
    shuffle_seed: int = 17,
    run_condition_fn: Callable = _run_condition,
    summarize_fn: Callable = summarize_bridge_offline_results,
    write_summary_fn: Callable = write_summary_files,
    export_review_fn: Callable = export_response_review_workbook,
    export_xlsx_fn: Callable = export_xlsx,
    progress_stream=None,
) -> dict:
    conditions = conditions or build_conditions(
        condition_set=condition_set,
        include_safe_scaffold=include_safe_scaffold,
    )
    conditions = filter_conditions_by_ids(conditions, condition_ids)
    rows = load_seed_rows(input_jsonl)
    rows = filter_rows_by_case_ids(rows, case_ids)
    if limit is not None:
        rows = rows[:limit]
    if not rows:
        raise ValueError(f"No seed rows found in {input_jsonl}")

    output_dir.mkdir(parents=True, exist_ok=True)
    combined_rows: list[dict] = []
    condition_outputs = []
    for condition in conditions:
        condition_id = condition["condition_id"]
        condition_rows = run_condition_fn(
            rows,
            condition,
            judge_provider=judge_provider,
            chat_model_provider=chat_model_provider,
            chat_thinking_mode=chat_thinking_mode,
            max_retries=max_retries,
            progress_stream=progress_stream,
        )
        for row in condition_rows:
            row["condition_id"] = condition_id
            row["baseline_group"] = row.get("baseline_group") or condition_id
        condition_output = output_dir / f"{condition_id}.jsonl"
        write_result_rows(condition_output, condition_rows)
        condition_outputs.append(str(condition_output))
        combined_rows.extend(condition_rows)

    combined_jsonl = output_dir / "combined_dev_ablation.jsonl"
    _write_jsonl(combined_jsonl, combined_rows)

    summary = summarize_fn(combined_rows)
    summary_json = output_dir / "combined_dev_ablation_summary.json"
    summary_md = output_dir / "combined_dev_ablation_summary.md"
    summary_md_zh = output_dir / "combined_dev_ablation_summary.zh.md"
    write_summary_fn(summary_json, summary_md, summary, summary_md_zh)

    review_csv = output_dir / "coach_response_review_workbook_dev_ablation.csv"
    review_key_csv = output_dir / "coach_response_review_workbook_dev_ablation.key.csv"
    review_row_count = export_review_fn(
        input_jsonl=combined_jsonl,
        output_csv=review_csv,
        key_csv=review_key_csv,
        shuffle_seed=shuffle_seed,
        id_salt=output_dir.name,
    )
    review_xlsx = output_dir / "coach_response_review_workbook_dev_ablation.zh.xlsx"
    export_xlsx_fn(input_csv=review_csv, output_xlsx=review_xlsx)

    manifest = {
        "input_jsonl": str(input_jsonl),
        "output_dir": str(output_dir),
        "case_count": len(rows),
        "condition_set": condition_set,
        "condition_count": len(conditions),
        "conditions": conditions,
        "selected_case_ids": [_seed_case_id(row, index) for index, row in enumerate(rows, 1)],
        "selected_condition_ids": [condition["condition_id"] for condition in conditions],
        "condition_outputs": condition_outputs,
        "combined_row_count": len(combined_rows),
        "combined_jsonl": str(combined_jsonl),
        "summary_json": str(summary_json),
        "summary_md": str(summary_md),
        "summary_md_zh": str(summary_md_zh),
        "review_csv": str(review_csv),
        "review_key_csv": str(review_key_csv),
        "review_xlsx": str(review_xlsx),
        "review_row_count": review_row_count,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Research v1 development ablation suite.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_JSONL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--limit", type=int, help="Optional case limit for dev smoke or 10-20 case ablation.")
    parser.add_argument("--chat-model-provider", default="deepseek_flash")
    parser.add_argument("--judge-provider", default="deepseek")
    parser.add_argument("--chat-thinking-mode", choices=["enabled", "disabled"])
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument(
        "--condition-id",
        action="append",
        dest="condition_ids",
        help="Run only this condition id. Repeat or pass comma-separated ids for targeted reruns.",
    )
    parser.add_argument(
        "--case-id",
        action="append",
        dest="case_ids",
        help="Run only this case id. Repeat or pass comma-separated ids for targeted reruns.",
    )
    parser.add_argument(
        "--condition-set",
        choices=[
            "default",
            "edf_core",
            "heldout_main",
            "dialogue_state_v3_main",
            "dialogue_state_v3_repair_fairness_addon",
            "prompt_compression",
            "dbox_bridge_hybrid",
            "guard_repair_fairness_addon",
        ],
        default="default",
        help=(
            "Named condition set. Use dialogue_state_v3_main for the reviewed-candidate "
            "50-case response generation table; heldout_main is the earlier 8-condition matrix."
        ),
    )
    parser.add_argument(
        "--include-safe-scaffold",
        action="store_true",
        help="Append the dev-only deterministic safe scaffold appendix condition.",
    )
    parser.add_argument("--shuffle-seed", type=int, default=17)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    manifest = run_dev_ablation_suite(
        input_jsonl=args.input_jsonl,
        output_dir=args.output_dir,
        limit=args.limit,
        chat_model_provider=args.chat_model_provider,
        judge_provider=args.judge_provider,
        chat_thinking_mode=args.chat_thinking_mode,
        max_retries=args.max_retries,
        condition_set=args.condition_set,
        condition_ids=args.condition_ids,
        case_ids=args.case_ids,
        include_safe_scaffold=args.include_safe_scaffold,
        shuffle_seed=args.shuffle_seed,
        progress_stream=sys.stderr,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
