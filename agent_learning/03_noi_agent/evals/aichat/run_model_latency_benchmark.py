import argparse
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from openai import OpenAI

import api_server
import noi_agent
from auth import create_token
from evals.aichat.run_chat_batch import build_messages_from_case, load_cases
from evals.aichat.run_socratic_eval import evaluate_response


DEFAULT_CASES_PATH = Path("docs/common/aichat_socratic_eval_cases_2026_04.json")
DEFAULT_OUTPUT_ROOT = Path("evals/aichat/model_latency_runs")
DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_REPEAT = 3
DEFAULT_WARMUP = 1
DEFAULT_CASE_LIMIT = 12
DEFAULT_MAX_COMPLETION_TOKENS = 512


@dataclass(frozen=True)
class ProviderConfig:
    provider_id: str
    label: str
    base_url: str
    model: str
    api_key: str
    enabled: bool = True
    skip_reason: str = ""
    token_param: str = "max_completion_tokens"
    thinking_mode: str = "provider_default"
    extra_body: dict | None = None


class TimedOpenAIClient:
    def __init__(
        self,
        client: OpenAI,
        telemetry: dict,
        *,
        timeout_seconds: int,
        max_completion_tokens: int,
        token_param: str,
        extra_body: dict | None = None,
    ):
        self.chat = TimedChatResource(
            client.chat,
            telemetry,
            timeout_seconds=timeout_seconds,
            max_completion_tokens=max_completion_tokens,
            token_param=token_param,
            extra_body=extra_body,
        )


class TimedChatResource:
    def __init__(
        self,
        chat_resource,
        telemetry: dict,
        *,
        timeout_seconds: int,
        max_completion_tokens: int,
        token_param: str,
        extra_body: dict | None,
    ):
        self.completions = TimedCompletionsResource(
            chat_resource.completions,
            telemetry,
            timeout_seconds=timeout_seconds,
            max_completion_tokens=max_completion_tokens,
            token_param=token_param,
            extra_body=extra_body,
        )


class TimedCompletionsResource:
    def __init__(
        self,
        completions_resource,
        telemetry: dict,
        *,
        timeout_seconds: int,
        max_completion_tokens: int,
        token_param: str,
        extra_body: dict | None,
    ):
        self._completions_resource = completions_resource
        self._telemetry = telemetry
        self._timeout_seconds = timeout_seconds
        self._max_completion_tokens = max_completion_tokens
        self._token_param = token_param
        self._extra_body = extra_body

    def create(self, **kwargs):
        kwargs.setdefault("timeout", self._timeout_seconds)
        kwargs.setdefault(self._token_param, self._max_completion_tokens)
        if self._extra_body:
            kwargs["extra_body"] = {
                **self._extra_body,
                **(kwargs.get("extra_body") or {}),
            }
        started = time.perf_counter()
        try:
            return self._completions_resource.create(**kwargs)
        finally:
            self._telemetry["llm_ms"] = int((time.perf_counter() - started) * 1000)


def _env_value(env: dict[str, str], key: str) -> str:
    return (env.get(key) or "").strip()


def build_provider_configs(env: dict[str, str] | None = None) -> list[ProviderConfig]:
    env = dict(os.environ if env is None else env)
    kimi_key = _env_value(env, "MOONSHOT_API_KEY")
    mimo_key = _env_value(env, "MIMO_API_KEY") or _env_value(env, "XIAOMI_MIMO_API_KEY")
    deepseek_key = _env_value(env, "DEEPSEEK_API_KEY")
    mimo_model = _env_value(env, "MIMO_MODEL") or "mimo-v2.5-pro"
    deepseek_model = _env_value(env, "DEEPSEEK_MODEL") or "deepseek-v4-flash"

    return [
        ProviderConfig(
            provider_id="kimi",
            label="Kimi K2.6",
            base_url="https://api.moonshot.cn/v1",
            model="kimi-k2.6",
            api_key=kimi_key,
            enabled=bool(kimi_key),
            skip_reason="" if kimi_key else "missing MOONSHOT_API_KEY",
            thinking_mode="enabled",
        ),
        ProviderConfig(
            provider_id="mimo",
            label="Xiaomi MiMo",
            base_url="https://api.xiaomimimo.com/v1",
            model=mimo_model,
            api_key=mimo_key,
            enabled=bool(mimo_key),
            skip_reason="" if mimo_key else "missing MIMO_API_KEY",
            token_param="max_tokens",
            thinking_mode="enabled",
        ),
        ProviderConfig(
            provider_id="deepseek",
            label="DeepSeek",
            base_url="https://api.deepseek.com",
            model=deepseek_model,
            api_key=deepseek_key,
            enabled=bool(deepseek_key),
            skip_reason="" if deepseek_key else "missing DEEPSEEK_API_KEY",
            token_param="max_tokens",
            thinking_mode="enabled",
            extra_body={"thinking": {"type": "enabled"}},
        ),
    ]


