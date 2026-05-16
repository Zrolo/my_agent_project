import json
import os
import tempfile
import time
import unittest

from fastapi.testclient import TestClient

import api_server
import auth


class TeacherChangePasswordTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_accounts_file = auth.ACCOUNTS_FILE
        auth.ACCOUNTS_FILE = os.path.join(self.temp_dir.name, "accounts.json")
        auth.tokens.clear()
        api_server.app.dependency_overrides.clear()
        self._write_account("teacher_test", "teacher", "old-pass-123")
        self.teacher_token = auth.create_token("teacher_test", "teacher")
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        auth.tokens.clear()
        auth.ACCOUNTS_FILE = self.original_accounts_file
        self.temp_dir.cleanup()

    def _write_account(self, user_id: str, role: str, password: str):
        salt = "salt-" + user_id
        now = str(int(time.time()))
        with open(auth.ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    user_id: {
                        "id": user_id,
                        "display_name": user_id,
                        "password_hash": auth.hash_password(password, salt),
                        "salt": salt,
                        "role": role,
                        "active": True,
                        "created_at": now,
                        "updated_at": now,
                    }
                },
                f,
                ensure_ascii=False,
            )

    def _post_change(self, payload, token=None):
        return self.client.post(
            "/api/teacher/change-password",
            json=payload,
            headers={"Authorization": f"Bearer {token or self.teacher_token}"},
        )

    def test_teacher_can_change_own_password_to_explicit_new_password(self):
        response = self._post_change(
            {
                "current_password": "old-pass-123",
                "new_password": "new-pass-456",
                "confirm_password": "new-pass-456",
            }
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertNotIn("password", payload)
        self.assertIsNone(auth.authenticate_user("teacher_test", "old-pass-123"))
        self.assertEqual(
            {"id": "teacher_test", "role": "teacher"},
            auth.authenticate_user("teacher_test", "new-pass-456"),
        )

    def test_wrong_current_password_does_not_change_password(self):
        response = self._post_change(
            {
                "current_password": "wrong-pass",
                "new_password": "new-pass-456",
                "confirm_password": "new-pass-456",
            }
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("当前密码", response.json()["detail"]["message"])
        self.assertEqual(
            {"id": "teacher_test", "role": "teacher"},
            auth.authenticate_user("teacher_test", "old-pass-123"),
        )
        self.assertIsNone(auth.authenticate_user("teacher_test", "new-pass-456"))

    def test_password_confirmation_must_match(self):
        response = self._post_change(
            {
                "current_password": "old-pass-123",
                "new_password": "new-pass-456",
                "confirm_password": "different-pass",
            }
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("两次输入", response.json()["detail"]["message"])

    def test_student_token_cannot_change_teacher_password(self):
        self._write_account("student_test", "student", "student-pass")
        student_token = auth.create_token("student_test", "student")

        response = self._post_change(
            {
                "current_password": "student-pass",
                "new_password": "student-new-pass",
                "confirm_password": "student-new-pass",
            },
            token=student_token,
        )

        self.assertEqual(403, response.status_code)


if __name__ == "__main__":
    unittest.main()
