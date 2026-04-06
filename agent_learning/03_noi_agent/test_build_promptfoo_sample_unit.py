import json
import tempfile
import unittest
from pathlib import Path

from evals.review import build_promptfoo_sample


class BuildPromptfooSampleTests(unittest.TestCase):
    def test_should_select_shortest_case_per_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "promptfoo_tests.jsonl"
            target = Path(tmpdir) / "promptfoo_tests.sample.jsonl"

            rows = [
                {
                    "description": "long-a",
                    "vars": {"case": json.dumps({"id": "a-long", "extra": "x" * 80})},
                    "metadata": {"mode": "failed_verdict"},
                },
                {
                    "description": "short-a",
                    "vars": {"case": json.dumps({"id": "a-short"})},
                    "metadata": {"mode": "failed_verdict"},
                },
                {
                    "description": "long-b",
                    "vars": {"case": json.dumps({"id": "b-long", "extra": "x" * 100})},
                    "metadata": {"mode": "stuck_bridge"},
                },
                {
                    "description": "short-b",
                    "vars": {"case": json.dumps({"id": "b-short"})},
                    "metadata": {"mode": "stuck_bridge"},
                },
            ]

            source.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                encoding="utf-8",
            )

            counts = build_promptfoo_sample.build_sample(source, target, per_mode=1)
            selected = [
                json.loads(line)
                for line in target.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

            self.assertEqual(counts["failed_verdict"], 1)
            self.assertEqual(counts["stuck_bridge"], 1)
            self.assertEqual(
                [json.loads(row["vars"]["case"])["id"] for row in selected],
                ["a-short", "b-short"],
            )


if __name__ == "__main__":
    unittest.main()
