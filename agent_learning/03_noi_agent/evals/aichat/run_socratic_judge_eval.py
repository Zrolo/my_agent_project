import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from evals.aichat import run_socratic_eval
from evals.review import run_review_case_kimi_cli


DEFAULT_CASES_PATH = Path("docs/common/aichat_socratic_eval_cases_2026_04.json")
JudgeFn = Callable[[str], str]


def load_cases(cases_path: Path = DEFAULT_CASES_PATH) -> dict:
    return json.loads(cases_path.read_text(encoding="utf-8"))


def build_judge_prompt(case: dict, response_text: str, rubric: dict) -> str:
    llm_criteria = rubric.get("automation_mapping", {}).get("llm_judge", [])
    criteria_lines = "\n".join(f"{idx}. {criterion}" for idx, criterion in enumerate(llm_criteria, 1))
    expected_lines = "\n".join(f"- {item}" for item in case.get("expected_reply_behavior", []))
    forbidden_lines = "\n".join(f"- {item}" for item in case.get("forbidden_reply_behavior", []))
    prior_messages = json.dumps(case.get("prior_messages", []), ensure_ascii=False)

    return "\n".join(
        [
            "你是 AIChat 教学质量评委。请判断信息学竞赛 AI 教练的单轮回复是否符合苏格拉底式引导、ZPD、Adaptive Scaffolding 与 Evidence-Driven Feedback。",
            "只输出 JSON，不要输出 Markdown。",
            "",
            "输出格式：",
            '{"pass": true|false, "score": 0-3, "reasons": ["...", "..."], "failed_criteria": ["...", "..."]}',
            "",
            "评分含义：",
            "3 = 贴题、只推进半步、没有泄露关键桥；2 = 基本合格但略泛；1 = 没泄题但教学引导弱；0 = 直接泄题或明显偏离。",
            "不能只因为回复安全就给高分；安全只是底线，贴合该 case 的具体证据才是高分条件。",
            "如果回复用 A/B、二选一或“是不是 X，还是 Y”的形式夹入完整关键桥，即使是问句，也应判为泄露关键桥。",
            "如果学生贴代码但没有失败样例、错误现象、怀疑行或手动 trace，回复不得追踪代码执行或暗示 bug 位置；必须先要求代码证据。",
            "如果 expected_reply_behavior 要求追问具体题面证据，而回复只是“你为什么这么猜”“先说说想法”等泛问题，最高只能给 2 分，通常应判 pass=false。",
            "如果回复没有点到该题的核心对象、条件、错误现象或 expected_reply_behavior 中的具体桥，不能给 3 分。",
            "",
            "通用评审标准：",
            criteria_lines or "- 是否只提出一个核心问题\n- 是否围绕题面证据而不是泛算法建议\n- 是否保持半步支架而没有泄露完整桥",
            "",
            f"case_id: {case.get('id', '')}",
            f"problem_ref: {case.get('problem_ref', '')}",
            f"student_message: {case.get('student_message', '')}",
            f"problem_context: {case.get('problem_context', '')}",
            f"prior_messages: {prior_messages}",
            "",
            "该 case 的期望行为：",
            expected_lines or "- 无",
            "",
            "该 case 的禁止行为：",
            forbidden_lines or "- 无",
            "",
            "AIChat 实际回复：",
            response_text,
        ]
    )


def extract_judge_result(output: str) -> dict:
    cleaned = run_review_case_kimi_cli._strip_json_fence(output or "")
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "pass": False,
            "score": 0,
            "reasons": [f"invalid_json: {exc}"],
            "failed_criteria": ["invalid_json"],
            "raw_output": cleaned[:1000],
        }

    score = parsed.get("score")
    passed = parsed.get("pass")
    if not isinstance(passed, bool) or not isinstance(score, int) or score < 0 or score > 3:
        return {
            "ok": False,
            "pass": False,
            "score": 0,
            "reasons": ["invalid_schema"],
            "failed_criteria": ["invalid_schema"],
            "raw_output": cleaned[:1000],
        }

    reasons = parsed.get("reasons") or []
    failed_criteria = parsed.get("failed_criteria") or []
    if not isinstance(reasons, list):
        reasons = [str(reasons)]
    if not isinstance(failed_criteria, list):
        failed_criteria = [str(failed_criteria)]
    return {
        "ok": True,
        "pass": passed,
        "score": score,
        "reasons": [str(reason) for reason in reasons],
        "failed_criteria": [str(criterion) for criterion in failed_criteria],
    }


def judge_response(case: dict, response_text: str, rubric: dict, judge_fn: JudgeFn = run_review_case_kimi_cli._run_kimi_cli) -> dict:
    prompt = build_judge_prompt(case, response_text, rubric)
    try:
        return extract_judge_result(judge_fn(prompt))
    except Exception as exc:
        return {
            "ok": False,
            "pass": False,
            "score": 0,
            "reasons": [f"judge_failed: {exc}"],
            "failed_criteria": ["judge_failed"],
        }


def evaluate_judge(cases_data: dict, responses: dict[str, str], judge_fn: JudgeFn = run_review_case_kimi_cli._run_kimi_cli) -> dict:
    rubric = cases_data.get("rubric", {})
    results = []
    for case in cases_data.get("cases", []):
        case_id = case["id"]
        response_text = responses.get(case_id)
        if response_text is None:
            results.append(
                {
                    "case_id": case_id,
                    "passed": False,
                    "score": 0,
                    "ok": False,
                    "reasons": ["missing_response"],
                    "failed_criteria": ["missing_response"],
                }
            )
            continue
        judged = judge_response(case, response_text, rubric, judge_fn=judge_fn)
        passed = bool(judged["ok"] and judged["pass"] and judged["score"] >= 3)
        results.append(
            {
                "case_id": case_id,
                "passed": passed,
                "score": judged["score"],
                "ok": judged["ok"],
                "reasons": judged["reasons"],
                "failed_criteria": judged["failed_criteria"],
            }
        )

    case_count = len(results)
    passed_case_count = sum(1 for result in results if result["passed"])
    failed_case_count = case_count - passed_case_count
    average_score = round(sum(result["score"] for result in results) / case_count, 3) if case_count else 0.0
    return {
        "case_count": case_count,
        "passed_case_count": passed_case_count,
        "failed_case_count": failed_case_count,
        "pass_rate": round(passed_case_count / case_count, 3) if case_count else 0.0,
        "average_score": average_score,
        "results": results,
    }


def evaluate_judge_file(cases_path: Path, responses_path: Path, judge_fn: JudgeFn = run_review_case_kimi_cli._run_kimi_cli) -> dict:
    return evaluate_judge(load_cases(cases_path), run_socratic_eval.load_responses(responses_path), judge_fn=judge_fn)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM-as-judge AIChat Socratic eval.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH, help="AIChat Socratic case JSON file.")
    parser.add_argument("--responses-jsonl", type=Path, required=True, help="JSONL with case_id and response_text fields.")
    parser.add_argument("--output-json", type=Path, help="Optional path to write judge summary JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    summary = evaluate_judge_file(args.cases, args.responses_jsonl)
    output = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output_json:
        args.output_json.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if summary["failed_case_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
