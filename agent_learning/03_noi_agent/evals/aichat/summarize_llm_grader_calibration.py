"""Summarize LLM-grader calibration predictions against coach references.

Input JSONL rows should contain:
- grader_type
- case_id
- condition_id
- coach_reference: human/adjudicated labels
- grader_prediction: model output parsed as a dict

This script does not call any LLM. It only computes calibration metrics from
already generated predictions.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_OUTPUT_JSON = Path("docs/research/llm_grader_calibration_metrics_20260517.json")
DEFAULT_OUTPUT_MD = Path("docs/research/llm_grader_calibration_metrics_20260517.md")

CRITICAL = {"major_bridge_leakage", "answer_leakage"}


def _read_jsonl(path: Path) -> list[dict]:
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


def _choice(value: object) -> str:
    raw = str(value or "").strip()
    if "｜" in raw:
        raw = raw.split("｜", 1)[0].strip()
    if "|" in raw:
        raw = raw.split("|", 1)[0].strip()
    return raw


def _as_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def _ready_from_reference(ref: dict) -> str:
    value = _choice(ref.get("student_ready") or ref.get("student_ready_pass"))
    if value in {"yes", "borderline", "no"}:
        return value
    if value == "True":
        return "yes"
    if value == "False":
        return "no"
    return value


def summarize(rows: list[dict]) -> dict:
    by_grader: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_grader[str(row.get("grader_type") or "unknown")].append(row)

    output = {}
    for grader, items in sorted(by_grader.items()):
        status_counts = Counter(str(row.get("grader_status") or "ok") for row in items)
        valid_items = [
            row
            for row in items
            if str(row.get("grader_status") or "ok") == "ok"
        ]
        leakage_total = leakage_match = 0
        ready_total = ready_match = 0
        safe_total = safe_match = 0
        tp = fp = tn = fn = 0
        major_fn = 0
        unknown = 0
        ref_overall: list[float] = []
        pred_overall: list[float] = []
        abs_errors: list[float] = []
        for row in valid_items:
            ref = row.get("coach_reference") or row.get("reference") or {}
            pred = row.get("grader_prediction") or row.get("prediction") or {}
            ref_leak = _choice(ref.get("leakage_label"))
            pred_leak = _choice(pred.get("leakage_label"))
            if not pred_leak or pred_leak.upper() == "UNKNOWN":
                unknown += 1
            if ref_leak and pred_leak and pred_leak.upper() != "UNKNOWN":
                leakage_total += 1
                leakage_match += int(ref_leak == pred_leak)
                ref_crit = ref_leak in CRITICAL
                pred_crit = pred_leak in CRITICAL
                if ref_crit and pred_crit:
                    tp += 1
                elif not ref_crit and pred_crit:
                    fp += 1
                elif ref_crit and not pred_crit:
                    fn += 1
                    major_fn += 1
                else:
                    tn += 1

            ref_ready = _ready_from_reference(ref)
            pred_ready = _choice(pred.get("student_ready"))
            if ref_ready and pred_ready and pred_ready.upper() != "UNKNOWN":
                ready_total += 1
                ready_match += int(ref_ready == pred_ready)

            ref_safe = bool(ref_ready == "yes" and ref_leak == "no_leakage")
            pred_safe = bool(pred_ready == "yes" and pred_leak == "no_leakage")
            if ref_ready and ref_leak and pred_ready and pred_leak and pred_leak.upper() != "UNKNOWN":
                safe_total += 1
                safe_match += int(ref_safe == pred_safe)

            ro = _as_float(ref.get("overall_quality") or ref.get("overall_quality_score"))
            po = _as_float(pred.get("overall_quality") or pred.get("overall_quality_score"))
            if ro is not None and po is not None:
                ref_overall.append(ro)
                pred_overall.append(po)
                abs_errors.append(abs(po - ro))

        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        f1 = 2 * precision * recall / (precision + recall) if precision and recall else None
        output[grader] = {
            "n": len(items),
            "valid_n": len(valid_items),
            "invalid_rate": (len(items) - len(valid_items)) / len(items) if items else None,
            "status_counts": dict(sorted(status_counts.items())),
            "unknown_rate": unknown / len(valid_items) if valid_items else None,
            "leakage_label_accuracy": leakage_match / leakage_total if leakage_total else None,
            "critical_precision": precision,
            "critical_recall": recall,
            "critical_f1": f1,
            "major_leakage_false_negative_rate": major_fn / (tp + fn) if tp + fn else None,
            "student_ready_agreement": ready_match / ready_total if ready_total else None,
            "safe_ready_agreement": safe_match / safe_total if safe_total else None,
            "overall_pearson": _pearson(ref_overall, pred_overall),
            "overall_mae": sum(abs_errors) / len(abs_errors) if abs_errors else None,
            "critical_confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        }
    return output


def _fmt(value: object) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_markdown(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LLM Grader Calibration Metrics",
        "",
        "These metrics compare LLM grader predictions with coach/adjudicated references. LLM graders remain auxiliary graders, not gold labels.",
        "",
        "| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for grader, item in summary.items():
        lines.append(
            f"| `{grader}` | {item['n']} | {item['valid_n']} | {_fmt(item['invalid_rate'])} | "
            f"{_fmt(item['unknown_rate'])} | {_fmt(item['leakage_label_accuracy'])} | "
            f"{_fmt(item['critical_precision'])}/{_fmt(item['critical_recall'])}/{_fmt(item['critical_f1'])} | "
            f"{_fmt(item['major_leakage_false_negative_rate'])} | {_fmt(item['student_ready_agreement'])} | "
            f"{_fmt(item['safe_ready_agreement'])} | {_fmt(item['overall_pearson'])} | {_fmt(item['overall_mae'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions-jsonl", required=True, type=Path)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)

    summary = summarize(_read_jsonl(args.predictions_jsonl))
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(summary, args.output_md)
    print(f"Wrote LLM grader calibration metrics for {len(summary)} grader types")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
