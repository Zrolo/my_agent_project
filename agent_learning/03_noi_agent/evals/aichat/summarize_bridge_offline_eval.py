import argparse
import json
import math
import sys
from pathlib import Path


DEFAULT_INPUT_PATH = Path("evals/aichat/bridge_offline_eval_results.jsonl")
DEFAULT_SUMMARY_JSON_PATH = Path("evals/aichat/bridge_offline_eval_summary.json")
DEFAULT_SUMMARY_MD_PATH = Path("evals/aichat/bridge_offline_eval_summary.md")
DEFAULT_SUMMARY_MD_ZH_PATH = Path("evals/aichat/bridge_offline_eval_summary.zh.md")
_CONTRACT_ENUMS = {
    "turn_type": {
        "diagnosable_learning_turn",
        "insufficient_context",
        "complete_solution_request",
        "complete_code_request",
        "critical_bridge_request",
        "algorithm_confirmation_request",
        "local_completion_request",
        "code_debugging_without_evidence",
        "code_debugging_with_evidence",
        "step_validation_request",
        "reflection_or_transfer_turn",
        "emotional_or_time_pressure",
        "unknown",
    },
    "diagnosis_uncertainty": {"low", "medium", "high", "unknown"},
    "algorithm_topic_l1": {
        "dp",
        "binary_search",
        "graph",
        "tree",
        "data_structure",
        "string",
        "greedy",
        "search",
        "math",
        "implementation",
        "debugging",
        "unknown",
    },
    "primary_bridge_family": {
        "goal_constraint_bridge",
        "modeling_bridge",
        "method_selection_bridge",
        "representation_state_bridge",
        "transition_recurrence_bridge",
        "predicate_condition_bridge",
        "ordering_dependency_bridge",
        "aggregation_contribution_bridge",
        "data_structure_operation_bridge",
        "correctness_invariant_bridge",
        "complexity_optimization_bridge",
        "implementation_boundary_bridge",
        "debugging_evidence_bridge",
        "reflection_transfer_bridge",
        "unknown_or_not_applicable",
        "unknown_bridge",
    },
    "max_scaffold_level": {"L0", "L1", "L2", "L3"},
    "leakage_risk": {"low", "medium", "high", "unknown"},
}


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


def _round_ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 3)


def _prediction(row: dict, key: str) -> str:
    bridge = row.get("bridge_judge_result") or {}
    contract = row.get("runtime_bridge_contract") or {}
    if key == "bridge_family":
        return str((bridge.get("missing_bridge") or {}).get("family") or contract.get("primary_bridge_family") or "")
    if key == "known_focus":
        return str((bridge.get("missing_bridge") or {}).get("known_focus") or contract.get("selected_focus_id") or "")
    if key == "student_state":
        return str(bridge.get("problem_solving_state") or "")
    if key == "allowed_help_level":
        return str(bridge.get("allowed_help_level") or contract.get("max_scaffold_level") or "")
    return str(bridge.get(key) or "")


def _gold(row: dict, key: str) -> str:
    return str((row.get("gold") or {}).get(key) or "")


def _accuracy(rows: list[dict], key: str) -> float | None:
    comparable = [row for row in rows if _gold(row, key) and _prediction(row, key)]
    if not comparable:
        return None
    correct = sum(1 for row in comparable if _gold(row, key) == _prediction(row, key))
    return _round_ratio(correct, len(comparable))


def _known_focus_accuracy_on_registered(rows: list[dict]) -> float | None:
    comparable = [
        row
        for row in rows
        if _gold(row, "known_focus")
        and _gold(row, "known_focus") != "unknown"
        and _prediction(row, "known_focus")
    ]
    if not comparable:
        return None
    correct = sum(1 for row in comparable if _gold(row, "known_focus") == _prediction(row, "known_focus"))
    return _round_ratio(correct, len(comparable))


def _unknown_focus_recall(rows: list[dict]) -> float | None:
    unknown_rows = [
        row
        for row in rows
        if _gold(row, "known_focus") == "unknown" or bool((row.get("gold") or {}).get("needs_new_focus"))
    ]
    if not unknown_rows:
        return None
    correct = 0
    for row in unknown_rows:
        bridge = row.get("bridge_judge_result") or {}
        missing_bridge = bridge.get("missing_bridge") or {}
        contract = row.get("runtime_bridge_contract") or {}
        if (
            missing_bridge.get("known_focus") == "unknown"
            or bool(missing_bridge.get("needs_new_focus"))
            or contract.get("selected_focus_id") in {"unknown", "not_applicable"}
        ):
            correct += 1
    return _round_ratio(correct, len(unknown_rows))


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if percentile == 50:
        middle = len(ordered) // 2
        if len(ordered) % 2:
            return round(ordered[middle], 3)
        return round((ordered[middle - 1] + ordered[middle]) / 2, 3)
    index = max(0, min(len(ordered) - 1, math.ceil((percentile / 100) * len(ordered)) - 1))
    return round(ordered[index], 3)


