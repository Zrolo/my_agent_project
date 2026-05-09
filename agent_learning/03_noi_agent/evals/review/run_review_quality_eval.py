import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from evals.review import run_review_case_kimi_cli
import review_engine

RUBRIC_FILE = REPO_ROOT / "evals/review/review_rubric_v2.json"

PROVIDERS = [
    ("baseline_current_kimi_cli", {"REVIEW_EVAL_FORCE_MODE": "independent_reflect"}),
    ("mode_route_kimi_cli", {}),
]


def _write_attempt_log(stream, event: str, **fields) -> None:
    if stream is None:
        return
    parts = [event] + [f"{key}={value}" for key, value in fields.items()]
    stream.write(" ".join(parts) + "\n")
    flush = getattr(stream, "flush", None)
    if callable(flush):
        flush()


def _load_rubric() -> dict:
    return json.loads(RUBRIC_FILE.read_text())


def _max_rubric_score(rubric: dict) -> int:
    return max(1, len(rubric.get("checks", [])))


def _build_rubric_prompt_text(rubric: dict) -> str:
    max_score = _max_rubric_score(rubric)
    lines = [
        "你是代码学习复盘的评审老师。请阅读题目信息和 AI 复盘结果，只输出 JSON，不要输出 Markdown。",
        "",
        "输出格式：",
        f'{{"score": 0-{max_score}, "reasons": ["...", "..."]}}',
        "",
        "评分规则：",
    ]
    for idx, check in enumerate(rubric.get("checks", []), 1):
        lines.append(f"{idx}. {check['field']} {check['rule']}")
    lines.extend(
        [
            "",
            f"每条满足记 1 分，总分 0-{max_score}。",
            "如果信息接近但仍偏空泛，不给分。",
        ]
    )
    return "\n".join(lines)


def _compact_review_for_eval(review: dict) -> dict:
    return {
        "problem_focus": review.get("problem_focus") or review.get("main_block", ""),
        "key_bridge": review.get("key_bridge", ""),
        "guided_walkthrough": review.get("guided_walkthrough", ""),
        "try_now": review.get("try_now") or review.get("next_step", ""),
        "transfer_signal": review.get("transfer_signal", ""),
    }


def _strip_json_fence(text: str) -> str:
    return run_review_case_kimi_cli._strip_json_fence(text)


def _extract_rubric_score(output: str, max_score: int = 4) -> dict:
    cleaned = _strip_json_fence(output or "")
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return {"ok": False, "score": 0, "reasons": [f"invalid_json: {exc}"], "raw_output": cleaned[:1000]}

    score = parsed.get("score")
    reasons = parsed.get("reasons") or []
    if not isinstance(score, int) or score < 0 or score > max_score:
        return {"ok": False, "score": 0, "reasons": ["invalid_score"], "raw_output": cleaned[:1000]}
    if not isinstance(reasons, list):
        reasons = [str(reasons)]
    return {"ok": True, "score": score, "reasons": [str(r) for r in reasons]}


def _build_rubric_prompt(case: dict, review: dict) -> str:
    rubric = _load_rubric()
    inp = case["input"]
    compact_review = _compact_review_for_eval(review)
    return (
        f"{_build_rubric_prompt_text(rubric)}\n\n"
        f"题目：{inp.get('problem_title', '')}\n"
        f"完成状态：{inp.get('completion_status', '')}\n"
        f"卡点：{inp.get('bottleneck_text', '')}\n"
        f"题目补充：{inp.get('problem_context', '')}\n\n"
        f"AI复盘：{json.dumps(compact_review, ensure_ascii=False)}"
    )


def _run_review(case: dict, extra_env: dict) -> tuple[bool, dict, float]:
    runner = REPO_ROOT / "evals/review/run_review_case_kimi_cli.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    # Quality eval is a long-form reasoning workload; use the larger official
    # recommendation here to reduce budget-induced empty outputs.
    env.setdefault("NOI_REVIEW_MAX_TOKENS", "98304")
    env.update(extra_env)
    started = time.time()
    try:
        proc = subprocess.run(
            ["python3", str(runner), json.dumps(case, ensure_ascii=False)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO_ROOT),
            timeout=240,
        )
    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - started, 2)
        return False, {"error": "review_timeout"}, elapsed
    elapsed = round(time.time() - started, 2)
    if proc.returncode != 0:
        return False, {"error": proc.stderr.strip() or proc.stdout.strip() or "runner_failed"}, elapsed
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return False, {"error": f"invalid_json: {exc}", "raw_output": proc.stdout[:1000]}, elapsed
    return True, parsed, elapsed


