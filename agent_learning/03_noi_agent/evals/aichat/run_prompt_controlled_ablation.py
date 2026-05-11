"""Run prompt-controlled ablations for Bridge Contract pilot studies.

This runner separates three possible sources of quality gains:

1. prompt effect: a stronger tutoring prompt without a specific bridge contract;
2. diagnosis effect: a predicted bridge contract from Bridge Judge;
3. contract validity effect: oracle vs shuffled bridge contracts.

It is offline-only and does not modify online AIChat behavior.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Callable

from noi_agent import bridge_judge_v1, chat as noi_agent_chat

from evals.aichat.run_bridge_offline_eval import (
    _call_bridge_contract_tutor,
    _call_single_llm_structured_tutor,
    _call_stage_with_retries,
    build_messages_from_seed_row,
    load_seed_rows,
)


DEFAULT_INPUT_JSONL = Path("docs/research/bridgebench_cp_seed_v1.jsonl")
DEFAULT_OUTPUT_JSONL = Path("evals/aichat/ad_hoc_runs/prompt_controlled_ablation_smoke_20260511.jsonl")

DEFAULT_VARIANTS = [
    "single_llm_structured",
    "enhanced_prompt_only",
    "bridge_contract_predicted",
    "bridge_contract_shuffled",
    "bridge_contract_oracle",
]


def build_oracle_bridge_result(row: dict) -> dict:
    forbidden = row.get("gold_forbidden_completion") or ""
    return {
        "problem_solving_state": row.get("gold_student_state") or "",
        "missing_bridge": {
            "family": row.get("gold_bridge_family") or "unknown_or_not_applicable",
            "subtype": "",
            "description": row.get("gold_missing_link") or "",
            "evidence": [row.get("student_message") or ""],
            "known_focus": row.get("gold_known_focus") or "unknown",
            "needs_new_focus": bool(row.get("needs_new_focus", False)),
        },
        "help_seeking_type": row.get("gold_help_seeking_type") or "",
        "allowed_help_level": row.get("gold_allowed_help_level") or "L1",
        "help_form": "guiding_question",
        "help_forms": ["guiding_question", "micro_example"],
        "forbidden_content": [forbidden] if forbidden else [],
        "leakage_risk": "high" if forbidden else "unknown",
        "confidence": 1.0,
        "reason": "oracle coach gold fields for prompt-controlled ablation",
    }


def build_shuffled_oracle_bridge_results(rows: list[dict]) -> dict[str, dict]:
    if not rows:
        return {}
    shuffled = {}
    for index, row in enumerate(rows):
        source = rows[(index + 1) % len(rows)]
        shuffled[row.get("id") or row.get("case_id") or str(index)] = {
            "source_case_id": source.get("id") or source.get("case_id") or str((index + 1) % len(rows)),
            "bridge_result": build_oracle_bridge_result(source),
        }
    return shuffled


def _enhanced_prompt_message() -> dict:
    return {
        "role": "assistant",
        "content": "\n".join(
            [
                "[Offline Enhanced Tutor Prompt - research control, not student text]",
                "你正在生成算法竞赛辅导回复，但这一组实验不给你具体 Bridge Contract。",
                "请遵守以下通用教学规则：",
                "1. 不要直接给完整题解或完整代码。",
                "2. 不要直接补完学生当前缺失的关键桥，例如完整状态定义、转移式、check 条件、边界更新、贪心准则或标记公式。",
                "3. 先根据学生话语判断当前最可能缺的桥，但不要输出内部标签。",
                "4. 如果使用微型例子，先说明这个例子要观察的桥梁问题；给足够小的例子；只问一个局部问题；最后要求学生抽象成可迁移规则。",
                "5. 只给一个清晰、可回答的下一步问题。",
                "6. 如果信息不足，先索取题面、代码、错误现象或学生已有尝试。",
                "7. 回复自然，不输出 JSON、[LEVEL:] 或内部评测字段。",
            ]
        ),
    }


def _call_enhanced_prompt_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    enhanced_messages = [*messages[:-1], _enhanced_prompt_message(), messages[-1]] if messages else [_enhanced_prompt_message()]
    problem_ref = (row.get("problem_ref") or row.get("id") or "unknown_problem").strip()
    case_id = row.get("id") or row.get("case_id") or problem_ref
    response_text, history_text, level = noi_agent_chat(
        enhanced_messages,
        "prompt_controlled_ablation_student",
        f"{problem_ref}::{case_id}",
        chat_model_provider=chat_model_provider,
    )
    return {
        "baseline_group": "enhanced_prompt_only",
        "tutor_mode": "enhanced_prompt_only",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": response_text,
        "history_text": history_text,
        "level": level,
    }


def _case_id(row: dict, fallback: int) -> str:
    return str(row.get("id") or row.get("case_id") or fallback)


def _finish_result(base: dict, tutor_result: dict, *, latency_ms: dict, total_start: float) -> dict:
    response_text = tutor_result.get("response_text") or ""
    base.update(
        {
            "candidate_response_text": response_text,
            "final_response_text": response_text,
            "final_response_source": "candidate",
            "tutor_response": tutor_result,
            "latency_ms": {**latency_ms, "total_latency_ms": round((time.perf_counter() - total_start) * 1000, 3)},
        }
    )
    return base


def _run_tutor_stage(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    *,
    tutor_fn: Callable,
    chat_model_provider: str | None,
) -> tuple[dict, float]:
    start = time.perf_counter()
    tutor_result = tutor_fn(row, messages, bridge_result, chat_model_provider=chat_model_provider)
    return tutor_result, round((time.perf_counter() - start) * 1000, 3)


def run_prompt_controlled_ablation(
    rows: list[dict],
    *,
    variants: list[str] | None = None,
    single_llm_tutor_fn: Callable = _call_single_llm_structured_tutor,
    enhanced_prompt_tutor_fn: Callable = _call_enhanced_prompt_tutor,
    bridge_contract_tutor_fn: Callable = _call_bridge_contract_tutor,
    bridge_judge_fn: Callable = bridge_judge_v1,
    chat_model_provider: str | None = None,
    judge_provider: str = "deepseek",
    max_retries: int = 0,
    progress_stream=None,
) -> list[dict]:
    variants = variants or DEFAULT_VARIANTS
    shuffled_contracts = build_shuffled_oracle_bridge_results(rows)
    results = []
    for ordinal, row in enumerate(rows, start=1):
        case_id = _case_id(row, ordinal)
        messages = build_messages_from_seed_row(row)
        for variant in variants:
            total_start = time.perf_counter()
            latency_ms: dict[str, float] = {}
            llm_call_count = 0
            retry_count = 0
            stage_errors: dict[str, str] = {}
            bridge_result: dict = {}
            contract_source = "none"
            contract_source_case_id = ""

            base = {
                "case_id": case_id,
                "problem_ref": row.get("problem_ref", ""),
                "topic": row.get("topic", ""),
                "student_message": row.get("student_message", ""),
                "problem_context": row.get("problem_context", ""),
                "ablation_variant": variant,
                "tutor_mode": variant,
                "guard_mode": "none",
                "pipeline_mode": "prompt_controlled_ablation",
                "contract_source": contract_source,
                "contract_source_case_id": contract_source_case_id,
                "chat_model_provider": chat_model_provider or "default",
                "judge_provider": judge_provider,
                "models": {
                    "tutor_mode": variant,
                    "guard_mode": "none",
                    "pipeline_mode": "prompt_controlled_ablation",
                    "tutor_model_provider": chat_model_provider or "default",
                    "judge_provider": judge_provider,
                },
                "llm_call_count": 0,
                "retry_count": 0,
                "stage_errors": stage_errors,
            }

            try:
                if variant == "single_llm_structured":
                    tutor_result, tutor_latency = _run_tutor_stage(
                        row,
                        messages,
                        {},
                        tutor_fn=single_llm_tutor_fn,
                        chat_model_provider=chat_model_provider,
                    )
                    llm_call_count += 1
                elif variant == "enhanced_prompt_only":
                    tutor_result, tutor_latency = _run_tutor_stage(
                        row,
                        messages,
                        {},
                        tutor_fn=enhanced_prompt_tutor_fn,
                        chat_model_provider=chat_model_provider,
                    )
                    llm_call_count += 1
                elif variant == "bridge_contract_predicted":
                    bridge_start = time.perf_counter()
                    bridge_result, bridge_retries = _call_stage_with_retries(
                        bridge_judge_fn,
                        {
                            "student_message": row.get("student_message", ""),
                            "messages": messages,
                            "problem_context": {
                                "problem_ref": row.get("problem_ref", ""),
                                "summary": row.get("problem_context", ""),
                            },
                            "student_code": row.get("student_code"),
                            "available_known_focus": row.get("available_known_focus", []),
                        },
                        judge_provider=judge_provider,
                        max_retries=max_retries,
                    )
                    latency_ms["bridge_judge_latency_ms"] = round((time.perf_counter() - bridge_start) * 1000, 3)
                    llm_call_count += 1 + bridge_retries
                    retry_count += bridge_retries
                    contract_source = "predicted"
                    tutor_result, tutor_latency = _run_tutor_stage(
                        row,
                        messages,
                        bridge_result,
                        tutor_fn=bridge_contract_tutor_fn,
                        chat_model_provider=chat_model_provider,
                    )
                    llm_call_count += 1
                elif variant == "bridge_contract_shuffled":
                    shuffled = shuffled_contracts.get(case_id) or {}
                    bridge_result = shuffled.get("bridge_result") or {}
                    contract_source = "shuffled_oracle"
                    contract_source_case_id = shuffled.get("source_case_id") or ""
                    tutor_result, tutor_latency = _run_tutor_stage(
                        row,
                        messages,
                        bridge_result,
                        tutor_fn=bridge_contract_tutor_fn,
                        chat_model_provider=chat_model_provider,
                    )
                    llm_call_count += 1
                elif variant == "bridge_contract_oracle":
                    bridge_result = build_oracle_bridge_result(row)
                    contract_source = "oracle_gold"
                    contract_source_case_id = case_id
                    tutor_result, tutor_latency = _run_tutor_stage(
                        row,
                        messages,
                        bridge_result,
                        tutor_fn=bridge_contract_tutor_fn,
                        chat_model_provider=chat_model_provider,
                    )
                    llm_call_count += 1
                else:
                    raise ValueError(f"Unsupported ablation variant: {variant}")
            except Exception as exc:
                stage_errors["ablation"] = f"{type(exc).__name__}: {exc}"
                tutor_result = {"response_text": ""}
                tutor_latency = 0.0

            latency_ms["tutor_latency_ms"] = tutor_latency
            base.update(
                {
                    "contract_source": contract_source,
                    "contract_source_case_id": contract_source_case_id,
                    "bridge_result": bridge_result,
                    "llm_call_count": llm_call_count,
                    "retry_count": retry_count,
                    "stage_errors": stage_errors,
                }
            )
            result = _finish_result(base, tutor_result, latency_ms=latency_ms, total_start=total_start)
            results.append(result)
            if progress_stream is not None:
                progress_stream.write(
                    f"prompt_controlled_case_done case={case_id} variant={variant} "
                    f"source={contract_source} error={bool(stage_errors)}\n"
                )
                progress_stream.flush()
    return results


def write_jsonl(path: Path | str, rows: list[dict]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_JSONL)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--chat-model-provider", default="deepseek")
    parser.add_argument("--judge-provider", default="deepseek")
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument(
        "--variants",
        default=",".join(DEFAULT_VARIANTS),
        help="Comma-separated variants to run.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    rows = load_seed_rows(args.input_jsonl)
    if args.limit > 0:
        rows = rows[: args.limit]
    variants = [item.strip() for item in args.variants.split(",") if item.strip()]
    results = run_prompt_controlled_ablation(
        rows,
        variants=variants,
        chat_model_provider=args.chat_model_provider,
        judge_provider=args.judge_provider,
        max_retries=max(0, args.max_retries),
        progress_stream=None,
    )
    write_jsonl(args.output_jsonl, results)
    print(json.dumps({"output_jsonl": str(args.output_jsonl), "row_count": len(results)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
