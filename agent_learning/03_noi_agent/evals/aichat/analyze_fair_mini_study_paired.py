"""Paired analysis for the fair 20-case response blind review.

The blind-review rows are repeated measures: each case has multiple system
responses. This script analyzes those rows case-by-case instead of treating
all response rows as independent samples.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


DEFAULT_INPUT_JSONL = Path("docs/research/coach_response_review_labels_fair_mini_study_20_20260511.jsonl")
DEFAULT_OUTPUT_JSON = Path("docs/research/fair_mini_study_20_paired_analysis_20260511.summary.json")
DEFAULT_OUTPUT_MD_ZH = Path("docs/research/fair_mini_study_20_paired_analysis_20260511.zh.md")
DEFAULT_OUTPUT_MD = Path("docs/research/fair_mini_study_20_paired_analysis_20260511.md")

DEFAULT_SYSTEMS = [
    "current_system",
    "single_llm",
    "single_llm+guard",
    "single_llm+guard+repair",
    "bridge_contract",
    "bridge_contract+guard",
    "bridge_contract+guard+repair",
]

CORE_SCORE_KEYS = [
    "bridge_identification",
    "groundedness",
    "scaffold_appropriateness",
    "bridge_leakage_control",
    "next_step_clarity",
    "single_focus_coherence",
]


def load_label_rows(path: Path | str = DEFAULT_INPUT_JSONL) -> list[dict]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL row: {exc}") from exc
            rows.append(row)
    return rows


def _float(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def _numeric_rank(row: dict) -> float | None:
    raw = str(row.get("preference_rank", "")).strip()
    try:
        return float(raw)
    except ValueError:
        return None


def _core_scores(row: dict) -> list[float]:
    scores = row.get("scores") or {}
    return [_float(scores.get(key)) for key in CORE_SCORE_KEYS]


def _micro_score(row: dict) -> float:
    scores = row.get("scores") or {}
    return _float(scores.get("bridge_oriented_micro_example"))


def student_ready_pass(row: dict) -> bool:
    if _float(row.get("overall_quality_score")) < 4:
        return False
    if str(row.get("would_show_to_student", "")).strip() != "yes":
        return False
    if row.get("leakage_label") in {"major_bridge_leakage", "answer_leakage"}:
        return False
    return all(score > 0 for score in _core_scores(row))


def student_ready_safe_pass(row: dict) -> bool:
    return student_ready_pass(row) and row.get("leakage_label") == "no_leakage"


def _rows_by_system(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("system", ""))].append(row)
    return grouped


def _rows_by_case_and_system(rows: list[dict]) -> dict[str, dict[str, dict]]:
    grouped: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        case_id = str(row.get("case_id", ""))
        system = str(row.get("system", ""))
        grouped[case_id][system] = row
    return grouped


def build_system_summary(rows: list[dict], *, systems: list[str] | None = None) -> dict:
    systems = systems or DEFAULT_SYSTEMS
    grouped = _rows_by_system(rows)
    summary = {}
    for system in systems:
        system_rows = grouped.get(system, [])
        ranks = [rank for row in system_rows if (rank := _numeric_rank(row)) is not None]
        summary[system] = {
            "n": len(system_rows),
            "core6_mean": _mean([_mean(_core_scores(row)) for row in system_rows]),
            "with_micro7_mean": _mean([_mean([*_core_scores(row), _micro_score(row)]) for row in system_rows]),
            "overall_quality_mean": _mean([_float(row.get("overall_quality_score")) for row in system_rows]),
            "rank_mean": _mean(ranks),
            "rank1_count": sum(1 for row in system_rows if _numeric_rank(row) == 1),
            "student_ready_pass_count": sum(1 for row in system_rows if student_ready_pass(row)),
            "student_ready_safe_pass_count": sum(1 for row in system_rows if student_ready_safe_pass(row)),
            "would_show_yes_count": sum(1 for row in system_rows if row.get("would_show_to_student") == "yes"),
            "would_show_no_count": sum(1 for row in system_rows if row.get("would_show_to_student") == "no"),
            "major_or_answer_leakage_count": sum(
                1 for row in system_rows if row.get("leakage_label") in {"major_bridge_leakage", "answer_leakage"}
            ),
            "major_bridge_leakage_count": sum(
                1 for row in system_rows if row.get("leakage_label") == "major_bridge_leakage"
            ),
            "minor_bridge_leakage_count": sum(
                1 for row in system_rows if row.get("leakage_label") == "minor_bridge_leakage"
            ),
            "answer_leakage_count": sum(1 for row in system_rows if row.get("leakage_label") == "answer_leakage"),
            "repair_applied_count": sum(1 for row in system_rows if str(row.get("repair_applied")) == "true"),
            "blocked_count": sum(1 for row in system_rows if str(row.get("blocked")) == "true"),
        }
    return summary


def _metric_value(row: dict, metric: str) -> float:
    if metric == "overall_quality_score":
        return _float(row.get("overall_quality_score"))
    if metric == "core6_mean":
        return _mean(_core_scores(row))
    if metric == "with_micro7_mean":
        return _mean([*_core_scores(row), _micro_score(row)])
    raise ValueError(f"unsupported metric: {metric}")


def _bootstrap_ci95(diffs: list[float], *, rounds: int = 2000, seed: int = 20260511) -> list[float]:
    if not diffs:
        return [0.0, 0.0]
    rng = random.Random(seed)
    means = []
    n = len(diffs)
    for _ in range(rounds):
        sample = [diffs[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    low = means[int(0.025 * (rounds - 1))]
    high = means[int(0.975 * (rounds - 1))]
    return [round(low, 4), round(high, 4)]


def compute_paired_comparisons(
    rows: list[dict],
    *,
    systems: list[str] | None = None,
    metric: str = "overall_quality_score",
    bootstrap_rounds: int = 2000,
) -> dict:
    systems = systems or DEFAULT_SYSTEMS
    grouped = _rows_by_case_and_system(rows)
    comparisons = {}
    for system_a in systems:
        for system_b in systems:
            if system_a == system_b:
                continue
            diffs = []
            wins = ties = losses = 0
            case_diffs = {}
            for case_id, case_rows in grouped.items():
                if system_a not in case_rows or system_b not in case_rows:
                    continue
                diff = _metric_value(case_rows[system_a], metric) - _metric_value(case_rows[system_b], metric)
                diff = round(diff, 4)
                diffs.append(diff)
                case_diffs[case_id] = diff
                if diff > 0:
                    wins += 1
                elif diff < 0:
                    losses += 1
                else:
                    ties += 1
            comparisons[f"{system_a}__vs__{system_b}"] = {
                "system_a": system_a,
                "system_b": system_b,
                "metric": metric,
                "paired_cases": len(diffs),
                "wins": wins,
                "ties": ties,
                "losses": losses,
                "mean_diff": _mean(diffs),
                "bootstrap_ci95": _bootstrap_ci95(diffs, rounds=bootstrap_rounds),
                "case_diffs": case_diffs,
            }
    return comparisons


def _table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def _render_report_zh(payload: dict) -> str:
    summary = payload["system_summary"]
    comparisons = payload["paired_comparisons"]
    rows = []
    for system, item in summary.items():
        rows.append(
            [
                system,
                item["overall_quality_mean"],
                item["student_ready_pass_count"],
                item["student_ready_safe_pass_count"],
                item["rank1_count"],
                item["major_or_answer_leakage_count"],
                item["repair_applied_count"],
            ]
        )

    important_keys = [
        "bridge_contract+guard+repair__vs__single_llm+guard",
        "bridge_contract+guard+repair__vs__single_llm+guard+repair",
        "bridge_contract__vs__single_llm",
        "bridge_contract+guard+repair__vs__current_system",
    ]
    comp_rows = []
    for key in important_keys:
        item = comparisons.get(key)
        if not item:
            continue
        comp_rows.append(
            [
                f"{item['system_a']} - {item['system_b']}",
                item["mean_diff"],
                item["bootstrap_ci95"],
                f"{item['wins']}/{item['ties']}/{item['losses']}",
                item["paired_cases"],
            ]
        )

    return "\n\n".join(
        [
            "# Fair 20-case Paired Analysis（2026-05-11）",
            "本报告把 20 个 case 当作配对样本分析，而不是把 140 行回复当作独立样本。它是 development / pilot evidence，不是最终 held-out test。",
            "## 系统汇总",
            _table(
                [
                    "系统",
                    "总体质量均分",
                    "student_ready_pass",
                    "student_ready_safe_pass",
                    "rank=1",
                    "major/answer 泄露",
                    "repair_applied",
                ],
                rows,
            ),
            "## 关键配对比较（总体质量）",
            _table(["比较", "均值差", "bootstrap 95% CI", "win/tie/loss", "配对 case"], comp_rows),
            "## 解释边界",
            "- `single_llm+guard` 的质量高于 `single_llm` 不能归因于 Guard 本身；当前 guard-only 条件没有修改 final response，差异更可能来自 LLM 多次生成的 run-to-run variance。\n"
            "- Guard/Repair 的因果作用需要复用同一个 candidate 做 paired before/after ablation，不能只比较分别生成的系统输出。\n"
            "- 当前最稳定的 pilot 信号是：Bridge Contract variants 在 case-level preference 和 student-ready 指标上更强；critical bridge leakage 仍未完全解决。",
        ]
    ) + "\n"


def _render_report_en(payload: dict) -> str:
    summary = payload["system_summary"]
    comparisons = payload["paired_comparisons"]
    rows = []
    for system, item in summary.items():
        rows.append(
            [
                system,
                item["overall_quality_mean"],
                item["student_ready_pass_count"],
                item["student_ready_safe_pass_count"],
                item["rank1_count"],
                item["major_or_answer_leakage_count"],
                item["repair_applied_count"],
            ]
        )

    important_keys = [
        "bridge_contract+guard+repair__vs__single_llm+guard",
        "bridge_contract+guard+repair__vs__single_llm+guard+repair",
        "bridge_contract__vs__single_llm",
        "bridge_contract+guard+repair__vs__current_system",
    ]
    comp_rows = []
    for key in important_keys:
        item = comparisons.get(key)
        if not item:
            continue
        comp_rows.append(
            [
                f"{item['system_a']} - {item['system_b']}",
                item["mean_diff"],
                item["bootstrap_ci95"],
                f"{item['wins']}/{item['ties']}/{item['losses']}",
                item["paired_cases"],
            ]
        )

    return "\n\n".join(
        [
            "# Fair 20-case Paired Analysis 2026-05-11",
            "This report treats the 20 cases as paired samples rather than treating the 140 response rows as independent observations. It is development / pilot evidence, not a final held-out result.",
            "## System Summary",
            _table(
                [
                    "System",
                    "Overall Quality Mean",
                    "student_ready_pass",
                    "student_ready_safe_pass",
                    "rank=1",
                    "major/answer leakage",
                    "repair_applied",
                ],
                rows,
            ),
            "## Key Paired Comparisons (Overall Quality)",
            _table(["Comparison", "Mean Diff", "Bootstrap 95% CI", "Win/Tie/Loss", "Paired Cases"], comp_rows),
            "## Interpretation Boundary",
            "- The higher score of `single_llm+guard` over `single_llm` should not be attributed to Guard itself; in the current guard-only condition, the guard did not modify the final response, so the difference is more plausibly run-to-run generation variance.\n"
            "- The causal effect of Guard/Repair requires a paired before/after ablation that reuses the same candidate response.\n"
            "- The most stable pilot signal is that Bridge Contract variants are stronger on case-level preference and student-ready metrics, while critical bridge leakage remains unsolved.",
        ]
    ) + "\n"


def write_analysis_outputs(
    rows: list[dict],
    *,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md_zh: Path = DEFAULT_OUTPUT_MD_ZH,
    output_md: Path = DEFAULT_OUTPUT_MD,
    systems: list[str] | None = None,
    bootstrap_rounds: int = 2000,
) -> dict:
    systems = systems or DEFAULT_SYSTEMS
    payload = {
        "input_rows": len(rows),
        "case_count": len({row.get("case_id") for row in rows}),
        "systems": systems,
        "system_summary": build_system_summary(rows, systems=systems),
        "paired_comparisons": compute_paired_comparisons(
            rows,
            systems=systems,
            metric="overall_quality_score",
            bootstrap_rounds=bootstrap_rounds,
        ),
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md_zh.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md_zh.write_text(_render_report_zh(payload), encoding="utf-8")
    output_md.write_text(_render_report_en(payload), encoding="utf-8")
    return payload


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_JSONL)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md-zh", type=Path, default=DEFAULT_OUTPUT_MD_ZH)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--bootstrap-rounds", type=int, default=2000)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    payload = write_analysis_outputs(
        load_label_rows(args.input_jsonl),
        output_json=args.output_json,
        output_md_zh=args.output_md_zh,
        output_md=args.output_md,
        bootstrap_rounds=max(100, args.bootstrap_rounds),
    )
    print(
        json.dumps(
            {
                "output_json": str(args.output_json),
                "output_md_zh": str(args.output_md_zh),
                "output_md": str(args.output_md),
                "case_count": payload["case_count"],
                "input_rows": payload["input_rows"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
