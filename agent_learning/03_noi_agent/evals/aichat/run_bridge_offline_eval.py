import argparse
import inspect
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

from noi_agent import bridge_judge_v1, chat as noi_agent_chat, leakage_judge_v1, repair_response_v1


DEFAULT_SEED_PATH = Path("docs/research/bridgebench_cp_seed_v1.jsonl")
DEFAULT_OUTPUT_PATH = Path("evals/aichat/bridge_offline_eval_results.jsonl")
DEFAULT_FOCUS_REGISTRY_PATH = Path("docs/research/focus_registry_v1.json")

BridgeJudgeFn = Callable[..., dict]
TutorFn = Callable[[dict, list[dict], dict], dict]
LeakageJudgeFn = Callable[..., dict]
RepairFn = Callable[..., dict]


def _judge_model_name(judge_provider: str = "deepseek") -> str:
    if judge_provider == "kimi":
        return os.environ.get("KIMI_MODEL", "kimi-k2.6")
    if judge_provider in {"deepseek", "deepseek_flash", "deepseek-v4-flash"}:
        return os.environ.get("NOI_PEDAGOGICAL_JUDGE_MODEL", "deepseek-v4-flash")
    return judge_provider


def load_seed_rows(path: Path = DEFAULT_SEED_PATH) -> list[dict]:
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


def load_focus_registry(path: Path = DEFAULT_FOCUS_REGISTRY_PATH) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("focuses", [])
    if not isinstance(data, list):
        raise ValueError(f"Focus registry must be a list or contain a focuses list: {path}")
    registry = []
    for item in data:
        if isinstance(item, str):
            registry.append({"focus_id": item})
        elif isinstance(item, dict) and item.get("focus_id"):
            registry.append(dict(item))
    return registry


def _compact_focus_registry(focus_registry: list | None) -> list:
    compact = []
    for item in focus_registry or []:
        if isinstance(item, str):
            compact.append(item)
            continue
        if not isinstance(item, dict):
            continue
        focus_id = item.get("focus_id")
        if not focus_id:
            continue
        aliases = item.get("aliases") or []
        compact.append(
            {
                "focus_id": focus_id,
                "bridge_family": item.get("bridge_family", ""),
                "description": item.get("description", ""),
                "aliases": aliases[:8] if isinstance(aliases, list) else [],
            }
        )
    return compact


def _focus_registry_for_row(row: dict, focus_registry: list | None) -> list:
    if "available_known_focus" in row:
        return _compact_focus_registry(row.get("available_known_focus") or [])
    return _compact_focus_registry(focus_registry)


def _compact_context_line(label: str, value: str, max_chars: int = 1800) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "..."
    return f"{label}: {text}"


def build_messages_from_seed_row(row: dict) -> list[dict]:
    messages = [dict(message) for message in row.get("prior_messages", [])]
    context_lines = [
        _compact_context_line("题目编号/链接", row.get("problem_ref", ""), 300),
        _compact_context_line("题面/题意/约束", row.get("problem_context", ""), 1800),
    ]
    context_lines = [line for line in context_lines if line]
    student_message = row.get("student_message", "")
    if context_lines:
        content = "\n".join(
            [
                "[学生原始问题]",
                student_message,
                "",
                "[当前题目上下文：只用于离线研究诊断，不要直接照抄题解]",
                *context_lines,
                "",
                "请围绕学生当前卡点生成或评估渐进脚手架。",
            ]
        )
    else:
        content = student_message
    messages.append({"role": "user", "content": content})
    return messages


def _call_current_system_tutor(row: dict, messages: list[dict], chat_model_provider: str | None = None) -> dict:
    problem_ref = (row.get("problem_ref") or row.get("id") or "unknown_problem").strip()
    case_id = row.get("id") or problem_ref
    response_text, history_text, level = noi_agent_chat(
        messages,
        "bridge_offline_eval_student",
        f"{problem_ref}::{case_id}",
        chat_model_provider=chat_model_provider,
    )
    return {
        "baseline_group": "current_system",
        "tutor_mode": "current_system",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": response_text,
        "history_text": history_text,
        "level": level,
    }


