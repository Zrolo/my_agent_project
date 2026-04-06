"""
Luogu problem-bank helpers for local corpus ingestion and compact/full problem cards.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from database import (
    create_problem_analysis_placeholder,
    get_problem_analysis,
    get_problem_by_luogu_pid,
    get_problem_tags,
    mark_problem_analysis_failed,
    reset_problem_analysis_for_retry,
    upsert_luogu_problem_analysis,
    upsert_luogu_problemset,
)
from review_engine import ANALYSIS_VERSION_V1, generate_problem_analysis

LUOGU_PID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
LUOGU_PROBLEM_PATH_RE = re.compile(r"^https?://(?:www\.)?luogu\.(?:com|com\.cn)/(?:problem|problemnew/show)/([A-Za-z0-9_]+)(?:[/?#].*)?$", re.I)

CONTEST_TAG_KEYWORDS = (
    "NOI",
    "CSP",
    "NOIP",
    "提高组",
    "普及组",
    "省选",
    "入门组",
    "IOI",
    "USACO",
)


def classify_tag(tag: str) -> str:
    text = (tag or "").strip()
    if not text:
        return "other"
    if re.fullmatch(r"\d{4}", text):
        return "year"
    if any(keyword in text for keyword in CONTEST_TAG_KEYWORDS):
        return "contest"
    return "algo"


def normalize_luogu_problem_ref(raw_ref: str | None) -> tuple[str | None, str | None]:
    raw = (raw_ref or "").strip()
    if not raw:
        return None, None

    if LUOGU_PROBLEM_PATH_RE.match(raw):
        pid = LUOGU_PROBLEM_PATH_RE.match(raw).group(1)
        return pid, f"https://www.luogu.com.cn/problem/{pid}"

    if LUOGU_PID_RE.fullmatch(raw):
        pid = raw
        return pid, f"https://www.luogu.com.cn/problem/{pid}"

    return None, None


def clean_text(text: str | None) -> str:
    content = text or ""
    content = re.sub(r"!\[.*?\]\(.*?\)", "[图]", content)
    content = re.sub(r"<[^>]+>", "", content)
    content = re.sub(r"\r\n?", "\n", content)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()


def smart_truncate(text: str | None, limit: int) -> str:
    content = clean_text(text)
    if len(content) <= limit:
        return content

    sentence_cut = content.rfind("。", 0, limit)
    if sentence_cut != -1 and sentence_cut >= max(40, limit // 3):
        return content[: sentence_cut + 1]

    paragraph_cut = content.rfind("\n", 0, limit)
    if paragraph_cut != -1 and paragraph_cut >= max(40, limit // 3):
        return content[:paragraph_cut].rstrip()

    return content[:limit].rstrip() + "…"


def extract_data_range(hint_text: str | None) -> str:
    hint = clean_text(hint_text)
    if not hint:
        return ""

    marker = hint.find("数据范围")
    snippet = hint[marker:] if marker != -1 else hint
    snippet = snippet.replace("【数据范围】", "数据范围：").replace("[Data Range]", "数据范围：")
    snippet = snippet.replace("数据范围】", "数据范围：")
    lines = [line.strip() for line in snippet.splitlines() if line.strip()]
    kept: list[str] = []
    for line in lines:
        if "数据范围" in line or any(token in line for token in ("<=", "≤", ">=", "≥", "%", "n ", "m ", "a,", "k", "s ")):
            kept.append(line)
        if len(" ".join(kept)) >= 180:
            break
    if not kept:
        return smart_truncate(snippet, 150)
    return smart_truncate(" ".join(kept), 150)


def _load_statement(problem: dict) -> dict[str, str]:
    raw = problem.get("statement_json") or {}
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = {}
    return {
        "description": raw.get("description") or "",
        "inputFormat": raw.get("inputFormat") or "",
        "outputFormat": raw.get("outputFormat") or "",
        "hint": raw.get("hint") or "",
    }


def build_problem_context(problem: dict) -> str:
    statement = _load_statement(problem)
    sections: list[str] = []
    description = smart_truncate(statement.get("description"), 2200)
    input_format = smart_truncate(statement.get("inputFormat"), 900)
    output_format = smart_truncate(statement.get("outputFormat"), 500)
    hint = clean_text(statement.get("hint"))
    if description:
        sections.append(f"## 题目描述\n{description}")
    if input_format:
        sections.append(f"## 输入格式\n{input_format}")
    if output_format:
        sections.append(f"## 输出格式\n{output_format}")

    try:
        samples = json.loads(problem.get("samples_json") or "[]")
    except Exception:
        samples = []
    if isinstance(samples, list) and samples:
        sample_blocks: list[str] = []
        for idx, sample in enumerate(samples[:2], start=1):
            if not isinstance(sample, list) or len(sample) < 2:
                continue
            sample_in = clean_text(sample[0])
            sample_out = clean_text(sample[1])
            sample_blocks.append(
                f"### 样例 {idx}\n输入：\n```text\n{sample_in}\n```\n输出：\n```text\n{sample_out}\n```"
            )
        if sample_blocks:
            sections.append("## 样例\n" + "\n\n".join(sample_blocks))

    range_text = extract_data_range(hint)
    limit_parts: list[str] = []
    if problem.get("time_limit_ms"):
        limit_parts.append(f"时间限制：{problem['time_limit_ms']} ms")
    if problem.get("memory_limit_kb"):
        limit_parts.append(f"内存限制：{problem['memory_limit_kb'] // 1024} MB")
    if range_text:
        limit_parts.append(range_text)
    if limit_parts:
        sections.append("## 限制\n" + "；".join(limit_parts))

    return "\n\n".join(section for section in sections if section).strip()


def build_compact_card(problem: dict) -> dict[str, Any]:
    statement = _load_statement(problem)
    algo_tags = get_problem_tags(problem["problem_id"], tag_type="algo")
    return {
        "title": problem.get("title", ""),
        "algo_tags": algo_tags[:3],
        "description_compact": smart_truncate(statement.get("description"), 400),
        "input_compact": smart_truncate(statement.get("inputFormat"), 200),
        "output_compact": smart_truncate(statement.get("outputFormat"), 100),
        "range_compact": extract_data_range(statement.get("hint")),
        "time_limit_ms": problem.get("time_limit_ms"),
    }


def build_full_card(problem: dict, analysis: dict) -> dict[str, Any]:
    compact = build_compact_card(problem)
    return {
        "title": problem.get("title", ""),
        "algo_tags": compact["algo_tags"],
        "summary": analysis.get("summary") or compact.get("description_compact", ""),
        "input_compact": compact["input_compact"],
        "output_compact": compact["output_compact"],
        "range_compact": compact["range_compact"],
        "time_limit_ms": compact["time_limit_ms"],
        "strategy_types": analysis.get("strategy_types") or [],
        "knowledge_points": analysis.get("knowledge_points") or [],
        "common_mistakes": analysis.get("common_mistakes") or [],
    }


def get_problem_card_by_ref(raw_ref: str | None) -> tuple[dict | None, str | None]:
    pid, _ = normalize_luogu_problem_ref(raw_ref)
    if not pid:
        return None, None

    problem = get_problem_by_luogu_pid(pid)
    if not problem:
        return None, None

    analysis = get_problem_analysis(problem["problem_id"])
    if analysis and analysis.get("status") == "completed":
        return build_full_card(problem, analysis), "full_card"
    return build_compact_card(problem), "compact_fallback"


def import_problemset_file(ndjson_path: str | Path, limit: int | None = None) -> dict[str, int]:
    path = Path(ndjson_path)
    if not path.exists():
        raise FileNotFoundError(f"latest.ndjson not found: {path}")

    imported = 0
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            raw = line.strip()
            if not raw:
                continue
            payload = json.loads(raw)
            upsert_luogu_problemset(payload, classify_tag)
            imported += 1
            if limit and imported >= limit:
                break
            if imported % 1000 == 0:
                print(f"[problem_import] imported {imported} rows...")

    return {"imported": imported}


def _run_problem_analysis(problem: dict) -> tuple[bool, str]:
    problem_id = problem["problem_id"]
    compact_card = build_compact_card(problem)
    try:
        analysis = generate_problem_analysis(
            problem_title=problem.get("title", ""),
            difficulty=problem.get("difficulty"),
            compact_card=compact_card,
        )
    except Exception as exc:
        mark_problem_analysis_failed(problem_id, str(exc))
        return False, "failed"

    if not analysis.get("ok"):
        mark_problem_analysis_failed(problem_id, analysis.get("message", "analysis unavailable"))
        return False, "failed"

    upsert_luogu_problem_analysis(
        problem_id=problem_id,
        summary=analysis["analysis"]["summary"],
        strategy_types=analysis["analysis"]["strategy_types"],
        knowledge_points=analysis["analysis"]["knowledge_points"],
        common_mistakes=analysis["analysis"]["common_mistakes"],
        analysis_version=ANALYSIS_VERSION_V1,
    )
    return True, "completed"


def ensure_problem_analysis(problem: dict) -> tuple[bool, str]:
    problem_id = problem["problem_id"]
    existing = get_problem_analysis(problem_id)
    if existing and existing.get("status") in {"pending", "completed"}:
        return False, existing.get("status")

    created = create_problem_analysis_placeholder(problem_id, ANALYSIS_VERSION_V1)
    if not created:
        existing = get_problem_analysis(problem_id)
        return False, (existing or {}).get("status", "pending")

    return _run_problem_analysis(problem)


def retry_problem_analysis_by_pid(pid: str | None) -> tuple[bool, str]:
    if not pid:
        return False, "missing_pid"

    problem = get_problem_by_luogu_pid(pid)
    if not problem:
        return False, "not_found"

    reset_problem_analysis_for_retry(problem["problem_id"], ANALYSIS_VERSION_V1)
    return _run_problem_analysis(problem)
