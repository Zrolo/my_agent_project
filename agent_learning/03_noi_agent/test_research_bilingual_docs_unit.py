import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import validate_research_bilingual_docs


class ResearchBilingualDocsTests(unittest.TestCase):
    def test_companion_name_uses_plain_md_for_english_and_zh_md_for_chinese(self):
        self.assertEqual(
            "short_constructed_response_smoke_20260512.md",
            validate_research_bilingual_docs.companion_name(
                "short_constructed_response_smoke_20260512.zh.md"
            ),
        )
        self.assertEqual(
            "short_constructed_response_smoke_20260512.zh.md",
            validate_research_bilingual_docs.companion_name(
                "short_constructed_response_smoke_20260512.md"
            ),
        )

    def test_validate_reports_new_unpaired_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "new_report.zh.md").write_text("# 中文\n", encoding="utf-8")

            report = validate_research_bilingual_docs.validate_bilingual_docs(
                root,
                legacy_allowlist=set(),
            )

            self.assertEqual(1, report["unpaired_count"])
            self.assertEqual("new_report.zh.md", report["unpaired_docs"][0]["file"])
            self.assertEqual("new_report.md", report["unpaired_docs"][0]["expected_pair"])

    def test_validate_accepts_bilingual_pairs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "new_report.zh.md").write_text("# 中文\n", encoding="utf-8")
            (root / "new_report.md").write_text("# English\n", encoding="utf-8")

            report = validate_research_bilingual_docs.validate_bilingual_docs(
                root,
                legacy_allowlist=set(),
            )

            self.assertEqual(0, report["unpaired_count"])
            self.assertEqual([], report["unpaired_docs"])

    def test_validate_tracks_legacy_unpaired_docs_without_failing_new_policy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "legacy_only.md").write_text("# Legacy\n", encoding="utf-8")

            report = validate_research_bilingual_docs.validate_bilingual_docs(
                root,
                legacy_allowlist={"legacy_only.md"},
            )

            self.assertEqual(0, report["unpaired_count"])
            self.assertEqual(1, report["legacy_unpaired_count"])
            self.assertEqual("legacy_only.md", report["legacy_unpaired_docs"][0]["file"])

    def test_main_exits_nonzero_when_new_unpaired_docs_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_json = root / "report.json"
            (root / "new_report.md").write_text("# English\n", encoding="utf-8")

            exit_code = validate_research_bilingual_docs.main(
                [
                    "--root",
                    str(root),
                    "--output-json",
                    str(output_json),
                    "--no-default-legacy-allowlist",
                ]
            )

            self.assertEqual(1, exit_code)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(1, payload["unpaired_count"])


if __name__ == "__main__":
    unittest.main()