def _latency_summary(rows: list[dict]) -> dict:
    totals = []
    for row in rows:
        latency = row.get("latency_ms") or {}
        value = latency.get("total_latency_ms")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            totals.append(float(value))
    return {
        "total_p50": _percentile(totals, 50),
        "total_p95": _percentile(totals, 95),
    }


def _stage_error_counts(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        stage_errors = row.get("stage_errors") or {}
        if not isinstance(stage_errors, dict):
            continue
        for stage, error in stage_errors.items():
            if error:
                counts[str(stage)] = counts.get(str(stage), 0) + 1
    return dict(sorted(counts.items()))


def _runtime_contract_rows(rows: list[dict]) -> list[dict]:
    return [row for row in rows if isinstance(row.get("runtime_bridge_contract"), dict)]


def _is_valid_runtime_contract(contract: dict) -> bool:
    if len(contract.get("help_forms") or []) > 2:
        return False
    if len(contract.get("forbidden_content") or []) > 3:
        return False
    for key in [
        "turn_type",
        "diagnosis_uncertainty",
        "algorithm_topic_l1",
        "algorithm_topic_l2",
        "primary_bridge_family",
        "selected_focus_id",
        "max_scaffold_level",
        "leakage_risk",
    ]:
        if not contract.get(key):
            return False
    for key, allowed_values in _CONTRACT_ENUMS.items():
        if contract.get(key) not in allowed_values:
            return False
    for key in ["selected_focus_confidence", "confidence"]:
        value = contract.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0 or value > 1:
            return False
    return True


def _invalid_label_rate(rows: list[dict]) -> float | None:
    contract_rows = _runtime_contract_rows(rows)
    if not contract_rows:
        return None
    invalid_count = sum(1 for row in contract_rows if not _is_valid_runtime_contract(row["runtime_bridge_contract"]))
    return _round_ratio(invalid_count, len(contract_rows))


def _focus_out_of_registry_rate(rows: list[dict]) -> float | None:
    comparable = []
    for row in _runtime_contract_rows(rows):
        contract = row["runtime_bridge_contract"]
        selected_focus_id = str(contract.get("selected_focus_id") or "")
        if selected_focus_id in {"", "unknown", "not_applicable"}:
            continue
        candidate_ids = set(row.get("candidate_retrieval", {}).get("focus_candidate_ids") or [])
        if not candidate_ids:
            continue
        comparable.append((selected_focus_id, candidate_ids))
    if not comparable:
        return None
    out_count = sum(1 for selected_focus_id, candidate_ids in comparable if selected_focus_id not in candidate_ids)
    return _round_ratio(out_count, len(comparable))


def _self_contradiction_rate(rows: list[dict]) -> float | None:
    comparable = []
    for row in _runtime_contract_rows(rows):
        bridge_family = _prediction(row, "bridge_family")
        contract_family = str(row["runtime_bridge_contract"].get("primary_bridge_family") or "")
        if bridge_family and contract_family:
            comparable.append((bridge_family, contract_family))
    if not comparable:
        return None
    contradiction_count = sum(1 for bridge_family, contract_family in comparable if bridge_family != contract_family)
    return _round_ratio(contradiction_count, len(comparable))


def _average_prompt_tokens(rows: list[dict]) -> float | None:
    values = []
    for row in rows:
        estimate = row.get("prompt_budget_estimate") or {}
        value = estimate.get("total_prompt_tokens_estimate")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(float(value))
    return _avg(values)


def _average_llm_call_count(rows: list[dict]) -> float | None:
    values = []
    for row in rows:
        value = row.get("llm_call_count")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(float(value))
    return _avg(values)


def _experimental_group_key(row: dict) -> str:
    models = row.get("models") or {}
    tutor_response = row.get("tutor_response") or {}
    tutor_mode = row.get("tutor_mode") or models.get("tutor_mode") or tutor_response.get("tutor_mode") or "unknown"
    guard_mode = row.get("guard_mode") or models.get("guard_mode") or "unknown"
    pipeline_mode = row.get("pipeline_mode") or models.get("pipeline_mode") or "unknown"
    judge_schema_mode = row.get("judge_schema_mode") or models.get("judge_schema_mode") or "unknown"
    tutor_model_provider = (
        models.get("tutor_model_provider") or tutor_response.get("tutor_model_provider") or "unknown"
    )
    chat_thinking_mode = models.get("chat_thinking_mode") or "profile_default"
    return (
        f"tutor_mode={tutor_mode}|guard_mode={guard_mode}|pipeline_mode={pipeline_mode}|"
        f"judge_schema_mode={judge_schema_mode}|tutor_model_provider={tutor_model_provider}|"
        f"chat_thinking_mode={chat_thinking_mode}"
    )


def _group_summaries(rows: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        key = _experimental_group_key(row)
        grouped.setdefault(key, []).append(row)
    return {
        key: summarize_bridge_offline_results(group_rows, include_groups=False)
        for key, group_rows in sorted(grouped.items())
    }


def summarize_bridge_offline_results(rows: list[dict], *, include_groups: bool = True) -> dict:
    completed = [
        row
        for row in rows
        if not row.get("error")
        and isinstance(row.get("bridge_judge_result"), dict)
        and not row.get("bridge_judge_result", {}).get("_failed")
    ]
    leakage_rows = [row for row in completed if isinstance(row.get("leakage_judge_result"), dict)]
    leakage_count = sum(1 for row in leakage_rows if int(row["leakage_judge_result"].get("leakage_level") or 0) > 0)
    critical_count = sum(1 for row in leakage_rows if bool(row["leakage_judge_result"].get("is_critical_bridge_leakage")))
    answer_or_code_count = sum(1 for row in leakage_rows if bool(row["leakage_judge_result"].get("is_answer_or_code_leakage")))
    rewrite_count = sum(1 for row in leakage_rows if row["leakage_judge_result"].get("safe_action") == "rewrite")
    block_count = sum(1 for row in leakage_rows if row["leakage_judge_result"].get("safe_action") == "block")
    repair_count = sum(1 for row in completed if isinstance(row.get("repair_result"), dict))

    safe_action_counts: dict[str, int] = {}
    leakage_level_counts: dict[str, int] = {}
    for row in leakage_rows:
        leakage = row["leakage_judge_result"]
        safe_action = str(leakage.get("safe_action") or "unknown")
        safe_action_counts[safe_action] = safe_action_counts.get(safe_action, 0) + 1
        level = str(leakage.get("leakage_level", "unknown"))
        leakage_level_counts[level] = leakage_level_counts.get(level, 0) + 1

    confidences = []
    for row in completed:
        confidence = row.get("bridge_judge_result", {}).get("confidence")
        if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
            confidences.append(float(confidence))

    return {
        "case_count": len(rows),
        "completed_count": len(completed),
        "error_count": len(rows) - len(completed),
        "student_state_accuracy": _accuracy(completed, "student_state"),
        "bridge_family_accuracy": _accuracy(completed, "bridge_family"),
        "known_focus_accuracy": _accuracy(completed, "known_focus"),
        "known_focus_accuracy_on_registered": _known_focus_accuracy_on_registered(completed),
        "unknown_focus_recall": _unknown_focus_recall(completed),
        "help_seeking_type_accuracy": _accuracy(completed, "help_seeking_type"),
        "allowed_help_level_accuracy": _accuracy(completed, "allowed_help_level"),
        "leakage_rate": _round_ratio(leakage_count, len(leakage_rows)),
        "critical_bridge_leakage_rate": _round_ratio(critical_count, len(leakage_rows)),
        "answer_or_code_leakage_rate": _round_ratio(answer_or_code_count, len(leakage_rows)),
        "rewrite_rate": _round_ratio(rewrite_count, len(leakage_rows)),
        "block_rate": _round_ratio(block_count, len(leakage_rows)),
        "repair_rate": _round_ratio(repair_count, len(completed)),
        "invalid_label_rate": _invalid_label_rate(completed),
        "focus_out_of_registry_rate": _focus_out_of_registry_rate(completed),
        "self_contradiction_rate": _self_contradiction_rate(completed),
        "average_prompt_tokens": _average_prompt_tokens(completed),
        "average_llm_call_count": _average_llm_call_count(completed),
        "avg_bridge_judge_confidence": _avg(confidences),
        "latency_ms": _latency_summary(completed),
        "stage_error_counts": _stage_error_counts(rows),
        "groups": _group_summaries(rows) if include_groups else {},
        "safe_action_counts": dict(sorted(safe_action_counts.items())),
        "leakage_level_counts": dict(sorted(leakage_level_counts.items())),
        "error_cases": [
            str(row.get("case_id") or row.get("id") or "")
            for row in rows
            if row.get("error") or row.get("bridge_judge_result", {}).get("_failed")
        ],
    }


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def render_markdown_report(summary: dict) -> str:
    metrics = [
        ("Case Count", summary.get("case_count")),
        ("Completed Count", summary.get("completed_count")),
        ("Error Count", summary.get("error_count")),
        ("Student State Accuracy", summary.get("student_state_accuracy")),
        ("Bridge Family Accuracy", summary.get("bridge_family_accuracy")),
        ("Known Focus Accuracy", summary.get("known_focus_accuracy")),
        ("Known Focus Accuracy On Registered", summary.get("known_focus_accuracy_on_registered")),
        ("Unknown Focus Recall", summary.get("unknown_focus_recall")),
        ("Help Seeking Type Accuracy", summary.get("help_seeking_type_accuracy")),
        ("Allowed Help Level Accuracy", summary.get("allowed_help_level_accuracy")),
        ("Leakage Rate", summary.get("leakage_rate")),
        ("Critical Bridge Leakage Rate", summary.get("critical_bridge_leakage_rate")),
        ("Answer Or Code Leakage Rate", summary.get("answer_or_code_leakage_rate")),
        ("Rewrite Rate", summary.get("rewrite_rate")),
        ("Block Rate", summary.get("block_rate")),
        ("Repair Rate", summary.get("repair_rate")),
        ("Invalid Label Rate", summary.get("invalid_label_rate")),
        ("Focus Out Of Registry Rate", summary.get("focus_out_of_registry_rate")),
        ("Self Contradiction Rate", summary.get("self_contradiction_rate")),
        ("Average Prompt Tokens", summary.get("average_prompt_tokens")),
        ("Average LLM Call Count", summary.get("average_llm_call_count")),
        ("Avg Bridge Judge Confidence", summary.get("avg_bridge_judge_confidence")),
        ("Total Latency P50 ms", (summary.get("latency_ms") or {}).get("total_p50")),
        ("Total Latency P95 ms", (summary.get("latency_ms") or {}).get("total_p95")),
    ]
    lines = [
        "# Bridge Offline Eval Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {name} | {_fmt(value)} |" for name, value in metrics)
    lines.extend(
        [
            "",
            "## Leakage Levels",
            "",
            "```json",
            json.dumps(summary.get("leakage_level_counts", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## Safe Actions",
            "",
            "```json",
            json.dumps(summary.get("safe_action_counts", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## Stage Errors",
            "",
            "```json",
            json.dumps(summary.get("stage_error_counts", {}), ensure_ascii=False, indent=2),
            "```",
        ]
    )
    groups = summary.get("groups") or {}
    if groups:
        lines.extend(["", "## Groups", ""])
        for key, group_summary in groups.items():
            lines.extend(
                [
                    f"### {key}",
                    "",
                    "| Metric | Value |",
                    "| --- | ---: |",
                    f"| Case Count | {_fmt(group_summary.get('case_count'))} |",
                    f"| Completed Count | {_fmt(group_summary.get('completed_count'))} |",
                    f"| Bridge Family Accuracy | {_fmt(group_summary.get('bridge_family_accuracy'))} |",
                    f"| Critical Bridge Leakage Rate | {_fmt(group_summary.get('critical_bridge_leakage_rate'))} |",
                    f"| Average LLM Call Count | {_fmt(group_summary.get('average_llm_call_count'))} |",
                    f"| Total Latency P50 ms | {_fmt((group_summary.get('latency_ms') or {}).get('total_p50'))} |",
                    "",
                ]
            )
    error_cases = summary.get("error_cases") or []
    if error_cases:
        lines.extend(["", "## Error Cases", ""])
        lines.extend(f"- {case_id}" for case_id in error_cases)
    return "\n".join(lines) + "\n"


def render_markdown_report_zh(summary: dict) -> str:
    metrics = [
        ("样本数", summary.get("case_count")),
        ("完成数", summary.get("completed_count")),
        ("错误数", summary.get("error_count")),
        ("学生状态准确率", summary.get("student_state_accuracy")),
        ("桥梁大类准确率", summary.get("bridge_family_accuracy")),
        ("知识焦点准确率", summary.get("known_focus_accuracy")),
        ("已注册知识焦点准确率", summary.get("known_focus_accuracy_on_registered")),
        ("未知焦点召回率", summary.get("unknown_focus_recall")),
        ("求助类型准确率", summary.get("help_seeking_type_accuracy")),
        ("帮助强度准确率", summary.get("allowed_help_level_accuracy")),
        ("泄露率", summary.get("leakage_rate")),
        ("关键桥梁泄露率", summary.get("critical_bridge_leakage_rate")),
        ("答案/代码泄露率", summary.get("answer_or_code_leakage_rate")),
        ("重写率", summary.get("rewrite_rate")),
        ("阻断率", summary.get("block_rate")),
        ("修复率", summary.get("repair_rate")),
        ("无效标签率", summary.get("invalid_label_rate")),
        ("焦点越界率", summary.get("focus_out_of_registry_rate")),
        ("自相矛盾率", summary.get("self_contradiction_rate")),
        ("平均 Prompt Token 估计", summary.get("average_prompt_tokens")),
        ("平均 LLM 调用次数", summary.get("average_llm_call_count")),
        ("Bridge Judge 平均置信度", summary.get("avg_bridge_judge_confidence")),
        ("总延迟 P50 ms", (summary.get("latency_ms") or {}).get("total_p50")),
        ("总延迟 P95 ms", (summary.get("latency_ms") or {}).get("total_p95")),
    ]
    lines = [
        "# Bridge 离线评测摘要",
        "",
        "| 指标 | 数值 |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {name} | {_fmt(value)} |" for name, value in metrics)
    lines.extend(
        [
            "",
            "## 泄露等级分布",
            "",
            "```json",
            json.dumps(summary.get("leakage_level_counts", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 安全动作分布",
            "",
            "```json",
            json.dumps(summary.get("safe_action_counts", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 阶段错误",
            "",
            "```json",
            json.dumps(summary.get("stage_error_counts", {}), ensure_ascii=False, indent=2),
            "```",
        ]
    )
    groups = summary.get("groups") or {}
    if groups:
        lines.extend(["", "## 分组结果", ""])
        for key, group_summary in groups.items():
            lines.extend(
                [
                    f"### {key}",
                    "",
                    "| 指标 | 数值 |",
                    "| --- | ---: |",
                    f"| 样本数 | {_fmt(group_summary.get('case_count'))} |",
                    f"| 完成数 | {_fmt(group_summary.get('completed_count'))} |",
                    f"| 桥梁大类准确率 | {_fmt(group_summary.get('bridge_family_accuracy'))} |",
                    f"| 关键桥梁泄露率 | {_fmt(group_summary.get('critical_bridge_leakage_rate'))} |",
                    f"| 平均 LLM 调用次数 | {_fmt(group_summary.get('average_llm_call_count'))} |",
                    f"| 总延迟 P50 ms | {_fmt((group_summary.get('latency_ms') or {}).get('total_p50'))} |",
                    "",
                ]
            )
    error_cases = summary.get("error_cases") or []
    if error_cases:
        lines.extend(["", "## 错误样本", ""])
        lines.extend(f"- {case_id}" for case_id in error_cases)
    return "\n".join(lines) + "\n"


def _default_zh_md_path(md_path: Path) -> Path:
    return md_path.with_name(f"{md_path.stem}.zh{md_path.suffix}")


def write_summary_files(json_path: Path, md_path: Path, summary: dict, md_zh_path: Path | None = None) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown_report(summary), encoding="utf-8")
    if md_zh_path is not None:
        md_zh_path.parent.mkdir(parents=True, exist_ok=True)
        md_zh_path.write_text(render_markdown_report_zh(summary), encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize offline Bridge Judge evaluation JSONL results.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_PATH, help="Bridge offline eval result JSONL.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_SUMMARY_JSON_PATH, help="Summary JSON output path.")
    parser.add_argument("--output-md", type=Path, default=DEFAULT_SUMMARY_MD_PATH, help="Markdown report output path.")
    parser.add_argument(
        "--output-md-zh",
        type=Path,
        help="Chinese Markdown report output path. Defaults to <output-md stem>.zh.md.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    summary = summarize_bridge_offline_results(load_result_rows(args.input_jsonl))
    md_zh_path = args.output_md_zh or _default_zh_md_path(args.output_md)
    write_summary_files(args.output_json, args.output_md, summary, md_zh_path)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
