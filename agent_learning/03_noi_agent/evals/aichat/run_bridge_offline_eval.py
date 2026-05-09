import argparse
from contextlib import contextmanager
import inspect
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

from evals.aichat.bridge_candidate_retriever import (
    retrieve_algorithm_topic_candidates,
    retrieve_focus_candidates,
)
from noi_agent import bridge_judge_v1, chat as noi_agent_chat, leakage_judge_v1, repair_response_v1


DEFAULT_SEED_PATH = Path("docs/research/bridgebench_cp_seed_v1.jsonl")
DEFAULT_OUTPUT_PATH = Path("evals/aichat/bridge_offline_eval_results.jsonl")
DEFAULT_FOCUS_REGISTRY_PATH = Path("docs/research/focus_registry_v1.json")
PIPELINE_MODES = {
    "diagnosis_only",
    "tutor_only",
    "tutor_plus_guard",
    "tutor_plus_guard_plus_repair",
}
JUDGE_SCHEMA_MODES = {
    "full_schema_judge",
    "compact_contract_judge",
    "retrieval_augmented_compact_judge",
}

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
        bridge_family = item.get("bridge_family_v2") or item.get("bridge_family", "")
        compact.append(
            {
                "focus_id": focus_id,
                "bridge_family": bridge_family,
                "legacy_bridge_family": item.get("bridge_family", ""),
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


def _dialogue_to_text(messages: list | None) -> str:
    parts = []
    for item in messages or []:
        if not isinstance(item, dict):
            continue
        role = item.get("role") or "unknown"
        content = (item.get("content") or "").strip()
        if content:
            parts.append(f"{role}: {content}")
    return "\n".join(parts)


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
    micro_example_policy = "\n".join(
        [
            "桥梁导向微型例子规则：",
            "如果 help_form/help_forms 包含 micro_example，微型例子不能只是让学生完成临时填空、选择题或计算任务。",
            "必须按四步组织：",
            "1. 先说明这个例子要观察的桥梁问题。",
            "2. 给一个足够小、但仍贴近原题的小例子。",
            "3. 只问一个局部、可回答的问题。",
            "4. 要求学生把观察抽象成一句可迁移规则。",
        ]
    )
    return {
        "role": "assistant",
        "content": "\n".join(
            [
                "[Offline Bridge Contract - research control, not student text]",
                json.dumps(contract, ensure_ascii=False, indent=2),
                "请下一轮回复严格遵守 allowed_help_level 和 help_form，只补半步，不要出现 forbidden_content。",
                micro_example_policy,
                "如果学生问的是“为什么/含义/原理”，可以先给一句简短概念解释，再用一个问题引导迁移；不要一次连续抛出多个问题。",
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
    accepts_var_kwargs = any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()
    )
    accepts_provider = "judge_provider" in signature.parameters or accepts_var_kwargs
    if not accepts_var_kwargs:
        kwargs = {key: value for key, value in kwargs.items() if key in signature.parameters}
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


def _confidence_to_uncertainty(confidence: float | int | None) -> str:
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        return "unknown"
    if confidence >= 0.8:
        return "low"
    if confidence >= 0.6:
        return "medium"
    return "high"


def _first_topic(candidates: list[dict] | None) -> dict:
    if candidates:
        return candidates[0]
    return {"topic_l1": "unknown", "topic_l2": "unknown"}


def _runtime_bridge_contract_from_result(
    bridge_result: dict,
    *,
    algorithm_topic_candidates: list[dict] | None = None,
) -> dict:
    existing = bridge_result.get("runtime_bridge_contract")
    if isinstance(existing, dict):
        contract = dict(existing)
    else:
        missing_bridge = bridge_result.get("missing_bridge") or {}
        topic = _first_topic(algorithm_topic_candidates)
        focus_id = missing_bridge.get("known_focus") or bridge_result.get("selected_focus_id") or "unknown"
        confidence = bridge_result.get("confidence")
        contract = {
            "turn_type": bridge_result.get("turn_type") or "diagnosable_learning_turn",
            "diagnosis_uncertainty": bridge_result.get("diagnosis_uncertainty")
            or _confidence_to_uncertainty(confidence),
            "algorithm_topic_l1": topic.get("topic_l1") or "unknown",
            "algorithm_topic_l2": topic.get("topic_l2") or "unknown",
            "primary_bridge_family": missing_bridge.get("family")
            or bridge_result.get("primary_bridge_family")
            or "unknown_or_not_applicable",
            "selected_focus_id": focus_id,
            "selected_focus_confidence": confidence if isinstance(confidence, (int, float)) else 0,
            "max_scaffold_level": bridge_result.get("allowed_help_level")
            or bridge_result.get("max_scaffold_level")
            or "L1",
            "help_forms": _bridge_help_forms(bridge_result)[:2],
            "forbidden_content": list(bridge_result.get("forbidden_content") or [])[:3],
            "leakage_risk": bridge_result.get("leakage_risk") or "unknown",
            "confidence": confidence if isinstance(confidence, (int, float)) else 0,
        }
    contract["help_forms"] = list(contract.get("help_forms") or [])[:2]
    contract["forbidden_content"] = list(contract.get("forbidden_content") or [])[:3]
    return contract


def _estimate_tokens_from_payload(payload: object) -> int:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return max(1, round(len(text) / 4))


def _build_candidate_retrieval(
    row: dict,
    *,
    focus_registry: list | None,
) -> dict:
    student_message = row.get("student_message", "")
    problem_context = row.get("problem_context", "")
    topic_candidates = retrieve_algorithm_topic_candidates(
        student_message=student_message,
        problem_context=problem_context,
        limit=5,
    )
    focus_candidates = retrieve_focus_candidates(
        student_message=student_message,
        problem_context=problem_context,
        algorithm_topic_candidates=topic_candidates,
        focus_registry=focus_registry,
        limit=5,
    )
    return {
        "algorithm_topic_candidates": topic_candidates,
        "focus_candidates": focus_candidates,
        "focus_candidate_ids": [candidate.get("focus_id", "") for candidate in focus_candidates],
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
    result.setdefault("candidate_response_text", "")
    result.setdefault("final_response_text", "")
    result.setdefault("final_response_source", "none")
    result.setdefault("repair_applied", False)
    result.setdefault("blocked", False)
    result.setdefault("llm_call_count", 0)
    return result


def _record_latency(latency_ms: dict[str, float], key: str, start: float) -> None:
    latency_ms[key] = round((time.perf_counter() - start) * 1000, 3)


def _add_llm_calls(result: dict, count: int = 1) -> None:
    result["llm_call_count"] = int(result.get("llm_call_count") or 0) + count


def _effective_chat_thinking_mode(chat_thinking_mode: str | None) -> str:
    return (chat_thinking_mode or os.environ.get("NOI_CHAT_THINKING_MODE") or "profile_default").strip()


@contextmanager
def _temporary_chat_thinking_mode(chat_thinking_mode: str | None):
    if not chat_thinking_mode:
        yield
        return
    previous = os.environ.get("NOI_CHAT_THINKING_MODE")
    os.environ["NOI_CHAT_THINKING_MODE"] = chat_thinking_mode
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("NOI_CHAT_THINKING_MODE", None)
        else:
            os.environ["NOI_CHAT_THINKING_MODE"] = previous


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
    pipeline_mode: str,
    judge_schema_mode: str,
    judge_provider: str,
    max_retries: int,
    chat_thinking_mode: str | None,
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
        "problem_context": row.get("problem_context", ""),
        "recent_dialogue": _dialogue_to_text(row.get("prior_messages") or row.get("recent_dialogue")),
        "student_code_excerpt": row.get("student_code") or row.get("student_code_excerpt") or "",
        "tutor_mode": tutor_mode,
        "guard_mode": guard_mode,
        "pipeline_mode": pipeline_mode,
        "judge_schema_mode": judge_schema_mode,
        "focus_registry_size": len(_focus_registry_for_row(row, focus_registry)),
        "models": {
            "judge_model": _judge_model_name(judge_provider),
            "judge_provider": judge_provider,
            "tutor_model_provider": chat_model_provider or "default",
            "chat_thinking_mode": _effective_chat_thinking_mode(chat_thinking_mode),
            "tutor_mode": tutor_mode,
            "guard_mode": guard_mode,
            "pipeline_mode": pipeline_mode,
            "judge_schema_mode": judge_schema_mode,
        },
        "gold": _case_gold(row),
        "llm_call_count": 0,
    }

    available_focus = _focus_registry_for_row(row, focus_registry)
    candidate_retrieval = None
    if judge_schema_mode == "retrieval_augmented_compact_judge":
        stage_start = time.perf_counter()
        candidate_retrieval = _build_candidate_retrieval(row, focus_registry=available_focus)
        _record_latency(latency_ms, "candidate_retrieval_latency_ms", stage_start)
        result["candidate_retrieval"] = candidate_retrieval

    stage_start = time.perf_counter()
    try:
        bridge_kwargs = {
            "student_message": student_message,
            "messages": messages,
            "problem_context": problem_context,
            "student_code": row.get("student_code"),
            "available_known_focus": (candidate_retrieval or {}).get("focus_candidates") or available_focus,
        }
        if candidate_retrieval:
            bridge_kwargs.update(
                {
                    "top_k_algorithm_topics": candidate_retrieval["algorithm_topic_candidates"],
                    "top_k_registered_focus": candidate_retrieval["focus_candidates"],
                }
            )
        bridge_result, bridge_retries = _call_stage_with_retries(
            bridge_judge_fn,
            bridge_kwargs,
            judge_provider=judge_provider,
            max_retries=max_retries,
        )
        _add_llm_calls(result, 1 + bridge_retries)
        result["retry_count"] = bridge_retries
    except Exception as exc:
        _add_llm_calls(result)
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

    if judge_schema_mode != "full_schema_judge":
        result["runtime_bridge_contract"] = _runtime_bridge_contract_from_result(
            bridge_result,
            algorithm_topic_candidates=(candidate_retrieval or {}).get("algorithm_topic_candidates"),
        )
    result["prompt_budget_estimate"] = {
        "total_prompt_tokens_estimate": _estimate_tokens_from_payload(
            {
                "student_message": student_message,
                "problem_context": problem_context,
                "candidate_retrieval": candidate_retrieval or {},
                "runtime_bridge_contract": result.get("runtime_bridge_contract", {}),
            }
        )
    }

    if pipeline_mode == "diagnosis_only":
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)

    stage_start = time.perf_counter()
    try:
        with _temporary_chat_thinking_mode(chat_thinking_mode):
            tutor_result = tutor_fn(row, messages, bridge_result)
        _add_llm_calls(result)
    except Exception as exc:
        _add_llm_calls(result)
        _record_latency(latency_ms, "tutor_latency_ms", stage_start)
        stage_errors["tutor"] = f"{type(exc).__name__}: {exc}"
        result["error"] = "tutor_exception"
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)
    _record_latency(latency_ms, "tutor_latency_ms", stage_start)
    result["tutor_response"] = tutor_result
    candidate_response = tutor_result.get("response_text", "")
    result["candidate_response_text"] = candidate_response
    result["final_response_text"] = candidate_response
    result["final_response_source"] = "candidate"

    if pipeline_mode == "tutor_only":
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)

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
        _add_llm_calls(result, 1 + leakage_retries)
        result["retry_count"] = result.get("retry_count", 0) + leakage_retries
    except Exception as exc:
        _add_llm_calls(result)
        _record_latency(latency_ms, "leakage_judge_latency_ms", stage_start)
        stage_errors["leakage_judge"] = f"{type(exc).__name__}: {exc}"
        result["error"] = "leakage_judge_exception"
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)
    _record_latency(latency_ms, "leakage_judge_latency_ms", stage_start)
    result["leakage_judge_result"] = leakage_result
    if leakage_result.get("_failed"):
        stage_errors["leakage_judge"] = str(leakage_result.get("_error") or leakage_result.get("_reason") or "_failed")

    safe_action = leakage_result.get("safe_action")
    if safe_action == "block" and pipeline_mode == "tutor_plus_guard":
        result["final_response_text"] = ""
        result["final_response_source"] = "blocked"
        result["blocked"] = True

    if (
        pipeline_mode == "tutor_plus_guard_plus_repair"
        and safe_action in {"rewrite", "block"}
        and not leakage_result.get("_failed")
    ):
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
            _add_llm_calls(result, 1 + repair_retries)
            result["repair_result"] = repair_result
            result["retry_count"] = result.get("retry_count", 0) + repair_retries
            repaired_response = repair_result.get("repaired_response")
            if repaired_response:
                result["final_response_text"] = repaired_response
                result["final_response_source"] = "repair"
                result["repair_applied"] = True
                result["blocked"] = False
            elif safe_action == "block":
                result["final_response_text"] = ""
                result["final_response_source"] = "blocked"
                result["blocked"] = True
        except Exception as exc:
            _add_llm_calls(result)
            stage_errors["repair"] = f"{type(exc).__name__}: {exc}"
            result["error"] = "repair_exception"
            if safe_action == "block":
                result["final_response_text"] = ""
                result["final_response_source"] = "blocked"
                result["blocked"] = True
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
    pipeline_mode: str = "tutor_plus_guard_plus_repair",
    judge_schema_mode: str = "full_schema_judge",
    judge_provider: str = "deepseek",
    max_retries: int = 0,
    chat_thinking_mode: str | None = None,
    focus_registry: list | None = None,
    focus_registry_path: Path | None = DEFAULT_FOCUS_REGISTRY_PATH,
    limit: int | None = None,
    progress_stream=None,
) -> list[dict]:
    if guard_mode not in {"predicted", "oracle"}:
        raise ValueError(f"Unsupported guard_mode: {guard_mode}")
    if tutor_mode not in {"current_system", "bridge_contract"}:
        raise ValueError(f"Unsupported tutor_mode: {tutor_mode}")
    if pipeline_mode not in PIPELINE_MODES:
        raise ValueError(f"Unsupported pipeline_mode: {pipeline_mode}")
    if judge_schema_mode not in JUDGE_SCHEMA_MODES:
        raise ValueError(f"Unsupported judge_schema_mode: {judge_schema_mode}")
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    if chat_thinking_mode not in {None, "enabled", "disabled"}:
        raise ValueError(f"Unsupported chat_thinking_mode: {chat_thinking_mode}")
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
                pipeline_mode=pipeline_mode,
                judge_schema_mode=judge_schema_mode,
                judge_provider=judge_provider,
                max_retries=max_retries,
                chat_thinking_mode=chat_thinking_mode,
            )
            _write_progress(progress_stream, "CASE_DONE", index=index, total=total, case_id=case_id)
        except Exception as exc:
            result = {
                "case_id": case_id,
                "problem_ref": row.get("problem_ref", ""),
                "student_message": row.get("student_message", ""),
                "problem_context": row.get("problem_context", ""),
                "recent_dialogue": _dialogue_to_text(row.get("prior_messages") or row.get("recent_dialogue")),
                "student_code_excerpt": row.get("student_code") or row.get("student_code_excerpt") or "",
                "tutor_mode": tutor_mode,
                "guard_mode": guard_mode,
                "pipeline_mode": pipeline_mode,
                "judge_schema_mode": judge_schema_mode,
                "models": {
                    "judge_model": _judge_model_name(judge_provider),
                    "judge_provider": judge_provider,
                    "tutor_model_provider": chat_model_provider or "default",
                    "chat_thinking_mode": _effective_chat_thinking_mode(chat_thinking_mode),
                    "tutor_mode": tutor_mode,
                    "guard_mode": guard_mode,
                    "pipeline_mode": pipeline_mode,
                    "judge_schema_mode": judge_schema_mode,
                },
                "gold": _case_gold(row),
                "error": f"{type(exc).__name__}: {exc}",
                "latency_ms": {},
                "stage_errors": {"case": f"{type(exc).__name__}: {exc}"},
                "retry_count": 0,
                "candidate_response_text": "",
                "final_response_text": "",
                "final_response_source": "none",
                "repair_applied": False,
                "blocked": False,
                "llm_call_count": 0,
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
        "--pipeline-mode",
        choices=sorted(PIPELINE_MODES),
        default="tutor_plus_guard_plus_repair",
        help="Offline ablation pipeline: diagnosis only, tutor only, tutor plus guard, or full guard plus repair.",
    )
    parser.add_argument(
        "--judge-schema-mode",
        choices=sorted(JUDGE_SCHEMA_MODES),
        default="full_schema_judge",
        help="Bridge Judge schema mode: full human-like schema, compact contract, or retrieval-augmented compact contract.",
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
        "--chat-thinking-mode",
        choices=["enabled", "disabled"],
        help="Optional thinking mode override for current AIChat tutor calls.",
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
        pipeline_mode=args.pipeline_mode,
        judge_schema_mode=args.judge_schema_mode,
        judge_provider=args.judge_provider,
        max_retries=args.max_retries,
        chat_thinking_mode=args.chat_thinking_mode,
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
