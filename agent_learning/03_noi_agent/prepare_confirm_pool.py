import argparse
import json
from collections import Counter
from pathlib import Path

from problem_bank import classify_tag


def load_rows(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def build_stats(path: Path) -> dict:
    total_rows = 0
    tag_type_counts = Counter()
    algo_tags = Counter()
    tag_pairs = Counter()

    for row in load_rows(path):
        total_rows += 1
        tags = [str(tag).strip() for tag in (row.get("tags") or []) if str(tag).strip()]
        normalized = []
        for tag in tags:
            tag_type = classify_tag(tag)
            tag_type_counts[tag_type] += 1
            normalized.append(tag)
            if tag_type == "algo":
                algo_tags[tag] += 1
        unique_tags = sorted(set(normalized))
        for idx, left in enumerate(unique_tags):
            for right in unique_tags[idx + 1 :]:
                tag_pairs[f"{left} | {right}"] += 1

    return {
        "total_rows": total_rows,
        "tag_type_counts": dict(tag_type_counts.most_common()),
        "top_algo_tags": [{"tag": tag, "count": count} for tag, count in algo_tags.most_common(50)],
        "top_tag_pairs": [{"pair": pair, "count": count} for pair, count in tag_pairs.most_common(50)],
    }


def main():
    parser = argparse.ArgumentParser(description="统计 latest.ndjson 中的高频标签，给 confirm_pool 映射表做前置准备。")
    parser.add_argument("ndjson_path", help="latest.ndjson 文件路径")
    parser.add_argument("--out", help="可选：把统计结果写到指定 JSON 文件")
    args = parser.parse_args()

    stats = build_stats(Path(args.ndjson_path).expanduser())
    output = json.dumps(stats, ensure_ascii=False, indent=2)
    if args.out:
        out_path = Path(args.out).expanduser()
        out_path.write_text(output, encoding="utf-8")
        print(f"[confirm_pool] tag stats written to {out_path}")
        return
    print(output)


if __name__ == "__main__":
    main()
