import json
import io
import tempfile
import unittest
from pathlib import Path

from evals.aichat import run_chat_batch


class AIChatBatchRunnerTests(unittest.TestCase):
    def test_build_messages_from_case_should_keep_prior_messages_and_append_contextual_user_turn(self):
        case = {
            "id": "case_1",
            "problem_ref": "P3128",
            "student_message": "这题是不是树上差分？",
            "problem_context": "树上多条路径计数。",
            "prior_messages": [
                {"role": "user", "content": "我不知道怎么统计路径。"},
                {"role": "assistant", "content": "先看一条路径影响哪些点。"},
            ],
        }

        messages = run_chat_batch.build_messages_from_case(case)

        self.assertEqual("我不知道怎么统计路径。", messages[0]["content"])
        self.assertEqual("assistant", messages[1]["role"])
        self.assertEqual("user", messages[2]["role"])
        self.assertIn("[学生原始问题]", messages[2]["content"])
        self.assertIn("这题是不是树上差分？", messages[2]["content"])
        self.assertIn("题目编号/链接: P3128", messages[2]["content"])
        self.assertIn("题面/题意/约束: 树上多条路径计数。", messages[2]["content"])

    def test_generate_response_rows_should_call_chat_and_keep_case_metadata(self):
        cases_data = {
            "cases": [
                {
                    "id": "case_1",
                    "problem_ref": "P3128",
                    "student_message": "这题是不是树上差分？",
                    "problem_context": "树上多条路径计数。",
                    "prior_messages": [],
                }
            ]
        }
        calls = []

        def fake_chat(messages, student_id, problem_id):
            calls.append((messages, student_id, problem_id))
            return "展示回复", "历史回复", "L2"

        rows = run_chat_batch.generate_response_rows(cases_data, chat_fn=fake_chat, student_id="eval_student")

        self.assertEqual(1, len(rows))
        self.assertEqual("case_1", rows[0]["case_id"])
        self.assertEqual("展示回复", rows[0]["response_text"])
        self.assertEqual("历史回复", rows[0]["history_text"])
        self.assertEqual("L2", rows[0]["level"])
        self.assertEqual("eval_student", calls[0][1])
        self.assertEqual("P3128::case_1", calls[0][2])

    def test_write_response_rows_should_emit_jsonl(self):
        rows = [
            {
                "case_id": "case_1",
                "problem_ref": "P3128",
                "response_text": "回复",
                "history_text": "回复",
                "level": "L2",
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "responses.jsonl"

            run_chat_batch.write_response_rows(output_path, rows)

            loaded = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(rows, loaded)

    def test_generate_response_rows_should_write_progress_when_stream_is_provided(self):
        cases_data = {
            "cases": [
                {
                    "id": "case_1",
                    "problem_ref": "P3128",
                    "student_message": "卡住了",
                    "problem_context": "",
                    "prior_messages": [],
                }
            ]
        }
        progress = io.StringIO()

        run_chat_batch.generate_response_rows(
            cases_data,
            chat_fn=lambda messages, student_id, problem_id: ("回复", "回复", "L2"),
            progress_stream=progress,
        )

        log = progress.getvalue()
        self.assertIn("CASE_START index=1 total=1 case_id=case_1", log)
        self.assertIn("CASE_DONE index=1 total=1 case_id=case_1 level=L2", log)


if __name__ == "__main__":
    unittest.main()