def _default_tutor_fn(row: dict, messages: list[dict], bridge_result: dict) -> dict:
    return _call_current_system_tutor(row, messages)


def _make_default_tutor_fn(chat_model_provider: str | None) -> TutorFn:
    return lambda row, messages, bridge_result: _call_current_system_tutor(
        row,
        messages,
        chat_model_provider=chat_model_provider,
    )


def _bridge_contract_message(bridge_result: dict) -> dict:
    missing_bridge = bridge_result.get("missing_bridge") or {}
    contract = {
        "missing_bridge": {
            "family": missing_bridge.get("family", ""),
            "subtype": missing_bridge.get("subtype", ""),
            "known_focus": missing_bridge.get("known_focus", ""),
            "description": missing_bridge.get("description", ""),
        },
        "allowed_help_level": bridge_result.get("allowed_help_level", ""),
        "help_form": bridge_result.get("help_form", ""),
        "help_forms": _bridge_help_forms(bridge_result),
        "forbidden_content": bridge_result.get("forbidden_content") or [],
        "leakage_risk": bridge_result.get("leakage_risk", ""),
    }
    return {
        "role": "assistant",
        "content": "\n".join(
            [
                "[Offline Bridge Contract - research control, not student text]",
                json.dumps(contract, ensure_ascii=False, indent=2),
                "请下一轮回复严格遵守 allowed_help_level 和 help_form，只补半步，不要出现 forbidden_content。",
            ]
        ),
    }


def _call_bridge_contract_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    if messages:
        contract_messages = [*messages[:-1], _bridge_contract_message(bridge_result), messages[-1]]
    else:
        contract_messages = [_bridge_contract_message(bridge_result)]
    problem_ref = (row.get("problem_ref") or row.get("id") or "unknown_problem").strip()
    case_id = row.get("id") or problem_ref
    response_text, history_text, level = noi_agent_chat(
        contract_messages,
        "bridge_offline_eval_student",
        f"{problem_ref}::{case_id}",
        chat_model_provider=chat_model_provider,
    )
    return {
        "baseline_group": "bridge_contract_tutor",
        "tutor_mode": "bridge_contract",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": response_text,
        "history_text": history_text,
        "level": level,
    }


def _make_tutor_fn(tutor_mode: str, chat_model_provider: str | None) -> TutorFn:
    if tutor_mode == "bridge_contract":
        return lambda row, messages, bridge_result: _call_bridge_contract_tutor(
            row,
            messages,
            bridge_result,
            chat_model_provider=chat_model_provider,
        )
    return _make_default_tutor_fn(chat_model_provider)


def _make_bridge_judge_fn(judge_provider: str) -> BridgeJudgeFn:
    return bridge_judge_v1


def _make_leakage_judge_fn(judge_provider: str) -> LeakageJudgeFn:
    return leakage_judge_v1


def _make_repair_fn(judge_provider: str) -> RepairFn:
    return repair_response_v1


def _call_with_optional_judge_provider(fn: Callable, kwargs: dict, judge_provider: str) -> dict:
    signature = inspect.signature(fn)
    accepts_provider = "judge_provider" in signature.parameters or any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()
    )
    if accepts_provider:
        return fn(**kwargs, judge_provider=judge_provider)
    return fn(**kwargs)


def _call_stage_with_retries(
    fn: Callable,
    kwargs: dict,
    *,
    judge_provider: str,
    max_retries: int,
) -> tuple[dict, int]:
    retry_count = 0
    while True:
        result = _call_with_optional_judge_provider(fn, kwargs, judge_provider)
        if not result.get("_failed") or retry_count >= max_retries:
            return result, retry_count
        retry_count += 1


def _bridge_help_forms(bridge_result: dict) -> list[str]:
    help_forms = bridge_result.get("help_forms")
    if isinstance(help_forms, list):
        return [item for item in help_forms if isinstance(item, str) and item.strip()]
    help_form = bridge_result.get("help_form")
    return [help_form] if isinstance(help_form, str) and help_form.strip() else []


