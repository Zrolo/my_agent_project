import json
import sqlite3
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "noi_agent.db"
CASES_PATH = PROJECT_ROOT / "evals" / "review" / "cases.jsonl"
PROMPTFOO_TESTS_PATH = PROJECT_ROOT / "evals" / "review" / "promptfoo_tests.jsonl"

MODE_QUOTAS = {
    "failed_verdict": 6,
    "stuck_bridge": 6,
    "independent_reflect": 6,
    "editorial_transfer": 5,
}


def detect_mode(completion_status: str, submission_result: str | None) -> str:
    submission_result = (submission_result or "unknown").strip().lower()
    if submission_result in {"wa", "tle", "re", "ce"}:
        return "failed_verdict"
    if completion_status == "editorial":
        return "editorial_transfer"
    if completion_status in {"unfinished", "hinted"}:
        return "stuck_bridge"
    return "independent_reflect"


def parse_json_list(raw: str | None) -> list:
    if not raw:
        return []
    try:
        value = json.loads(raw)
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def load_candidate_rows() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT
            c.id,
            c.problem_title,
            c.oj_source,
            c.completion_status,
            c.bottleneck_text,
            c.error_types,
            c.reflection,
            c.problem_context,
            c.submission_result,
            c.student_code,
            c.problem_tags,
            r.main_block,
            r.key_bridge,
            r.next_step,
            r.transfer_signal,
            r.diagnosis,
            r.error_layer
        FROM checkins c
        JOIN reviews r ON r.checkin_id = c.id
        WHERE r.review_status = 'completed'
          AND COALESCE(r.main_block, '') <> ''
          AND COALESCE(r.key_bridge, '') <> ''
          AND COALESCE(r.next_step, '') <> ''
          AND COALESCE(r.transfer_signal, '') <> ''
        ORDER BY c.id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def choose_cases(rows: list[dict]) -> list[dict]:
    picked: list[dict] = []
    seen_signatures: set[tuple] = set()
    counts = defaultdict(int)

    for row in rows:
        mode = detect_mode(row["completion_status"], row["submission_result"])
        if counts[mode] >= MODE_QUOTAS[mode]:
            continue

        signature = (
            mode,
            row["problem_title"],
            (row["bottleneck_text"] or "").strip(),
            row["completion_status"],
            (row["submission_result"] or "unknown").strip().lower(),
        )
        if signature in seen_signatures:
            continue

        input_payload = {
            "problem_title": row["problem_title"],
            "oj_source": row["oj_source"] or "",
            "completion_status": row["completion_status"],
            "bottleneck_text": row["bottleneck_text"],
            "error_types": parse_json_list(row["error_types"]),
            "submission_result": (row["submission_result"] or "unknown").strip().lower(),
        }

        if row.get("reflection"):
            input_payload["reflection"] = row["reflection"]
        if row.get("problem_context"):
            input_payload["problem_context"] = row["problem_context"]

        problem_tags = parse_json_list(row["problem_tags"])
        if problem_tags:
            input_payload["problem_tags"] = problem_tags

        if row.get("student_code"):
            input_payload["student_code"] = row["student_code"]

        case = {
            "id": f"{mode}_{row['id']}",
            "mode": mode,
            "input": input_payload,
            "notes": f"checkin {row['id']} | layer={row['error_layer']} | diagnosis={row['diagnosis'] or ''}",
        }
        picked.append(case)
        seen_signatures.add(signature)
        counts[mode] += 1

        if all(counts[key] >= MODE_QUOTAS[key] for key in MODE_QUOTAS):
            break

    return picked


def write_cases(cases: list[dict]) -> None:
    CASES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CASES_PATH.open("w", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")


def write_promptfoo_tests(cases: list[dict]) -> None:
    with PROMPTFOO_TESTS_PATH.open("w", encoding="utf-8") as f:
        for case in cases:
            if case.get("mode", "").endswith("_low_quality"):
                continue
            record = {
                "description": case["id"],
                "vars": {
                    "case": json.dumps(case, ensure_ascii=False),
                },
                "metadata": {
                    "mode": case["mode"],
                    "notes": case["notes"],
                },
                "assert": [
                    {
                        "type": "is-json",
                        "description": "输出必须是合法 JSON",
                    },
                    {
                        "type": "javascript",
                        "description": "五个引导式复盘字段必须非空",
                        "value": """
const r = JSON.parse(output);
return !!(r.problem_focus && r.key_bridge && r.guided_walkthrough && r.try_now && r.transfer_signal);
""".strip(),
                    },
                    {
                        "type": "llm-rubric",
                        "provider": "openai:chat:kimi-k2.5",
                        "value": """
problem_focus 必须提到题目中具体的对象、条件、错误现象或步骤，不能只写“建模问题”这类分类名。
key_bridge 必须包含具体结构或公式，不能只写“理解XX”。
visual_hint 不能直接给出最终比较结果或完整答案，应该更像半成品提示。
guided_walkthrough 必须是贴当前题对象的 2-3 步微引导，不能只写“画图”“手推”“再想想”，而且 guided_walkthrough 每一步只推进一个动作。
try_now 必须是今天立刻可回答、可验证的一个小动作，try_now 必须直接检查当前桥有没有真的打通，不应该只做表面算数或机械抄写，除非当前桥本身就是规模估算。
transfer_signal 必须说明看到什么题目特征才联想，不能只写题目名。
按以上 6 条，每条 0 或 1 分，输出总分 0-6。
""".strip(),
                        "threshold": 0.75,
                    },
                ],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    rows = load_candidate_rows()
    cases = choose_cases(rows)
    write_cases(cases)
    write_promptfoo_tests(cases)
    counts = defaultdict(int)
    for case in cases:
        counts[case["mode"]] += 1
    print(json.dumps({"total_cases": len(cases), "counts": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