def _run_mode_gate(case: dict, review: dict) -> dict:
    """按 mode 判断 review 是否满足模式特定要求。

    返回结构：
        {
            "pass": bool,
            "mode": str,
            "family": str,           # "failure_diagnosis" | "success_reflection" | "unknown"
            "kb_gap_exempt": bool,   # True 表示 kb_leaves_reasoning_gap 在此 mode 下豁免
            "reason": str,
        }
    不影响主 rubric 分数。

    Family 归属：
        failure_diagnosis  — failed_verdict / stuck_bridge / editorial_transfer
        success_reflection — independent_reflect
    kb_gap_exempt 仅对 failure_diagnosis family 下的 stuck_bridge / editorial_transfer 为 True；
    failed_verdict 下学生已走过题目，不豁免。
    """
    rubric = _load_rubric()
    gate_def = rubric.get("mode_gate", {})
    families = gate_def.get("families", [])
    if not families:
        return {"pass": True, "mode": "unknown", "family": "unknown", "kb_gap_exempt": False, "reason": "no_gate_defined"}

    inp = case.get("input", {})
    completion_status = (inp.get("completion_status") or "").strip().lower()
    submission_result = (inp.get("submission_result") or "").strip().lower()

    matched_mode = review_engine._detect_review_mode(completion_status, submission_result)

    # 在 families 中找到匹配的 family + gate_rule
    matched_family_name = "unknown"
    matched_family_def = None
    gate_rule = None
    for family_def in families:
        for gate in family_def.get("gates", []):
            if gate["mode"] == matched_mode:
                matched_family_name = family_def.get("family", "unknown")
                matched_family_def = family_def
                gate_rule = gate
                break
        if gate_rule is not None:
            break

    if gate_rule is None:
        return {"pass": True, "mode": matched_mode, "family": matched_family_name, "kb_gap_exempt": False, "reason": "no_gate_for_mode"}

    # kb_gap_exempt：family 有豁免说明 且 当前 mode 在豁免范围内
    exemption_text = matched_family_def.get("kb_gap_exemption") if matched_family_def else None
    kb_gap_exempt = bool(exemption_text) and matched_mode in {"stuck_bridge", "editorial_transfer"}

    compact_review = _compact_review_for_eval(review)
    prompt = (
        "你是代码学习复盘的评审老师。请判断下面这份复盘是否满足当前模式的要求。"
        "只输出 JSON，不要输出 Markdown。\n\n"
        f"当前模式：{matched_mode}（所属 family：{matched_family_name}）\n"
        f"模式要求：{gate_rule['rule']}\n"
    )
    if matched_mode == "independent_reflect":
        prompt += (
            "注意：transfer_signal 里使用题目中出现的具体名词（如物品名、数量关系）是允许的，"
            "只要不直接引用题目名称本身；禁止的是把具体条件替换成类型模板"
            "（如“多个节点做决策”“需要同时满足约束”）。\n"
        )
    if kb_gap_exempt and exemption_text:
        prompt += f"注意：{exemption_text}\n"
    prompt += (
        f"\n题目：{inp.get('problem_title', '')}\n"
        f"完成状态：{completion_status}\n"
        f"提交结果：{submission_result}\n"
        f"卡点：{inp.get('bottleneck_text', '')}\n\n"
        f"AI复盘：{json.dumps(compact_review, ensure_ascii=False)}\n\n"
        '输出格式：{"pass": true|false, "reason": "一句话说明"}'
    )
    try:
        output = run_review_case_kimi_cli._run_kimi_cli(prompt)
    except Exception as exc:
        return {"pass": False, "mode": matched_mode, "family": matched_family_name, "kb_gap_exempt": kb_gap_exempt, "reason": f"gate_judge_failed: {exc}"}

    cleaned = _strip_json_fence(output or "")
    try:
        parsed = json.loads(cleaned)
        return {
            "pass": bool(parsed.get("pass", False)),
            "mode": matched_mode,
            "family": matched_family_name,
            "kb_gap_exempt": kb_gap_exempt,
            "reason": str(parsed.get("reason", "")),
        }
    except json.JSONDecodeError:
        return {"pass": False, "mode": matched_mode, "family": matched_family_name, "kb_gap_exempt": kb_gap_exempt, "reason": f"invalid_json: {cleaned[:200]}"}