def _case_gold(row: dict) -> dict:
    return {
        "student_state": row.get("gold_student_state", ""),
        "bridge_family": row.get("gold_bridge_family", ""),
        "known_focus": row.get("gold_known_focus", ""),
        "help_seeking_type": row.get("gold_help_seeking_type", ""),
        "missing_link": row.get("gold_missing_link", ""),
        "allowed_help_level": row.get("gold_allowed_help_level", ""),
        "forbidden_completion": row.get("gold_forbidden_completion", ""),
        "needs_new_focus": bool(row.get("needs_new_focus", False)),
    }


def _write_progress(progress_stream, event: str, **fields) -> None:
    if progress_stream is None:
        return
    line = " ".join([event] + [f"{key}={value}" for key, value in fields.items()])
    progress_stream.write(line + "\n")
    flush = getattr(progress_stream, "flush", None)
    if callable(flush):
        flush()


def _finish_case_result(
    result: dict,
    *,
    latency_ms: dict[str, float],
    stage_errors: dict[str, str],
    total_start: float,
) -> dict:
    latency_ms["total_latency_ms"] = round((time.perf_counter() - total_start) * 1000, 3)
    result["latency_ms"] = latency_ms
    result["stage_errors"] = stage_errors
    result.setdefault("retry_count", 0)
    return result


def _record_latency(latency_ms: dict[str, float], key: str, start: float) -> None:
    latency_ms[key] = round((time.perf_counter() - start) * 1000, 3)


def _run_one_bridge_offline_case(
    row: dict,
    *,
    bridge_judge_fn: BridgeJudgeFn,
    tutor_fn: TutorFn,
    leakage_judge_fn: LeakageJudgeFn,
    repair_fn: RepairFn,
    chat_model_provider: str | None,
    focus_registry: list | None,
    guard_mode: str,
    tutor_mode: str,
    judge_provider: str,
    max_retries: int,
) -> dict:
    total_start = time.perf_counter()
    latency_ms: dict[str, float] = {}
    stage_errors: dict[str, str] = {}
    messages = build_messages_from_seed_row(row)
    student_message = row.get("student_message", "")
    problem_context = {
        "problem_ref": row.get("problem_ref", ""),
        "summary": row.get("problem_context", ""),
    }
    case_id = row.get("id") or row.get("case_id") or ""
    result = {
        "case_id": case_id,
        "problem_ref": row.get("problem_ref", ""),
        "topic": row.get("topic", ""),
        "student_message": student_message,
        "tutor_mode": tutor_mode,
        "guard_mode": guard_mode,
        "focus_registry_size": len(_focus_registry_for_row(row, focus_registry)),
        "models": {
            "judge_model": _judge_model_name(judge_provider),
            "judge_provider": judge_provider,
            "tutor_model_provider": chat_model_provider or "default",
            "tutor_mode": tutor_mode,
            "guard_mode": guard_mode,
        },
        "gold": _case_gold(row),
    }

    stage_start = time.perf_counter()
    try:
        bridge_result, bridge_retries = _call_stage_with_retries(
            bridge_judge_fn,
            {
                "student_message": student_message,
                "messages": messages,
                "problem_context": problem_context,
                "student_code": row.get("student_code"),
                "available_known_focus": _focus_registry_for_row(row, focus_registry),
            },
            judge_provider=judge_provider,
            max_retries=max_retries,
        )
        result["retry_count"] = bridge_retries
    except Exception as exc:
        _record_latency(latency_ms, "bridge_judge_latency_ms", stage_start)
        stage_errors["bridge_judge"] = f"{type(exc).__name__}: {exc}"
        result["error"] = "bridge_judge_exception"
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)
    _record_latency(latency_ms, "bridge_judge_latency_ms", stage_start)
    result["bridge_judge_result"] = bridge_result
    if bridge_result.get("_failed"):
        stage_errors["bridge_judge"] = str(bridge_result.get("_error") or bridge_result.get("_reason") or "_failed")
        result["error"] = "bridge_judge_failed"
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)

    stage_start = time.perf_counter()
    try:
        tutor_result = tutor_fn(row, messages, bridge_result)
    except Exception as exc:
        _record_latency(latency_ms, "tutor_latency_ms", stage_start)
        stage_errors["tutor"] = f"{type(exc).__name__}: {exc}"
        result["error"] = "tutor_exception"
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)
    _record_latency(latency_ms, "tutor_latency_ms", stage_start)
    result["tutor_response"] = tutor_result
    candidate_response = tutor_result.get("response_text", "")

    forbidden_content = list(bridge_result.get("forbidden_content") or [])
    used_gold_forbidden = False
    if (
        guard_mode == "oracle"
        and row.get("gold_forbidden_completion")
        and row["gold_forbidden_completion"] not in forbidden_content
    ):
        forbidden_content = [*forbidden_content, row["gold_forbidden_completion"]]
        used_gold_forbidden = True
    result["guard_contract"] = {
        "guard_mode": guard_mode,
        "used_gold_forbidden_completion": used_gold_forbidden,
        "forbidden_content": forbidden_content,
    }

    stage_start = time.perf_counter()
    try:
        leakage_result, leakage_retries = _call_stage_with_retries(
            leakage_judge_fn,
            {
                "student_message": student_message,
                "messages": messages,
                "problem_context": problem_context,
                "current_missing_bridge": bridge_result.get("missing_bridge", {}),
                "allowed_help_level": bridge_result.get("allowed_help_level", ""),
                "help_forms": _bridge_help_forms(bridge_result),
                "forbidden_content": forbidden_content,
                "candidate_response": candidate_response,
                "student_already_stated_bridge": bool(row.get("student_already_stated_bridge", False)),
            },
            judge_provider=judge_provider,
            max_retries=max_retries,
        )
        result["retry_count"] = result.get("retry_count", 0) + leakage_retries
    except Exception as exc:
        _record_latency(latency_ms, "leakage_judge_latency_ms", stage_start)
        stage_errors["leakage_judge"] = f"{type(exc).__name__}: {exc}"
        result["error"] = "leakage_judge_exception"
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)
    _record_latency(latency_ms, "leakage_judge_latency_ms", stage_start)
    result["leakage_judge_result"] = leakage_result
    if leakage_result.get("_failed"):
        stage_errors["leakage_judge"] = str(leakage_result.get("_error") or leakage_result.get("_reason") or "_failed")

    if leakage_result.get("safe_action") in {"rewrite", "block"} and not leakage_result.get("_failed"):
        stage_start = time.perf_counter()
        try:
            repair_result, repair_retries = _call_stage_with_retries(
                repair_fn,
                {
                    "original_candidate_response": candidate_response,
                    "leakage_judge_result": leakage_result,
                    "bridge_judge_result": bridge_result,
                    "student_message": student_message,
                    "messages": messages,
                },
                judge_provider=judge_provider,
                max_retries=max_retries,
            )
            result["repair_result"] = repair_result
            result["retry_count"] = result.get("retry_count", 0) + repair_retries
        except Exception as exc:
            stage_errors["repair"] = f"{type(exc).__name__}: {exc}"
            result["error"] = "repair_exception"
        finally:
            _record_latency(latency_ms, "repair_latency_ms", stage_start)

    return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)


