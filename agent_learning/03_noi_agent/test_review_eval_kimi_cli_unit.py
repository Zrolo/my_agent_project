import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from evals.review import run_review_case_kimi_cli


class ReviewEvalKimiCliRunnerTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "id": "failed_001",
            "mode": "failed_verdict",
            "input": {
                "problem_title": "P5536 核心城市",
                "oj_source": "luogu",
                "completion_status": "unfinished",
                "bottleneck_text": "我知道先求直径 d，再套公式，但不明白这个公式为什么成立。",
                "error_types": ["模型转化", "知道算法但不会证明"],
                "submission_result": " WA ",
                "problem_context": "选 k 个连通核心城市，使其他城市到核心集合的最大最小距离最小。",
                "problem_tags": ["树的直径", "贪心"],
                "student_code": "cout << max(0ll, (d - k + 2) / 2);",
            },
        }

    def test_build_prompt_should_reuse_review_engine_prompt_builders(self):
        with (
            patch.object(run_review_case_kimi_cli.review_engine, "_detect_review_mode", return_value="failed_verdict") as mocked_detect,
            patch.object(run_review_case_kimi_cli.review_engine, "_build_review_system_prompt", return_value="SYSTEM") as mocked_system,
            patch.object(run_review_case_kimi_cli.review_engine, "_build_review_user_prompt", return_value="USER") as mocked_user,
        ):
            prompt = run_review_case_kimi_cli.build_prompt_from_case(self.case)

        mocked_detect.assert_called_once_with("unfinished", "wa")
        mocked_system.assert_called_once_with(mode="failed_verdict")
        mocked_user.assert_called_once()
        self.assertIn("SYSTEM", prompt)
        self.assertIn("USER", prompt)

    def test_build_prompt_should_allow_forced_mode_for_baseline(self):
        with (
            patch.object(run_review_case_kimi_cli.review_engine, "_detect_review_mode") as mocked_detect,
            patch.object(run_review_case_kimi_cli.review_engine, "_build_review_system_prompt", return_value="SYSTEM") as mocked_system,
            patch.object(run_review_case_kimi_cli.review_engine, "_build_review_user_prompt", return_value="USER"),
        ):
            run_review_case_kimi_cli.build_prompt_from_case(self.case, forced_mode="independent_reflect")

        mocked_detect.assert_not_called()
        mocked_system.assert_called_once_with(mode="independent_reflect")

    def test_run_should_call_kimi_cli_and_return_parsed_json(self):
        fake_output = json.dumps(
            {
                "error_tags": ["公式理解"],
                "error_layer": "core_design",
                "error_layer_confidence": "high",
                "core_design_subtags": ["greedy_basis"],
                "diagnosis": "诊断",
                "next_action": "行动",
                "suggested_topic": "专题",
                "main_block": "卡点",
                "key_bridge": "桥梁",
                "next_step": "下一步",
                "transfer_signal": "迁移",
            },
            ensure_ascii=False,
        )

        with patch.object(run_review_case_kimi_cli, "_run_kimi_cli", return_value=fake_output) as mocked_run:
            result = run_review_case_kimi_cli.run(self.case, forced_mode="independent_reflect")

        mocked_run.assert_called_once()
        self.assertEqual("卡点", result["main_block"])

    def test_run_should_strip_json_fence_from_kimi_output(self):
        fenced_output = """```json
{"error_tags":["公式理解"],"error_layer":"core_design","error_layer_confidence":"high","core_design_subtags":["greedy_basis"],"diagnosis":"诊断","next_action":"行动","suggested_topic":"专题","main_block":"卡点","key_bridge":"桥梁","next_step":"下一步","transfer_signal":"迁移"}
```"""

        with patch.object(run_review_case_kimi_cli, "_run_kimi_cli", return_value=fenced_output):
            result = run_review_case_kimi_cli.run(self.case, forced_mode="independent_reflect")

        self.assertEqual("卡点", result["main_block"])

    def test_run_kimi_cli_should_pass_explicit_moonshot_config_and_budget_env(self):
        fake_proc = MagicMock(returncode=0, stdout='{"ok": true}', stderr="")

        with (
            patch.dict(
                "os.environ",
                {"MOONSHOT_API_KEY": "sk-test", "NOI_REVIEW_MAX_TOKENS": "98304"},
                clear=False,
            ),
            patch.object(run_review_case_kimi_cli.subprocess, "run", return_value=fake_proc) as mocked_run,
        ):
            output = run_review_case_kimi_cli._run_kimi_cli("hello")

        self.assertEqual('{"ok": true}', output)
        cmd = mocked_run.call_args.args[0]
        self.assertIn("--config", cmd)
        config = json.loads(cmd[cmd.index("--config") + 1])
        self.assertEqual("moonshot/kimi-k2.5", config["default_model"])
        self.assertEqual("kimi", config["providers"]["moonshot"]["type"])
        self.assertEqual("sk-test", config["providers"]["moonshot"]["api_key"])
        self.assertEqual("moonshot/kimi-k2.5", cmd[cmd.index("--model") + 1])
        passed_env = mocked_run.call_args.kwargs["env"]
        self.assertEqual("98304", passed_env["KIMI_MODEL_MAX_TOKENS"])

    def test_load_case_should_support_promptfoo_argv_payload(self):
        case = json.dumps(self.case, ensure_ascii=False)
        argv = ["runner.py", case, '{"ignored":"provider"}', '{"ignored":"vars"}']

        loaded = run_review_case_kimi_cli._load_case_from_cli(argv=argv, stdin_text="")

        self.assertEqual(self.case["id"], loaded["id"])

    def test_read_cli_stdin_should_not_block_on_tty(self):
        fake_stdin = MagicMock()
        fake_stdin.isatty.return_value = True
        fake_stdin.read.side_effect = AssertionError("read should not be called for tty stdin")

        text = run_review_case_kimi_cli._read_cli_stdin(fake_stdin)

        self.assertEqual("", text)
        fake_stdin.read.assert_not_called()

    def test_run_kimi_cli_should_raise_structured_timeout_error(self):
        with (
            patch.dict("os.environ", {"REVIEW_EVAL_KIMI_TIMEOUT_SECONDS": "12"}, clear=False),
            patch.object(
                run_review_case_kimi_cli.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(cmd=["kimi"], timeout=12),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "kimi_cli_timeout: 12s"):
                run_review_case_kimi_cli._run_kimi_cli("hello")

    def test_run_kimi_cli_should_include_stderr_excerpt_on_failure(self):
        fake_proc = MagicMock(returncode=1, stdout="", stderr="network exploded\ntrace")

        with patch.object(run_review_case_kimi_cli.subprocess, "run", return_value=fake_proc):
            with self.assertRaisesRegex(RuntimeError, "kimi_cli_failed: network exploded"):
                run_review_case_kimi_cli._run_kimi_cli("hello")


if __name__ == "__main__":
    unittest.main()
