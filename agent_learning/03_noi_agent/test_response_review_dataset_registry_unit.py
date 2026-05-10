import unittest
from pathlib import Path

import api_server


class ResponseReviewDatasetRegistryTests(unittest.TestCase):
    def test_repair_before_after_dataset_is_registered_as_default(self):
        datasets = {
            str(dataset.get("dataset_id")): dataset
            for dataset in api_server._response_review_dataset_list()
        }

        self.assertEqual("repair_before_after_20260510", api_server.DEFAULT_RESPONSE_REVIEW_DATASET_ID)
        self.assertIn("repair_before_after_20260510", datasets)
        dataset = datasets["repair_before_after_20260510"]
        self.assertTrue(Path(dataset["workbook_csv_path"]).exists())
        self.assertIn("repair_before_after", str(dataset["labels_jsonl_path"]))


if __name__ == "__main__":
    unittest.main()