def run_bridge_offline_eval_rows(
    rows: list[dict],
    *,
    bridge_judge_fn: BridgeJudgeFn | None = None,
    tutor_fn: TutorFn | None = None,
    leakage_judge_fn: LeakageJudgeFn | None = None,
    repair_fn: RepairFn | None = None,
    chat_model_provider: str | None = None,
    tutor_mode: str = "current_system",
    guard_mode: str = "predicted",
    judge_provider: str = "deepseek",
    max_retries: int = 0,
    focus_registry: list | None = None,
    focus_registry_path: Path | None = DEFAULT_FOCUS_REGISTRY_PATH,
    limit: int | None = None,
    progress_stream=None,
) -> list[dict]:
    if guard_mode not in {"predicted", "oracle"}:
        raise ValueError(f"Unsupported guard_mode: {guard_mode}")
    if tutor_mode not in {"current_system", "bridge_contract"}:
        raise ValueError(f"Unsupported tutor_mode: {tutor_mode}")
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    selected = rows[:limit] if limit is not None else rows
    effective_bridge_judge_fn = bridge_judge_fn or _make_bridge_judge_fn(judge_provider)
    effective_tutor_fn = tutor_fn or _make_tutor_fn(tutor_mode, chat_model_provider)
    effective_leakage_judge_fn = leakage_judge_fn or _make_leakage_judge_fn(judge_provider)
    effective_repair_fn = repair_fn or _make_repair_fn(judge_provider)
    effective_focus_registry = focus_registry
    if effective_focus_registry is None and focus_registry_path is not None:
        effective_focus_registry = load_focus_registry(focus_registry_path)
    result_rows = []
    total = len(selected)
    for index, row in enumerate(selected, 1):
        case_id = row.get("id") or row.get("case_id") or f"case_{index}"
        _write_progress(progress_stream, "CASE_START", index=index, total=total, case_id=case_id)
        try:
            result = _run_one_bridge_offline_case(
                row,
                bridge_judge_fn=effective_bridge_judge_fn,
                tutor_fn=effective_tutor_fn,
                leakage_judge_fn=effective_leakage_judge_fn,
                repair_fn=effective_repair_fn,
                chat_model_provider=chat_model_provider,
                focus_registry=effective_focus_registry,
                guard_mode=guard_mode,
                tutor_mode=tutor_mode,
                judge_provider=judge_provider,
                max_retries=max_retries,
            )
            _write_progress(progress_stream, "CASE_DONE", index=index, total=total, case_id=case_id)
        except Exception as exc:
            result = {
                "case_id": case_id,
                "problem_ref": row.get("problem_ref", ""),
                "student_message": row.get("student_message", ""),
                "tutor_mode": tutor_mode,
                "guard_mode": guard_mode,
                "models": {
                    "judge_model": _judge_model_name(judge_provider),
                    "judge_provider": judge_provider,
                    "tutor_model_provider": chat_model_provider or "default",
                    "tutor_mode": tutor_mode,
                    "guard_mode": guard_mode,
                },
                "gold": _case_gold(row),
                "error": f"{type(exc).__name__}: {exc}",
                "latency_ms": {},
                "stage_errors": {"case": f"{type(exc).__name__}: {exc}"},
                "retry_count": 0,
            }
            _write_progress(
                progress_stream,
                "CASE_ERROR",
                index=index,
                total=total,
                case_id=case_id,
                error=str(exc)[:120],
            )
        result_rows.append(result)
    return result_rows


