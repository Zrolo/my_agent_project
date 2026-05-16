import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import summarize_bridge_offline_eval


def _result_row(
    *,
    case_id: str,
    gold_family: str,
    pred_family: str,
    gold_focus: str = "state_design",
    pred_focus: str = "state_design",
    leakage_level: int = 0,
    safe_action: str = "pass",
    repaired: bool = False,
    confidence: float = 0.8,
    tutor_mode: str = "current_system",
    guard_mode: str = "predicted",
    pipeline_mode: str = "tutor_plus_guard_plus_repair",
    tutor_model_provider: str = "deepseek",
    chat_thinking_mode: str = "profile_default",
    total_latency_ms: float = 100.0,
    llm_call_count: int = 3,
    stage_errors: dict | None = None,
    post_repair_level: int | None = None,
    post_repair_safe_action: str = "pass",
    final_static_risk_types: list[str] | None = None,
):
    row = {
        "case_id": case_id,
        "tutor_mode": tutor_mode,
        "guard_mode": guard_mode,
        "pipeline_mode": pipeline_mode,
        "models": {
            "tutor_model_provider": tutor_model_provider,
            "chat_thinking_mode": chat_thinking_mode,
            "tutor_mode": tutor_mode,
            "guard_mode": guard_mode,
            "pipeline_mode": pipeline_mode,
        },
        "gold": {
            "student_state": "strategy_application_gap",
            "bridge_family": gold_family,
            "known_focus": gold_focus,
            "help_seeking_type": "instrumental_help",
            "allowed_help_level": "L2",
        },
        "bridge_judge_result": {
            "problem_solving_state": "strategy_application_gap",
            "missing_bridge": {
                "family": pred_family,
                "known_focus": pred_focus,
            },
            "help_seeking_type": "instrumental_help",
            "allowed_help_level": "L2",
            "confidence": confidence,
        },
        "tutor_response": {
            "baseline_group": "current_system",
            "tutor_mode": tutor_mode,
            "tutor_model_provider": tutor_model_provider,
            "response_text": "回复",
            "level": "L2",
        },
        "leakage_judge_result": {
            "leakage_level": leakage_level,
            "leakage_types": ["critical_bridge"] if leakage_level >= 3 else [],
            "is_critical_bridge_leakage": leakage_level >= 3,
            "is_answer_or_code_leakage": False,
            "safe_action": safe_action,
        },
        "latency_ms": {
            "bridge_judge_latency_ms": 20.0,
            "tutor_latency_ms": 50.0,
            "leakage_judge_latency_ms": 30.0,
            "total_latency_ms": total_latency_ms,
        },
        "llm_call_count": llm_call_count,
        "stage_errors": stage_errors or {},
    }
    if final_static_risk_types is not None:
        row["final_static_leakage_risk_lint"] = {
            "answer_slot_risk_flag": "answer_slot" in final_static_risk_types,
            "filled_trace_risk_flag": "filled_trace" in final_static_risk_types,
            "worked_example_risk_flag": "worked_example" in final_static_risk_types,
            "risk_types": final_static_risk_types,
            "is_diagnostic_only": True,
        }
    if repaired:
        row["repair_result"] = {
            "repaired_response": "修复后回复",
            "still_needs_leakage_check": True,
        }
    if post_repair_level is not None:
        row["post_repair_leakage_judge_result"] = {
            "leakage_level": post_repair_level,
            "is_critical_bridge_leakage": post_repair_level >= 3,
            "is_answer_or_code_leakage": False,
            "safe_action": post_repair_safe_action,
        }
        row["repair_still_leaks"] = post_repair_level >= 3
        row["post_repair_safe_action"] = post_repair_safe_action
    return row


