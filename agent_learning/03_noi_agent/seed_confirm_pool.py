import argparse
import json
import sqlite3
from pathlib import Path

from database import upsert_confirm_pool_entry


def load_seed_entries(seed_path: Path) -> list[dict]:
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    return data.get("entries") or []


def fetch_problem_row(conn: sqlite3.Connection, luogu_pid: str) -> dict | None:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT problem_id, luogu_pid, title, difficulty
        FROM problems
        WHERE luogu_pid = ?
        LIMIT 1
        """,
        (luogu_pid,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def seed_confirm_pool(seed_path: Path, apply_changes: bool) -> list[dict]:
    conn = sqlite3.connect("noi_agent.db")
    results = []
    for entry in load_seed_entries(seed_path):
        problem = fetch_problem_row(conn, entry["luogu_pid"])
        if not problem:
            results.append(
                {
                    "structure_type": entry["structure_type"],
                    "luogu_pid": entry["luogu_pid"],
                    "status": "missing_problem",
                }
            )
            continue

        results.append(
            {
                "structure_type": entry["structure_type"],
                "luogu_pid": entry["luogu_pid"],
                "status": "ready" if not apply_changes else "seeded",
                "title": problem["title"],
            }
        )
        if not apply_changes:
            continue

        upsert_confirm_pool_entry(
            problem_id=problem["problem_id"],
            problem_url=entry["problem_url"],
            structure_type=entry["structure_type"],
            difficulty=entry.get("difficulty") or problem.get("difficulty"),
            bridge_note=entry["bridge_note"],
            status="usable",
        )

    conn.close()
    return results


def main():
    parser = argparse.ArgumentParser(description="把第一批固定种子题导入 confirm_pool。默认 dry-run，只打印将要导入的结果。")
    parser.add_argument(
        "--seed-file",
        default="docs/subjects/noi/confirm_pool_seed_v1.json",
        help="种子文件路径",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="真正写入数据库；默认只做 dry-run",
    )
    args = parser.parse_args()

    results = seed_confirm_pool(Path(args.seed_file), apply_changes=args.apply)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
