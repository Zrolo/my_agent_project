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
    limit: int | None = None,
    chat_model_provider: str | None = "deepseek_flash",
    judge_provider: str = "deepseek",
    chat_thinking_mode: str | None = None,
    max_retries: int = 0,
    shuffle_seed: int = 17,
    run_condition_fn: Callable = _run_condition,
    summarize_fn: Callable = summarize_bridge_offline_results,
    write_summary_fn: Callable = write_summary_files,
    export_review_fn: Callable = export_response_review_workbook,
    export_xlsx_fn: Callable = export_xlsx,
    progress_stream=None,
) -> dict:
    conditions = conditions or DEFAULT_CONDITIONS
    rows = load_seed_rows(input_jsonl)
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
        "condition_count": len(conditions),
        "conditions": conditions,
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
        shuffle_seed=args.shuffle_seed,
        progress_stream=sys.stderr,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
