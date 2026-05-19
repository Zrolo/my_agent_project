import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "evals/aichat/validate_real_student_5case_coach_review_cn_v2.py"
SCHEMA_PATH = REPO_ROOT / "docs/research/real_student_online_5case_coach_review_cn_schema_v2.json"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("coach_review_cn_validator", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class CoachReviewCnV2ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator_module()
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.fieldnames = list(self.schema["properties"].keys())
        self.base_row = {field: "" for field in self.fieldnames}
        self.base_row.update(
            {
                "干跑案例编号": "dryrun_20260519_01",
                "候选轮次编号": "rs_screen_20260519_001",
                "试点案例编号": "rs_online_20260519_001",
                "30例候选序号": "1",
                "时间桶": "2026-W19",
                "题目名称/匿名题号": "匿名题目A",
                "题目任务摘要": "学生需要判断一个局部调试输出为何与题目目标不一致。",
                "关键约束/输入输出摘要": "已脱敏，保留足以判断当前卡点的输入输出目标。",
                "当前学生状态摘要": "学生看到输出差异，但还没有定位到是哪一步含义不一致。",
                "是否有完整题目上下文": "是",
                "题目摘要是否足够评分": "足够",
                "是否需要查看完整题面才能评分": "否",
                "题目摘要来源": "教练人工改写",
                "题目/场景摘要": "已脱敏题目摘要",
                "学生问题（已脱敏）": "已脱敏学生问题",
                "近期对话（已脱敏，可空）": "已脱敏近期对话",
                "学生代码片段（已脱敏，可空）": "",
                "当前AIChat回复字段说明": "线上已展示回复，观察项，非实验条件",
                "当前AIChat回复（已脱敏）": "已脱敏AI回复",
                "复核状态": "已复核",
                "隐私复核状态": "可内部复核",
                "上下文是否足够": "足够",
                "识别当前缺失桥是否准确（0/1/2）": "2",
                "回复是否基于当前材料（0/1/2）": "2",
                "脚手架是否合适（0/1/2）": "1",
                "是否控制关键桥泄露（0/1/2）": "1",
                "下一步是否清楚（0/1/2）": "2",
                "是否单焦点连贯（0/1/2）": "2",
                "微例是否围绕桥梁（0/1/2/不适用）": "不适用",
                "微例适用性": "不适用",
                "泄露标签": "轻微关键桥泄露",
                "总体质量（1-5）": "3",
                "是否愿意给学生看": "边界",
                "学生回答负担": "中",
                "复核信心": "中",
                "是否需要讨论": "否",
                "缺失桥家族（中文）": "调试定位桥",
                "当前缺失桥实例（中文简述）": "学生需要先定位输出差异来自哪一步",
                "禁止直接说出的内容（中文）": "不要直接给出完整修复方式",
                "可以提示到什么程度（中文）": "可以让学生比较一次局部状态",
                "期望学生下一步（中文）": "学生能说明下一步应检查的变量",
                "是否匹配现有taxonomy": "是",
                "新桥候选（如无填“无”）": "无",
                "观察到的下一轮进展": "不可用",
                "是否同意AI预标注": "部分同意",
                "是否需要裁决": "否",
                "知情/报告门": "待完成",
                "教练备注（中文）": "可内部复核，暂不公开报告。",
            }
        )

    def validate_rows(self, rows: list[dict[str, str]], expected_rows: int = 5):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "coach_review_cn_v2.csv"
            write_csv(csv_path, rows, self.fieldnames)
            header, loaded = self.validator.read_csv(csv_path)
        return self.validator.validate(loaded, header, self.schema, expected_rows)

    def test_reviewed_chinese_rows_with_50_case_dimensions_are_valid(self):
        rows = []
        for index in range(5):
            row = dict(self.base_row)
            row["干跑案例编号"] = f"dryrun_20260519_{index + 1:02d}"
            row["候选轮次编号"] = f"rs_screen_20260519_{index + 1:03d}"
            row["试点案例编号"] = f"rs_online_20260519_{index + 1:03d}"
            row["30例候选序号"] = str(index + 1)
            rows.append(row)

        result = self.validate_rows(rows)

        self.assertTrue(result["ok"])
        self.assertEqual(result["total_rows"], 5)
        self.assertEqual(result["reviewed_rows_count"], 5)
        self.assertEqual(result["reportable_after_consent_count"], 0)
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["warnings"]), 5)

    def test_invalid_english_label_is_rejected(self):
        rows = []
        for index in range(5):
            row = dict(self.base_row)
            row["干跑案例编号"] = f"dryrun_20260519_{index + 1:02d}"
            row["候选轮次编号"] = f"rs_screen_20260519_{index + 1:03d}"
            rows.append(row)
        rows[0]["泄露标签"] = "minor_bridge_leakage"

        result = self.validate_rows(rows)

        self.assertFalse(result["ok"])
        self.assertTrue(any("泄露标签" in error for error in result["errors"]))

    def test_reviewed_row_requires_bridge_text_when_context_is_available(self):
        row = dict(self.base_row)
        row["当前缺失桥实例（中文简述）"] = ""
        rows = [dict(row, 干跑案例编号=f"dryrun_20260519_{i + 1:02d}", 候选轮次编号=f"rs_{i}") for i in range(5)]

        result = self.validate_rows(rows)

        self.assertFalse(result["ok"])
        self.assertTrue(any("当前缺失桥实例" in error for error in result["errors"]))

    def test_reviewed_row_requires_problem_context_summary_fields(self):
        row = dict(self.base_row)
        row["题目任务摘要"] = ""
        row["题目摘要是否足够评分"] = ""
        rows = [dict(row, 干跑案例编号=f"dryrun_20260519_{i + 1:02d}", 候选轮次编号=f"rs_{i}") for i in range(5)]

        result = self.validate_rows(rows)

        self.assertFalse(result["ok"])
        self.assertTrue(any("题目任务摘要" in error for error in result["errors"]))
        self.assertTrue(any("题目摘要是否足够评分" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
