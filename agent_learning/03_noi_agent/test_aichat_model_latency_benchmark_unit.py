import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import run_model_latency_benchmark as bench


class AIChatModelLatencyBenchmarkTests(unittest.TestCase):
    def test_provider_configs_use_three_requested_models_and_skip_missing_keys(self):
        env = {
            "MOONSHOT_API_KEY": "moonshot-key",
            "MIMO_API_KEY": "mimo-key",
            "MIMO_MODEL": "mimo-v2.5-pro",
            "DEEPSEEK_API_KEY": "deepseek-key",
        }

        configs = bench.build_provider_configs(env)

        self.assertEqual(["kimi", "mimo", "deepseek"], [config.provider_id for config in configs])
        self.assertEqual("kimi-k2.6", configs[0].model)
        self.assertEqual("https://api.moonshot.cn/v1", configs[0].base_url)
        self.assertTrue(configs[1].enabled)
        self.assertEqual("https://api.xiaomimimo.com/v1", configs[1].base_url)
        self.assertEqual("mimo-v2.5-pro", configs[1].model)
        self.assertEqual("deepseek-v4-flash", configs[2].model)
        self.assertEqual("enabled", configs[2].thinking_mode)
        self.assertEqual({"thinking": {"type": "enabled"}}, configs[2].extra_body)
        self.assertTrue(configs[2].enabled)

    def test_multiturn_scenarios_expand_into_ordered_turns(self):
        cases_data = {
            "scenarios": [
                {
                    "id": "binary_search_problem_only",
                    "input_mode": "problem_only",
                    "algorithm_tag": "二分答案",
                    "problem_ref": "P2678",
                    "problem_context": "跳石头，最大化最小跳跃距离。",
                    "turns": [
                        {"student_message": "为什么要二分？"},
                        {"student_message": "大概次数太多？"},
                        {"student_message": "check 在检查什么？"},
                    ],
                }
            ]
        }

        turns = bench.expand_benchmark_items(cases_data, case_limit=10)

        self.assertEqual(3, len(turns))
        self.assertEqual("binary_search_problem_only::turn_1", turns[0]["id"])
        self.assertEqual("binary_search_problem_only", turns[2]["scenario_id"])
        self.assertEqual(3, turns[2]["turn_index"])
        self.assertEqual("problem_only", turns[2]["input_mode"])
        self.assertEqual("二分答案", turns[2]["algorithm_tag"])
        self.assertEqual("P2678", turns[2]["problem_ref"])
        self.assertEqual("跳石头，最大化最小跳跃距离。", turns[2]["problem_context"])

    def test_summarize_rows_reports_latency_quality_and_errors(self):
        rows = [
            {
                "provider_id": "kimi",
                "case_id": "case_1",
                "input_mode": "problem_only",
                "algorithm_tag": "二分答案",
                "run_kind": "measured",
                "ok": True,
                "request_ms": 1000,
                "llm_ms": 800,
                "quality_gate_pass": True,
            },
            {
                "provider_id": "kimi",
                "case_id": "case_2",
                "input_mode": "code_only",
                "algorithm_tag": "无题目代码防误判",
                "run_kind": "measured",
                "ok": False,
                "request_ms": 3000,
                "llm_ms": 2500,
                "quality_gate_pass": False,
                "error": "timeout",
            },
            {
                "provider_id": "deepseek",
                "case_id": "case_1",
                "input_mode": "problem_only",
                "algorithm_tag": "二分答案",
                "run_kind": "measured",
                "ok": True,
                "request_ms": 500,
                "llm_ms": 400,
                "quality_gate_pass": True,
            },
        ]

        summary = bench.summarize_rows(rows)

        self.assertEqual(2, summary["providers"]["kimi"]["measured_count"])
        self.assertEqual(0.5, summary["providers"]["kimi"]["success_rate"])
        self.assertEqual(2000, summary["providers"]["kimi"]["request_ms_avg"])
        self.assertEqual(3000, summary["providers"]["kimi"]["request_ms_p95"])
        self.assertEqual(0.5, summary["providers"]["kimi"]["quality_gate_pass_rate"])
        self.assertEqual(1000, summary["by_input_mode"]["kimi"]["problem_only"]["request_ms_avg"])
        self.assertEqual(3000, summary["by_input_mode"]["kimi"]["code_only"]["request_ms_avg"])
        self.assertEqual(500, summary["by_algorithm_tag"]["deepseek"]["二分答案"]["request_ms_avg"])
        self.assertEqual(1, summary["providers"]["deepseek"]["measured_count"])
        self.assertEqual("deepseek", summary["fastest_provider_by_avg_request_ms"])

    def test_write_outputs_creates_raw_summary_and_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            rows = [
                {
                    "provider_id": "kimi",
                    "provider_label": "Kimi K2.6",
                    "model": "kimi-k2.6",
                    "case_id": "case_1",
                    "run_kind": "measured",
                    "ok": True,
                    "request_ms": 1000,
                    "llm_ms": 800,
                    "reply_chars": 42,
                    "quality_gate_pass": True,
                }
            ]
            summary = bench.summarize_rows(rows)

            bench.write_outputs(output_dir, rows, summary)

            raw_rows = [
                json.loads(line)
                for line in (output_dir / "raw.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            summary_exists = (output_dir / "summary.json").exists()
            report = (output_dir / "report.md").read_text(encoding="utf-8")

        self.assertEqual("kimi", raw_rows[0]["provider_id"])
        self.assertTrue(summary_exists)
        self.assertIn("三模型 AIChat 速度测试报告", report)
        self.assertIn("Kimi K2.6", report)
        self.assertIn("质量通过率", report)
        self.assertIn("按输入形态", report)
        self.assertIn("按算法标签", report)
        self.assertIn("最慢 Case", report)


if __name__ == "__main__":
    unittest.main()
