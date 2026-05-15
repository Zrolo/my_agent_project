# Dialogue-State v3 50-Case Generation Report

This is a development draft report. The v3 cases add fixed follow-up tutoring contexts and F1-F4 scaffold-followability labels; coach review is still required and this is not gold data.

- row_count: 50
- source_jsonl: `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- output_jsonl: `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- reference_label_status: `draft_needs_coach_review`

## Distributions

- turn_position_counts: `{'initial': 10, 'followup': 40}`
- context_type_counts: `{'initial_question': 10, 'followup_after_partial_answer': 9, 'followup_after_correct_short_answer': 6, 'followup_after_wrong_answer': 7, 'followup_after_code_attempt': 10, 'followup_after_prerequisite_gap': 5, 'policy_direct_answer_special': 3}`
- followability_counts: `{'NA': 10, 'F2': 19, 'F1': 6, 'F3': 10, 'F4': 5}`
- expected_tutor_move_counts: `{'micro_step': 27, 'clarify': 9, 'advance': 6, 'prerequisite_repair': 5, 'safe_redirect': 3}`
- low_confidence_count: 0
