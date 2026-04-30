#!/usr/bin/env python3
"""Probe pedagogical_judge_v2 real-call latency.

This script intentionally does not modify business code or persist results.
It temporarily raises the judge timeout to 15s by default, runs real calls,
and prints p50 / p95 / p99 / max latency numbers.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        return 0.0
    index = max(0, min(len(values) - 1, math.ceil((percentile / 100) * len(values)) - 1))
    return values[index]


def _sample_payload() -> dict:
    return {
        "user_input": "这道题我知道用 Floyd，但不知道为什么不能每个询问跑 Dijkstra。",
        "messages": [
            {"role": "user", "content": "P1119 灾后重建怎么做？我感觉是最短路。"},
            {"role": "assistant", "content": "先看时间不下降：每次会新增一些已经修好的村庄。"},
            {"role": "user", "content": "那是不是每个询问跑一次 Dijkstra？"},
            {"role": "assistant", "content": "先估一下 Q 很大时每次跑的总量。"},
            {"role": "user", "content": "N=200，M 接近 20000，Q=50000。"},
        ],
        "problem_context": {
            "problem_ref": "P1119",
            "title": "灾后重建",
            "summary": (
                "村庄按修复时间 t_i 逐步可用，询问时间不下降。"
                "每个询问问在第 t 天 x 到 y 经过已修复村庄的最短路。"
            ),
        },
        "student_code": None,
        "rule_weak_signals": ["method_selection", "complexity_analysis"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe pedagogical_judge_v2 latency.")
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    _load_dotenv(ROOT / ".env")
    os.environ["NOI_PEDAGOGICAL_JUDGE_TIMEOUT_SECONDS"] = str(args.timeout)

    from noi_agent import pedagogical_judge_v2

    payload = _sample_payload()
    latencies_ms: list[float] = []
    failures: list[dict] = []

    for index in range(args.runs):
        start = time.perf_counter()
        result = pedagogical_judge_v2(**payload)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies_ms.append(elapsed_ms)
        if result.get("_failed"):
            failures.append({"run": index + 1, "reason": result.get("_reason", "unknown")})
        print(
            json.dumps(
                {
                    "run": index + 1,
                    "latency_ms": round(elapsed_ms, 2),
                    "failed": bool(result.get("_failed")),
                    "reason": result.get("_reason"),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    ordered = sorted(latencies_ms)
    summary = {
        "runs": args.runs,
        "timeout_seconds": args.timeout,
        "failures": len(failures),
        "p50_ms": round(_percentile(ordered, 50), 2),
        "p95_ms": round(_percentile(ordered, 95), 2),
        "p99_ms": round(_percentile(ordered, 99), 2),
        "max_ms": round(max(ordered) if ordered else 0.0, 2),
    }
    print("SUMMARY " + json.dumps(summary, ensure_ascii=False), flush=True)
    if failures:
        print("FAILURES " + json.dumps(failures, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
