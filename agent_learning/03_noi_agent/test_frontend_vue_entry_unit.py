import unittest

from fastapi.testclient import TestClient

import api_server


class FrontendVueEntryTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api_server.app)

    def test_workspace_chat_path_serves_frontend_entry_without_redirect(self):
        response = self.client.get("/app/workspace/chat", follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn('id="app"', response.text)

    def test_archive_detail_path_serves_frontend_entry_without_redirect(self):
        response = self.client.get("/app/archive/123", follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn('id="app"', response.text)

    def test_teacher_overview_path_serves_frontend_entry_without_redirect(self):
        response = self.client.get("/app/teacher/overview", follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn('id="app"', response.text)

    def test_unknown_app_path_redirects_to_frontend_home(self):
        response = self.client.get("/app/not-a-real-section", follow_redirects=False)
        self.assertEqual(307, response.status_code)
        self.assertEqual("/app", response.headers["location"])
