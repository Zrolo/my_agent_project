import csv
import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import api_server
from evals.aichat.export_coach_response_review_workbook import REVIEW_COLUMNS


class TeacherResponseReviewApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_workbook = getattr(api_server, "RESPONSE_REVIEW_WORKBOOK_CSV_PATH", None)
        self.original_labels = getattr(api_server, "RESPONSE_REVIEW_LABELS_JSONL_PATH", None)
        self.original_datasets = getattr(api_server, "RESPONSE_REVIEW_DATASETS", None)
        self.original_default_dataset = getattr(api_server, "DEFAULT_RESPONSE_REVIEW_DATASET_ID", None)
        self.workbook_path = Path(self.temp_dir.name) / "response_review.csv"
        self.labels_path = Path(self.temp_dir.name) / "response_review_labels.jsonl"
        self.micro_workbook_path = Path(self.temp_dir.name) / "response_review_micro.csv"
        self.micro_labels_path = Path(self.temp_dir.name) / "response_review_micro_labels.jsonl"
        api_server.RESPONSE_REVIEW_WORKBOOK_CSV_PATH = self.workbook_path
        api_server.RESPONSE_REVIEW_LABELS_JSONL_PATH = self.labels_path
        api_server.DEFAULT_RESPONSE_REVIEW_DATASET_ID = "baseline"
        api_server.RESPONSE_REVIEW_DATASETS = [
            {
                "dataset_id": "baseline",
                "label": "基线批次",
                "description": "旧 prompt 对照",
                "workbook_csv_path": self.workbook_path,
                "labels_jsonl_path": self.labels_path,
            },
            {
                "dataset_id": "micro",
                "label": "桥梁导向微型例子",
                "description": "新 prompt 批次",
                "workbook_csv_path": self.micro_workbook_path,
                "labels_jsonl_path": self.micro_labels_path,
            },
        ]
        api_server.app.dependency_overrides.clear()
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "coach_001", "role": "teacher"}
        )
        self.client = TestClient(api_server.app)
        with self.workbook_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerow(
                {
                    "case_id": "cp_bridge_001",
                    "anonymized_response_id": "resp_001",
                    "problem_ref": "P3128",
                    "student_message": "我知道要 LCA，但不知道每条路径在哪里加减标记。",
                    "problem_context": "树上路径统计。",
                    "recent_dialogue": "学生：我知道 LCA。",
                    "response_text": "先看一条路径对端点和 LCA 的贡献。",
                    "review_status": "unlabeled",
                }
            )
        with self.micro_workbook_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerow(
                {
                    "case_id": "cp_bridge_002",
                    "anonymized_response_id": "resp_micro_001",
                    "problem_ref": "P1182",
                    "student_message": "check(mid) 到底返回 true 还是 false？",
                    "problem_context": "二分答案。",
                    "recent_dialogue": "N/A",
                    "response_text": "先看 mid 的含义，再判断可行性方向。",
                    "review_status": "unlabeled",
                }
            )

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        if self.original_workbook is None:
            delattr(api_server, "RESPONSE_REVIEW_WORKBOOK_CSV_PATH")
        else:
            api_server.RESPONSE_REVIEW_WORKBOOK_CSV_PATH = self.original_workbook
        if self.original_labels is None:
            delattr(api_server, "RESPONSE_REVIEW_LABELS_JSONL_PATH")
        else:
            api_server.RESPONSE_REVIEW_LABELS_JSONL_PATH = self.original_labels
        if self.original_datasets is None:
            delattr(api_server, "RESPONSE_REVIEW_DATASETS")
        else:
            api_server.RESPONSE_REVIEW_DATASETS = self.original_datasets
        if self.original_default_dataset is None:
            delattr(api_server, "DEFAULT_RESPONSE_REVIEW_DATASET_ID")
        else:
            api_server.DEFAULT_RESPONSE_REVIEW_DATASET_ID = self.original_default_dataset
        self.temp_dir.cleanup()

    def test_teacher_can_list_response_review_items_from_workbook_csv(self):
        response = self.client.get("/api/teacher/research/response-review-items")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual(1, payload["total"])
        item = payload["items"][0]
        self.assertEqual("resp_001", item["anonymized_response_id"])
        self.assertEqual("cp_bridge_001", item["case_id"])
        self.assertIn("LCA", item["student_message"])
        self.assertEqual("unlabeled", item["review_status"])
        self.assertEqual("", item["overall_quality"])

    def test_teacher_can_list_response_review_datasets_and_load_selected_dataset(self):
        datasets_response = self.client.get("/api/teacher/research/response-review-datasets")
        self.assertEqual(200, datasets_response.status_code)
        payload = datasets_response.json()
        self.assertEqual("baseline", payload["default_dataset_id"])
        self.assertEqual(["baseline", "micro"], [item["dataset_id"] for item in payload["datasets"]])

        response = self.client.get("/api/teacher/research/response-review-items?dataset_id=micro")
        self.assertEqual(200, response.status_code)
        item = response.json()["items"][0]
        self.assertEqual("resp_micro_001", item["anonymized_response_id"])
        self.assertEqual("micro", item["dataset_id"])
        self.assertIn("check", item["student_message"])

    def test_teacher_can_save_quick_response_review_and_export_csv(self):
        save_response = self.client.post(
            "/api/teacher/research/response-review-labels",
            json={
                "anonymized_response_id": "resp_001",
                "case_id": "cp_bridge_001",
                "dataset_id": "baseline",
                "overall_quality": "good",
                "leakage_label": "no_leakage",
                "preference_rank": "1",
                "notes": "方向合适，没说穿公式。",
                "review_status": "labeled",
            },
        )
        self.assertEqual(200, save_response.status_code)
        self.assertTrue(save_response.json()["label"]["saved"])

        list_response = self.client.get("/api/teacher/research/response-review-items")
        item = list_response.json()["items"][0]
        self.assertEqual("good", item["overall_quality"])
        self.assertEqual("no_leakage", item["leakage_label"])
        self.assertEqual("labeled", item["review_status"])

        export_response = self.client.get("/api/teacher/research/response-review-labels/export?format=csv")
        self.assertEqual(200, export_response.status_code)
        self.assertIn("text/csv", export_response.headers["content-type"])
        self.assertIn("anonymized_response_id,case_id,overall_quality", export_response.text)
        self.assertIn("resp_001,cp_bridge_001,good,no_leakage", export_response.text)

        lines = [line for line in self.labels_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(1, len(lines))
        self.assertEqual("coach_001", json.loads(lines[0])["annotator_id"])

    def test_teacher_saves_labels_to_selected_dataset_file(self):
        save_response = self.client.post(
            "/api/teacher/research/response-review-labels",
            json={
                "dataset_id": "micro",
                "anonymized_response_id": "resp_micro_001",
                "case_id": "cp_bridge_002",
                "overall_quality": "okay",
                "leakage_label": "minor_bridge_leakage",
                "review_status": "labeled",
            },
        )

        self.assertEqual(200, save_response.status_code)
        self.assertFalse(self.labels_path.exists())
        lines = [line for line in self.micro_labels_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(1, len(lines))
        saved = json.loads(lines[0])
        self.assertEqual("micro", saved["dataset_id"])
        self.assertEqual("resp_micro_001", saved["anonymized_response_id"])


if __name__ == "__main__":
    unittest.main()
