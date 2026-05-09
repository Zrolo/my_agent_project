import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import review_engine


def run(case: dict) -> dict:
    inp = case["input"]
    forced_mode = os.getenv("REVIEW_EVAL_FORCE_MODE", "").strip()

    call_kwargs = dict(
        problem_title=inp["problem_title"],
        oj_source=inp.get("oj_source", ""),
        completion_status=inp["completion_status"],
        bottleneck_text=inp["bottleneck_text"],
        error_types=inp.get("error_types", []),
        reflection=inp.get("reflection"),
        problem_context=inp.get("problem_context"),
        problem_tags=inp.get("problem_tags"),
        student_code=inp.get("student_code"),
        submission_result=inp.get("submission_result"),
    )

    if forced_mode:
        with patch.object(review_engine, "_detect_review_mode", return_value=forced_mode):
            result = review_engine.generate_review(**call_kwargs)
    else:
        result = review_engine.generate_review(**call_kwargs)

    if not result["ok"]:
        return {"error": result["message"]}
    return result["review"]


if __name__ == "__main__":
    case = json.loads(sys.stdin.read())
    print(json.dumps(run(case), ensure_ascii=False))