def _percentile(values: list[int], percentile: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile))))
    return int(ordered[index])


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _summarize_measured_group(rows: list[dict]) -> dict:
    successful = [row for row in rows if row.get("ok")]
    request_values = [int(row.get("request_ms") or 0) for row in rows if row.get("request_ms") is not None]
    llm_values = [int(row.get("llm_ms") or 0) for row in rows if row.get("llm_ms") is not None]
    quality_rows = [row for row in rows if row.get("quality_gate_pass") is not None]
    return {
        "measured_count": len(rows),
        "success_count": len(successful),
        "error_count": len(rows) - len(successful),
        "success_rate": _rate(len(successful), len(rows)),
        "error_rate": _rate(len(rows) - len(successful), len(rows)),
        "quality_gate_pass_rate": _rate(
            sum(1 for row in quality_rows if row.get("quality_gate_pass")),
            len(quality_rows),
        ),
        "request_ms_avg": int(statistics.mean(request_values)) if request_values else 0,
        "request_ms_p50": _percentile(request_values, 0.5),
        "request_ms_p95": _percentile(request_values, 0.95),
        "llm_ms_avg": int(statistics.mean(llm_values)) if llm_values else 0,
        "llm_ms_p95": _percentile(llm_values, 0.95),
    }


def _summarize_by_field(rows: list[dict], field: str) -> dict:
    grouped: dict[str, dict] = {}
    measured = [row for row in rows if row.get("run_kind") == "measured"]
    for row in measured:
        provider_id = row.get("provider_id") or "unknown"
        value = row.get(field) or "未标注"
        grouped.setdefault(provider_id, {}).setdefault(value, []).append(row)
    return {
        provider_id: {
            value: _summarize_measured_group(group_rows)
            for value, group_rows in values.items()
        }
        for provider_id, values in grouped.items()
    }


def summarize_rows(rows: list[dict]) -> dict:
    provider_ids = sorted({row.get("provider_id", "") for row in rows if row.get("provider_id")})
    providers = {}
    for provider_id in provider_ids:
        provider_rows = [row for row in rows if row.get("provider_id") == provider_id]
        measured = [row for row in provider_rows if row.get("run_kind") == "measured"]
        providers[provider_id] = {
            "provider_id": provider_id,
            "provider_label": (provider_rows[0].get("provider_label") if provider_rows else provider_id),
            "model": (provider_rows[0].get("model") if provider_rows else ""),
            "thinking_mode": (provider_rows[0].get("thinking_mode") if provider_rows else ""),
            **_summarize_measured_group(measured),
        }

    ranked = sorted(
        [item for item in providers.values() if item["measured_count"] and item["success_count"]],
        key=lambda item: item["request_ms_avg"],
    )
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "provider_count": len(providers),
        "row_count": len(rows),
        "providers": providers,
        "by_input_mode": _summarize_by_field(rows, "input_mode"),
        "by_algorithm_tag": _summarize_by_field(rows, "algorithm_tag"),
        "fastest_provider_by_avg_request_ms": ranked[0]["provider_id"] if ranked else "",
    }


def _format_ms(value: int) -> str:
    return f"{value} ms" if value else "-"


