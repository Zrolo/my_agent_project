import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import merge_ablation_reruns


class MergeAblationRerunsTests(unittest.TestCase):
    def test_merge_replaces_empty_source_pair_with_successful_retry_row(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "source"
            retry_dir = root / "retry"
            output_dir = root / "merged"
            source_dir.mkdir()
            retry_dir.mkdir()
            source_combined = source_dir / "combined.jsonl"
            source_manifest = source_dir / "manifest.json"
            retry_combined = retry_dir / "combined.jsonl"
            retry_manifest = retry_dir / "manifest.json"
            source_rows = [
                {
                    "case_id": "case_1",
                    "condition_id": "enhanced_prompt_only_clean",
                    "final_response_text": "ok",
                    "stage_errors": {},
                },
                {
                    "case_id": "case_1",
                    "condition_id": "dbox_inspired_guard",
                    "final_response_text": "",
                    "stage_errors": {"case": "timeout"},
                },
            ]
            retry_rows = [
                {
                    "case_id": "case_1",
                    "condition_id": "dbox_inspired_guard",
                    "final_response_text": "retry ok",
                    "stage_errors": {},
                }
            ]
            source_combined.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in source_rows) + "\n",
                encoding="utf-8",
            )
            retry_combined.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in retry_rows) + "\n",
                encoding="utf-8",
            )
            source_manifest.write_text(
                json.dumps(
                    {
                        "input_jsonl": str(root / "seed.jsonl"),
                        "output_dir": str(source_dir),
                        "case_count": 1,
                        "condition_set": "edf_core",
                        "condition_count": 2,
                        "conditions": [
                            {"condition_id": "enhanced_prompt_only_clean"},
                            {"condition_id": "dbox_inspired_guard"},
                        ],
                        "combined_jsonl": str(source_combined),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            retry_manifest.write_text(
                json.dumps({"combined_jsonl": str(retry_combined)}, ensure_ascii=False),
                encoding="utf-8",
            )

            def fake_summary(rows):
                return {"case_count": 1, "completed_count": len(rows)}

            def fake_write_summary(json_path, md_path, summary, md_zh_path=None):
                json_path.write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")
                md_path.write_text("# Summary\n", encoding="utf-8")
                md_zh_path.write_text("# 摘要\n", encoding="utf-8")

            def fake_export_review(input_jsonl, output_csv, key_csv, shuffle_seed=17, id_salt=""):
                output_csv.write_text("case_id,response_text\ncase_1,ok\ncase_1,retry ok\n", encoding="utf-8")
                key_csv.write_text("anonymized_response_id,condition_id\nr1,a\nr2,b\n", encoding="utf-8")
                return 2

            def fake_export_xlsx(input_csv, output_xlsx):
                output_xlsx.write_text("xlsx placeholder", encoding="utf-8")
                return 1

            manifest = merge_ablation_reruns.merge_ablation_reruns(
                source_manifest=source_manifest,
                retry_manifests=[retry_manifest],
                output_dir=output_dir,
                summarize_fn=fake_summary,
                write_summary_fn=fake_write_summary,
                export_review_fn=fake_export_review,
                export_xlsx_fn=fake_export_xlsx,
            )
            merged_rows = [
                json.loads(line)
                for line in Path(manifest["combined_jsonl"]).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            review_xlsx_exists = Path(manifest["review_xlsx"]).exists()

        self.assertEqual("retry ok", merged_rows[1]["final_response_text"])
        self.assertEqual([{"case_id": "case_1", "condition_id": "dbox_inspired_guard"}], manifest["replaced_pairs"])
        self.assertEqual([], manifest["skipped_retry_pairs"])
        self.assertEqual(2, manifest["review_row_count"])
        self.assertTrue(review_xlsx_exists)

    def test_merge_skips_empty_retry_rows_without_replacing_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "source"
            retry_dir = root / "retry"
            source_dir.mkdir()
            retry_dir.mkdir()
            source_combined = source_dir / "combined.jsonl"
            retry_combined = retry_dir / "combined.jsonl"
            source_manifest = source_dir / "manifest.json"
            retry_manifest = retry_dir / "manifest.json"
            source_combined.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "condition_id": "dbox_inspired_guard",
                        "final_response_text": "",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            retry_combined.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "condition_id": "dbox_inspired_guard",
                        "final_response_text": "",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            source_manifest.write_text(
                json.dumps(
                    {
                        "input_jsonl": str(root / "seed.jsonl"),
                        "output_dir": str(source_dir),
                        "case_count": 1,
                        "condition_set": "edf_core",
                        "condition_count": 1,
                        "conditions": [{"condition_id": "dbox_inspired_guard"}],
                        "combined_jsonl": str(source_combined),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            retry_manifest.write_text(
                json.dumps({"combined_jsonl": str(retry_combined)}, ensure_ascii=False),
                encoding="utf-8",
            )

            manifest = merge_ablation_reruns.merge_ablation_reruns(
                source_manifest=source_manifest,
                retry_manifests=[retry_manifest],
                output_dir=root / "merged",
                summarize_fn=lambda rows: {},
                write_summary_fn=lambda json_path, md_path, summary, md_zh_path=None: (
                    json_path.write_text("{}", encoding="utf-8"),
                    md_path.write_text("# Summary\n", encoding="utf-8"),
                    md_zh_path.write_text("# 摘要\n", encoding="utf-8"),
                ),
                export_review_fn=lambda input_jsonl, output_csv, key_csv, shuffle_seed=17, id_salt="": 0,
                export_xlsx_fn=lambda input_csv, output_xlsx: output_xlsx.write_text("xlsx", encoding="utf-8"),
            )

        self.assertEqual([], manifest["replaced_pairs"])
        self.assertEqual([{"case_id": "case_1", "condition_id": "dbox_inspired_guard"}], manifest["skipped_retry_pairs"])


if __name__ == "__main__":
    unittest.main()
