#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

echo "========================================"
echo "NOI Agent 当前可信回归基线"
echo "========================================"
echo

echo "[1/7] Python 语法检查..."
python3 -m py_compile api_server.py database.py review_engine.py evals/review/run_review_quality_eval.py evals/review/export_cases.py evals/aichat/run_socratic_eval.py evals/aichat/run_chat_batch.py evals/aichat/run_socratic_judge_eval.py evals/aichat/run_socratic_suite.py
echo

echo "[2/7] 核心后端回归..."
python3 -m unittest \
  test_review_async_api_unit.py \
  test_frontend_vue_entry_unit.py \
  test_review_engine_messages_unit.py \
  test_aichat_socratic_eval_cases_unit.py \
  test_aichat_socratic_eval_runner_unit.py \
  test_aichat_chat_batch_runner_unit.py \
  test_aichat_socratic_judge_eval_unit.py \
  test_aichat_socratic_suite_unit.py \
  test_aichat_runtime_policy_unit.py \
  test_checkin_handoff_receiver_unit.py \
  test_review_quality_eval_unit.py \
  test_review_eval_kimi_cli_unit.py \
  test_export_review_cases_unit.py
echo

echo "[3/7] 学习流 API 集成回归..."
python3 test_learning_flow_api_integration.py
echo

echo "[4/7] focus 检测回归..."
python3 test_focus_detection.py
echo

echo "[5/7] 前端构建回归..."
npm run build
echo

echo "[6/7] 前端 Node 测试..."
node --test \
  test_checkin_review_ui.mjs \
  test_review_family_ui.mjs \
  test_student_routes.mjs \
  test_teacher_routes.mjs \
  test_route_access.mjs \
  test_checkin_options.mjs \
  test_checkin_identity.mjs \
  test_api_error_formatting.mjs \
  test_student_entry_ui.mjs \
  test_teacher_vue_ui.mjs \
  test_teacher_manual_review_ui.mjs \
  test_teacher_stats_ui.mjs \
  test_aichat_checkin_handoff_frontend.mjs \
  test_vue_app_shell.mjs
echo

echo "[7/7] 前端语法检查..."
node --check \
  vite.config.js \
  postcss.config.js \
  tailwind.config.js \
  frontend/src/main.js \
  frontend/src/router/index.js \
  frontend/src/services/api.js \
  frontend/src/stores/auth.js \
  frontend/src/utils/checkinIdentity.js \
  static/student_routes.js \
  static/teacher_routes.js \
  static/review_family_ui.js \
  static/checkin_review_ui.js \
  static/teacher_stats_ui.js \
  static/teacher_manual_review_ui.js
echo

if [[ "${1:-}" == "--with-quota" ]]; then
    echo "附加运行：遗留 quota 手工脚本"

    if [[ -z "${MOONSHOT_API_KEY:-}" ]] && [[ -f "$HOME/.moonshot_key" ]]; then
        export MOONSHOT_API_KEY
        MOONSHOT_API_KEY="$(cat "$HOME/.moonshot_key")"
    fi

    if [[ -z "${MOONSHOT_API_KEY:-}" ]]; then
        echo "请输入你的 MOONSHOT_API_KEY:"
        read -s MOONSHOT_API_KEY
        export MOONSHOT_API_KEY
    fi

    echo
    python3 test_quota.py
else
    echo "已跳过 quota 手工脚本。"
    echo "如需附加运行，请使用：./run_test.sh --with-quota"
fi
