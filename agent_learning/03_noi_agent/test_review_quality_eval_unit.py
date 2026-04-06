import json
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.review import run_review_quality_eval


class ReviewQualityEvalTests(unittest.TestCase):
    def test_extract_rubric_score_should_parse_fenced_json(self):
        output = """```json
{"score": 3, "reasons": ["a", "b"]}
```"""
        parsed = run_review_quality_eval._extract_rubric_score(output)
        self.assertTrue(parsed["ok"])
        self.assertEqual(3, parsed["score"])

    def test_extract_rubric_score_should_fail_on_invalid_score(self):
        parsed = run_review_quality_eval._extract_rubric_score('{"score":"4","reasons":[]}')
        self.assertFalse(parsed["ok"])
        self.assertEqual(0, parsed["score"])

    def test_build_rubric_prompt_should_only_include_four_student_fields(self):
        case = {
            "input": {
                "problem_title": "P5536 核心城市",
                "completion_status": "unfinished",
                "bottleneck_text": "不明白公式为什么成立",
                "problem_context": "选 k 个连通核心城市。",
            }
        }
        review = {
            "main_block": "卡点",
            "key_bridge": "桥梁",
            "next_step": "下一步",
            "transfer_signal": "迁移",
            "diagnosis": "不要带进去",
        }
        prompt = run_review_quality_eval._build_rubric_prompt(case, review)
        self.assertIn('"main_block": "卡点"', prompt)
        self.assertNotIn("不要带进去", prompt)
        self.assertIn("main_block 必须提到题目里的具体对象、条件或步骤", prompt)

    def test_build_rubric_prompt_text_should_render_checks_from_json(self):
        rubric = {
            "checks": [
                {"field": "main_block", "rule": "必须具体。"},
                {"field": "key_bridge", "rule": "必须具体。"},
            ]
        }
        prompt = run_review_quality_eval._build_rubric_prompt_text(rubric)
        self.assertIn("1. main_block 必须具体。", prompt)
        self.assertIn("2. key_bridge 必须具体。", prompt)
        self.assertIn('{"score": 0-2, "reasons": ["...", "..."]}', prompt)
        self.assertIn("每条满足记 1 分，总分 0-2。", prompt)

    def test_extract_rubric_score_should_allow_dynamic_max_score(self):
        parsed = run_review_quality_eval._extract_rubric_score('{"score":7,"reasons":["ok"]}', max_score=7)
        self.assertTrue(parsed["ok"])
        self.assertEqual(7, parsed["score"])

    def test_evaluate_tests_should_aggregate_provider_metrics(self):
        rows = [
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_1",
                            "mode": "failed_verdict",
                            "input": {"problem_title": "A"},
                        },
                        ensure_ascii=False,
                    )
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tests.jsonl"
            path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")

            with (
                patch.object(
                    run_review_quality_eval,
                    "_run_review",
                    return_value=(
                        True,
                        {
                            "main_block": "卡点",
                            "key_bridge": "桥梁",
                            "next_step": "动作",
                            "transfer_signal": "信号",
                        },
                        12.3,
                    ),
                ),
                patch.object(
                    run_review_quality_eval,
                    "_judge_review",
                    return_value={"ok": True, "score": 3, "reasons": ["ok"]},
                ),
                patch.object(
                    run_review_quality_eval,
                    "_run_mode_gate",
                    return_value={"pass": True, "mode": "failed_verdict", "family": "failure_diagnosis", "kb_gap_exempt": False, "reason": "ok"},
                ),
            ):
                summary = run_review_quality_eval.evaluate_tests(path)

        self.assertEqual(1.0, summary["baseline_current_kimi_cli"]["json_ok_rate"])
        self.assertEqual(1.0, summary["mode_route_kimi_cli"]["fields_ok_rate"])
        self.assertEqual(3.0, summary["mode_route_kimi_cli"]["rubric_avg_score"])
        self.assertEqual(6, summary["mode_route_kimi_cli"]["rubric_max_score"])
        self.assertEqual(0.5, summary["mode_route_kimi_cli"]["rubric_avg_ratio"])
        self.assertEqual(1, summary["mode_route_kimi_cli"]["quality_case_count"])
        self.assertEqual(1.0, summary["mode_route_kimi_cli"]["quality_case_rate"])

    def test_evaluate_tests_should_average_repeated_attempts(self):
        rows = [
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_repeat",
                            "mode": "stuck_bridge",
                            "input": {"problem_title": "A"},
                        },
                        ensure_ascii=False,
                    )
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tests.jsonl"
            path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")

            review_side_effect = [
                (True, {"main_block": "卡点", "key_bridge": "桥梁", "next_step": "动作", "transfer_signal": "信号"}, 10.0),
                (True, {"error": "bad"}, 20.0),
                (True, {"main_block": "卡点", "key_bridge": "桥梁", "next_step": "动作", "transfer_signal": "信号"}, 30.0),
                (True, {"main_block": "卡点", "key_bridge": "桥梁", "next_step": "动作", "transfer_signal": "信号"}, 40.0),
            ]
            judge_side_effect = [
                {"ok": True, "score": 4, "reasons": ["ok"]},
                {"ok": True, "score": 2, "reasons": ["ok"]},
                {"ok": True, "score": 3, "reasons": ["ok"]},
            ]
            with (
                patch.object(run_review_quality_eval, "_run_review", side_effect=review_side_effect),
                patch.object(run_review_quality_eval, "_judge_review", side_effect=judge_side_effect),
                patch.object(
                    run_review_quality_eval,
                    "_run_mode_gate",
                    side_effect=[
                        {"pass": True, "mode": "stuck_bridge", "family": "failure_diagnosis", "kb_gap_exempt": True, "reason": "ok"},
                        {"pass": False, "mode": "stuck_bridge", "family": "failure_diagnosis", "kb_gap_exempt": True, "reason": "skipped"},
                        {"pass": True, "mode": "stuck_bridge", "family": "failure_diagnosis", "kb_gap_exempt": True, "reason": "ok"},
                        {"pass": True, "mode": "stuck_bridge", "family": "failure_diagnosis", "kb_gap_exempt": True, "reason": "ok"},
                    ],
                ),
            ):
                summary = run_review_quality_eval.evaluate_tests(path, repeats=2)

        self.assertEqual(2, summary["baseline_current_kimi_cli"]["repeats"])
        self.assertEqual(0.5, summary["baseline_current_kimi_cli"]["fields_ok_rate"])
        self.assertEqual(15.0, summary["baseline_current_kimi_cli"]["avg_elapsed_seconds"])
        self.assertEqual(4.0, summary["baseline_current_kimi_cli"]["rubric_avg_score"])
        self.assertEqual(1, summary["baseline_current_kimi_cli"]["quality_case_count"])
        self.assertEqual(1.0, summary["baseline_current_kimi_cli"]["quality_case_rate"])

    def test_evaluate_tests_should_exclude_failed_attempts_from_quality_average(self):
        rows = [
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_timeout",
                            "mode": "failed_verdict",
                            "input": {"problem_title": "A"},
                        },
                        ensure_ascii=False,
                    )
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tests.jsonl"
            path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")

            with (
                patch.object(
                    run_review_quality_eval,
                    "_run_review",
                    side_effect=[
                        (False, {"error": "review_timeout"}, 240.0),
                        (False, {"error": "review_timeout"}, 240.0),
                    ],
                ),
            ):
                summary = run_review_quality_eval.evaluate_tests(path, repeats=1)

        self.assertIsNone(summary["baseline_current_kimi_cli"]["rubric_avg_score"])
        self.assertIsNone(summary["baseline_current_kimi_cli"]["rubric_avg_ratio"])
        self.assertIsNone(summary["baseline_current_kimi_cli"]["gate_pass_rate"])
        self.assertEqual(0, summary["baseline_current_kimi_cli"]["quality_case_count"])
        self.assertEqual(0.0, summary["baseline_current_kimi_cli"]["quality_case_rate"])

    def test_run_review_should_return_timeout_error_instead_of_crashing(self):
        with patch.object(
            run_review_quality_eval.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(cmd=["python3"], timeout=240),
        ):
            ok, parsed, elapsed = run_review_quality_eval._run_review({"id": "x"}, {})

        self.assertFalse(ok)
        self.assertEqual("review_timeout", parsed["error"])
        self.assertGreaterEqual(elapsed, 0)

    def test_run_review_should_default_to_reasoning_max_tokens_but_allow_override(self):
        captured_env = {}

        def fake_run(*args, **kwargs):
            captured_env.update(kwargs["env"])

            class Proc:
                returncode = 0
                stdout = '{"main_block":"a","key_bridge":"b","next_step":"c","transfer_signal":"d"}'
                stderr = ""

            return Proc()

        with patch.object(run_review_quality_eval.subprocess, "run", side_effect=fake_run):
            ok, parsed, _elapsed = run_review_quality_eval._run_review({"id": "x"}, {})

        self.assertTrue(ok)
        self.assertEqual("98304", captured_env["NOI_REVIEW_MAX_TOKENS"])

        captured_env.clear()
        with (
            patch.dict(run_review_quality_eval.os.environ, {"NOI_REVIEW_MAX_TOKENS": "1600"}, clear=False),
            patch.object(run_review_quality_eval.subprocess, "run", side_effect=fake_run),
        ):
            ok, parsed, _elapsed = run_review_quality_eval._run_review({"id": "x"}, {})

        self.assertTrue(ok)
        self.assertEqual("1600", captured_env["NOI_REVIEW_MAX_TOKENS"])

    def test_judge_review_should_return_failed_reason_on_exception(self):
        case = {"input": {"problem_title": "A", "completion_status": "unfinished", "bottleneck_text": "", "problem_context": ""}}
        review = {"main_block": "a", "key_bridge": "b", "next_step": "c", "transfer_signal": "d"}
        with patch.object(run_review_quality_eval.run_review_case_kimi_cli, "_run_kimi_cli", side_effect=RuntimeError("boom")):
            parsed = run_review_quality_eval._judge_review(case, review)

        self.assertFalse(parsed["ok"])
        self.assertIn("judge_failed", parsed["reasons"][0])

    def test_judge_review_should_validate_score_against_rubric_check_count(self):
        case = {"input": {"problem_title": "A", "completion_status": "unfinished", "bottleneck_text": "", "problem_context": ""}}
        review = {"main_block": "a", "key_bridge": "b", "next_step": "c", "transfer_signal": "d"}
        with (
            patch.object(
                run_review_quality_eval,
                "_load_rubric",
                return_value={"checks": [{"field": "a", "rule": "x"} for _ in range(7)]},
            ),
            patch.object(
                run_review_quality_eval.run_review_case_kimi_cli,
                "_run_kimi_cli",
                return_value='{"score":7,"reasons":["ok"]}',
            ),
        ):
            parsed = run_review_quality_eval._judge_review(case, review)

        self.assertTrue(parsed["ok"])
        self.assertEqual(7, parsed["score"])

    # --- helpers for mode_gate tests ---

    _FAMILIES_RUBRIC = {
        "checks": [],
        "mode_gate": {
            "families": [
                {
                    "family": "failure_diagnosis",
                    "modes": ["failed_verdict", "stuck_bridge", "editorial_transfer"],
                    "kb_gap_exemption": "stuck_bridge/editorial_transfer 下豁免。",
                    "gates": [
                        {"mode": "failed_verdict", "condition": "submission_result in {wa,tle,re,ce}", "rule": "main_block 必须点名代码位置。"},
                        {"mode": "stuck_bridge", "condition": "completion_status in {unfinished,hinted}", "rule": "key_bridge 必须用题目对象名。"},
                        {"mode": "editorial_transfer", "condition": "completion_status==editorial", "rule": "说清为什么这方法能解题。"},
                    ],
                },
                {
                    "family": "success_reflection",
                    "modes": ["independent_reflect"],
                    "kb_gap_exemption": None,
                    "gates": [
                        {"mode": "independent_reflect", "condition": "fallback", "rule": "transfer_signal 必须给可观察题面特征。"},
                    ],
                },
            ]
        },
    }

    def test_run_mode_gate_should_return_pass_for_failed_verdict(self):
        case = {
            "input": {
                "problem_title": "P3275 糖果",
                "completion_status": "unfinished",
                "submission_result": "wa",
                "bottleneck_text": "判断方向搞反了",
            }
        }
        review = {"main_block": "第3行的松弛条件写反", "key_bridge": "b", "next_step": "c", "transfer_signal": "d"}
        with (
            patch.object(run_review_quality_eval, "_load_rubric", return_value=self._FAMILIES_RUBRIC),
            patch.object(run_review_quality_eval.review_engine, "_detect_review_mode", return_value="failed_verdict"),
            patch.object(
                run_review_quality_eval.run_review_case_kimi_cli,
                "_run_kimi_cli",
                return_value='{"pass": true, "reason": "点名了代码位置"}',
            ),
        ):
            result = run_review_quality_eval._run_mode_gate(case, review)

        self.assertTrue(result["pass"])
        self.assertEqual("failed_verdict", result["mode"])
        self.assertEqual("failure_diagnosis", result["family"])
        # failed_verdict 不豁免
        self.assertFalse(result["kb_gap_exempt"])

    def test_run_mode_gate_should_return_fail_on_judge_exception(self):
        case = {
            "input": {
                "problem_title": "A",
                "completion_status": "unfinished",
                "submission_result": "wa",
                "bottleneck_text": "",
            }
        }
        review = {"main_block": "a", "key_bridge": "b", "next_step": "c", "transfer_signal": "d"}
        with (
            patch.object(run_review_quality_eval, "_load_rubric", return_value=self._FAMILIES_RUBRIC),
            patch.object(run_review_quality_eval.review_engine, "_detect_review_mode", return_value="failed_verdict"),
            patch.object(
                run_review_quality_eval.run_review_case_kimi_cli,
                "_run_kimi_cli",
                side_effect=RuntimeError("boom"),
            ),
        ):
            result = run_review_quality_eval._run_mode_gate(case, review)

        self.assertFalse(result["pass"])
        self.assertIn("gate_judge_failed", result["reason"])

    def test_run_mode_gate_should_clarify_independent_reflect_allows_specific_nouns(self):
        case = {
            "input": {
                "problem_title": "P1016 旅行家的预算",
                "completion_status": "independent",
                "submission_result": "not_submitted",
                "bottleneck_text": "不知道贪心证明",
            }
        }
        review = {"main_block": "a", "key_bridge": "b", "next_step": "c", "transfer_signal": "供应点有不同单价"}
        captured = {}

        def fake_run(prompt: str):
            captured["prompt"] = prompt
            return '{"pass": true, "reason": "ok"}'

        with (
            patch.object(run_review_quality_eval, "_load_rubric", return_value=self._FAMILIES_RUBRIC),
            patch.object(run_review_quality_eval.review_engine, "_detect_review_mode", return_value="independent_reflect"),
            patch.object(run_review_quality_eval.run_review_case_kimi_cli, "_run_kimi_cli", side_effect=fake_run),
        ):
            result = run_review_quality_eval._run_mode_gate(case, review)

        self.assertTrue(result["pass"])
        self.assertIn("使用题目中出现的具体名词", captured["prompt"])
        self.assertIn("禁止的是把具体条件替换成类型模板", captured["prompt"])

    def test_run_mode_gate_should_pass_when_no_gate_defined(self):
        case = {"input": {"completion_status": "ac", "submission_result": ""}}
        review = {"main_block": "a", "key_bridge": "b", "next_step": "c", "transfer_signal": "d"}
        with patch.object(run_review_quality_eval, "_load_rubric", return_value={"checks": [], "mode_gate": {}}):
            result = run_review_quality_eval._run_mode_gate(case, review)

        self.assertTrue(result["pass"])
        self.assertEqual("no_gate_defined", result["reason"])

    def test_evaluate_tests_should_include_gate_pass_rate_in_summary(self):
        rows = [
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_gate",
                            "mode": "failed_verdict",
                            "input": {"problem_title": "A"},
                        },
                        ensure_ascii=False,
                    )
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tests.jsonl"
            path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")

            with (
                patch.object(
                    run_review_quality_eval,
                    "_run_review",
                    return_value=(
                        True,
                        {
                            "main_block": "卡点",
                            "key_bridge": "桥梁",
                            "next_step": "动作",
                            "transfer_signal": "信号",
                        },
                        12.3,
                    ),
                ),
                patch.object(
                    run_review_quality_eval,
                    "_judge_review",
                    return_value={"ok": True, "score": 5, "reasons": ["ok"]},
                ),
                patch.object(
                    run_review_quality_eval,
                    "_run_mode_gate",
                    return_value={"pass": True, "mode": "failed_verdict", "family": "failure_diagnosis", "kb_gap_exempt": False, "reason": "ok"},
                ),
            ):
                summary = run_review_quality_eval.evaluate_tests(path)

        self.assertIn("gate_pass_rate", summary["baseline_current_kimi_cli"])
        self.assertEqual(1.0, summary["baseline_current_kimi_cli"]["gate_pass_rate"])

    def test_evaluate_tests_should_include_by_mode_breakdown_in_summary(self):
        rows = [
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_failed",
                            "mode": "failed_verdict",
                            "input": {"problem_title": "A"},
                        },
                        ensure_ascii=False,
                    )
                }
            },
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_stuck",
                            "mode": "stuck_bridge",
                            "input": {"problem_title": "B"},
                        },
                        ensure_ascii=False,
                    )
                }
            },
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tests.jsonl"
            path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")

            with (
                patch.object(
                    run_review_quality_eval,
                    "_run_review",
                    side_effect=[
                        (True, {"main_block": "卡点1", "key_bridge": "桥梁1", "next_step": "动作1", "transfer_signal": "信号1"}, 10.0),
                        (True, {"main_block": "卡点2", "key_bridge": "桥梁2", "next_step": "动作2", "transfer_signal": "信号2"}, 20.0),
                        (True, {"main_block": "卡点3", "key_bridge": "桥梁3", "next_step": "动作3", "transfer_signal": "信号3"}, 30.0),
                        (True, {"main_block": "卡点4", "key_bridge": "桥梁4", "next_step": "动作4", "transfer_signal": "信号4"}, 40.0),
                    ],
                ),
                patch.object(
                    run_review_quality_eval,
                    "_judge_review",
                    side_effect=[
                        {"ok": True, "score": 5, "reasons": ["ok"]},
                        {"ok": True, "score": 4, "reasons": ["ok"]},
                        {"ok": True, "score": 3, "reasons": ["ok"]},
                        {"ok": True, "score": 2, "reasons": ["ok"]},
                    ],
                ),
                patch.object(
                    run_review_quality_eval,
                    "_run_mode_gate",
                    side_effect=[
                        {"pass": True, "mode": "failed_verdict", "family": "failure_diagnosis", "kb_gap_exempt": False, "reason": "ok"},
                        {"pass": False, "mode": "stuck_bridge", "family": "failure_diagnosis", "kb_gap_exempt": True, "reason": "miss"},
                        {"pass": True, "mode": "failed_verdict", "family": "failure_diagnosis", "kb_gap_exempt": False, "reason": "ok"},
                        {"pass": True, "mode": "stuck_bridge", "family": "failure_diagnosis", "kb_gap_exempt": True, "reason": "ok"},
                    ],
                ),
            ):
                summary = run_review_quality_eval.evaluate_tests(path)

        by_mode = summary["baseline_current_kimi_cli"]["by_mode"]
        self.assertIn("failed_verdict", by_mode)
        self.assertIn("stuck_bridge", by_mode)
        self.assertEqual(1, by_mode["failed_verdict"]["case_count"])
        self.assertEqual(1, by_mode["stuck_bridge"]["case_count"])
        self.assertEqual(5.0, by_mode["failed_verdict"]["rubric_avg_score"])
        self.assertEqual(4.0, by_mode["stuck_bridge"]["rubric_avg_score"])
        self.assertEqual(1.0, by_mode["failed_verdict"]["json_ok_rate"])
        self.assertEqual(1.0, by_mode["stuck_bridge"]["fields_ok_rate"])

    def test_run_mode_gate_should_use_production_mode_detection(self):
        case = {
            "input": {
                "problem_title": "A",
                "completion_status": "unfinished",
                "submission_result": "wa",
                "bottleneck_text": "",
            }
        }
        review = {"main_block": "a", "key_bridge": "b", "next_step": "c", "transfer_signal": "d"}
        with (
            patch.object(run_review_quality_eval, "_load_rubric", return_value=self._FAMILIES_RUBRIC),
            patch.object(run_review_quality_eval.review_engine, "_detect_review_mode", return_value="independent_reflect"),
            patch.object(
                run_review_quality_eval.run_review_case_kimi_cli,
                "_run_kimi_cli",
                return_value='{"pass": true, "reason": "ok"}',
            ),
        ):
            result = run_review_quality_eval._run_mode_gate(case, review)

        self.assertTrue(result["pass"])
        self.assertEqual("independent_reflect", result["mode"])
        self.assertEqual("success_reflection", result["family"])
        self.assertFalse(result["kb_gap_exempt"])

    def test_run_mode_gate_should_set_kb_gap_exempt_for_stuck_bridge(self):
        """stuck_bridge 属于 failure_diagnosis，且在豁免范围内，kb_gap_exempt 应为 True。"""
        case = {
            "input": {
                "problem_title": "P1234 差分约束",
                "completion_status": "unfinished",
                "submission_result": "",
                "bottleneck_text": "不知道怎么建图",
            }
        }
        review = {"main_block": "a", "key_bridge": "b", "next_step": "c", "transfer_signal": "d"}
        with (
            patch.object(run_review_quality_eval, "_load_rubric", return_value=self._FAMILIES_RUBRIC),
            patch.object(run_review_quality_eval.review_engine, "_detect_review_mode", return_value="stuck_bridge"),
            patch.object(
                run_review_quality_eval.run_review_case_kimi_cli,
                "_run_kimi_cli",
                return_value='{"pass": true, "reason": "ok"}',
            ),
        ):
            result = run_review_quality_eval._run_mode_gate(case, review)

        self.assertEqual("stuck_bridge", result["mode"])
        self.assertEqual("failure_diagnosis", result["family"])
        self.assertTrue(result["kb_gap_exempt"])

    def test_run_mode_gate_should_set_kb_gap_exempt_for_editorial_transfer(self):
        """editorial_transfer 属于 failure_diagnosis，且在豁免范围内，kb_gap_exempt 应为 True。"""
        case = {
            "input": {
                "problem_title": "P5536 核心城市",
                "completion_status": "editorial",
                "submission_result": "",
                "bottleneck_text": "看了题解才知道贪心做法",
            }
        }
        review = {"main_block": "a", "key_bridge": "b", "next_step": "c", "transfer_signal": "d"}
        with (
            patch.object(run_review_quality_eval, "_load_rubric", return_value=self._FAMILIES_RUBRIC),
            patch.object(run_review_quality_eval.review_engine, "_detect_review_mode", return_value="editorial_transfer"),
            patch.object(
                run_review_quality_eval.run_review_case_kimi_cli,
                "_run_kimi_cli",
                return_value='{"pass": true, "reason": "ok"}',
            ),
        ):
            result = run_review_quality_eval._run_mode_gate(case, review)

        self.assertEqual("editorial_transfer", result["mode"])
        self.assertEqual("failure_diagnosis", result["family"])
        self.assertTrue(result["kb_gap_exempt"])

    def test_evaluate_tests_should_include_gate_family_in_attempt(self):
        """evaluate_tests 的 attempt 记录应包含 gate_family 字段。"""
        rows = [
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_family",
                            "mode": "stuck_bridge",
                            "input": {"problem_title": "A"},
                        },
                        ensure_ascii=False,
                    )
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tests.jsonl"
            path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")

            with (
                patch.object(
                    run_review_quality_eval,
                    "_run_review",
                    return_value=(
                        True,
                        {"main_block": "卡点", "key_bridge": "桥梁", "next_step": "动作", "transfer_signal": "信号"},
                        10.0,
                    ),
                ),
                patch.object(
                    run_review_quality_eval,
                    "_judge_review",
                    return_value={"ok": True, "score": 4, "reasons": ["ok"]},
                ),
                patch.object(
                    run_review_quality_eval,
                    "_run_mode_gate",
                    return_value={"pass": True, "mode": "stuck_bridge", "family": "failure_diagnosis", "kb_gap_exempt": True, "reason": "ok"},
                ),
            ):
                summary = run_review_quality_eval.evaluate_tests(path)

        attempt = summary["baseline_current_kimi_cli"]["cases"][0]["attempts"][0]
        self.assertIn("gate_family", attempt)
        self.assertEqual("failure_diagnosis", attempt["gate_family"])
        self.assertIn("gate_kb_gap_exempt", attempt)
        self.assertTrue(attempt["gate_kb_gap_exempt"])

    def test_main_should_optionally_write_output_file(self):
        rows = [
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_write",
                            "mode": "failed_verdict",
                            "input": {"problem_title": "A"},
                        },
                        ensure_ascii=False,
                    )
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "tests.jsonl"
            out_path = Path(tmpdir) / "result.json"
            test_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
            summary = {
                "baseline_current_kimi_cli": {"json_ok_rate": 1.0},
                "mode_route_kimi_cli": {"json_ok_rate": 1.0},
            }
            with patch.object(run_review_quality_eval, "evaluate_tests", return_value=summary):
                output = json.dumps(run_review_quality_eval.evaluate_tests(test_path, repeats=1), ensure_ascii=False, indent=2)
                out_path.write_text(output + "\n")

            self.assertIn("baseline_current_kimi_cli", out_path.read_text())

    def test_evaluate_tests_should_emit_attempt_level_trace_logs(self):
        rows = [
            {
                "vars": {
                    "case": json.dumps(
                        {
                            "id": "case_trace",
                            "mode": "failed_verdict",
                            "input": {"problem_title": "A"},
                        },
                        ensure_ascii=False,
                    )
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tests.jsonl"
            path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
            stream = io.StringIO()
            with (
                patch.object(
                    run_review_quality_eval,
                    "_run_review",
                    return_value=(
                        True,
                        {
                            "main_block": "卡点",
                            "key_bridge": "桥梁",
                            "next_step": "动作",
                            "transfer_signal": "信号",
                        },
                        12.3,
                    ),
                ),
                patch.object(
                    run_review_quality_eval,
                    "_judge_review",
                    return_value={"ok": True, "score": 5, "reasons": ["ok"]},
                ),
                patch.object(
                    run_review_quality_eval,
                    "_run_mode_gate",
                    return_value={"pass": True, "mode": "failed_verdict", "reason": "ok"},
                ),
            ):
                run_review_quality_eval.evaluate_tests(path, attempt_log=stream)

        log_text = stream.getvalue()
        self.assertIn("ATTEMPT_START provider=baseline_current_kimi_cli case=case_trace attempt=1", log_text)
        self.assertIn("ATTEMPT_REVIEW_DONE provider=baseline_current_kimi_cli case=case_trace attempt=1 ok=True fields_ok=True elapsed=12.3", log_text)
        self.assertIn("ATTEMPT_JUDGE_DONE provider=baseline_current_kimi_cli case=case_trace attempt=1 rubric_ok=True rubric_score=5", log_text)
        self.assertIn("ATTEMPT_GATE_DONE provider=baseline_current_kimi_cli case=case_trace attempt=1 gate_pass=True gate_mode=failed_verdict", log_text)

    def test_main_should_write_attempt_log_when_path_provided(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "tests.jsonl"
            out_path = Path(tmpdir) / "out.json"
            log_path = Path(tmpdir) / "attempt.log"
            test_path.write_text('{"vars":{"case":"{\\"id\\": \\"x\\", \\"mode\\": \\"failed_verdict\\", \\"input\\": {\\"problem_title\\": \\"A\\"}}"}}\n')

            captured = {}

            def fake_evaluate_tests(path, repeats=1, attempt_log=None):
                captured["path"] = path
                captured["repeats"] = repeats
                captured["attempt_log_is_none"] = attempt_log is None
                attempt_log.write("ATTEMPT_START provider=baseline_current_kimi_cli case=x attempt=1\n")
                attempt_log.flush()
                return {"baseline_current_kimi_cli": {"json_ok_rate": 1.0}}

            with patch.object(run_review_quality_eval, "evaluate_tests", side_effect=fake_evaluate_tests):
                run_review_quality_eval.main([str(test_path), "1", str(out_path), str(log_path)])

            self.assertEqual(test_path, captured["path"])
            self.assertEqual(1, captured["repeats"])
            self.assertFalse(captured["attempt_log_is_none"])
            self.assertIn("ATTEMPT_START provider=baseline_current_kimi_cli case=x attempt=1", log_path.read_text())
            self.assertIn("baseline_current_kimi_cli", out_path.read_text())


if __name__ == "__main__":
    unittest.main()
