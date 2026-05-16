import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import validate_heldout_50_dataset
from evals.aichat.coach_labeling_schema_v2 import BRIDGE_SPECIFIC_FORBIDDEN_CONTENT, GENERAL_FORBIDDEN_CONTENT


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _valid_row(case_id: str = "heldout_cp_001", category: str = "dp_state") -> dict:
    return {
        "case_id": case_id,
        "category": category,
        "problem_ref": "draft_problem",
        "problem_source_platform": "luogu",
        "problem_source_id": "P1000",
        "problem_source_url": "https://www.luogu.com.cn/problem/P1000",
        "problem_statement": "给定一个算法竞赛题目，要求根据题目条件设计正确的求解步骤。",
        "problem_statement_public_summary": "真实平台题目的本地改写摘要，用于说明题目目标和必要约束。",
        "problem_statement_rights_note": "本地教练评审可使用必要题面；公开材料仅保留来源链接和改写摘要。",
        "problem_statement_access_level": "public_summary_only",
        "student_message": "我知道大概方向，但不知道当前这一步该怎么判断。",
        "problem_context": "这是一条用于 held-out 草稿的算法竞赛辅导样本。",
        "recent_dialogue": "N/A",
        "student_code_excerpt": "N/A",
        "student_known_state": "学生已经知道大方向，但没有构造当前关键桥。",
        "missing_bridge": "缺把当前已知信息转成可执行的下一步判断。",
        "allowed_help_level": "L2",
        "forbidden_content": ["no_full_solution", "no_direct_current_bridge"],
        "success_criteria": ["回复能让学生先观察局部证据。"],
        "review_notes_for_coach": "检查回复是否过早补完当前桥。",
        "reference_label_status": "draft_needs_coach_review",
    }


