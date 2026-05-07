import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
import code_runner
from auth import create_token


def auth_headers(student_id: str = "runner_student") -> dict:
    token = create_token(student_id, "student")
    return {"Authorization": f"Bearer {token}"}


class StudentCodeRunnerApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api_server.app)

    def test_runner_health_is_unavailable_without_firejail(self):
        with patch("code_runner.shutil.which") as mocked_which:
            mocked_which.side_effect = lambda name: "/usr/bin/g++" if name == "g++" else None

            response = self.client.get("/api/health/runner")

        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()
        self.assertFalse(payload["available"])
        self.assertIn("暂不支持代码运行", payload["message"])

    def test_runner_rejects_request_when_sandbox_is_unavailable(self):
        with patch("code_runner.shutil.which") as mocked_which:
            mocked_which.side_effect = lambda name: "/usr/bin/g++" if name == "g++" else None

            response = self.client.post(
                "/api/student/code/run",
                headers=auth_headers(),
                json={
                    "language": "cpp17",
                    "code": "#include <iostream>\nint main(){std::cout << 1;}",
                    "stdin": "",
                    "expected_output": "1",
                    "problem_ref": "P1000",
                },
            )

        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()
        self.assertEqual("runner_unavailable", payload["status"])
        self.assertIn("暂不支持代码运行", payload["message"])

    def test_runner_rejects_non_cpp_language(self):
        response = self.client.post(
            "/api/student/code/run",
            headers=auth_headers(),
            json={
                "language": "python",
                "code": "print(1)",
                "stdin": "",
                "expected_output": "1",
                "problem_ref": "P1000",
            },
        )

        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()
        self.assertEqual("invalid_request", payload["status"])
        self.assertIn("目前只支持 C++17", payload["message"])

    def test_runner_uses_firejail_and_compares_expected_output(self):
        commands = []

        def fake_which(name: str):
            return {
                "g++": "/usr/bin/g++",
                "firejail": "/usr/bin/firejail",
            }.get(name)

        def fake_run(command, **kwargs):
            commands.append(command)
            if "g++" in command:
                Path(kwargs["cwd"], "main").write_text("compiled", encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="3\n", stderr="")

        with (
            patch.object(code_runner.platform, "system", return_value="Linux"),
            patch.object(code_runner.shutil, "which", side_effect=fake_which),
            patch.object(code_runner.subprocess, "run", side_effect=fake_run),
        ):
            response = self.client.post(
                "/api/student/code/run",
                headers=auth_headers(),
                json={
                    "language": "cpp17",
                    "code": "#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout << a+b << '\\n';}",
                    "stdin": "1 2\n",
                    "expected_output": "3",
                    "problem_ref": "P1000",
                },
            )

        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual("3\n", payload["stdout"])
        self.assertTrue(payload["matched_expected"])
        self.assertTrue(commands)
        self.assertTrue(all(command[0] == "/usr/bin/firejail" for command in commands))

    def test_runner_endpoint_requires_student_login(self):
        response = self.client.post(
            "/api/student/code/run",
            json={
                "language": "cpp17",
                "code": "int main(){return 0;}",
                "stdin": "",
                "expected_output": "",
                "problem_ref": "P1000",
            },
        )

        self.assertEqual(401, response.status_code)


if __name__ == "__main__":
    unittest.main()
