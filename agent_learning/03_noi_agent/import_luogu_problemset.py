#!/usr/bin/env python3
"""
Import Luogu latest.ndjson into the local NOI coach database.

Usage:
    python3 import_luogu_problemset.py /path/to/latest.ndjson
"""

from __future__ import annotations

import sys
from pathlib import Path

from database import init_db
from problem_bank import import_problemset_file


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 import_luogu_problemset.py /path/to/latest.ndjson")
        return 1

    ndjson_path = Path(sys.argv[1]).expanduser()
    if not ndjson_path.exists():
        print(f"[problem_import] file not found: {ndjson_path}")
        return 1

    init_db()
    summary = import_problemset_file(ndjson_path)
    print(f"[problem_import] import completed: {summary['imported']} problems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
