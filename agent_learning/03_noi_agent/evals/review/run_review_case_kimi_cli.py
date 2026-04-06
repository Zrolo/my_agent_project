import json
import os
import subprocess
import sys

sys.path.insert(0, "/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent")

import review_engine


RESULT_MAP = {
    "not_submitted": "尚未提交",
    "wa": "WA（答案错误）",
    "tle": "TLE（超时）",
    "re": "RE（运行错误）",
    "ce": "CE（编译错误）",
    "unknown": "不确定",
}

STATUS_MAP = {
    "independent": "独立完成",
    "hinted": "需要提示",
    "editorial": "看题解",
    "unfinished": "未完成",
}


def _strip_json_fence(text: str) -> str:
    stripped = (text or "").strip()
    if stripped.startswith("```json"):
        stripped = stripped[len("```json") :].strip()
    elif stripped.startswith("```"):
        stripped = stripped[len("```") :].strip()
    if stripped.endswith("```"):
        stripped = stripped[:-3].strip()
    return stripped


def _read_cli_stdin(stdin) -> str:
    try:
        if stdin is not None and stdin.isatty():
            return ""
    except Exception:
        pass
    return stdin.read() if stdin is not None else ""


def _load_case_from_cli(argv: list[str], stdin_text: str) -> dict:
    raw = (stdin_text or "").strip()
    if raw:
        return json.loads(raw)

    for arg in argv[1:]:
        try:
            parsed = json.loads(arg)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and "input" in parsed and "id" in parsed:
            return parsed

    raise ValueError("no case payload found in stdin or argv")


def build_prompt_from_case(case: dict, forced_mode: str | None = None) -> str:
    inp = case["input"]
    submission_result = (inp.get("submission_result") or "unknown").strip().lower()
    mode = forced_mode or review_engine._detect_review_mode(inp["completion_status"], submission_result)
    system_prompt = review_engine._build_review_system_prompt(mode=mode)
    user_prompt = review_engine._build_review_user_prompt(
        problem_title=inp["problem_title"],
        oj_source=inp.get("oj_source", ""),
        status_text=STATUS_MAP.get(inp["completion_status"], inp["completion_status"]),
        bottleneck_text=inp["bottleneck_text"],
        error_types=inp.get("error_types", []),
        reflection=inp.get("reflection"),
        problem_context=inp.get("problem_context"),
        problem_tags=inp.get("problem_tags"),
        chat_context_summary=inp.get("chat_context_summary"),
        problem_card=inp.get("problem_card"),
        submission_text=RESULT_MAP.get(submission_result, ""),
        student_code=inp.get("student_code"),
    )
    return f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}\n"


def _build_kimi_cli_config() -> str:
    model = os.getenv("REVIEW_EVAL_KIMI_MODEL", "kimi-k2.5")
    model_id = f"moonshot/{model}"
    api_key = os.getenv("MOONSHOT_API_KEY", "")
    config = {
        "default_model": model_id,
        "models": {
            model_id: {
                "provider": "moonshot",
                "model": model,
                "max_context_size": 262144,
                "capabilities": ["thinking"],
            }
        },
        "providers": {
            "moonshot": {
                "type": "kimi",
                "base_url": "https://api.moonshot.cn/v1",
                "api_key": api_key,
            }
        },
    }
    return json.dumps(config, ensure_ascii=False)


def _run_kimi_cli(prompt: str) -> str:
    model = os.getenv("REVIEW_EVAL_KIMI_MODEL", "kimi-k2.5")
    model_id = f"moonshot/{model}"
    cmd = [
        "kimi",
        "--config",
        _build_kimi_cli_config(),
        "--print",
        "--output-format",
        "text",
        "--final-message-only",
        "--model",
        model_id,
        "-p",
        prompt,
    ]
    env = os.environ.copy()
    review_budget = env.get("NOI_REVIEW_MAX_TOKENS", "").strip()
    if review_budget and not env.get("KIMI_MODEL_MAX_TOKENS"):
        env["KIMI_MODEL_MAX_TOKENS"] = review_budget
    timeout_seconds = int(env.get("REVIEW_EVAL_KIMI_TIMEOUT_SECONDS", "240"))
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, env=env, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"kimi_cli_timeout: {timeout_seconds}s") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "kimi cli failed").strip().splitlines()[0][:300]
        raise RuntimeError(f"kimi_cli_failed: {detail}")
    return (proc.stdout or "").strip()


def run(case: dict, forced_mode: str | None = None) -> dict:
    prompt = build_prompt_from_case(case, forced_mode=forced_mode)
    output = _strip_json_fence(_run_kimi_cli(prompt))
    if not output:
        return {"error": "kimi-cli returned empty output"}
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        return {
            "error": f"invalid_json: {exc}",
            "raw_output": output[:2000],
        }


if __name__ == "__main__":
    case = _load_case_from_cli(sys.argv, _read_cli_stdin(sys.stdin))
    forced_mode = os.getenv("REVIEW_EVAL_FORCE_MODE", "").strip() or None
    print(json.dumps(run(case, forced_mode=forced_mode), ensure_ascii=False))
