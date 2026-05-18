"""Verify dialogue-state v3 paper reports against machine-readable evidence.

This is a report gate, not a new experiment. It checks a deliberately small set
of paper-facing headline numbers and fails if the checked-in Markdown reports
drift from the reproduced JSON/CSV/JSONL evidence bundle.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:  # Support direct `python evals/aichat/...py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.aichat import reproduce_dialogue_state_v3_tables

MAIN_TABLE_REPORT = Path(
    "docs/research/dialogue_state_v3_main_paper_ready_tables_20260517.zh.md"
)
PAIRWISE_REPORT = Path(
    "docs/research/dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md"
)
REPAIR_REPORT = Path("docs/research/repair_same_candidate_stress_result_20260517.zh.md")
DBOX_REPORT = Path("docs/research/dbox_guard_repair_fairness_report_20260517.zh.md")
LLM_REPORT = Path(
    "docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md"
)


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _fmt_signed(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NA"
    return f"{float(value):+.{digits}f}"


def _fmt_prf(value: Any) -> str:
    return "NA" if value is None else f"{float(value):.3f}"


def _expect_contains(
    diffs: list[str], report_text: str, expected: str, label: str
) -> None:
    if expected not in report_text:
        diffs.append(f"{label}: expected line not found: {expected}")


def _check_main_tables(root: Path, bundle: dict[str, Any], diffs: list[str]) -> None:
    text = (root / MAIN_TABLE_REPORT).read_text(encoding="utf-8")
    for case_slice, scenario_tables in bundle["main_paper_ready_tables"].items():
        primary = scenario_tables["priority60_adjudicated_plus_coachA"]
        for condition, item in primary.items():
            if item["n"] == 0:
                continue
            burden = item["burden"]
            expected = (
                f"| `{condition}` | {item['n']} | {_fmt(item['overall'])} | "
                f"{item['student_ready']} | {item['safe_ready']} | {item['no_leakage']} | "
                f"{item['minor']} | {item['major_answer']} | {_fmt(item['scaffold_avg'], 2)} | "
                f"{burden['low']}/{burden['medium']}/{burden['high']} |"
            )
            _expect_contains(
                diffs, text, expected, f"main table {case_slice}/{condition}"
            )


def _check_pairwise(root: Path, bundle: dict[str, Any], diffs: list[str]) -> None:
    text = (root / PAIRWISE_REPORT).read_text(encoding="utf-8")
    primary = bundle["pairwise"]["priority60_adjudicated_plus_coachA"]
    for key, item in primary.items():
        first, second = key.split("__vs__")
        wtl = item["win_tie_loss"]
        ci = f"[{_fmt_signed(item['bootstrap_ci95_low'])}, {_fmt_signed(item['bootstrap_ci95_high'])}]"
        expected = (
            f"| `{first}` vs `{second}` | {item['n']} | "
            f"{wtl['win']}/{wtl['tie']}/{wtl['loss']} | {_fmt_signed(item['mean_delta_overall'])} | "
            f"{ci} | {_fmt(item['sign_flip_permutation_p'], 4)} | "
            f"{item['safe_ready_delta']:+d} | {item['major_answer_delta']:+d} |"
        )
        _expect_contains(diffs, text, expected, f"pairwise {key}")


def _check_repair(root: Path, bundle: dict[str, Any], diffs: list[str]) -> None:
    text = (root / REPAIR_REPORT).read_text(encoding="utf-8")
    item = bundle["repair_same_candidate_summary"]
    wtl = item["repair_win_tie_loss"]
    pref = item["repair_pair_preference"]
    leakage = item["leakage_delta"]
    burden = item["burden_delta"]
    total = item["total_rows"]
    checks = {
        "labeled pairs": f"| labeled pairs | {item['labeled_pairs']} / {total} |",
        "before overall mean": f"| before overall mean | {_fmt(item['before_overall_mean'])} |",
        "after overall mean": f"| after overall mean | {_fmt(item['after_overall_mean'])} |",
        "mean overall delta": f"| mean overall delta | {_fmt_signed(item['mean_overall_delta'])} |",
        "quality win/tie/loss": f"| quality win / tie / loss | {wtl['win']} / {wtl['tie']} / {wtl['loss']} |",
        "repair preference": (
            "| repair preferred / original preferred / tie | "
            f"{pref.get('repair_preferred', 0)} / {pref.get('original_preferred', 0)} / {pref.get('tie', 0)} |"
        ),
        "leakage delta": (
            f"| leakage improved / same / worse | {leakage['improved']} / {leakage['same']} / {leakage['worse']} |"
        ),
        "burden delta": (
            f"| burden improved / same / worse | {burden['improved']} / {burden['same']} / {burden['worse']} |"
        ),
        "still leaks": f"| still-leaks rate | {_fmt(item['still_leaks_rate'])} |",
        "too vague": f"| too-vague-after-repair rate | {_fmt(item['too_vague_after_repair_rate'])} |",
    }
    for label, expected in checks.items():
        _expect_contains(diffs, text, expected, f"repair {label}")

    before_leak = item["before_leakage_distribution"]
    after_leak = item["after_leakage_distribution"]
    for label in [
        "no_leakage",
        "minor_bridge_leakage",
        "major_bridge_leakage",
        "answer_leakage",
    ]:
        expected = (
            f"| {label} | {before_leak.get(label, 0)} | {after_leak.get(label, 0)} |"
        )
        _expect_contains(diffs, text, expected, f"repair leakage distribution {label}")


def _check_dbox(root: Path, bundle: dict[str, Any], diffs: list[str]) -> None:
    text = (root / DBOX_REPORT).read_text(encoding="utf-8")
    for condition in [
        "dbox_repair_addon_review20",
        "main_dbox_guard_priority60_plus_coachA_same20",
        "main_bridge_repair_priority60_plus_coachA_same20",
    ]:
        item = bundle["dbox_fairness_addon"]["summaries"][condition]
        expected = (
            f"| `{condition}` | {item['n']} | {_fmt(item['overall'])} | "
            f"{item['ready_yes']} | {item['safe_ready']} | {item['no_leakage']} | {item['minor']} | "
            f"{item['major_answer']} | {_fmt(item['sufficiency'])} | "
            f"{item['burden_low']}/{item['burden_medium']}/{item['burden_high']} | "
            f"{item['needs_discussion']} |"
        )
        _expect_contains(diffs, text, expected, f"dbox summary {condition}")

    for comparison in [
        "dbox_repair_addon_minus_main_dbox_guard_A",
        "bridge_repair_A_minus_dbox_repair_addon",
        "bridge_repair_A_minus_main_dbox_guard_A",
    ]:
        item = bundle["dbox_fairness_addon"]["paired"][comparison]
        wtl = item["win_tie_loss"]
        expected = (
            f"| `{comparison}` | {item['n']} | {_fmt_signed(item['mean_overall_delta'])} | "
            f"{wtl['win']}/{wtl['tie']}/{wtl['loss']} | {item['safe_ready_delta_count']:+d} | "
            f"{_fmt_signed(item['mean_leakage_severity_delta'])} | {_fmt_signed(item['mean_burden_delta'])} |"
        )
        _expect_contains(diffs, text, expected, f"dbox paired {comparison}")


def _llm_reference_label(view: str) -> str:
    return {
        "priority60_adjudicated_deepseek": "priority60",
        "adj_coachA_sample20_deepseek": "adj+CoachA sample20",
        "adj_coachB_sample20_deepseek": "adj+CoachB sample20",
    }[view]


def _check_llm(root: Path, bundle: dict[str, Any], diffs: list[str]) -> None:
    text = (root / LLM_REPORT).read_text(encoding="utf-8")
    for view, metrics in bundle["llm_grader_calibration"].items():
        reference = _llm_reference_label(view)
        for grader, item in metrics.items():
            critical = (
                f"{_fmt_prf(item['critical_precision'])}/"
                f"{_fmt_prf(item['critical_recall'])}/"
                f"{_fmt_prf(item['critical_f1'])}"
            )
            expected = (
                f"| {reference} | `{grader}` | {item['valid_n']}/{item['n']} | "
                f"{_fmt_prf(item['leakage_label_accuracy'])} | {critical} | "
                f"{_fmt_prf(item['major_leakage_false_negative_rate'])} | "
                f"{_fmt_prf(item['student_ready_agreement'])} | {_fmt_prf(item['safe_ready_agreement'])} | "
                f"{_fmt_prf(item['overall_pearson'])} | {_fmt_prf(item['overall_mae'])} |"
            )
            _expect_contains(diffs, text, expected, f"llm {view}/{grader}")


def collect_diffs(
    root: Path | str = Path("."), bundle: dict[str, Any] | None = None
) -> list[str]:
    root_path = Path(root)
    evidence = bundle or reproduce_dialogue_state_v3_tables.reproduce(root_path)
    diffs: list[str] = []
    _check_main_tables(root_path, evidence, diffs)
    _check_pairwise(root_path, evidence, diffs)
    _check_repair(root_path, evidence, diffs)
    _check_dbox(root_path, evidence, diffs)
    _check_llm(root_path, evidence, diffs)
    return diffs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable diff output."
    )
    args = parser.parse_args(argv)

    diffs = collect_diffs(args.root)
    if args.json:
        print(
            json.dumps({"ok": not diffs, "diffs": diffs}, ensure_ascii=False, indent=2)
        )
    elif diffs:
        print("Dialogue-state v3 report verification failed:")
        for diff in diffs:
            print(f"- {diff}")
    else:
        print("Dialogue-state v3 report verification passed.")
    return 1 if diffs else 0


if __name__ == "__main__":
    raise SystemExit(main())
