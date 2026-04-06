import json
from collections import defaultdict
from pathlib import Path


ROOT = Path("/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review")
SOURCE = ROOT / "promptfoo_tests.jsonl"
TARGET = ROOT / "promptfoo_tests.sample.jsonl"
PER_MODE = 1


def _case_size(row: dict) -> int:
    return len(row.get("vars", {}).get("case", ""))


def build_sample(source: Path, target: Path, per_mode: int = PER_MODE) -> dict[str, int]:
    grouped = defaultdict(list)
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        mode = row.get("metadata", {}).get("mode", "unknown")
        grouped[mode].append(row)

    selected = []
    for mode in sorted(grouped):
        rows = sorted(grouped[mode], key=_case_size)
        selected.extend(rows[:per_mode])

    target.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in selected) + "\n",
        encoding="utf-8",
    )

    return {mode: min(len(rows), per_mode) for mode, rows in grouped.items()}


def main() -> None:
    counts = build_sample(SOURCE, TARGET, per_mode=PER_MODE)
    total = sum(counts.values())
    print(json.dumps({"target": str(TARGET), "total": total, "counts": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