class BridgeOfflineEvalSummaryTests(unittest.TestCase):
    def test_summarize_bridge_offline_results_counts_accuracy_and_leakage_rates(self):
        rows = [
            _result_row(
                case_id="case_1",
                gold_family="representation_bridge",
                pred_family="representation_bridge",
                leakage_level=3,
                safe_action="rewrite",
                repaired=True,
                confidence=0.9,
            ),
            _result_row(
                case_id="case_2",
                gold_family="predicate_bridge",
                pred_family="transition_bridge",
                gold_focus="check_condition",
                pred_focus="transition_design",
                confidence=0.7,
                total_latency_ms=200.0,
            ),
            {
                "case_id": "case_3",
                "gold": {"bridge_family": "aggregation_bridge"},
                "error": "bridge_judge_failed",
            },
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(3, summary["case_count"])
        self.assertEqual(2, summary["completed_count"])
        self.assertEqual(1, summary["error_count"])
        self.assertEqual(0.5, summary["bridge_family_accuracy"])
        self.assertEqual(0.5, summary["known_focus_accuracy"])
        self.assertEqual(0.5, summary["known_focus_accuracy_on_registered"])
        self.assertEqual(1.0, summary["student_state_accuracy"])
        self.assertEqual(0.5, summary["leakage_rate"])
        self.assertEqual(0.5, summary["critical_bridge_leakage_rate"])
        self.assertEqual(0.5, summary["rewrite_rate"])
        self.assertEqual(0.5, summary["repair_rate"])
        self.assertEqual(0.0, summary["post_repair_check_rate"])
        self.assertIsNone(summary["repair_still_leaks_rate"])
        self.assertEqual(0.8, summary["avg_bridge_judge_confidence"])
        self.assertEqual(150.0, summary["latency_ms"]["total_p50"])

    def test_summarize_bridge_offline_results_reports_post_repair_check_rates(self):
        rows = [
            _result_row(
                case_id="case_repair_safe",
                gold_family="representation_bridge",
                pred_family="representation_bridge",
                leakage_level=3,
                safe_action="rewrite",
                repaired=True,
                post_repair_level=0,
                post_repair_safe_action="pass",
            ),
            _result_row(
                case_id="case_repair_still_leaks",
                gold_family="predicate_bridge",
                pred_family="predicate_bridge",
                leakage_level=3,
                safe_action="rewrite",
                repaired=True,
                post_repair_level=3,
                post_repair_safe_action="rewrite",
            ),
            _result_row(
                case_id="case_no_repair",
                gold_family="ordering_bridge",
                pred_family="ordering_bridge",
                leakage_level=0,
                safe_action="pass",
                repaired=False,
            ),
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(0.667, summary["post_repair_check_rate"])
        self.assertEqual(0.5, summary["repair_still_leaks_rate"])
        self.assertEqual(0.5, summary["post_repair_rewrite_or_block_rate"])

    def test_summarize_bridge_offline_results_reports_static_leakage_risk_rates(self):
        rows = [
            _result_row(
                case_id="case_answer_slot",
                gold_family="predicate_bridge",
                pred_family="predicate_bridge",
                final_static_risk_types=["answer_slot"],
            ),
            _result_row(
                case_id="case_filled_trace",
                gold_family="representation_bridge",
                pred_family="representation_bridge",
                final_static_risk_types=["filled_trace", "worked_example"],
            ),
            _result_row(
                case_id="case_safe",
                gold_family="debugging_bridge",
                pred_family="debugging_bridge",
                final_static_risk_types=[],
            ),
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(0.667, summary["final_static_risk_rate"])
        self.assertEqual(0.333, summary["final_static_answer_slot_risk_rate"])
        self.assertEqual(0.333, summary["final_static_filled_trace_risk_rate"])
        self.assertEqual(0.333, summary["final_static_worked_example_risk_rate"])

    def test_summarize_bridge_offline_results_adds_static_risk_dev_gate(self):
        rows = [
            _result_row(
                case_id="case_answer_slot",
                gold_family="predicate_bridge",
                pred_family="predicate_bridge",
                final_static_risk_types=["answer_slot"],
            ),
            _result_row(
                case_id="case_safe",
                gold_family="debugging_bridge",
                pred_family="debugging_bridge",
                final_static_risk_types=[],
            ),
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertFalse(summary["dev_gate"]["automatic_headline_ready"])
        self.assertTrue(summary["dev_gate"]["review_required"])
        self.assertIn("final_static_answer_slot_risk", summary["dev_gate"]["reasons"])

    def test_summarize_bridge_offline_results_marks_safe_static_gate_ready(self):
        rows = [
            _result_row(
                case_id="case_safe",
                gold_family="debugging_bridge",
                pred_family="debugging_bridge",
                final_static_risk_types=[],
            )
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertTrue(summary["dev_gate"]["automatic_headline_ready"])
        self.assertFalse(summary["dev_gate"]["review_required"])
        self.assertEqual([], summary["dev_gate"]["reasons"])

    def test_summarize_bridge_offline_results_backfills_static_lint_for_legacy_rows(self):
        rows = [
            {
                **_result_row(
                    case_id="case_legacy_risky",
                    gold_family="predicate_bridge",
                    pred_family="predicate_bridge",
                ),
                "final_response_text": "请回答 check(mid) 应该返回 true 还是 false，并填写可行返回____。",
            },
            {
                **_result_row(
                    case_id="case_legacy_safe",
                    gold_family="debugging_bridge",
                    pred_family="debugging_bridge",
                ),
                "final_response_text": "你先贴出最小错误样例和当前输出。",
            },
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(0.5, summary["final_static_risk_rate"])
        self.assertEqual(0.5, summary["final_static_answer_slot_risk_rate"])

    def test_summarize_bridge_offline_results_groups_by_experimental_condition(self):
        rows = [
            _result_row(
                case_id="case_1",
                gold_family="representation_bridge",
                pred_family="representation_bridge",
                tutor_mode="current_system",
                guard_mode="predicted",
                tutor_model_provider="deepseek",
                chat_thinking_mode="disabled",
                total_latency_ms=100.0,
                llm_call_count=2,
            ),
            _result_row(
                case_id="case_2",
                gold_family="predicate_bridge",
                pred_family="predicate_bridge",
                gold_focus="unknown",
                pred_focus="unknown",
                tutor_mode="bridge_contract",
                guard_mode="oracle",
                tutor_model_provider="kimi",
                chat_thinking_mode="enabled",
                total_latency_ms=300.0,
                llm_call_count=4,
                stage_errors={"repair": "timeout"},
            ),
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        current_key = "tutor_mode=current_system|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=unknown|tutor_model_provider=deepseek|chat_thinking_mode=disabled"
        contract_key = "tutor_mode=bridge_contract|guard_mode=oracle|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=unknown|tutor_model_provider=kimi|chat_thinking_mode=enabled"
        self.assertEqual(1, summary["groups"][current_key]["case_count"])
        self.assertEqual(1, summary["groups"][contract_key]["case_count"])
        self.assertEqual(1.0, summary["unknown_focus_recall"])
        self.assertEqual({"repair": 1}, summary["stage_error_counts"])
        self.assertEqual(200.0, summary["latency_ms"]["total_p50"])
        self.assertEqual(300.0, summary["latency_ms"]["total_p95"])
        self.assertEqual(3.0, summary["average_llm_call_count"])

    def test_summarize_bridge_offline_results_reports_runtime_contract_quality(self):
        rows = [
            {
                **_result_row(
                    case_id="case_contract_1",
                    gold_family="predicate_condition_bridge",
                    pred_family="predicate_condition_bridge",
                    gold_focus="check_condition",
                    pred_focus="check_condition",
                ),
                "candidate_retrieval": {
                    "focus_candidate_ids": ["check_condition", "unknown"],
                },
                "runtime_bridge_contract": {
                    "turn_type": "diagnosable_learning_turn",
                    "diagnosis_uncertainty": "low",
                    "algorithm_topic_l1": "binary_search",
                    "algorithm_topic_l2": "binary_search_answer",
                    "primary_bridge_family": "predicate_condition_bridge",
                    "selected_focus_id": "check_condition",
                    "selected_focus_confidence": 0.86,
                    "max_scaffold_level": "L2",
                    "help_forms": ["micro_example", "guiding_question"],
                    "forbidden_content": ["不要给完整 check。"],
                    "leakage_risk": "high",
                    "confidence": 0.86,
                },
                "prompt_budget_estimate": {"total_prompt_tokens_estimate": 420},
            },
            {
                **_result_row(
                    case_id="case_contract_2",
                    gold_family="representation_state_bridge",
                    pred_family="representation_state_bridge",
                    gold_focus="state_design",
                    pred_focus="hallucinated_focus",
                ),
                "candidate_retrieval": {
                    "focus_candidate_ids": ["state_design", "unknown"],
                },
                "runtime_bridge_contract": {
                    "turn_type": "diagnosable_learning_turn",
                    "diagnosis_uncertainty": "medium",
                    "algorithm_topic_l1": "dp",
                    "algorithm_topic_l2": "dp_state_transition",
                    "primary_bridge_family": "wrong_family",
                    "selected_focus_id": "hallucinated_focus",
                    "selected_focus_confidence": 0.8,
                    "max_scaffold_level": "L2",
                    "help_forms": ["question", "micro_example", "checklist"],
                    "forbidden_content": ["a", "b", "c", "d"],
                    "leakage_risk": "medium",
                    "confidence": 0.8,
                },
                "prompt_budget_estimate": {"total_prompt_tokens_estimate": 580},
            },
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(0.5, summary["invalid_label_rate"])
        self.assertEqual(0.5, summary["focus_out_of_registry_rate"])
        self.assertEqual(0.5, summary["self_contradiction_rate"])
        self.assertEqual(500.0, summary["average_prompt_tokens"])

    def test_summarize_single_llm_structured_uses_runtime_contract_for_agreement(self):
        rows = [
            {
                "case_id": "case_single",
                "tutor_mode": "single_llm_structured",
                "guard_mode": "predicted",
                "pipeline_mode": "tutor_only",
                "models": {
                    "tutor_model_provider": "deepseek_flash",
                    "chat_thinking_mode": "disabled",
                    "tutor_mode": "single_llm_structured",
                    "guard_mode": "predicted",
                    "pipeline_mode": "tutor_only",
                },
                "gold": {
                    "bridge_family": "representation_state_bridge",
                    "known_focus": "state_design",
                    "allowed_help_level": "L2",
                },
                "bridge_judge_result": {},
                "runtime_bridge_contract": {
                    "turn_type": "diagnosable_learning_turn",
                    "diagnosis_uncertainty": "low",
                    "algorithm_topic_l1": "dp",
                    "algorithm_topic_l2": "knapsack",
                    "primary_bridge_family": "representation_state_bridge",
                    "selected_focus_id": "state_design",
                    "selected_focus_confidence": 0.86,
                    "max_scaffold_level": "L2",
                    "help_forms": ["micro_example", "guiding_question"],
                    "forbidden_content": ["不要直接给完整状态定义。"],
                    "leakage_risk": "high",
                    "confidence": 0.86,
                },
                "latency_ms": {"total_latency_ms": 100.0},
                "llm_call_count": 1,
                "stage_errors": {},
            }
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(1.0, summary["bridge_family_accuracy"])
        self.assertEqual(1.0, summary["known_focus_accuracy"])
        self.assertEqual(1.0, summary["known_focus_accuracy_on_registered"])
        self.assertEqual(1.0, summary["allowed_help_level_accuracy"])

    def test_summarize_current_system_no_diagnosis_counts_completed_response_rows(self):
        rows = [
            {
                "case_id": "case_current_only",
                "tutor_mode": "current_system",
                "guard_mode": "predicted",
                "pipeline_mode": "tutor_only_no_diagnosis",
                "judge_schema_mode": "retrieval_augmented_compact_judge",
                "models": {
                    "tutor_model_provider": "deepseek_flash",
                    "chat_thinking_mode": "disabled",
                    "tutor_mode": "current_system",
                    "guard_mode": "predicted",
                    "pipeline_mode": "tutor_only_no_diagnosis",
                    "judge_schema_mode": "retrieval_augmented_compact_judge",
                },
                "gold": {
                    "bridge_family": "representation_state_bridge",
                    "known_focus": "state_design",
                    "allowed_help_level": "L2",
                },
                "tutor_response": {
                    "baseline_group": "current_system",
                    "tutor_mode": "current_system",
                    "response_text": "你先说说 dp 需要记录什么。",
                    "level": "L2",
                },
                "candidate_response_text": "你先说说 dp 需要记录什么。",
                "final_response_text": "你先说说 dp 需要记录什么。",
                "final_response_source": "candidate",
                "latency_ms": {"total_latency_ms": 100.0},
                "llm_call_count": 1,
                "stage_errors": {},
            }
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(1, summary["case_count"])
        self.assertEqual(1, summary["completed_count"])
        self.assertEqual(0, summary["error_count"])
        self.assertIsNone(summary["bridge_family_accuracy"])
        self.assertEqual(1.0, summary["average_llm_call_count"])
        self.assertEqual(100.0, summary["latency_ms"]["total_p50"])

    def test_runtime_contract_with_out_of_schema_enum_counts_as_invalid(self):
        rows = [
            {
                **_result_row(
                    case_id="case_bad_enum",
                    gold_family="aggregation_contribution_bridge",
                    pred_family="aggregation_contribution_bridge",
                ),
                "runtime_bridge_contract": {
                    "turn_type": "diagnosable_learning_turn",
                    "diagnosis_uncertainty": "low",
                    "algorithm_topic_l1": "tree",
                    "algorithm_topic_l2": "tree_path_difference",
                    "primary_bridge_family": "树上差分标记位置",
                    "selected_focus_id": "tree_path_difference",
                    "selected_focus_confidence": 0.8,
                    "max_scaffold_level": "L2",
                    "help_forms": ["引导性提问"],
                    "forbidden_content": ["不要直接给公式。"],
                    "leakage_risk": "high",
                    "confidence": 0.8,
                },
            }
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(1.0, summary["invalid_label_rate"])

    def test_render_markdown_report_includes_core_metrics(self):
        summary = {
            "case_count": 3,
            "completed_count": 2,
            "error_count": 1,
            "bridge_family_accuracy": 0.5,
            "known_focus_accuracy": 0.5,
            "known_focus_accuracy_on_registered": 0.5,
            "unknown_focus_recall": None,
            "student_state_accuracy": 1.0,
            "help_seeking_type_accuracy": 1.0,
            "allowed_help_level_accuracy": 1.0,
            "leakage_rate": 0.5,
            "critical_bridge_leakage_rate": 0.5,
            "answer_or_code_leakage_rate": 0.0,
            "rewrite_rate": 0.5,
            "block_rate": 0.0,
            "repair_rate": 0.5,
            "post_repair_check_rate": 0.5,
            "repair_still_leaks_rate": 0.0,
            "post_repair_rewrite_or_block_rate": 0.0,
            "invalid_label_rate": 0.0,
            "focus_out_of_registry_rate": 0.0,
            "self_contradiction_rate": 0.0,
            "average_prompt_tokens": 400.0,
            "average_llm_call_count": 3.0,
            "avg_bridge_judge_confidence": 0.8,
            "safe_action_counts": {"pass": 1, "rewrite": 1},
            "leakage_level_counts": {"0": 1, "3": 1},
            "latency_ms": {"total_p50": 100.0, "total_p95": 100.0},
            "stage_error_counts": {},
            "groups": {},
            "error_cases": ["case_3"],
            "dev_gate": {
                "automatic_headline_ready": False,
                "review_required": True,
                "reasons": ["final_static_answer_slot_risk"],
            },
        }

        report = summarize_bridge_offline_eval.render_markdown_report(summary)

        self.assertIn("# Bridge Offline Eval Summary", report)
        self.assertIn("| Automatic Headline Ready | False |", report)
        self.assertIn("| Dev Gate Reasons | final_static_answer_slot_risk |", report)
        self.assertIn("| Bridge Family Accuracy | 0.500 |", report)
        self.assertIn("| Known Focus Accuracy On Registered | 0.500 |", report)
        self.assertIn("| Critical Bridge Leakage Rate | 0.500 |", report)
        self.assertIn("| Repair Still Leaks Rate | 0.000 |", report)
        self.assertIn("| Invalid Label Rate | 0.000 |", report)
        self.assertIn("| Average Prompt Tokens | 400.000 |", report)
        self.assertIn("| Average LLM Call Count | 3.000 |", report)
        self.assertIn("case_3", report)

    def test_render_markdown_report_group_tables_include_static_risk_metrics(self):
        summary = {
            "case_count": 2,
            "completed_count": 2,
            "error_count": 0,
            "groups": {
                "tutor_mode=enhanced_prompt_only|guard_mode=none": {
                    "case_count": 2,
                    "completed_count": 2,
                    "bridge_family_accuracy": None,
                    "critical_bridge_leakage_rate": None,
                    "average_llm_call_count": 1.0,
                    "latency_ms": {"total_p50": 100.0},
                    "final_static_risk_rate": 0.5,
                    "final_static_answer_slot_risk_rate": 0.5,
                    "final_static_filled_trace_risk_rate": 0.0,
                    "final_static_worked_example_risk_rate": 0.0,
                    "dev_gate": {
                        "automatic_headline_ready": False,
                        "review_required": True,
                        "reasons": ["final_static_answer_slot_risk"],
                    },
                }
            },
            "safe_action_counts": {},
            "leakage_level_counts": {},
            "stage_error_counts": {},
            "error_cases": [],
            "dev_gate": {
                "automatic_headline_ready": False,
                "review_required": True,
                "reasons": ["final_static_answer_slot_risk"],
            },
        }

        report = summarize_bridge_offline_eval.render_markdown_report(summary)
        report_zh = summarize_bridge_offline_eval.render_markdown_report_zh(summary)

        self.assertIn("| Final Static Risk Rate | 0.500 |", report)
        self.assertIn("| Final Static Answer Slot Risk Rate | 0.500 |", report)
        self.assertIn("| Final Static Filled Trace Risk Rate | 0.000 |", report)
        self.assertIn("| Final Static Worked Example Risk Rate | 0.000 |", report)
        self.assertIn("| Automatic Headline Ready | False |", report)
        self.assertIn("| Dev Gate Reasons | final_static_answer_slot_risk |", report)
        self.assertIn("| 最终回复静态风险率 | 0.500 |", report_zh)
        self.assertIn("| 最终回复答案槽位静态风险率 | 0.500 |", report_zh)
        self.assertIn("| 最终回复已填 trace 静态风险率 | 0.000 |", report_zh)
        self.assertIn("| 最终回复完整微例静态风险率 | 0.000 |", report_zh)
        self.assertIn("| 自动进入主结果候选 | False |", report_zh)
        self.assertIn("| Dev Gate 原因 | final_static_answer_slot_risk |", report_zh)

    def test_render_markdown_report_zh_includes_core_metrics(self):
        summary = {
            "case_count": 3,
            "completed_count": 2,
            "error_count": 1,
            "bridge_family_accuracy": 0.5,
            "known_focus_accuracy": 0.5,
            "known_focus_accuracy_on_registered": 0.5,
            "unknown_focus_recall": None,
            "student_state_accuracy": 1.0,
            "help_seeking_type_accuracy": 1.0,
            "allowed_help_level_accuracy": 1.0,
            "leakage_rate": 0.5,
            "critical_bridge_leakage_rate": 0.5,
            "answer_or_code_leakage_rate": 0.0,
            "rewrite_rate": 0.5,
            "block_rate": 0.0,
            "repair_rate": 0.5,
            "post_repair_check_rate": 0.5,
            "repair_still_leaks_rate": 0.0,
            "post_repair_rewrite_or_block_rate": 0.0,
            "invalid_label_rate": 0.0,
            "focus_out_of_registry_rate": 0.0,
            "self_contradiction_rate": 0.0,
            "average_prompt_tokens": 400.0,
            "average_llm_call_count": 3.0,
            "avg_bridge_judge_confidence": 0.8,
            "safe_action_counts": {"pass": 1, "rewrite": 1},
            "leakage_level_counts": {"0": 1, "3": 1},
            "latency_ms": {"total_p50": 100.0, "total_p95": 100.0},
            "stage_error_counts": {},
            "groups": {},
            "error_cases": ["case_3"],
            "dev_gate": {
                "automatic_headline_ready": False,
                "review_required": True,
                "reasons": ["final_static_answer_slot_risk"],
            },
        }

        report = summarize_bridge_offline_eval.render_markdown_report_zh(summary)

        self.assertIn("# Bridge 离线评测摘要", report)
        self.assertIn("| 自动进入主结果候选 | False |", report)
        self.assertIn("| Dev Gate 原因 | final_static_answer_slot_risk |", report)
        self.assertIn("| 桥梁大类准确率 | 0.500 |", report)
        self.assertIn("| 关键桥梁泄露率 | 0.500 |", report)
        self.assertIn("| 修复后仍泄露率 | 0.000 |", report)
        self.assertIn("| 平均 LLM 调用次数 | 3.000 |", report)
        self.assertIn("case_3", report)

    def test_load_and_write_summary_files(self):
        rows = [
            _result_row(
                case_id="case_1",
                gold_family="representation_bridge",
                pred_family="representation_bridge",
            )
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "results.jsonl"
            json_path = Path(tmpdir) / "summary.json"
            md_path = Path(tmpdir) / "summary.md"
            input_path.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                encoding="utf-8",
            )

            loaded = summarize_bridge_offline_eval.load_result_rows(input_path)
            summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(loaded)
            summarize_bridge_offline_eval.write_summary_files(json_path, md_path, summary)

            self.assertEqual(rows, loaded)
            self.assertEqual(1.0, json.loads(json_path.read_text(encoding="utf-8"))["bridge_family_accuracy"])
            self.assertIn("Bridge Offline Eval Summary", md_path.read_text(encoding="utf-8"))

    def test_main_writes_summary_and_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "results.jsonl"
            json_path = Path(tmpdir) / "summary.json"
            md_path = Path(tmpdir) / "summary.md"
            md_zh_path = Path(tmpdir) / "summary.zh.md"
            input_path.write_text(
                json.dumps(
                    _result_row(
                        case_id="case_1",
                        gold_family="representation_bridge",
                        pred_family="representation_bridge",
                    ),
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = summarize_bridge_offline_eval.main(
                    [
                        "--input-jsonl",
                        str(input_path),
                        "--output-json",
                        str(json_path),
                        "--output-md",
                        str(md_path),
                        "--output-md-zh",
                        str(md_zh_path),
                    ]
                )

            self.assertEqual(0, exit_code)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertTrue(md_zh_path.exists())
            self.assertIn('"case_count": 1', stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
