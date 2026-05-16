import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from evals.aichat import export_real_log_candidates_from_review as exporter


HEADERS = [
    "审查状态",
    "可公开展示",
    "隐私风险",
    "旧AI上下文污染确认",
    "是否自包含",
    "是否需要补充题面/代码上下文",
    "是否近重复样本",
    "是否代表真实卡点",
    "是否适合主评测",
    "删除旧AI后是否可理解",
    "建议split",
    "需重点复判",
    "候选ID",
    "类别",
    "题号/URL",
    "题目标题",
    "创建时间",
    "含题面",
    "含代码标记",
    "会话消息数",
    "完整近期对话（目标turn前，供污染/自包含判断）",
    "目标turn前最近AI回复（上下文，不评分）",
    "学生当前问题",
    "目标turn后旧系统回复（baseline观察，非上下文，非gold）",
    "missing_bridge（教练填）",
    "forbidden_content（教练填）",
    "success_criteria（教练填）",
    "教练备注",
]


def _write_workbook(path: Path, data_rows: list[list[str]]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "候选样本_v2"
    sheet.append(HEADERS)
    for row in data_rows:
        sheet.append(row)
    workbook.save(path)


V3_HEADERS = [
    "审查状态",
    "可公开展示",
    "隐私风险",
    "删除旧AI后是否可理解",
    "是否自包含",
    "是否需要补充题面/代码上下文",
    "是否近重复样本",
    "是否代表真实卡点",
    "是否适合主评测",
    "建议split",
    "需重点复判",
    "候选ID",
    "类别",
    "题号/URL",
    "题目标题",
    "创建时间",
    "含题面",
    "含代码标记",
    "会话消息数",
    "学生当前问题（主消融输入）",
    "目标turn前旧AI上下文（只供审计，不给模型）",
    "完整近期对话（只供审计，不给模型）",
    "目标turn后旧系统回复（baseline观察，非上下文，非gold）",
    "旧AI上下文污染初筛",
    "missing_bridge（教练填）",
    "forbidden_content（教练填）",
    "success_criteria（教练填）",
    "教练备注",
]


def _write_v3_workbook(path: Path, data_rows: list[list[str]]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "student_only候选_v3"
    sheet.append(V3_HEADERS)
    for row in data_rows:
        sheet.append(row)
    workbook.save(path)


class RealLogCandidateReviewExportTests(unittest.TestCase):
    def test_export_keeps_only_main_review_rows_and_maps_old_ai_as_observation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "review.xlsx"
            output_path = Path(tmpdir) / "real_log_candidates.jsonl"
            _write_workbook(
                input_path,
                [
                    [
                        "保留主评测",
                        "no",
                        "none",
                        "low",
                        "yes",
                        "no",
                        "no",
                        "yes",
                        "yes",
                        "yes",
                        "heldout_real_candidate",
                        "no",
                        "real_aichat_001",
                        "binary_search_check",
                        "P2678",
                        "跳石头",
                        "2026-05-12 10:00:00",
                        "True",
                        "False",
                        "4",
                        "[旧AI] 先想 check 的方向。",
                        "先想 check 的方向。",
                        "这题为什么要二分？",
                        "旧系统长回复，不当 gold。",
                        "学生缺少答案二分中 check(mid) 单调谓词的方向理解",
                        "不要直接给完整 check 条件和边界更新模板",
                        "让学生先判断一个 mid 是否可行，并说明理由",
                        "可用，但不要公开展示旧回复原文。",
                    ],
                    [
                        "转dev/regression",
                        "no",
                        "minor",
                        "medium",
                        "uncertain",
                        "yes",
                        "no",
                        "yes",
                        "no",
                        "yes",
                        "dev_regression",
                        "yes",
                        "real_aichat_002",
                        "dp_state_transition",
                        "P0000",
                        "DP 题",
                        "2026-05-12 10:05:00",
                        "True",
                        "False",
                        "8",
                        "",
                        "",
                        "状态怎么设？",
                        "旧系统回复。",
                        "状态语义",
                        "不要直接给状态定义",
                        "让学生列出状态需要记录的信息",
                        "只做 dev。",
                    ],
                ],
            )

            count = exporter.export_review_workbook_to_jsonl(input_path, output_path)
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(1, count)
        self.assertEqual("real_aichat_001", rows[0]["case_id"])
        self.assertEqual("online_real_aichat_log", rows[0]["source"])
        self.assertEqual("heldout_real_candidate", rows[0]["recommended_split"])
        self.assertEqual("旧系统长回复，不当 gold。", rows[0]["observed_current_system_response"])
        self.assertEqual("observed_current_system_response_only_not_gold", rows[0]["old_assistant_reply_use"])
        self.assertTrue(rows[0]["legacy_context_removed"])
        self.assertEqual("", rows[0]["generation_input"]["recent_dialogue"])
        self.assertEqual("这题为什么要二分？", rows[0]["generation_input"]["student_message"])
        self.assertEqual("low", rows[0]["legacy_ai_context_contamination"])
        self.assertEqual(
            "学生缺少答案二分中 check(mid) 单调谓词的方向理解",
            rows[0]["coach_label"]["missing_bridge"],
        )

    def test_export_rejects_incomplete_main_rows_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "review.xlsx"
            output_path = Path(tmpdir) / "real_log_candidates.jsonl"
            row = [
                "保留主评测",
                "uncertain",
                "needs_manual_review",
                "none",
                "yes",
                "no",
                "no",
                "yes",
                "yes",
                "no",
                "heldout_real_candidate",
                "no",
                "real_aichat_missing",
                "implementation_boundary",
                "P1000",
                "实现题",
                "2026-05-12 11:00:00",
                "True",
                "True",
                "6",
                "",
                "",
                "我的代码哪里错了？",
                "旧系统回复。",
                "",
                "不要直接给替换代码",
                "让学生先定位一个最小错误现象",
                "",
            ]
            _write_workbook(input_path, [row])

            with self.assertRaisesRegex(ValueError, "missing required coach fields"):
                exporter.export_review_workbook_to_jsonl(input_path, output_path)

    def test_export_rejects_accepted_rows_that_are_not_clean_student_only_cases(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "student_only_review.xlsx"
            output_path = Path(tmpdir) / "real_log_candidates.jsonl"
            _write_v3_workbook(
                input_path,
                [
                    [
                        "保留主评测",
                        "no",
                        "none",
                        "yes",
                        "uncertain",
                        "yes",
                        "yes",
                        "yes",
                        "yes",
                        "heldout_real_candidate",
                        "yes",
                        "real_aichat_unclean",
                        "graph_tree_modeling",
                        "P0001",
                        "树题",
                        "2026-05-12 12:00:00",
                        "True",
                        "False",
                        "8",
                        "这一步为什么要这样标记？",
                        "旧AI已经讲过一部分 LCA 标记。",
                        "学生：这里不懂。\nAI：旧回复。",
                        "旧系统回复。",
                        "medium",
                        "学生缺少树上路径贡献标记的语义",
                        "不要直接给端点/LCA 完整加减规则",
                        "让学生先判断一条路径的贡献该落在哪些节点",
                        "还不能进主评测。",
                    ]
                ],
            )

            with self.assertRaisesRegex(ValueError, "real_aichat_unclean"):
                exporter.export_review_workbook_to_jsonl(input_path, output_path)
            with self.assertRaisesRegex(ValueError, "legacy_ai_context_contamination must be none or low"):
                exporter.export_review_workbook_to_jsonl(input_path, output_path)

    def test_screen_report_collects_rejection_reasons_without_exporting_bad_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "student_only_review.xlsx"
            _write_v3_workbook(
                input_path,
                [
                    [
                        "保留主评测",
                        "no",
                        "none",
                        "yes",
                        "yes",
                        "no",
                        "no",
                        "yes",
                        "yes",
                        "heldout_real_candidate",
                        "no",
                        "real_aichat_clean",
                        "binary_search_check",
                        "P2678",
                        "跳石头",
                        "2026-05-12 12:00:00",
                        "True",
                        "False",
                        "5",
                        "check(mid) 到底返回 true 还是 false？",
                        "",
                        "",
                        "旧系统回复。",
                        "none",
                        "学生缺少 check(mid) 谓词方向语义",
                        "不要直接给完整 check 条件",
                        "让学生先判断一个 mid 的可行性并说明理由",
                        "可进入主评测。",
                    ],
                    [
                        "保留主评测",
                        "no",
                        "minor",
                        "yes",
                        "yes",
                        "no",
                        "no",
                        "yes",
                        "yes",
                        "heldout_real_candidate",
                        "no",
                        "real_aichat_privacy",
                        "implementation_boundary",
                        "P1000",
                        "实现题",
                        "2026-05-12 12:10:00",
                        "True",
                        "True",
                        "4",
                        "这是我的代码，哪里错了？",
                        "",
                        "",
                        "旧系统回复。",
                        "none",
                        "学生缺少最小错误现象定位",
                        "不要直接给替换代码",
                        "让学生先描述输入输出差异",
                        "隐私还没完全清。",
                    ],
                ],
            )

            report = exporter.screen_review_workbook(input_path)

        self.assertEqual(2, report["accepted_rows"])
        self.assertEqual(1, report["exportable_rows"])
        self.assertEqual(1, report["rejected_rows"])
        rejected = report["rows"][1]
        self.assertEqual("real_aichat_privacy", rejected["case_id"])
        self.assertIn("privacy_risk must be none", rejected["reasons"])

    def test_export_supports_v3_student_only_workbook_without_old_ai_context(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "student_only_review.xlsx"
            output_path = Path(tmpdir) / "real_log_candidates.jsonl"
            _write_v3_workbook(
                input_path,
                [
                    [
                        "保留主评测",
                        "no",
                        "none",
                        "yes",
                        "yes",
                        "no",
                        "no",
                        "yes",
                        "yes",
                        "heldout_real_candidate",
                        "no",
                        "real_aichat_v3_001",
                        "segment_tree_lazy",
                        "P3372",
                        "线段树 1",
                        "2026-05-12 12:00:00",
                        "True",
                        "False",
                        "6",
                        "lazy 到底表示还没做什么？",
                        "旧AI上一轮讲过 pushdown，但不要给模型。",
                        "学生：线段树区间加我会写一点。\nAI：先想 lazy。",
                        "旧系统把 lazy 完整语义说出来了。",
                        "low",
                        "学生缺少 lazy 标记表示未下传增量的语义",
                        "不要直接给完整 lazy 语义或 pushdown 模板",
                        "让学生先判断父节点打标记后子节点是否已经更新",
                        "适合作为学生-only 主评测。",
                    ]
                ],
            )

            count = exporter.export_review_workbook_to_jsonl(input_path, output_path)
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(1, count)
        self.assertEqual("real_aichat_v3_001", rows[0]["case_id"])
        self.assertEqual("lazy 到底表示还没做什么？", rows[0]["student_message"])
        self.assertEqual("", rows[0]["generation_input"]["recent_dialogue"])
        self.assertEqual("", rows[0]["generation_input"]["context_ai_reply"])
        self.assertEqual("", rows[0]["recent_dialogue"])
        self.assertEqual("", rows[0]["context_ai_reply"])
        self.assertTrue(rows[0]["legacy_context_removed"])
        self.assertEqual(
            "学生：线段树区间加我会写一点。\nAI：先想 lazy。",
            rows[0]["audit_context"]["recent_dialogue_before_target_turn"],
        )
        self.assertEqual(
            "旧AI上一轮讲过 pushdown，但不要给模型。",
            rows[0]["audit_context"]["context_ai_reply_before_target_turn"],
        )
        self.assertEqual("low", rows[0]["legacy_ai_context_contamination"])


if __name__ == "__main__":
    unittest.main()
