import argparse
import json
import os
import sys
from pathlib import Path

from evals.aichat import run_chat_batch, run_socratic_eval, run_socratic_judge_eval


DEFAULT_CASES_PATH = Path("docs/common/aichat_socratic_eval_cases_2026_04.json")
DEFAULT_OUTPUT_DIR = Path("evals/aichat/reports/latest")


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _failed_rows(summary: dict, limit: int = 8) -> list[dict]:
    return [result for result in summary.get("results", []) if not result.get("passed")][:limit]


def _judge_coverage_line(judge_summary: dict) -> str | None:
    coverage = judge_summary.get("coverage")
    if not coverage:
        return None
    case_count = judge_summary.get("case_count", 0)
    total_case_count = judge_summary.get("total_case_count")
    if total_case_count:
        return f"- Judge coverage: {coverage} ({case_count}/{total_case_count} cases)"
    return f"- Judge coverage: {coverage}"


def build_markdown_report(hard_summary: dict, judge_summary: dict | None = None, responses_path: Path | None = None) -> str:
    lines = [
        "# AIChat Socratic Eval Report",
        "",
    ]
    if responses_path:
        lines.extend(["## Inputs", "", f"- responses: `{responses_path}`", ""])

    lines.extend(
        [
            "## Hard Gate",
            "",
            f"- Cases: {hard_summary.get('case_count', 0)}",
            f"- Passed: {hard_summary.get('passed_case_count', 0)}",
            f"- Failed: {hard_summary.get('failed_case_count', 0)}",
            f"- Hard gate pass rate: {_pct(hard_summary.get('pass_rate', 0.0))}",
            "",
        ]
    )
    hard_failures = _failed_rows(hard_summary)
    if hard_failures:
        lines.extend(["### Hard Gate Failures", ""])
        for result in hard_failures:
            failures = ", ".join(result.get("failures", [])) or "unknown"
            lines.append(f"- `{result.get('case_id')}`: {failures}")
        lines.append("")

    if judge_summary is None:
        lines.extend(["## Judge Gate", "", "- Not run.", ""])
    else:
        coverage_line = _judge_coverage_line(judge_summary)
        judge_lines = [
            "## Judge Gate",
            "",
            f"- Cases: {judge_summary.get('case_count', 0)}",
        ]
        if coverage_line:
            judge_lines.append(coverage_line)
        judge_lines.extend(
            [
                f"- Passed: {judge_summary.get('passed_case_count', 0)}",
                f"- Failed: {judge_summary.get('failed_case_count', 0)}",
                f"- Judge pass rate: {_pct(judge_summary.get('pass_rate', 0.0))}",
                f"- Average judge score: {judge_summary.get('average_score', 0.0)} / 3",
                "",
            ]
        )
        lines.extend(judge_lines)
        judge_failures = _failed_rows(judge_summary)
        if judge_failures:
            lines.extend(["### Judge Failures", ""])
            for result in judge_failures:
                reasons = ", ".join(result.get("reasons", [])) or "unknown"
                lines.append(f"- `{result.get('case_id')}`: score={result.get('score', 0)}; {reasons}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _limit_cases_data(cases_data: dict, limit: int | None) -> dict:
    if limit is None:
        return cases_data
    limited = dict(cases_data)
    limited["cases"] = list(cases_data.get("cases", []))[:limit]
    return limited


def _validate_judge_coverage(with_judge: bool, raw_case_count: int, eval_case_count: int, allow_judge_smoke: bool) -> None:
    if with_judge and eval_case_count < raw_case_count and not allow_judge_smoke:
        raise ValueError(
            f"limited judge smoke is disabled by default: judging {eval_case_count}/{raw_case_count} cases. "
            "Run without --limit for full judge coverage, or pass --allow-judge-smoke for an explicit smoke check."
        )


def run_suite(
    cases_path: Path = DEFAULT_CASES_PATH,
    responses_path: Path | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    with_judge: bool = False,
    chat_fn=run_chat_batch.noi_agent_chat,
    judge_fn=run_socratic_judge_eval.run_review_case_kimi_cli._run_kimi_cli,
    student_id: str = "aichat_eval_student",
    limit: int | None = None,
    allow_judge_smoke: bool = False,
    progress_stream=None,
    judge_timeout_seconds: int | None = None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_cases_data = run_chat_batch.load_cases(cases_path)
    cases_data = _limit_cases_data(raw_cases_data, limit)
    _validate_judge_coverage(
        with_judge,
        raw_case_count=len(raw_cases_data.get("cases", [])),
        eval_case_count=len(cases_data.get("cases", [])),
        allow_judge_smoke=allow_judge_smoke,
    )
    eval_cases_path = cases_path
    if limit is not None:
        eval_cases_path = output_dir / "cases.limited.json"
        _write_json(eval_cases_path, cases_data)

    if responses_path is None:
        responses_path = output_dir / "responses.jsonl"
        rows = run_chat_batch.generate_response_rows(
            cases_data,
            chat_fn=chat_fn,
            student_id=student_id,
            limit=limit,
            progress_stream=progress_stream,
        )
        run_chat_batch.write_response_rows(responses_path, rows)

    hard_summary = run_socratic_eval.evaluate_response_file(eval_cases_path, responses_path)
    _write_json(output_dir / "hard_summary.json", hard_summary)

    judge_summary = None
    if with_judge:
        previous_timeout = os.environ.get("REVIEW_EVAL_KIMI_TIMEOUT_SECONDS")
        if judge_timeout_seconds is not None:
            os.environ["REVIEW_EVAL_KIMI_TIMEOUT_SECONDS"] = str(judge_timeout_seconds)
        try:
            judge_summary = run_socratic_judge_eval.evaluate_judge_file(
                eval_cases_path,
                responses_path,
                judge_fn=judge_fn,
                progress_stream=progress_stream,
            )
        finally:
            if judge_timeout_seconds is not None:
                if previous_timeout is None:
                    os.environ.pop("REVIEW_EVAL_KIMI_TIMEOUT_SECONDS", None)
                else:
                    os.environ["REVIEW_EVAL_KIMI_TIMEOUT_SECONDS"] = previous_timeout
        judge_summary["coverage"] = (
            "smoke" if len(cases_data.get("cases", [])) < len(raw_cases_data.get("cases", [])) else "full"
        )
        judge_summary["total_case_count"] = len(raw_cases_data.get("cases", []))
        _write_json(output_dir / "judge_summary.json", judge_summary)

    summary = {
        "cases_path": str(eval_cases_path),
        "responses_path": str(responses_path),
        "output_dir": str(output_dir),
        "with_judge": with_judge,
        "judge_coverage": (
            "not_run"
            if not with_judge
            else "smoke"
            if len(cases_data.get("cases", [])) < len(raw_cases_data.get("cases", []))
            else "full"
        ),
        "hard_summary": hard_summary,
        "judge_summary": judge_summary,
    }
    _write_json(output_dir / "suite_summary.json", summary)
    (output_dir / "report.md").write_text(
        build_markdown_report(hard_summary, judge_summary=judge_summary, responses_path=responses_path),
        encoding="utf-8",
    )
    return summary


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full AIChat Socratic eval suite.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH, help="AIChat Socratic case JSON file.")
    parser.add_argument("--responses-jsonl", type=Path, help="Existing response JSONL. If omitted, responses are generated.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for summary JSON and Markdown report.")
    parser.add_argument("--with-judge", action="store_true", help="Run LLM-as-judge after hard gate.")
    parser.add_argument("--student-id", default="aichat_eval_student", help="Student id used when generating responses.")
    parser.add_argument("--limit", type=int, help="Optional case limit when generating responses.")
    parser.add_argument(
        "--allow-judge-smoke",
        action="store_true",
        help="Allow --with-judge to run on a limited case set. Without this flag, judge runs must cover all cases.",
    )
    parser.add_argument(
        "--judge-timeout-seconds",
        type=int,
        help="Override REVIEW_EVAL_KIMI_TIMEOUT_SECONDS while running the judge.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        summary = run_suite(
            cases_path=args.cases,
            responses_path=args.responses_jsonl,
            output_dir=args.output_dir,
            with_judge=args.with_judge,
            student_id=args.student_id,
            limit=args.limit,
            allow_judge_smoke=args.allow_judge_smoke,
            progress_stream=sys.stderr,
            judge_timeout_seconds=args.judge_timeout_seconds,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output_dir": summary["output_dir"], "report": str(Path(summary["output_dir"]) / "report.md")}, ensure_ascii=False))
    hard_failed = summary["hard_summary"]["failed_case_count"] > 0
    judge_failed = bool(summary["judge_summary"] and summary["judge_summary"]["failed_case_count"] > 0)
    return 1 if hard_failed or judge_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
