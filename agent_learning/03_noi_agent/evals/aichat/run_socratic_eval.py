import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_CASES_PATH = Path("docs/common/aichat_socratic_eval_cases_2026_04.json")
DEFAULT_MAX_REPLY_CHARS = 300
DEFAULT_MAX_QUESTION_MARKS = 2


def load_cases(cases_path: Path = DEFAULT_CASES_PATH) -> dict:
    return json.loads(cases_path.read_text(encoding="utf-8"))


def load_responses(responses_path: Path) -> dict[str, str]:
    responses: dict[str, str] = {}
    for line_no, line in enumerate(responses_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        case_id = row.get("case_id") or row.get("id")
        response_text = row.get("response_text") or row.get("response") or row.get("text")
        if not case_id:
            raise ValueError(f"responses_jsonl line {line_no} missing case_id")
        if response_text is None:
            raise ValueError(f"responses_jsonl line {line_no} missing response_text")
        responses[str(case_id)] = str(response_text)
    return responses


def _regex_hits(patterns: list[str], text: str) -> list[str]:
    hits = []
    for pattern in patterns:
        try:
            if re.search(pattern, text):
                hits.append(pattern)
        except re.error as exc:
            hits.append(f"{pattern} [invalid_regex:{exc}]")
    return hits


def _looks_like_exact_forbidden_snippet(value: str) -> bool:
    snippet_markers = [
        "#include",
        "int main",
        "dp[",
        "union(",
        "while(",
        "s +=",
        "t +=",
        "lca -=",
        "r =",
        "完整代码如下",
        "AC 代码",
    ]
    return any(marker in value for marker in snippet_markers)


def _has_dp_state_definition_variant(forbidden: str, response_text: str) -> bool:
    """Catch equivalent DP state leaks that differ only by 表示/= wording."""
    if "dp[x][y]" not in forbidden or "出发" not in forbidden or "最长" not in forbidden:
        return False
    pattern = (
        r"dp\s*\[\s*x\s*\]\s*\[\s*y\s*\]\s*"
        r"(?:=|表示|代表|定义为)\s*"
        r"[^。！？\n]{0,20}"
        r"(?:从\s*\(?\s*x\s*,\s*y\s*\)?\s*出发|出发)"
        r"[^。！？\n]{0,20}"
        r"(?:最长路|最长路径)"
    )
    return re.search(pattern, response_text, re.IGNORECASE) is not None


def _has_ab_bridge_leak(response_text: str) -> bool:
    normalized = re.sub(r"\s+", "", response_text)
    has_two_option_shape = (
        ("A:" in response_text and "B:" in response_text)
        or ("还是" in response_text and "？" in response_text)
        or ("还是" in response_text and "?" in response_text)
    )
    dp_state_leak = "dp[x][y]" in normalized and "出发" in normalized and "最长" in normalized
    check_mid_leak = (
        "mid" in response_text
        and "至少" in response_text
        and "移走" in response_text
        and ("最短" in response_text or "最小" in response_text)
    )
    return has_two_option_shape and (dp_state_leak or check_mid_leak)


def _traces_code_before_evidence(case: dict, response_text: str) -> bool:
    expected_control = case.get("expected_control", {})
    if expected_control.get("tutor_action") != "ask_code_evidence":
        return False
    trace_patterns = [
        r"l.*r.*指向",
        r"停在哪里",
        r"如果.*没有",
        r"一定是第一个",
        r"这个循环",
        r"mid",
    ]
    return any(re.search(pattern, response_text, re.IGNORECASE) for pattern in trace_patterns)


def _semantic_forbidden_failures(forbidden: str, response_text: str) -> list[str]:
    failures = []
    if _has_dp_state_definition_variant(forbidden, response_text):
        failures.append("forbidden_semantic:dp_state_definition")
    return failures


def _missing_required_tutor_action(case: dict, response_text: str) -> str | None:
    expected_control = case.get("expected_control", {})
    tutor_action = expected_control.get("tutor_action")
    if tutor_action == "offer_checkin_reflection":
        if not re.search(r"(打卡|复盘|归档)", response_text):
            return f"missing_tutor_action:{tutor_action}"
    if tutor_action == "offer_micro_example_or_checkin" and expected_control.get("scaffold_stage", 1) >= 4:
        if not re.search(r"(打卡|复盘|归档)", response_text):
            return f"missing_tutor_action:{tutor_action}"
    return None


def evaluate_response(case: dict, response_text: str, rubric: dict) -> dict:
    failures = []

    for pattern in _regex_hits(rubric.get("hard_fail_patterns", []), response_text):
        failures.append(f"hard_fail_pattern:{pattern}")

    for forbidden in case.get("forbidden_reply_behavior", []):
        if _looks_like_exact_forbidden_snippet(forbidden) and forbidden in response_text:
            failures.append(f"forbidden_snippet:{forbidden}")
        failures.extend(_semantic_forbidden_failures(forbidden, response_text))

    if _has_ab_bridge_leak(response_text):
        failures.append("forbidden_semantic:ab_bridge_leak")
    if _traces_code_before_evidence(case, response_text):
        failures.append("forbidden_semantic:code_trace_before_evidence")

    missing_tutor_action = _missing_required_tutor_action(case, response_text)
    if missing_tutor_action:
        failures.append(missing_tutor_action)

    question_count = response_text.count("？") + response_text.count("?")
    if question_count > DEFAULT_MAX_QUESTION_MARKS:
        failures.append(f"too_many_questions:{question_count}")

    if len(response_text) > DEFAULT_MAX_REPLY_CHARS:
        failures.append(f"reply_too_long:{len(response_text)}")

    return {
        "case_id": case["id"],
        "passed": not failures,
        "failures": failures,
        "response_chars": len(response_text),
        "question_count": question_count,
    }


def evaluate_responses(cases_data: dict, responses: dict[str, str]) -> dict:
    rubric = cases_data.get("rubric", {})
    results = []
    for case in cases_data.get("cases", []):
        case_id = case["id"]
        if case_id not in responses:
            results.append(
                {
                    "case_id": case_id,
                    "passed": False,
                    "failures": ["missing_response"],
                    "response_chars": 0,
                    "question_count": 0,
                }
            )
            continue
        results.append(evaluate_response(case, responses[case_id], rubric))

    failed_case_count = sum(1 for result in results if not result["passed"])
    case_count = len(results)
    passed_case_count = case_count - failed_case_count
    return {
        "case_count": case_count,
        "passed_case_count": passed_case_count,
        "failed_case_count": failed_case_count,
        "pass_rate": round(passed_case_count / case_count, 3) if case_count else 0.0,
        "results": results,
    }


def evaluate_response_file(cases_path: Path, responses_path: Path) -> dict:
    return evaluate_responses(load_cases(cases_path), load_responses(responses_path))


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run hard-only AIChat Socratic eval assertions.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH, help="AIChat Socratic case JSON file.")
    parser.add_argument("--responses-jsonl", type=Path, required=True, help="JSONL with case_id and response_text fields.")
    parser.add_argument("--output-json", type=Path, help="Optional path to write the summary JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    summary = evaluate_response_file(args.cases, args.responses_jsonl)
    output = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output_json:
        args.output_json.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if summary["failed_case_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