def _render_group_table(title: str, grouped: dict, provider_labels: dict[str, str]) -> list[str]:
    lines = ["", f"## {title}", "", "| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    rows = []
    for provider_id, values in grouped.items():
        for group_name, metrics in values.items():
            rows.append((provider_id, group_name, metrics))
    rows.sort(key=lambda item: (provider_labels.get(item[0], item[0]), item[1]))
    if not rows:
        lines.append("| - | - | 0 | - | - | - | - |")
        return lines
    for provider_id, group_name, metrics in rows:
        lines.append(
            "| {provider} | {group} | {count} | {avg} | {p95} | {success:.0%} | {quality:.0%} |".format(
                provider=provider_labels.get(provider_id, provider_id),
                group=group_name,
                count=metrics.get("measured_count") or 0,
                avg=_format_ms(metrics.get("request_ms_avg") or 0),
                p95=_format_ms(metrics.get("request_ms_p95") or 0),
                success=metrics.get("success_rate") or 0,
                quality=metrics.get("quality_gate_pass_rate") or 0,
            )
        )
    return lines


def render_report(rows: list[dict], summary: dict) -> str:
    lines = [
        "# 三模型 AIChat 速度测试报告",
        "",
        f"生成时间：{summary.get('generated_at', '')}",
        "",
        "## 速度与质量概览",
        "",
        "| 模型 | 思考模式 | 请求均值 | 请求 p95 | LLM 均值 | 成功率 | 质量通过率 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for provider in summary.get("providers", {}).values():
        lines.append(
            "| {label} ({model}) | {thinking} | {avg} | {p95} | {llm_avg} | {success:.0%} | {quality:.0%} |".format(
                label=provider.get("provider_label") or provider.get("provider_id"),
                model=provider.get("model") or "-",
                thinking=provider.get("thinking_mode") or "-",
                avg=_format_ms(provider.get("request_ms_avg") or 0),
                p95=_format_ms(provider.get("request_ms_p95") or 0),
                llm_avg=_format_ms(provider.get("llm_ms_avg") or 0),
                success=provider.get("success_rate") or 0,
                quality=provider.get("quality_gate_pass_rate") or 0,
            )
        )

    provider_labels = {
        provider_id: provider.get("provider_label") or provider_id
        for provider_id, provider in summary.get("providers", {}).items()
    }
    lines.extend(_render_group_table("按输入形态", summary.get("by_input_mode", {}), provider_labels))
    lines.extend(_render_group_table("按算法标签", summary.get("by_algorithm_tag", {}), provider_labels))

    measured = [row for row in rows if row.get("run_kind") == "measured"]
    slowest = sorted(measured, key=lambda row: int(row.get("request_ms") or 0), reverse=True)[:10]
    lines.extend(["", "## 最慢 Case", "", "| 模型 | Case | 请求耗时 | LLM 耗时 | 状态 |", "| --- | --- | ---: | ---: | --- |"])
    for row in slowest:
        status = "ok" if row.get("ok") else (row.get("error") or "error")
        lines.append(
            f"| {row.get('provider_label') or row.get('provider_id')} | {row.get('case_id')} | "
            f"{_format_ms(row.get('request_ms') or 0)} | {_format_ms(row.get('llm_ms') or 0)} | {status} |"
        )

    skipped = [row for row in rows if row.get("run_kind") == "skipped"]
    if skipped:
        lines.extend(["", "## 跳过的模型", ""])
        for row in skipped:
            lines.append(f"- {row.get('provider_label')}: {row.get('error')}")

    failures = [row for row in measured if not row.get("ok") or row.get("quality_gate_pass") is False]
    if failures:
        lines.extend(["", "## 错误与质量失败", ""])
        for row in failures[:20]:
            reason = row.get("error") or "; ".join(row.get("quality_failures") or []) or "quality gate failed"
            lines.append(f"- {row.get('provider_label')} / {row.get('case_id')}: {reason}")

    return "\n".join(lines) + "\n"


def write_outputs(output_dir: Path, rows: list[dict], summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "raw.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "report.md").write_text(render_report(rows, summary), encoding="utf-8")


def expand_benchmark_items(cases_data: dict, case_limit: int | None = None) -> list[dict]:
    if "scenarios" not in cases_data:
        cases = [dict(case) for case in cases_data.get("cases", [])]
        return cases[:case_limit] if case_limit is not None else cases

    expanded: list[dict] = []
    for scenario in cases_data.get("scenarios", []):
        scenario_id = scenario["id"]
        for turn_index, turn in enumerate(scenario.get("turns", []), 1):
            item = {
                **{key: value for key, value in scenario.items() if key != "turns"},
                **turn,
                "id": f"{scenario_id}::turn_{turn_index}",
                "scenario_id": scenario_id,
                "turn_index": turn_index,
                "turn_count": len(scenario.get("turns", [])),
            }
            item.setdefault("prior_messages", [])
            item.setdefault("forbidden_reply_behavior", scenario.get("forbidden_reply_behavior", []))
            expanded.append(item)
            if case_limit is not None and len(expanded) >= case_limit:
                return expanded
    return expanded


def _case_problem_id(case: dict) -> str:
    problem_ref = (case.get("problem_ref") or case.get("scenario_id") or case.get("id") or "aichat_bench").strip()
    scenario_id = case.get("scenario_id") or case.get("id", "case")
    return f"{problem_ref}::bench::{scenario_id}"


def _chat_payload_from_case(case: dict, student_id: str, session_id: str) -> dict:
    messages = build_messages_from_case(case)
    user_content = messages[-1]["content"] if messages else case.get("student_message", "")
    return {
        "student_id": student_id,
        "problem_id": _case_problem_id(case),
        "session_id": session_id,
        "message": user_content,
        "problem_title": case.get("problem_title", ""),
        "problem_url": case.get("problem_ref", ""),
        "problem_context": case.get("problem_context", ""),
        "student_code": case.get("student_code", ""),
    }


def _quality_result(case: dict, reply: str, cases_data: dict) -> dict:
    return evaluate_response(case, reply, cases_data.get("rubric", {}))


def run_case_request(client: TestClient, headers: dict, payload: dict, timeout_seconds: int) -> tuple[int, dict]:
    started = time.perf_counter()
    response = client.post("/chat", headers=headers, json=payload, timeout=timeout_seconds)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    try:
        body = response.json()
    except Exception:
        body = {"detail": response.text[:500]}
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code}: {body.get('detail') or body}")
    return elapsed_ms, body


def run_benchmark(
    cases_data: dict,
    provider_configs: list[ProviderConfig],
    *,
    case_limit: int,
    repeat: int,
    warmup: int,
    timeout_seconds: int,
    max_completion_tokens: int,
    progress_stream=None,
) -> list[dict]:
    cases = expand_benchmark_items(cases_data, case_limit=case_limit)
    rows: list[dict] = []
    original_client = noi_agent.client
    original_models = os.environ.get("NOI_CHAT_MODELS")
    test_client = TestClient(api_server.app)

    def progress(message: str) -> None:
        if progress_stream is None:
            return
        progress_stream.write(message + "\n")
        progress_stream.flush()

    try:
        for config in provider_configs:
            if not config.enabled:
                rows.append(
                    {
                        "provider_id": config.provider_id,
                        "provider_label": config.label,
                        "model": config.model,
                        "thinking_mode": config.thinking_mode,
                        "run_kind": "skipped",
                        "ok": False,
                        "error": config.skip_reason,
                    }
                )
                progress(f"PROVIDER_SKIPPED provider={config.provider_id} reason={config.skip_reason}")
                continue

            os.environ["NOI_CHAT_MODELS"] = config.model
            telemetry: dict = {}
            real_client = OpenAI(api_key=config.api_key, base_url=config.base_url)
            noi_agent.client = TimedOpenAIClient(
                real_client,
                telemetry,
                timeout_seconds=timeout_seconds,
                max_completion_tokens=max_completion_tokens,
                token_param=config.token_param,
                extra_body=config.extra_body,
            )
            session_ids: dict[tuple[str, int], str] = {}

            for case_index, case in enumerate(cases, 1):
                total_runs = warmup + repeat
                for run_index in range(total_runs):
                    run_kind = "warmup" if run_index < warmup else "measured"
                    conversation_id = case.get("scenario_id") or case.get("id")
                    session_key = (conversation_id, run_index)
                    if session_key not in session_ids:
                        session_ids[session_key] = (
                            f"bench_{config.provider_id}_{conversation_id}_{run_index}_{int(time.time() * 1000)}"
                        )
                    session_id = session_ids[session_key]
                    student_id = f"aichat_bench_{config.provider_id}"
                    headers = {"Authorization": f"Bearer {create_token(student_id, 'student')}"}
                    payload = _chat_payload_from_case(case, student_id, session_id)
                    telemetry.clear()
                    row = {
                        "provider_id": config.provider_id,
                        "provider_label": config.label,
                        "base_url_alias": config.base_url,
                        "model": config.model,
                        "thinking_mode": config.thinking_mode,
                        "case_id": case.get("id"),
                        "scenario_id": case.get("scenario_id", ""),
                        "turn_index": case.get("turn_index", 1),
                        "input_mode": case.get("input_mode", ""),
                        "algorithm_tag": case.get("algorithm_tag", ""),
                        "case_index": case_index,
                        "run_index": run_index,
                        "run_kind": run_kind,
                    }
                    request_started = time.perf_counter()
                    try:
                        request_ms, body = run_case_request(test_client, headers, payload, timeout_seconds)
                        reply = body.get("reply", "")
                        quality = _quality_result(case, reply, cases_data)
                        row.update(
                            {
                                "ok": True,
                                "request_ms": request_ms,
                                "llm_ms": telemetry.get("llm_ms", 0),
                                "reply_chars": len(reply),
                                "level": body.get("level", ""),
                                "quality_gate_pass": quality.get("passed"),
                                "quality_failures": quality.get("failures", []),
                                "response_text": reply,
                            }
                        )
                    except Exception as exc:
                        row.update(
                            {
                                "ok": False,
                                "request_ms": int((time.perf_counter() - request_started) * 1000),
                                "llm_ms": telemetry.get("llm_ms", 0),
                                "reply_chars": 0,
                                "quality_gate_pass": False,
                                "quality_failures": [],
                                "error": str(exc),
                            }
                        )
                    rows.append(row)
                    progress(
                        "CASE_DONE provider={provider} case={case} run_kind={run_kind} ok={ok}".format(
                            provider=config.provider_id,
                            case=case.get("id"),
                            run_kind=run_kind,
                            ok=row.get("ok"),
                        )
                    )
    finally:
        noi_agent.client = original_client
        if original_models is None:
            os.environ.pop("NOI_CHAT_MODELS", None)
        else:
            os.environ["NOI_CHAT_MODELS"] = original_models

    return rows


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark AIChat latency across Kimi K2.6, MiMo, and DeepSeek.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--case-limit", type=int, default=DEFAULT_CASE_LIMIT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--repeat", type=int, default=int(os.getenv("AICHAT_BENCH_REPEAT", DEFAULT_REPEAT)))
    parser.add_argument("--warmup", type=int, default=int(os.getenv("AICHAT_BENCH_WARMUP", DEFAULT_WARMUP)))
    parser.add_argument("--timeout-seconds", type=int, default=int(os.getenv("AICHAT_BENCH_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)))
    parser.add_argument(
        "--max-completion-tokens",
        type=int,
        default=int(os.getenv("AICHAT_BENCH_MAX_COMPLETION_TOKENS", DEFAULT_MAX_COMPLETION_TOKENS)),
    )
    parser.add_argument(
        "--providers",
        default="kimi,mimo,deepseek",
        help="Comma-separated provider ids to run, for example: deepseek",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    cases_data = load_cases(args.cases)
    requested_providers = {item.strip() for item in args.providers.split(",") if item.strip()}
    providers = [
        config
        for config in build_provider_configs()
        if not requested_providers or config.provider_id in requested_providers
    ]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_output_dir = args.output_dir / timestamp
    rows = run_benchmark(
        cases_data,
        providers,
        case_limit=args.case_limit,
        repeat=args.repeat,
        warmup=args.warmup,
        timeout_seconds=args.timeout_seconds,
        max_completion_tokens=args.max_completion_tokens,
        progress_stream=sys.stderr,
    )
    summary = summarize_rows(rows)
    write_outputs(run_output_dir, rows, summary)
    print(json.dumps({"output_dir": str(run_output_dir), **summary}, ensure_ascii=False))
    return 0 if any(row.get("ok") for row in rows if row.get("run_kind") == "measured") else 1


if __name__ == "__main__":
    raise SystemExit(main())
