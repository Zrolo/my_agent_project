import os
import tempfile
import unittest

from fastapi.testclient import TestClient

import api_server
import auth


class TeacherStudentBulkTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_accounts_file = auth.ACCOUNTS_FILE
        auth.ACCOUNTS_FILE = os.path.join(self.temp_dir.name, "accounts.json")
        auth.tokens.clear()
        api_server.app.dependency_overrides.clear()
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "teacher_test", "role": "teacher"}
        )
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        auth.ACCOUNTS_FILE = self.original_accounts_file
        self.temp_dir.cleanup()

    def test_bulk_create_students_returns_success_and_failed_rows_with_chinese_reasons(self):
        response = self.client.post(
            "/api/teacher/students/bulk",
            json={
                "rows": [
                    {"display_name": "张三", "user_id": "stu001", "password": "pass123"},
                    {"display_name": "", "user_id": "stu002", "password": "pass123"},
                    {"display_name": "重复账号", "user_id": "stu001", "password": "pass456"},
                ]
            },
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual(1, len(payload["success_rows"]))
        self.assertEqual("stu001", payload["success_rows"][0]["student"]["user_id"])
        self.assertEqual(2, len(payload["failed_rows"]))
        self.assertEqual("missing_display_name", payload["failed_rows"][0]["error_code"])
        self.assertIn("显示姓名", payload["failed_rows"][0]["error_message"])
        self.assertEqual("duplicate_user_id", payload["failed_rows"][1]["error_code"])
        self.assertIn("已经存在", payload["failed_rows"][1]["error_message"])


if __name__ == "__main__":
    unittest.main()