class Heldout50DatasetValidatorTests(unittest.TestCase):
    def test_valid_dataset_reports_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            _write_jsonl(
                dataset,
                [
                    _valid_row("heldout_cp_001", "dp_state"),
                    _valid_row("heldout_cp_002", "binary_search_predicate"),
                ],
            )

            result = validate_heldout_50_dataset.validate_dataset(dataset, expected_count=2)

        self.assertTrue(result["ok"])
        self.assertEqual(2, result["row_count"])
        self.assertEqual({"dp_state": 1, "binary_search_predicate": 1}, result["category_counts"])
        self.assertEqual({"luogu": 2}, result["problem_source_platform_counts"])
        self.assertEqual({"public_summary_only": 2}, result["problem_statement_access_level_counts"])
        self.assertEqual([], result["errors"])

    def test_rejects_missing_or_invalid_problem_source_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            row = _valid_row("heldout_cp_001")
            row.pop("problem_source_platform")
            row["problem_source_url"] = "luogu P1000"
            row["problem_statement_access_level"] = "copied_full_statement_public"
            _write_jsonl(dataset, [row])

            result = validate_heldout_50_dataset.validate_dataset(dataset, expected_count=1)

        self.assertFalse(result["ok"])
        error_codes = {error["code"] for error in result["errors"]}
        self.assertIn("missing_required_field", error_codes)
        self.assertIn("invalid_problem_source_url", error_codes)
        self.assertIn("invalid_problem_statement_access_level", error_codes)

    def test_reports_recent_dialogue_distribution_and_enforces_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            no_context = _valid_row("heldout_cp_001")
            no_context["recent_dialogue"] = "N/A"
            short_context = _valid_row("heldout_cp_002")
            short_context["recent_dialogue"] = "student: 我知道大概方向。\nassistant: 先说你卡在哪一步。"
            long_context = _valid_row("heldout_cp_003")
            long_context["recent_dialogue"] = (
                "student: 我知道大概方向。\n"
                "assistant: 先说你卡在哪一步。\n"
                "student: 我卡在状态含义。\n"
                "assistant: 先分清下标和值。"
            )
            _write_jsonl(dataset, [no_context, short_context, long_context])

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=3,
                max_no_recent_dialogue=1,
                min_long_recent_dialogue=1,
            )

        self.assertTrue(result["ok"])
        self.assertEqual(
            {"none": 1, "short": 1, "long": 1},
            result["recent_dialogue_distribution"],
        )

    def test_rejects_recent_dialogue_ending_with_different_student_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            row = _valid_row("heldout_cp_001")
            row["student_message"] = "check 方向怎么定？"
            row["recent_dialogue"] = (
                "学生：这题为什么要二分？\n"
                "AI：先说你最不确定的点。\n"
                "学生：状态到底该记录什么？"
            )
            _write_jsonl(dataset, [row])

            result = validate_heldout_50_dataset.validate_dataset(dataset, expected_count=1)

        self.assertFalse(result["ok"])
        self.assertIn(
            "recent_dialogue_last_student_mismatch",
            {error["code"] for error in result["errors"]},
        )

    def test_reports_code_excerpt_distribution_and_enforces_minimum(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            no_code = _valid_row("heldout_cp_001")
            no_code["student_code_excerpt"] = "N/A"
            with_code = _valid_row("heldout_cp_002")
            with_code["student_code_excerpt"] = "for (int i = 1; i <= n; i++) ans += a[i];"
            _write_jsonl(dataset, [no_code, with_code])

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=2,
                min_code_excerpt=1,
            )

        self.assertTrue(result["ok"])
        self.assertEqual({"none": 1, "present": 1}, result["student_code_excerpt_distribution"])

    def test_reports_student_message_length_distribution_and_enforces_minimums(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            short = _valid_row("heldout_cp_001")
            short["student_message"] = "状态怎么设？"
            medium_short = _valid_row("heldout_cp_002")
            medium_short["student_message"] = "我知道要二分答案，但是 check(mid) 到底返回 true 还是 false 我总写反。"
            medium_long = _valid_row("heldout_cp_003")
            medium_long["student_message"] = (
                "我大概知道要用树上差分，也知道路径两端要打标记，但是到 LCA 的时候到底要加还是减，"
                "我每次都背公式，换一题就忘。尤其是多条路径叠加时，我不知道每个点统计到的值到底代表什么。"
            )
            long = _valid_row("heldout_cp_004")
            long["student_message"] = (
                "我写了一个线段树区间加区间求和的代码，pushdown 里面先把 lazy 下传到左右儿子，"
                "然后清空当前节点。我能照模板写出来，但我不理解为什么查询只查到一部分区间时必须先 pushdown。"
                "如果不下传，我感觉父节点 sum 已经是对的，为什么子节点会影响答案？"
                "另外我还想知道，如果连续做两次区间加，lazy 标记到底是覆盖还是累加，什么时候才真的把这些变化写到叶子节点上。"
            )
            _write_jsonl(dataset, [short, medium_short, medium_long, long])

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=4,
                min_student_message_length_buckets={
                    "short": 1,
                    "medium_short": 1,
                    "medium_long": 1,
                    "long": 1,
                },
            )

        self.assertTrue(result["ok"])
        self.assertEqual(
            {"short": 1, "medium_short": 1, "medium_long": 1, "long": 1},
            result["student_message_length_distribution"],
        )

    def test_rejects_missing_problem_statement_and_length_bucket_shortfall(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            row = _valid_row("heldout_cp_001")
            row.pop("problem_statement")
            _write_jsonl(dataset, [row])

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=1,
                min_student_message_length_buckets={"long": 1},
            )

        self.assertFalse(result["ok"])
        error_codes = {error["code"] for error in result["errors"]}
        self.assertIn("missing_required_field", error_codes)
        self.assertIn("too_few_student_message_length_bucket", error_codes)

    def test_rejects_too_few_code_excerpts(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            _write_jsonl(dataset, [_valid_row("heldout_cp_001"), _valid_row("heldout_cp_002")])

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=2,
                min_code_excerpt=1,
            )

        self.assertFalse(result["ok"])
        self.assertIn("too_few_code_excerpts", {error["code"] for error in result["errors"]})

    def test_rejects_too_many_na_and_too_few_long_contexts(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            _write_jsonl(
                dataset,
                [
                    _valid_row("heldout_cp_001"),
                    _valid_row("heldout_cp_002"),
                    _valid_row("heldout_cp_003"),
                ],
            )

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=3,
                max_no_recent_dialogue=1,
                min_long_recent_dialogue=1,
            )

        self.assertFalse(result["ok"])
        error_codes = {error["code"] for error in result["errors"]}
        self.assertIn("too_many_no_recent_dialogue", error_codes)
        self.assertIn("too_few_long_recent_dialogue", error_codes)

    def test_rejects_missing_fields_dev_overlap_and_gold_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            dev = Path(tmp) / "dev.jsonl"
            bad_missing = _valid_row("heldout_cp_002", "dp_state")
            bad_missing.pop("success_criteria")
            bad_gold = _valid_row("heldout_cp_003", "greedy_correctness")
            bad_gold["reference_label_status"] = "adjudicated_gold"
            _write_jsonl(
                dataset,
                [
                    _valid_row("cp_bridge_001", "dp_state"),
                    bad_missing,
                    bad_gold,
                ],
            )
            _write_jsonl(dev, [{"id": "cp_bridge_001"}])

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=3,
                dev_seed_paths=[dev],
            )

        self.assertFalse(result["ok"])
        error_codes = {error["code"] for error in result["errors"]}
        self.assertIn("case_id_overlaps_dev_seed", error_codes)
        self.assertIn("missing_required_field", error_codes)
        self.assertIn("gold_status_not_allowed", error_codes)

    def test_reviewed_candidate_is_allowed_before_formal_frozen_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            reviewed = _valid_row("heldout_cp_001", "dp_state")
            reviewed["reference_label_status"] = "reviewed_candidate"
            _write_jsonl(dataset, [reviewed])

            result = validate_heldout_50_dataset.validate_dataset(dataset, expected_count=1)

        self.assertTrue(result["ok"], result["errors"])

    def test_formal_preflight_requires_frozen_reference_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            draft = _valid_row("heldout_cp_001", "dp_state")
            frozen = _valid_row("heldout_cp_002", "greedy_correctness")
            frozen["reference_label_status"] = "adjudicated_reference"
            _write_jsonl(dataset, [draft, frozen])

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=2,
                require_frozen_status=True,
            )

        self.assertFalse(result["ok"])
        self.assertTrue(result["require_frozen_status"])
        self.assertEqual(
            [
                {
                    "code": "frozen_status_required",
                    "line_number": 1,
                    "case_id": "heldout_cp_001",
                    "reference_label_status": "draft_needs_coach_review",
                }
            ],
            [error for error in result["errors"] if error["code"] == "frozen_status_required"],
        )

    def test_formal_preflight_accepts_frozen_reference_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "heldout.jsonl"
            adjudicated = _valid_row("heldout_cp_001", "dp_state")
            adjudicated["reference_label_status"] = "adjudicated_reference"
            coach_reference = _valid_row("heldout_cp_002", "binary_search_predicate")
            coach_reference["reference_label_status"] = "coach_reference"
            _write_jsonl(dataset, [adjudicated, coach_reference])

            result = validate_heldout_50_dataset.validate_dataset(
                dataset,
                expected_count=2,
                require_frozen_status=True,
            )

        self.assertTrue(result["ok"])
        self.assertTrue(result["require_frozen_status"])

    def test_real_draft_forbidden_content_uses_canonical_abstract_labels(self):
        allowed = set(GENERAL_FORBIDDEN_CONTENT) | set(BRIDGE_SPECIFIC_FORBIDDEN_CONTENT)
        dataset = Path("docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl")
        unexpected = []
        for line in dataset.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            for value in row.get("forbidden_content") or []:
                if value not in allowed:
                    unexpected.append((row.get("case_id"), value))

        self.assertEqual([], unexpected)


if __name__ == "__main__":
    unittest.main()