def write_result_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run offline Bridge Judge + Leakage Judge evaluation rows.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_SEED_PATH, help="Seed turn JSONL file.")
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_PATH, help="Where to write result JSONL.")
    parser.add_argument("--limit", type=int, help="Optional case limit for smoke tests.")
    parser.add_argument(
        "--chat-model-provider",
        help="Optional provider id passed to current AIChat tutor, for model-controlled experiments.",
    )
    parser.add_argument(
        "--tutor-mode",
        choices=["current_system", "bridge_contract"],
        default="current_system",
        help="Tutor generation mode for offline comparison.",
    )
    parser.add_argument(
        "--guard-mode",
        choices=["predicted", "oracle"],
        default="predicted",
        help="Whether Leakage Judge sees only predicted forbidden content or oracle gold forbidden content.",
    )
    parser.add_argument(
        "--judge-provider",
        default="deepseek",
        help="Provider for offline Bridge/Leakage/Repair judges. Use deepseek or kimi.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=0,
        help="Retry count for failed offline judge stages.",
    )
    parser.add_argument(
        "--focus-registry",
        type=Path,
        default=DEFAULT_FOCUS_REGISTRY_PATH,
        help="Focus registry JSON used when seed rows do not provide available_known_focus.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    rows = run_bridge_offline_eval_rows(
        load_seed_rows(args.input_jsonl),
        limit=args.limit,
        chat_model_provider=args.chat_model_provider,
        tutor_mode=args.tutor_mode,
        guard_mode=args.guard_mode,
        judge_provider=args.judge_provider,
        max_retries=args.max_retries,
        focus_registry_path=args.focus_registry,
        progress_stream=sys.stderr,
    )
    write_result_rows(args.output_jsonl, rows)
    error_count = sum(1 for row in rows if row.get("error"))
    print(
        json.dumps(
            {
                "output_jsonl": str(args.output_jsonl),
                "case_count": len(rows),
                "error_count": error_count,
            },
            ensure_ascii=False,
        )
    )
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
