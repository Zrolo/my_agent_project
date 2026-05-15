import argparse
import json
from pathlib import Path


DEFAULT_ROOT = Path("docs/research")
DEFAULT_OUTPUT_JSON = Path("docs/research/bilingual_docs_validation_report.json")


LEGACY_UNPAIRED_DOCS = {
    "aichat_current_flow_v1.md",
    "aichat_risk_routing_policy_v1.md",
    "annotation_reliability_protocol_v1.md",
    "bridge_judge_offline_eval_v1.md",
    "bridge_schema_annotation_guide_v1.md",
    "bridge_tutor_rubric_v1.md",
    "coach_seed_labeling_guide_v1.md",
    "coach_seed_labeling_workbook_v1.md",
    "coach_seed_labeling_workbook_v2.md",
    "control_harness_policy_v1.md",
    "dev_ablation_bridge_contract_cases_20260511.zh.md",
    "field_usage_registry_v1.md",
    "index.md",
    "judge_prompt_patch_log.md",
    "judge_schema_smoke_report_20260509.md",
    "llm_judge_calibration_protocol_v1.zh.md",
    "paper_scope_v2.zh.md",
    "prompt_patch_log.md",
    "research_schema_v1.md",
    "research_v1_external_review_plan_20260511.zh.md",
    "research_v1_scope_lock.md",
    "response_ablation_smoke_report_20260509.md",
    "schema_mapping_human_to_runtime_v1.md",
}


def companion_name(name: str) -> str:
    if name.endswith(".zh.md"):
        return f"{name[:-6]}.md"
    if name.endswith(".md"):
        return f"{name[:-3]}.zh.md"
    raise ValueError(f"Not a Markdown research document: {name}")


def _markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.glob("*.md") if path.is_file())


def validate_bilingual_docs(
    root: Path = DEFAULT_ROOT,
    *,
    legacy_allowlist: set[str] | None = None,
) -> dict:
    legacy_allowlist = legacy_allowlist if legacy_allowlist is not None else LEGACY_UNPAIRED_DOCS
    markdown_files = _markdown_files(root)
    existing_names = {path.name for path in markdown_files}
    unpaired_docs = []
    legacy_unpaired_docs = []

    for path in markdown_files:
        expected_pair = companion_name(path.name)
        if expected_pair in existing_names:
            continue
        item = {
            "file": path.name,
            "expected_pair": expected_pair,
        }
        if path.name in legacy_allowlist:
            legacy_unpaired_docs.append(item)
        else:
            unpaired_docs.append(item)

    return {
        "root": str(root),
        "checked_count": len(markdown_files),
        "unpaired_count": len(unpaired_docs),
        "legacy_unpaired_count": len(legacy_unpaired_docs),
        "policy": "New docs/research Markdown files must have both English *.md and Chinese *.zh.md companions.",
        "unpaired_docs": unpaired_docs,
        "legacy_unpaired_docs": legacy_unpaired_docs,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate bilingual docs/research Markdown pairs.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument(
        "--no-default-legacy-allowlist",
        action="store_true",
        help="Treat every unpaired Markdown file as a current policy violation.",
    )
    args = parser.parse_args(argv)

    legacy_allowlist = set() if args.no_default_legacy_allowlist else LEGACY_UNPAIRED_DOCS
    report = validate_bilingual_docs(args.root, legacy_allowlist=legacy_allowlist)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 1 if report["unpaired_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