def _judge_review(case: dict, review: dict) -> dict:
    rubric = _load_rubric()
    prompt = _build_rubric_prompt(case, review)
    try:
        output = run_review_case_kimi_cli._run_kimi_cli(prompt)
    except Exception as exc:
        return {"ok": False, "score": 0, "reasons": [f"judge_failed: {exc}"]}
    return _extract_rubric_score(output, max_score=_max_rubric_score(rubric))


def evaluate_tests(test_file: Path, repeats: int = 1, attempt_log=None) -> dict:
    rows = [json.loads(line) for line in test_file.read_text().splitlines() if line.strip()]
    rubric = _load_rubric()
    rubric_max_score = _max_rubric_score(rubric)
    results = []
    for label, extra_env in PROVIDERS:
        for row in rows:
            case = json.loads(row["vars"]["case"])
            attempts = []
            for attempt_idx in range(repeats):
                _write_attempt_log(
                    attempt_log,
                    "ATTEMPT_START",
                    provider=label,
                    case=case["id"],
                    attempt=attempt_idx + 1,
                    mode=case["mode"],
                )
                ok, parsed, elapsed = _run_review(case, extra_env)
                fields_ok = bool(
                    ok
                    and isinstance(parsed, dict)
                    and all(parsed.get(k) for k in ("problem_focus", "key_bridge", "guided_walkthrough", "try_now", "transfer_signal"))
                )
                _write_attempt_log(
                    attempt_log,
                    "ATTEMPT_REVIEW_DONE",
                    provider=label,
                    case=case["id"],
                    attempt=attempt_idx + 1,
                    ok=bool(ok),
                    fields_ok=fields_ok,
                    elapsed=elapsed,
                    error=parsed.get("error", "") if isinstance(parsed, dict) else "",
                )
                rubric = {"ok": False, "score": 0, "reasons": ["skipped"]}
                gate = {"pass": False, "mode": "skipped", "family": "skipped", "kb_gap_exempt": False, "reason": "skipped"}
                if fields_ok:
                    rubric = _judge_review(case, parsed)
                    _write_attempt_log(
                        attempt_log,
                        "ATTEMPT_JUDGE_DONE",
                        provider=label,
                        case=case["id"],
                        attempt=attempt_idx + 1,
                        rubric_ok=bool(rubric.get("ok")),
                        rubric_score=int(rubric.get("score", 0)),
                    )
                    gate = _run_mode_gate(case, parsed)
                    _write_attempt_log(
                        attempt_log,
                        "ATTEMPT_GATE_DONE",
                        provider=label,
                        case=case["id"],
                        attempt=attempt_idx + 1,
                        gate_pass=bool(gate.get("pass", False)),
                        gate_mode=gate.get("mode", ""),
                    )
                attempts.append(
                    {
                        "attempt": attempt_idx + 1,
                        "json_ok": bool(ok),
                        "fields_ok": fields_ok,
                        "elapsed_seconds": elapsed,
                        "rubric_ok": bool(rubric.get("ok")),
                        "rubric_score": int(rubric.get("score", 0)),
                        "rubric_reasons": rubric.get("reasons", []),
                        "gate_pass": bool(gate.get("pass", False)),
                        "gate_mode": gate.get("mode", ""),
                        "gate_family": gate.get("family", ""),
                        "gate_kb_gap_exempt": bool(gate.get("kb_gap_exempt", False)),
                        "gate_reason": gate.get("reason", ""),
                    }
                )
            quality_attempts = [a for a in attempts if a["fields_ok"]]
            rubric_scores = [a["rubric_score"] for a in quality_attempts]
            gate_pass_values = [1.0 if a["gate_pass"] else 0.0 for a in quality_attempts]
            results.append(
                {
                    "provider": label,
                    "id": case["id"],
                    "mode": case["mode"],
                    "json_ok": round(sum(a["json_ok"] for a in attempts) / len(attempts), 3),
                    "fields_ok": round(sum(a["fields_ok"] for a in attempts) / len(attempts), 3),
                    "elapsed_seconds": round(sum(a["elapsed_seconds"] for a in attempts) / len(attempts), 2),
                    "rubric_ok": round(sum(a["rubric_ok"] for a in attempts) / len(attempts), 3),
                    "rubric_score": round(sum(rubric_scores) / len(rubric_scores), 3) if rubric_scores else None,
                    "rubric_max_score": rubric_max_score,
                    "rubric_score_ratio": round((sum(rubric_scores) / len(rubric_scores)) / rubric_max_score, 3)
                    if rubric_scores
                    else None,
                    "gate_pass_rate": round(sum(gate_pass_values) / len(gate_pass_values), 3) if gate_pass_values else None,
                    "quality_attempt_count": len(quality_attempts),
                    "quality_attempt_rate": round(len(quality_attempts) / len(attempts), 3),
                    "attempts": attempts,
                }
            )

    summary = {}
    for label, _ in PROVIDERS:
        subset = [r for r in results if r["provider"] == label]
        quality_subset = [r for r in subset if r["quality_attempt_count"] > 0]
        by_mode = {}
        for mode_name in sorted({r["mode"] for r in subset}):
            mode_subset = [r for r in subset if r["mode"] == mode_name]
            mode_quality_subset = [r for r in mode_subset if r["quality_attempt_count"] > 0]
            by_mode[mode_name] = {
                "case_count": len(mode_subset),
                "quality_case_count": len(mode_quality_subset),
                "json_ok_rate": round(sum(r["json_ok"] for r in mode_subset) / len(mode_subset), 3),
                "fields_ok_rate": round(sum(r["fields_ok"] for r in mode_subset) / len(mode_subset), 3),
                "rubric_avg_score": round(sum(r["rubric_score"] for r in mode_quality_subset) / len(mode_quality_subset), 3)
                if mode_quality_subset
                else None,
                "rubric_avg_ratio": round(
                    (sum(r["rubric_score"] for r in mode_quality_subset) / len(mode_quality_subset)) / rubric_max_score,
                    3,
                )
                if mode_quality_subset
                else None,
                "gate_pass_rate": round(sum(r["gate_pass_rate"] for r in mode_quality_subset) / len(mode_quality_subset), 3)
                if mode_quality_subset
                else None,
            }
        summary[label] = {
            "json_ok_rate": round(sum(r["json_ok"] for r in subset) / len(subset), 3),
            "fields_ok_rate": round(sum(r["fields_ok"] for r in subset) / len(subset), 3),
            "avg_elapsed_seconds": round(sum(r["elapsed_seconds"] for r in subset) / len(subset), 2),
            "rubric_avg_score": round(sum(r["rubric_score"] for r in quality_subset) / len(quality_subset), 3)
            if quality_subset
            else None,
            "rubric_max_score": rubric_max_score,
            "rubric_avg_ratio": round((sum(r["rubric_score"] for r in quality_subset) / len(quality_subset)) / rubric_max_score, 3)
            if quality_subset
            else None,
            "gate_pass_rate": round(sum(r["gate_pass_rate"] for r in quality_subset) / len(quality_subset), 3)
            if quality_subset
            else None,
            "quality_case_count": len(quality_subset),
            "quality_case_rate": round(len(quality_subset) / len(subset), 3),
            "repeats": repeats,
            "by_mode": by_mode,
            "cases": subset,
        }
    return summary


def main(argv=None) -> str:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) > 0:
        test_file = Path(argv[0])
    else:
        test_file = Path("/tmp/promptfoo_tests.sample.no_editorial.no_rubric.jsonl")
    repeats = int(argv[1]) if len(argv) > 1 else 1
    output_path = Path(argv[2]) if len(argv) > 2 else None
    attempt_log_path = Path(argv[3]) if len(argv) > 3 else None

    if attempt_log_path is not None:
        with attempt_log_path.open("w", encoding="utf-8") as attempt_log:
            output = json.dumps(evaluate_tests(test_file, repeats=repeats, attempt_log=attempt_log), ensure_ascii=False, indent=2)
    else:
        output = json.dumps(evaluate_tests(test_file, repeats=repeats), ensure_ascii=False, indent=2)

    if output_path is not None:
        output_path.write_text(output + "\n")
    return output


if __name__ == "__main__":
    print(main())
