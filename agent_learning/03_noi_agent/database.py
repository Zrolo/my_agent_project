"""
SQLite database layer for NOI Training Loop.
"""

import sqlite3
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "noi_agent.db"
REVIEW_STATUS_PENDING = "pending"
REVIEW_STATUS_COMPLETED = "completed"
REVIEW_STATUS_FAILED = "failed"
LEARNING_STATUS_NOT_STARTED = "not_started"
LEARNING_STATUS_QUIZ_IN_PROGRESS = "quiz_in_progress"
LEARNING_STATUS_SELF_CHECK_REQUIRED = "self_check_required"
LEARNING_STATUS_REMEDY_AVAILABLE = "remedy_available"
LEARNING_STATUS_REMEDY_IN_PROGRESS = "remedy_in_progress"
LEARNING_STATUS_KNOWLEDGE_BAILOUT = "knowledge_bailout"
LEARNING_STATUS_RESOLVED = "resolved"
LEARNING_STATUS_NEEDS_TEACHER = "needs_teacher_followup"
MASTERY_STATUS_NOT_ASSESSED = "not_assessed"
MASTERY_STATUS_INDEPENDENT_SUCCESS = "independent_success"
MASTERY_STATUS_ASSISTED_SUCCESS = "assisted_success"
MASTERY_STATUS_NOT_MASTERED = "not_mastered"

BRIDGE_TOPIC_MAP: dict[str, tuple[str, str]] = {
    "state_design": ("dp", "dp_basic"),
    "dp.state_design": ("dp", "dp_basic"),
    "transition_design": ("dp", "dp_basic"),
    "dp.transition_design": ("dp", "dp_basic"),
    "enumeration_order": ("basic", "enumeration"),
    "check_condition": ("basic", "binary_search"),
    "binary_search.check_condition": ("basic", "binary_search"),
    "left_bound_update": ("basic", "binary_search"),
    "binary_search.left_bound": ("basic", "binary_search"),
    "greedy_basis": ("basic", "greedy"),
    "tree_diameter_candidates": ("graph", "tree_diameter"),
    "shared_prefix_merging": ("string", "trie"),
    "string.trie.shared_prefix_merging": ("string", "trie"),
    "lazy_semantics": ("data_structure", "segment_tree"),
    "segment_tree.lazy_semantics": ("data_structure", "segment_tree"),
    "complexity_fit": ("basic", "complexity"),
    "modeling.scale_estimation": ("basic", "complexity"),
    "method_selection": ("basic", "method_selection"),
    "modeling.method_selection": ("basic", "method_selection"),
    "constraint_modeling": ("graph", "difference_constraints"),
    "general_modeling": ("basic", "general_modeling"),
}


def _json_loads_or_default(raw: str, default):
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def _get_table_columns(cursor, table_name: str) -> set[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row["name"] for row in cursor.fetchall()}


def _migrate_reviews_table(cursor):
    columns = set(_get_table_columns(cursor, "reviews"))
    migrations = [
        ("review_status", f"ALTER TABLE reviews ADD COLUMN review_status TEXT NOT NULL DEFAULT '{REVIEW_STATUS_COMPLETED}'"),
        ("error_layer", "ALTER TABLE reviews ADD COLUMN error_layer TEXT NOT NULL DEFAULT 'insufficient'"),
        ("error_layer_confidence", "ALTER TABLE reviews ADD COLUMN error_layer_confidence TEXT NOT NULL DEFAULT 'low'"),
        ("core_design_subtags", "ALTER TABLE reviews ADD COLUMN core_design_subtags TEXT NOT NULL DEFAULT '[]'"),
        ("retry_count", "ALTER TABLE reviews ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0"),
        ("last_error", "ALTER TABLE reviews ADD COLUMN last_error TEXT"),
        ("last_attempt_at", "ALTER TABLE reviews ADD COLUMN last_attempt_at TIMESTAMP"),
        # v2.1 学生纠偏层
        ("main_block", "ALTER TABLE reviews ADD COLUMN main_block TEXT"),
        ("key_bridge", "ALTER TABLE reviews ADD COLUMN key_bridge TEXT"),
        ("next_step", "ALTER TABLE reviews ADD COLUMN next_step TEXT"),
        ("transfer_signal", "ALTER TABLE reviews ADD COLUMN transfer_signal TEXT"),
        ("learning_status", f"ALTER TABLE reviews ADD COLUMN learning_status TEXT NOT NULL DEFAULT '{LEARNING_STATUS_NOT_STARTED}'"),
        ("remedy_count", "ALTER TABLE reviews ADD COLUMN remedy_count INTEGER NOT NULL DEFAULT 0"),
        ("understanding_self_check", "ALTER TABLE reviews ADD COLUMN understanding_self_check TEXT"),
        ("self_check_at", "ALTER TABLE reviews ADD COLUMN self_check_at TIMESTAMP"),
        ("bridge_path", "ALTER TABLE reviews ADD COLUMN bridge_path TEXT"),
        ("review_quality_flags", "ALTER TABLE reviews ADD COLUMN review_quality_flags TEXT NOT NULL DEFAULT '[]'"),
        ("problem_focus", "ALTER TABLE reviews ADD COLUMN problem_focus TEXT"),
        ("visual_hint", "ALTER TABLE reviews ADD COLUMN visual_hint TEXT"),
        ("guided_walkthrough", "ALTER TABLE reviews ADD COLUMN guided_walkthrough TEXT"),
        ("try_now", "ALTER TABLE reviews ADD COLUMN try_now TEXT"),
        ("mastery_status", f"ALTER TABLE reviews ADD COLUMN mastery_status TEXT NOT NULL DEFAULT '{MASTERY_STATUS_NOT_ASSESSED}'"),
        ("bridge_route_meta", "ALTER TABLE reviews ADD COLUMN bridge_route_meta TEXT NOT NULL DEFAULT '{}'"),
    ]

    for column_name, ddl in migrations:
        if column_name not in columns:
            try:
                cursor.execute(ddl)
                columns.add(column_name)
            except sqlite3.OperationalError as exc:
                if "duplicate column name" in str(exc).lower():
                    columns.add(column_name)
                    continue
                raise

    # 旧版本曾把失败占位内容写进 reviews，这里将其迁移为"待生成"
    cursor.execute(
        """
        UPDATE reviews
        SET review_status = ?,
            error_layer = 'insufficient',
            error_layer_confidence = 'low',
            core_design_subtags = '[]',
            last_error = COALESCE(last_error, diagnosis),
            learning_status = CASE
                WHEN learning_status IS NULL OR learning_status = '' THEN ?
                ELSE learning_status
            END
        WHERE diagnosis = 'AI 生成复盘失败，请联系老师'
           OR error_tags = '["系统错误"]'
        """,
        (REVIEW_STATUS_PENDING, LEARNING_STATUS_NOT_STARTED),
    )


def _migrate_checkins_table(cursor):
    columns = _get_table_columns(cursor, "checkins")
    migrations = [
        # v2.1 新增输入字段
        ("problem_context", "ALTER TABLE checkins ADD COLUMN problem_context TEXT"),
        ("submission_result", "ALTER TABLE checkins ADD COLUMN submission_result TEXT"),
        ("student_code", "ALTER TABLE checkins ADD COLUMN student_code TEXT"),
        ("problem_tags", "ALTER TABLE checkins ADD COLUMN problem_tags TEXT NOT NULL DEFAULT '[]'"),
        ("chat_context_summary", "ALTER TABLE checkins ADD COLUMN chat_context_summary TEXT NOT NULL DEFAULT ''"),
        ("session_id", "ALTER TABLE checkins ADD COLUMN session_id TEXT"),
    ]
    for column_name, ddl in migrations:
        if column_name not in columns:
            cursor.execute(ddl)


def _ensure_student_feedback_table(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS student_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            category TEXT NOT NULL,
            rating INTEGER NOT NULL,
            content TEXT NOT NULL,
            page_context TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_feedback_created ON student_feedback(created_at DESC)")


def _ensure_teacher_announcements_table(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS teacher_announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body_markdown TEXT NOT NULL,
            pinned INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'published',
            created_by TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_teacher_announcements_visible ON teacher_announcements(status, pinned DESC, published_at DESC, id DESC)"
    )


def _ensure_aichat_problem_closures_table(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS aichat_problem_closures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            problem_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            problem_title TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'quiz_ready',
            question TEXT NOT NULL,
            target_focus TEXT NOT NULL DEFAULT '',
            answer TEXT NOT NULL DEFAULT '',
            feedback TEXT NOT NULL DEFAULT '',
            followup TEXT NOT NULL DEFAULT '',
            points_awarded INTEGER NOT NULL DEFAULT 0,
            next_review_at TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_problem_closures_student_created ON aichat_problem_closures(student_id, created_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_problem_closures_session ON aichat_problem_closures(student_id, problem_id, session_id, created_at DESC)"
    )


def _ensure_aichat_problem_memory_table(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS aichat_problem_memory (
            student_id TEXT NOT NULL,
            problem_id TEXT NOT NULL,
            summary TEXT NOT NULL DEFAULT '',
            source_session_id TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (student_id, problem_id)
        )
        '''
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_problem_memory_updated ON aichat_problem_memory(updated_at DESC)"
    )


def _ensure_aichat_teaching_evidence_tables(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS aichat_conversation_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_username TEXT NOT NULL DEFAULT '',
            student_real_name TEXT NOT NULL DEFAULT '',
            problem_id TEXT NOT NULL DEFAULT '',
            session_id TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'text',
            has_code INTEGER NOT NULL DEFAULT 0,
            code_language TEXT NOT NULL DEFAULT '',
            model_provider TEXT NOT NULL DEFAULT '',
            model_name TEXT NOT NULL DEFAULT '',
            consent_for_research INTEGER NOT NULL DEFAULT 1,
            source TEXT NOT NULL DEFAULT 'aichat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS aichat_judge_shadow_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL DEFAULT 'judge_called',
            skip_reason TEXT NOT NULL DEFAULT '',
            conversation_message_id INTEGER,
            student_id TEXT NOT NULL,
            student_username TEXT NOT NULL DEFAULT '',
            student_real_name TEXT NOT NULL DEFAULT '',
            problem_id TEXT NOT NULL DEFAULT '',
            session_id TEXT NOT NULL DEFAULT '',
            user_input TEXT NOT NULL DEFAULT '',
            messages_json TEXT NOT NULL DEFAULT '[]',
            rule_max_level TEXT NOT NULL DEFAULT '',
            rule_tutor_action TEXT NOT NULL DEFAULT '',
            rule_risk_tags TEXT NOT NULL DEFAULT '[]',
            judge_failed INTEGER NOT NULL DEFAULT 0,
            failure_reason TEXT NOT NULL DEFAULT '',
            judge_latency_ms INTEGER NOT NULL DEFAULT 0,
            judge_primary_intent TEXT NOT NULL DEFAULT '',
            judge_phase TEXT NOT NULL DEFAULT '',
            judge_action_category TEXT NOT NULL DEFAULT '',
            judge_action_subtype TEXT NOT NULL DEFAULT '',
            judge_allowed_help_level TEXT NOT NULL DEFAULT '',
            judge_confidence REAL NOT NULL DEFAULT 0,
            injection_detected INTEGER NOT NULL DEFAULT 0,
            injection_source TEXT NOT NULL DEFAULT '',
            agreement_action_exact INTEGER NOT NULL DEFAULT 0,
            agreement_action_family INTEGER NOT NULL DEFAULT 0,
            agreement_help_level INTEGER NOT NULL DEFAULT 0,
            agreement_would_override INTEGER NOT NULL DEFAULT 0,
            final_tutor_action TEXT NOT NULL DEFAULT '',
            actual_reply_source TEXT NOT NULL DEFAULT 'rules',
            consent_for_research INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS aichat_turn_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_message_id INTEGER,
            student_id TEXT NOT NULL,
            student_username TEXT NOT NULL DEFAULT '',
            student_real_name TEXT NOT NULL DEFAULT '',
            problem_id TEXT NOT NULL DEFAULT '',
            session_id TEXT NOT NULL DEFAULT '',
            turn_id TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL DEFAULT 'student',
            primary_intent TEXT NOT NULL DEFAULT '',
            learning_issue TEXT NOT NULL DEFAULT '',
            understanding_evidence_json TEXT NOT NULL DEFAULT '[]',
            missing_evidence_json TEXT NOT NULL DEFAULT '[]',
            risk_flags_json TEXT NOT NULL DEFAULT '[]',
            injection_detected INTEGER NOT NULL DEFAULT 0,
            injection_source TEXT NOT NULL DEFAULT 'none',
            same_point_loop_signal INTEGER NOT NULL DEFAULT 0,
            suggested_level TEXT NOT NULL DEFAULT '',
            confidence REAL NOT NULL DEFAULT 0,
            short_reason TEXT NOT NULL DEFAULT '',
            model TEXT NOT NULL DEFAULT '',
            prompt_version TEXT NOT NULL DEFAULT '',
            consent_for_research INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS aichat_session_analyses (
            session_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL DEFAULT '',
            problem_id TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'processing',
            analysis_json TEXT NOT NULL DEFAULT '{}',
            main_issue TEXT NOT NULL DEFAULT '',
            teacher_next_action TEXT NOT NULL DEFAULT '',
            needs_followup INTEGER NOT NULL DEFAULT 0,
            model TEXT NOT NULL DEFAULT '',
            prompt_version TEXT NOT NULL DEFAULT '',
            failure_reason TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    columns = _get_table_columns(cursor, "aichat_judge_shadow_events")
    if "event_type" not in columns:
        cursor.execute("ALTER TABLE aichat_judge_shadow_events ADD COLUMN event_type TEXT NOT NULL DEFAULT 'judge_called'")
    if "skip_reason" not in columns:
        cursor.execute("ALTER TABLE aichat_judge_shadow_events ADD COLUMN skip_reason TEXT NOT NULL DEFAULT ''")
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS aichat_session_summary (
            session_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            student_username TEXT NOT NULL DEFAULT '',
            student_real_name TEXT NOT NULL DEFAULT '',
            problem_id TEXT NOT NULL DEFAULT '',
            message_count INTEGER NOT NULL DEFAULT 0,
            student_turn_count INTEGER NOT NULL DEFAULT 0,
            ai_turn_count INTEGER NOT NULL DEFAULT 0,
            has_understanding_evidence INTEGER NOT NULL DEFAULT 0,
            understanding_evidence_types TEXT NOT NULL DEFAULT '[]',
            same_gap_loop INTEGER NOT NULL DEFAULT 0,
            same_gap_loop_type TEXT NOT NULL DEFAULT '',
            latest_tutor_action TEXT NOT NULL DEFAULT '',
            latest_rule_max_level TEXT NOT NULL DEFAULT '',
            latest_judge_action_subtype TEXT NOT NULL DEFAULT '',
            last_student_message TEXT NOT NULL DEFAULT '',
            consent_for_research INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_conversation_student_created ON aichat_conversation_messages(student_id, created_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_conversation_session ON aichat_conversation_messages(student_id, problem_id, session_id, created_at)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_judge_events_student_created ON aichat_judge_shadow_events(student_id, created_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_judge_events_session ON aichat_judge_shadow_events(student_id, problem_id, session_id, created_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_turn_tags_session ON aichat_turn_tags(student_id, problem_id, session_id, created_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_turn_tags_student_created ON aichat_turn_tags(student_id, created_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_session_analyses_student ON aichat_session_analyses(student_id, updated_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_aichat_session_summary_student_updated ON aichat_session_summary(student_id, updated_at DESC)"
    )


def _ensure_student_problem_completions_table(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS student_problem_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            problem_id TEXT NOT NULL DEFAULT '',
            problem_title TEXT NOT NULL DEFAULT '',
            problem_url TEXT NOT NULL DEFAULT '',
            reported_completion TEXT NOT NULL DEFAULT 'unsure',
            inferred_support_level TEXT NOT NULL DEFAULT 'unknown',
            result_status TEXT NOT NULL DEFAULT 'unsure',
            key_step_summary TEXT NOT NULL DEFAULT '',
            confidence_note TEXT NOT NULL DEFAULT '',
            points_awarded INTEGER NOT NULL DEFAULT 0,
            session_id TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    columns = _get_table_columns(cursor, "student_problem_completions")
    if "points_awarded" not in columns:
        cursor.execute("ALTER TABLE student_problem_completions ADD COLUMN points_awarded INTEGER NOT NULL DEFAULT 0")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_student_problem_completions_student_created ON student_problem_completions(student_id, created_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_student_problem_completions_problem ON student_problem_completions(problem_id, created_at DESC)"
    )


def _migrate_problems_table(cursor):
    columns = _get_table_columns(cursor, "problems")
    migrations = [
        ("source_problem_id", "ALTER TABLE problems ADD COLUMN source_problem_id TEXT NOT NULL DEFAULT ''"),
        ("canonical_url", "ALTER TABLE problems ADD COLUMN canonical_url TEXT NOT NULL DEFAULT ''"),
    ]
    for column_name, ddl in migrations:
        if column_name not in columns:
            cursor.execute(ddl)
            columns.add(column_name)
    cursor.execute(
        "UPDATE problems SET source_problem_id = luogu_pid WHERE source_problem_id IS NULL OR source_problem_id = ''"
    )
    cursor.execute(
        "UPDATE problems SET canonical_url = source_url WHERE canonical_url IS NULL OR canonical_url = ''"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problems_source_ref ON problems(source, source_problem_id)")


def _ensure_problem_bottleneck_events_table(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS problem_bottleneck_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL DEFAULT '',
            problem_ref TEXT NOT NULL DEFAULT '',
            problem_id INTEGER,
            session_id TEXT NOT NULL DEFAULT '',
            source_event TEXT NOT NULL DEFAULT '',
            result_status TEXT NOT NULL DEFAULT '',
            bottleneck_type TEXT NOT NULL DEFAULT '',
            quiz_format TEXT NOT NULL DEFAULT '',
            target_focus TEXT NOT NULL DEFAULT '',
            evidence TEXT NOT NULL DEFAULT '',
            ai_confidence TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
        )
        '''
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problem_bottleneck_problem_ref ON problem_bottleneck_events(problem_ref, created_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problem_bottleneck_student ON problem_bottleneck_events(student_id, created_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problem_bottleneck_type ON problem_bottleneck_events(bottleneck_type, created_at DESC)")


def _ensure_teacher_student_notes_table(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS teacher_student_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            teacher_id TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'continue_followup',
            next_followup_at TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_teacher_student_notes_student_created ON teacher_student_notes(student_id, created_at DESC)"
    )
    columns = _get_table_columns(cursor, "teacher_student_notes")
    if "intervention_type" not in columns:
        cursor.execute("ALTER TABLE teacher_student_notes ADD COLUMN intervention_type TEXT NOT NULL DEFAULT ''")
    if "target_issue" not in columns:
        cursor.execute("ALTER TABLE teacher_student_notes ADD COLUMN target_issue TEXT NOT NULL DEFAULT ''")


def _migrate_teacher_flags_table(cursor):
    columns = _get_table_columns(cursor, "teacher_flags")
    migrations = [
        ("severity", "ALTER TABLE teacher_flags ADD COLUMN severity TEXT NOT NULL DEFAULT 'medium'"),
        ("review_id", "ALTER TABLE teacher_flags ADD COLUMN review_id INTEGER"),
        ("checkin_id", "ALTER TABLE teacher_flags ADD COLUMN checkin_id INTEGER"),
        ("target_bridge", "ALTER TABLE teacher_flags ADD COLUMN target_bridge TEXT"),
        ("status", "ALTER TABLE teacher_flags ADD COLUMN status TEXT NOT NULL DEFAULT 'open'"),
    ]
    for column_name, ddl in migrations:
        if column_name not in columns:
            cursor.execute(ddl)


def _migrate_review_quizzes_table(cursor):
    columns = _get_table_columns(cursor, "review_quizzes")
    migrations = [
        ("bridge_feedback", "ALTER TABLE review_quizzes ADD COLUMN bridge_feedback TEXT NOT NULL DEFAULT ''"),
        ("distractor_feedback", "ALTER TABLE review_quizzes ADD COLUMN distractor_feedback TEXT NOT NULL DEFAULT '{}'"),
        ("template_id", "ALTER TABLE review_quizzes ADD COLUMN template_id INTEGER"),
    ]
    for column_name, ddl in migrations:
        if column_name not in columns:
            cursor.execute(ddl)


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 打卡表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        problem_url TEXT NOT NULL,
        problem_title TEXT NOT NULL,
        oj_source TEXT NOT NULL,
        completion_status TEXT NOT NULL,
        bottleneck_text TEXT NOT NULL,
        error_types TEXT NOT NULL,
        reflection TEXT,
        problem_context TEXT,
        submission_result TEXT,
        student_code TEXT,
        problem_tags TEXT NOT NULL DEFAULT '[]',
        chat_context_summary TEXT NOT NULL DEFAULT '',
        session_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # AI 复盘表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_id INTEGER NOT NULL UNIQUE,
        student_id TEXT NOT NULL,
        error_tags TEXT NOT NULL,
        diagnosis TEXT NOT NULL,
        next_action TEXT NOT NULL,
        suggested_topic TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (checkin_id) REFERENCES checkins(id)
    )
    ''')
    _migrate_reviews_table(cursor)
    _migrate_checkins_table(cursor)

    # 教师标记表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teacher_flags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        flag_type TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    _migrate_teacher_flags_table(cursor)

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS review_quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_id INTEGER NOT NULL,
        student_id TEXT NOT NULL,
        checkin_id INTEGER NOT NULL,
        round INTEGER NOT NULL DEFAULT 1,
        quiz_role TEXT NOT NULL DEFAULT 'main',
        quiz_type TEXT NOT NULL,
        question_text TEXT NOT NULL,
        options_json TEXT NOT NULL DEFAULT '[]',
        correct_answer TEXT NOT NULL,
        explanation TEXT NOT NULL DEFAULT '',
        bridge_feedback TEXT NOT NULL DEFAULT '',
        distractor_feedback TEXT NOT NULL DEFAULT '{}',
        template_id INTEGER,
        target_bridge TEXT NOT NULL DEFAULT '',
        source_error_layer TEXT NOT NULL DEFAULT 'insufficient',
        status TEXT NOT NULL DEFAULT 'pending',
        meta_json TEXT NOT NULL DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (review_id) REFERENCES reviews(id),
        FOREIGN KEY (checkin_id) REFERENCES checkins(id)
    )
    ''')
    _migrate_review_quizzes_table(cursor)

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS review_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            checkin_id INTEGER NOT NULL,
            student_id TEXT NOT NULL,
            event_name TEXT NOT NULL,
            review_mode TEXT NOT NULL,
            review_family TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (checkin_id) REFERENCES checkins(id)
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS review_manual_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL UNIQUE,
            checkin_id INTEGER NOT NULL,
            student_id TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            review_mode TEXT NOT NULL,
            review_family TEXT NOT NULL,
            mode_correct TEXT NOT NULL,
            review_grounded TEXT NOT NULL,
            student_can_move_next TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (review_id) REFERENCES reviews(id),
            FOREIGN KEY (checkin_id) REFERENCES checkins(id)
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS bridge_rule_draft_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_kind TEXT NOT NULL,
            bridge_id TEXT NOT NULL,
            parent_focus TEXT NOT NULL DEFAULT '',
            teacher_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            draft_filename TEXT NOT NULL DEFAULT '',
            draft_markdown TEXT NOT NULL DEFAULT '',
            auto_promote INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(route_kind, bridge_id, teacher_id)
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS bridge_registry_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_decision_id INTEGER NOT NULL UNIQUE,
            route_kind TEXT NOT NULL,
            bridge_id TEXT NOT NULL,
            parent_focus TEXT NOT NULL DEFAULT '',
            teacher_id TEXT NOT NULL,
            registry_status TEXT NOT NULL DEFAULT 'registry_only',
            resolver_enabled INTEGER NOT NULL DEFAULT 0,
            draft_filename TEXT NOT NULL DEFAULT '',
            draft_markdown TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(route_kind, bridge_id),
            FOREIGN KEY (draft_decision_id) REFERENCES bridge_rule_draft_decisions(id)
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS quiz_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_role TEXT NOT NULL,
            quiz_type TEXT NOT NULL,
            source_error_layer TEXT NOT NULL DEFAULT 'insufficient',
            target_bridge TEXT NOT NULL DEFAULT '',
            structure_type TEXT NOT NULL DEFAULT '',
            question_text TEXT NOT NULL,
            options_json TEXT NOT NULL DEFAULT '[]',
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL DEFAULT '',
            bridge_feedback TEXT NOT NULL DEFAULT '',
            distractor_feedback TEXT NOT NULL DEFAULT '{}',
            meta_json TEXT NOT NULL DEFAULT '{}',
            quality_score REAL NOT NULL DEFAULT 0,
            usage_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS quiz_template_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_template_id INTEGER NOT NULL,
            option_key TEXT NOT NULL DEFAULT '',
            child_template_id INTEGER NOT NULL,
            edge_type TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(parent_template_id, option_key, child_template_id, edge_type)
        )
        '''
    )

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        student_id TEXT NOT NULL,
        answer_text TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        feedback_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (quiz_id) REFERENCES review_quizzes(id)
    )
    ''')
    
    # 使用统计表（仅用于观察，不做复杂分析）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usage_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stat_date DATE NOT NULL,
        checkin_count INTEGER DEFAULT 0,
        rejected_count INTEGER DEFAULT 0,
        total_bottleneck_chars INTEGER DEFAULT 0,
        avg_bottleneck_chars REAL DEFAULT 0,
        UNIQUE(stat_date)
    )
    ''')

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS aichat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            problem_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            problem_title TEXT NOT NULL DEFAULT '',
            problem_url TEXT NOT NULL DEFAULT '',
            has_problem_context INTEGER NOT NULL DEFAULT 0,
            has_student_code INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS student_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            category TEXT NOT NULL,
            rating INTEGER NOT NULL,
            content TEXT NOT NULL,
            page_context TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    _ensure_teacher_announcements_table(cursor)
    _ensure_aichat_problem_closures_table(cursor)

    # 本地题库表（洛谷知识底座）
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS problems (
            problem_id INTEGER PRIMARY KEY AUTOINCREMENT,
            luogu_pid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            difficulty INTEGER,
            statement_json TEXT NOT NULL DEFAULT '{}',
            samples_json TEXT NOT NULL DEFAULT '[]',
            time_limit_ms INTEGER,
            memory_limit_kb INTEGER,
            raw_json TEXT NOT NULL DEFAULT '{}',
            source TEXT NOT NULL DEFAULT 'luogu',
            source_url TEXT NOT NULL,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS problem_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            tag_name TEXT NOT NULL,
            tag_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(problem_id, tag_name),
            FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
        )
        '''
    )
    _migrate_problems_table(cursor)
    _ensure_problem_bottleneck_events_table(cursor)
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS problem_analysis (
            problem_id INTEGER PRIMARY KEY,
            summary TEXT NOT NULL DEFAULT '',
            strategy_types TEXT NOT NULL DEFAULT '[]',
            knowledge_points TEXT NOT NULL DEFAULT '[]',
            common_mistakes TEXT NOT NULL DEFAULT '[]',
            analysis_version TEXT NOT NULL DEFAULT 'v1',
            status TEXT NOT NULL DEFAULT 'pending',
            last_error TEXT,
            retry_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS review_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            problem_id INTEGER,
            checkin_id INTEGER,
            prompt_tokens INTEGER NOT NULL DEFAULT 0,
            completion_tokens INTEGER NOT NULL DEFAULT 0,
            latency_ms INTEGER NOT NULL DEFAULT 0,
            model_tier TEXT NOT NULL DEFAULT 'lite',
            analysis_source TEXT,
            prompt_cache_hit INTEGER NOT NULL DEFAULT 0,
            review_result_json TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems(problem_id),
            FOREIGN KEY (checkin_id) REFERENCES checkins(id)
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS confirm_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            problem_url TEXT NOT NULL,
            structure_type TEXT NOT NULL UNIQUE,
            difficulty INTEGER,
            bridge_note TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'usable',
            skip_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
        )
        '''
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problem_tags_type_name ON problem_tags(tag_type, tag_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problem_analysis_status_updated ON problem_analysis(status, updated_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_sessions_problem ON review_sessions(problem_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_sessions_checkin ON review_sessions(checkin_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_confirm_pool_status_structure ON confirm_pool(status, structure_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_aichat_messages_student_created ON aichat_messages(student_id, created_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_aichat_messages_session ON aichat_messages(student_id, problem_id, session_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_feedback_created ON student_feedback(created_at DESC)")
    _ensure_teacher_announcements_table(cursor)
    _ensure_aichat_problem_closures_table(cursor)
    _ensure_aichat_problem_memory_table(cursor)
    _ensure_aichat_teaching_evidence_tables(cursor)
    _ensure_student_problem_completions_table(cursor)
    _ensure_teacher_student_notes_table(cursor)
    
    conn.commit()
    conn.close()
    print(f"[db] Database initialized at {DB_PATH}")


# ============ Teacher Announcement Operations ============

def create_teacher_announcement(
    *,
    title: str,
    body_markdown: str,
    created_by: str = "",
    pinned: bool = True,
    status: str = "published",
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_teacher_announcements_table(cursor)
    clean_title = (title or "").strip()
    clean_body = (body_markdown or "").strip()
    clean_status = status if status in {"published", "draft", "archived"} else "published"
    cursor.execute(
        '''
        INSERT INTO teacher_announcements
        (title, body_markdown, pinned, status, created_by, published_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''',
        (
            clean_title,
            clean_body,
            1 if pinned else 0,
            clean_status,
            (created_by or "").strip(),
        ),
    )
    announcement_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return announcement_id


def list_teacher_announcements(limit: int = 20, include_archived: bool = False) -> list[dict]:
    safe_limit = max(1, min(int(limit or 20), 100))
    conn = get_db()
    cursor = conn.cursor()
    _ensure_teacher_announcements_table(cursor)
    where_sql = "" if include_archived else "WHERE status != 'archived'"
    cursor.execute(
        f'''
        SELECT id, title, body_markdown, pinned, status, created_by, created_at, updated_at, published_at
        FROM teacher_announcements
        {where_sql}
        ORDER BY pinned DESC, published_at DESC, id DESC
        LIMIT ?
        ''',
        (safe_limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_student_announcement() -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_teacher_announcements_table(cursor)
    cursor.execute(
        '''
        SELECT id, title, body_markdown, pinned, status, created_by, created_at, updated_at, published_at
        FROM teacher_announcements
        WHERE status = 'published'
        ORDER BY pinned DESC, published_at DESC, id DESC
        LIMIT 1
        '''
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def set_teacher_announcement_status(announcement_id: int, status: str) -> dict | None:
    clean_status = status if status in {"published", "draft", "archived"} else "published"
    conn = get_db()
    cursor = conn.cursor()
    _ensure_teacher_announcements_table(cursor)
    cursor.execute(
        '''
        UPDATE teacher_announcements
        SET status = ?,
            updated_at = CURRENT_TIMESTAMP,
            published_at = CASE WHEN ? = 'published' THEN CURRENT_TIMESTAMP ELSE published_at END
        WHERE id = ?
        ''',
        (clean_status, clean_status, int(announcement_id)),
    )
    conn.commit()
    cursor.execute(
        '''
        SELECT id, title, body_markdown, pinned, status, created_by, created_at, updated_at, published_at
        FROM teacher_announcements
        WHERE id = ?
        ''',
        (int(announcement_id),),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============ Student Feedback Operations ============

def create_student_feedback(
    *,
    student_id: str,
    category: str,
    rating: int,
    content: str,
    page_context: str = "",
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_student_feedback_table(cursor)
    cursor.execute(
        '''
        INSERT INTO student_feedback
        (student_id, category, rating, content, page_context)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (
            student_id,
            (category or "other").strip() or "other",
            int(rating),
            (content or "").strip(),
            (page_context or "").strip()[:300],
        ),
    )
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return feedback_id


def list_student_feedback(limit: int = 100, offset: int = 0) -> list[dict]:
    safe_limit = max(1, min(int(limit or 100), 200))
    safe_offset = max(0, int(offset or 0))
    conn = get_db()
    cursor = conn.cursor()
    _ensure_student_feedback_table(cursor)
    cursor.execute(
        '''
        SELECT id, student_id, category, rating, content, page_context, status, created_at
        FROM student_feedback
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        ''',
        (safe_limit, safe_offset),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ============ Student Problem Completion Operations ============

COMPLETION_METHOD_LABELS = {
    "self_solved": "自己做出来",
    "small_hint": "少量提示后完成",
    "classroom_taught": "课堂讲解后完成",
    "aichat_assisted": "AIChat 帮助后完成",
    "editorial_completed": "看题解后补完",
    "unsure": "还没完全确定",
}

COMPLETION_RESULT_LABELS = {
    "accepted": "AC",
    "sample_passed": "样例通过，还没提交",
    "unsure": "还不确定",
}


def _completion_confidence_note(reported_completion: str, key_step_summary: str) -> str:
    summary = (key_step_summary or "").strip()
    if len(summary) >= 12:
        return "已经写下关键做法，后续可以配合小验证确认是否真正掌握。"
    if reported_completion == "self_solved":
        return "已记录为自己做出，但还需要补一句关键原因，方便老师判断是否真的会了。"
    return "已记录完成情况，但还需要补一句关键原因，方便老师判断是否真的会了。"


def _inferred_support_level(reported_completion: str) -> str:
    if reported_completion == "self_solved":
        return "independent_claim"
    if reported_completion == "small_hint":
        return "light_support"
    if reported_completion == "classroom_taught":
        return "teacher_supported"
    if reported_completion == "aichat_assisted":
        return "ai_supported"
    if reported_completion == "editorial_completed":
        return "editorial_supported"
    return "unknown"


def _completion_points_awarded(reported_completion: str, result_status: str, key_step_summary: str) -> int:
    if reported_completion == "unsure" or result_status == "unsure":
        return 0
    has_clear_summary = len((key_step_summary or "").strip()) >= 12
    if reported_completion == "self_solved":
        return 3 if has_clear_summary and result_status == "accepted" else 1
    if reported_completion in {"small_hint", "classroom_taught"}:
        return 2 if has_clear_summary else 1
    if reported_completion in {"aichat_assisted", "editorial_completed"}:
        return 1
    return 0


def _support_fadeout_label(total: int, lower_support: int, higher_support: int) -> str:
    if total <= 0:
        return "还没有足够做题记录，先不用下结论。"
    if lower_support > higher_support:
        return "近 15 天自己完成或少量提示后完成的题更多，可以安排同类题继续独立试。"
    if higher_support > lower_support:
        return "近 15 天更多题是在 AIChat 或题解帮助后完成，建议老师挑一题当面确认关键步骤。"
    return "近 15 天自己完成和提示后完成比较接近，建议继续观察下一批同类题。"


def create_student_problem_completion(
    *,
    student_id: str,
    problem_id: str = "",
    problem_title: str = "",
    problem_url: str = "",
    reported_completion: str = "unsure",
    result_status: str = "unsure",
    key_step_summary: str = "",
    session_id: str = "",
) -> dict:
    clean_reported = reported_completion if reported_completion in COMPLETION_METHOD_LABELS else "unsure"
    clean_result = result_status if result_status in COMPLETION_RESULT_LABELS else "unsure"
    confidence_note = _completion_confidence_note(clean_reported, key_step_summary)
    points_awarded = _completion_points_awarded(clean_reported, clean_result, key_step_summary)
    conn = get_db()
    cursor = conn.cursor()
    _ensure_student_problem_completions_table(cursor)
    cursor.execute(
        '''
        INSERT INTO student_problem_completions
            (student_id, problem_id, problem_title, problem_url, reported_completion,
             inferred_support_level, result_status, key_step_summary, confidence_note, points_awarded, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            student_id or "",
            problem_id or "",
            problem_title or "",
            problem_url or "",
            clean_reported,
            _inferred_support_level(clean_reported),
            clean_result,
            (key_step_summary or "").strip(),
            confidence_note,
            points_awarded,
            session_id or "",
        ),
    )
    record_id = cursor.lastrowid
    conn.commit()
    cursor.execute(
        '''
        SELECT *
        FROM student_problem_completions
        WHERE id = ?
        ''',
        (record_id,),
    )
    row = cursor.fetchone()
    conn.close()
    record = dict(row)
    record["reported_completion_label"] = COMPLETION_METHOD_LABELS.get(record.get("reported_completion"), "未记录")
    record["result_status_label"] = COMPLETION_RESULT_LABELS.get(record.get("result_status"), "未记录")
    return record


def list_student_problem_completions(student_id: str, limit: int = 20, days: int = 30) -> list[dict]:
    safe_limit = max(1, min(int(limit or 20), 100))
    safe_days = max(1, min(int(days or 30), 365))
    conn = get_db()
    cursor = conn.cursor()
    _ensure_student_problem_completions_table(cursor)
    cursor.execute(
        '''
        SELECT *
        FROM student_problem_completions
        WHERE student_id = ?
          AND created_at >= datetime('now', ?)
        ORDER BY id DESC
        LIMIT ?
        ''',
        (student_id, f"-{safe_days} days", safe_limit),
    )
    rows = cursor.fetchall()
    conn.close()
    records = []
    for row in rows:
        record = dict(row)
        record["reported_completion_label"] = COMPLETION_METHOD_LABELS.get(record.get("reported_completion"), "未记录")
        record["result_status_label"] = COMPLETION_RESULT_LABELS.get(record.get("result_status"), "未记录")
        records.append(record)
    return records


def get_student_completion_summary(student_id: str, days: int = 15) -> dict:
    safe_days = max(1, min(int(days or 15), 365))
    conn = get_db()
    cursor = conn.cursor()
    _ensure_student_problem_completions_table(cursor)
    cursor.execute(
        '''
        SELECT
            COUNT(*) AS total_count,
            SUM(CASE WHEN reported_completion = 'self_solved' THEN 1 ELSE 0 END) AS self_solved_count,
            SUM(CASE WHEN reported_completion = 'aichat_assisted' THEN 1 ELSE 0 END) AS aichat_assisted_count,
            SUM(CASE WHEN reported_completion = 'small_hint' THEN 1 ELSE 0 END) AS small_hint_count,
            SUM(CASE WHEN reported_completion = 'classroom_taught' THEN 1 ELSE 0 END) AS classroom_taught_count,
            SUM(CASE WHEN reported_completion = 'editorial_completed' THEN 1 ELSE 0 END) AS editorial_count,
            SUM(CASE WHEN result_status = 'accepted' THEN 1 ELSE 0 END) AS accepted_count,
            SUM(CASE WHEN LENGTH(TRIM(key_step_summary)) < 12 THEN 1 ELSE 0 END) AS weak_summary_count,
            COALESCE(SUM(points_awarded), 0) AS points
        FROM student_problem_completions
        WHERE student_id = ?
          AND created_at >= datetime('now', ?)
        ''',
        (student_id, f"-{safe_days} days"),
    )
    row = cursor.fetchone()
    conn.close()
    total = int((row or {"total_count": 0})["total_count"] or 0)
    self_solved = int((row or {"self_solved_count": 0})["self_solved_count"] or 0)
    aichat_assisted = int((row or {"aichat_assisted_count": 0})["aichat_assisted_count"] or 0)
    small_hint = int((row or {"small_hint_count": 0})["small_hint_count"] or 0)
    classroom_taught = int((row or {"classroom_taught_count": 0})["classroom_taught_count"] or 0)
    editorial = int((row or {"editorial_count": 0})["editorial_count"] or 0)
    accepted = int((row or {"accepted_count": 0})["accepted_count"] or 0)
    weak_summary = int((row or {"weak_summary_count": 0})["weak_summary_count"] or 0)
    points = int((row or {"points": 0})["points"] or 0)
    lower_support = self_solved + small_hint
    higher_support = aichat_assisted + editorial
    independence_ratio = round(lower_support / total, 3) if total else 0.0
    if total == 0:
        trend = "近 15 天还没有完成记录，老师需要结合课堂观察判断。"
    elif weak_summary == total:
        trend = "已经记录了做题结果，可以补一句关键做法，方便老师知道你真正理解了哪一步。"
    elif aichat_assisted > max(self_solved, small_hint, editorial):
        trend = "这段时间主要借助 AIChat 完成，可以挑一道同类低难度题先自己试。"
    elif editorial > 0 and editorial >= lower_support:
        trend = "这段时间有看题解补完的记录，建议补一句关键做法，再找一道同类题确认。"
    elif lower_support > higher_support:
        trend = "这段时间自己做出或少量提示后做出的题更多，可以继续安排同类题独立试。"
    else:
        trend = "这段时间已有做题记录，建议每题补一句关键做法，方便之后回顾。"
    return {
        "days": safe_days,
        "last_15_days": total,
        "self_solved_15_days": self_solved,
        "aichat_assisted_15_days": aichat_assisted,
        "small_hint_15_days": small_hint,
        "classroom_taught_15_days": classroom_taught,
        "editorial_15_days": editorial,
        "accepted_15_days": accepted,
        "weak_summary_15_days": weak_summary,
        "points_15_days": points,
        "support_trend": trend,
        "independent_or_small_hint_15_days": lower_support,
        "supported_or_editorial_15_days": higher_support,
        "independence_ratio": independence_ratio,
        "support_fadeout_label": _support_fadeout_label(total, lower_support, higher_support),
    }


def get_class_completion_summary(days: int = 15) -> dict:
    safe_days = max(1, min(int(days or 15), 365))
    conn = get_db()
    cursor = conn.cursor()
    _ensure_student_problem_completions_table(cursor)
    cursor.execute(
        '''
        SELECT
            COUNT(*) AS total_count,
            COUNT(DISTINCT student_id) AS student_count,
            SUM(CASE WHEN reported_completion = 'self_solved' THEN 1 ELSE 0 END) AS self_solved_count,
            SUM(CASE WHEN reported_completion = 'aichat_assisted' THEN 1 ELSE 0 END) AS aichat_assisted_count,
            SUM(CASE WHEN reported_completion = 'small_hint' THEN 1 ELSE 0 END) AS small_hint_count,
            SUM(CASE WHEN reported_completion = 'classroom_taught' THEN 1 ELSE 0 END) AS classroom_taught_count,
            SUM(CASE WHEN reported_completion = 'editorial_completed' THEN 1 ELSE 0 END) AS editorial_count,
            SUM(CASE WHEN result_status = 'accepted' THEN 1 ELSE 0 END) AS accepted_count,
            COALESCE(SUM(points_awarded), 0) AS points
        FROM student_problem_completions
        WHERE created_at >= datetime('now', ?)
        ''',
        (f"-{safe_days} days",),
    )
    row = cursor.fetchone()
    conn.close()
    total = int((row or {"total_count": 0})["total_count"] or 0)
    self_solved = int((row or {"self_solved_count": 0})["self_solved_count"] or 0)
    aichat_assisted = int((row or {"aichat_assisted_count": 0})["aichat_assisted_count"] or 0)
    small_hint = int((row or {"small_hint_count": 0})["small_hint_count"] or 0)
    classroom_taught = int((row or {"classroom_taught_count": 0})["classroom_taught_count"] or 0)
    editorial = int((row or {"editorial_count": 0})["editorial_count"] or 0)
    lower_support = self_solved + small_hint
    higher_support = aichat_assisted + editorial
    return {
        "days": safe_days,
        "total_15_days": total,
        "student_count_15_days": int((row or {"student_count": 0})["student_count"] or 0),
        "self_solved_15_days": self_solved,
        "aichat_assisted_15_days": aichat_assisted,
        "small_hint_15_days": small_hint,
        "classroom_taught_15_days": classroom_taught,
        "editorial_15_days": editorial,
        "accepted_15_days": int((row or {"accepted_count": 0})["accepted_count"] or 0),
        "points_15_days": int((row or {"points": 0})["points"] or 0),
        "independent_or_small_hint_15_days": lower_support,
        "supported_or_editorial_15_days": higher_support,
        "independence_ratio": round(lower_support / total, 3) if total else 0.0,
        "support_fadeout_label": _support_fadeout_label(total, lower_support, higher_support),
    }


# ============ AIChat Problem Closure Operations ============

def create_aichat_problem_closure(
    *,
    student_id: str,
    problem_id: str,
    session_id: str,
    problem_title: str,
    question: str,
    target_focus: str = "",
    status: str = "quiz_ready",
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_problem_closures_table(cursor)
    cursor.execute(
        '''
        INSERT INTO aichat_problem_closures
        (student_id, problem_id, session_id, problem_title, status, question, target_focus)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            student_id,
            problem_id or "",
            session_id or "",
            problem_title or "",
            status or "quiz_ready",
            question or "",
            target_focus or "",
        ),
    )
    closure_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return closure_id


def get_aichat_problem_closure(closure_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_problem_closures_table(cursor)
    cursor.execute(
        '''
        SELECT
            id,
            student_id,
            problem_id,
            session_id,
            problem_title,
            status,
            question,
            target_focus,
            answer,
            feedback,
            followup,
            points_awarded,
            next_review_at,
            created_at,
            updated_at
        FROM aichat_problem_closures
        WHERE id = ?
        ''',
        (closure_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def grade_aichat_problem_closure(
    *,
    closure_id: int,
    student_id: str,
    status: str,
    answer: str,
    feedback: str,
    followup: str = "",
    points_awarded: int = 0,
    next_review_at: str = "",
) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_problem_closures_table(cursor)
    cursor.execute(
        '''
        UPDATE aichat_problem_closures
        SET status = ?,
            answer = ?,
            feedback = ?,
            followup = ?,
            points_awarded = ?,
            next_review_at = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND student_id = ?
        ''',
        (
            status or "failed",
            answer or "",
            feedback or "",
            followup or "",
            int(points_awarded or 0),
            next_review_at or "",
            closure_id,
            student_id,
        ),
    )
    conn.commit()
    conn.close()
    return get_aichat_problem_closure(closure_id)


def create_problem_bottleneck_event(
    *,
    student_id: str,
    problem_ref: str,
    problem_id: int | None = None,
    session_id: str = "",
    source_event: str,
    result_status: str,
    bottleneck_type: str = "",
    quiz_format: str = "",
    target_focus: str = "",
    evidence: str = "",
    ai_confidence: str = "",
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_problem_bottleneck_events_table(cursor)
    cursor.execute(
        '''
        INSERT INTO problem_bottleneck_events
        (student_id, problem_ref, problem_id, session_id, source_event, result_status,
         bottleneck_type, quiz_format, target_focus, evidence, ai_confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            student_id or "",
            problem_ref or "",
            problem_id,
            session_id or "",
            source_event or "",
            result_status or "",
            bottleneck_type or "",
            quiz_format or "",
            target_focus or "",
            evidence or "",
            ai_confidence or "",
        ),
    )
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id


def list_problem_bottleneck_events(
    *,
    problem_ref: str = "",
    problem_id: int | None = None,
    student_id: str = "",
    limit: int = 20,
) -> list[dict]:
    safe_limit = max(1, min(int(limit or 20), 200))
    clauses = []
    params = []
    if problem_ref:
        clauses.append("problem_ref = ?")
        params.append(problem_ref)
    if problem_id is not None:
        clauses.append("problem_id = ?")
        params.append(problem_id)
    if student_id:
        clauses.append("student_id = ?")
        params.append(student_id)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    conn = get_db()
    cursor = conn.cursor()
    _ensure_problem_bottleneck_events_table(cursor)
    cursor.execute(
        f'''
        SELECT *
        FROM problem_bottleneck_events
        {where_sql}
        ORDER BY id DESC
        LIMIT ?
        ''',
        (*params, safe_limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


EXIT_TRIGGER_SOURCE_EVENTS = {
    "aichat_exit_ready",
    "closure_quiz",
    "problem_closure_passed",
    "problem_closure_failed",
}


def has_problem_bottleneck_event(
    *,
    student_id: str,
    problem_ref: str,
    session_id: str = "",
    source_event: str,
) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_problem_bottleneck_events_table(cursor)
    cursor.execute(
        '''
        SELECT 1
        FROM problem_bottleneck_events
        WHERE student_id = ?
          AND problem_ref = ?
          AND session_id = ?
          AND source_event = ?
        LIMIT 1
        ''',
        (student_id or "", problem_ref or "", session_id or "", source_event or ""),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def _exit_trigger_summary_from_where(where_sql: str, params: tuple) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_problem_bottleneck_events_table(cursor)
    cursor.execute(
        f'''
        SELECT
            COUNT(*) AS total_count,
            SUM(CASE WHEN source_event = 'aichat_exit_ready' THEN 1 ELSE 0 END) AS exit_ready_count,
            SUM(CASE WHEN source_event = 'closure_quiz' THEN 1 ELSE 0 END) AS closure_quiz_count,
            SUM(CASE WHEN source_event = 'problem_closure_passed' THEN 1 ELSE 0 END) AS closure_passed_count,
            SUM(CASE WHEN source_event = 'problem_closure_failed' THEN 1 ELSE 0 END) AS closure_failed_count
        FROM problem_bottleneck_events
        {where_sql}
        ''',
        params,
    )
    row = cursor.fetchone()
    conn.close()
    return {
        "total_exit_events": int((row or {"total_count": 0})["total_count"] or 0),
        "exit_ready_count": int((row or {"exit_ready_count": 0})["exit_ready_count"] or 0),
        "closure_quiz_count": int((row or {"closure_quiz_count": 0})["closure_quiz_count"] or 0),
        "closure_passed_count": int((row or {"closure_passed_count": 0})["closure_passed_count"] or 0),
        "closure_failed_count": int((row or {"closure_failed_count": 0})["closure_failed_count"] or 0),
    }


def get_student_exit_trigger_summary(student_id: str, days: int = 15) -> dict:
    safe_days = max(1, min(int(days or 15), 365))
    event_marks = ",".join("?" for _ in EXIT_TRIGGER_SOURCE_EVENTS)
    summary = _exit_trigger_summary_from_where(
        f'''
        WHERE student_id = ?
          AND created_at >= datetime('now', ?)
          AND source_event IN ({event_marks})
        ''',
        (student_id or "", f"-{safe_days} days", *sorted(EXIT_TRIGGER_SOURCE_EVENTS)),
    )
    summary["days"] = safe_days
    return summary


def get_class_exit_trigger_summary(days: int = 15) -> dict:
    safe_days = max(1, min(int(days or 15), 365))
    event_marks = ",".join("?" for _ in EXIT_TRIGGER_SOURCE_EVENTS)
    summary = _exit_trigger_summary_from_where(
        f'''
        WHERE created_at >= datetime('now', ?)
          AND source_event IN ({event_marks})
        ''',
        (f"-{safe_days} days", *sorted(EXIT_TRIGGER_SOURCE_EVENTS)),
    )
    summary["days"] = safe_days
    return summary


# ============ Checkin Operations ============

def create_checkin(
    student_id: str,
    problem_url: str,
    problem_title: str,
    oj_source: str,
    completion_status: str,
    bottleneck_text: str,
    error_types: list,
    reflection: str = None,
    problem_context: str = None,
    submission_result: str = None,
    student_code: str = None,
    problem_tags: list = None,
    chat_context_summary: str = "",
    session_id: str = None,
) -> int:
    """创建打卡记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO checkins
    (student_id, problem_url, problem_title, oj_source, completion_status, bottleneck_text, error_types, reflection,
     problem_context, submission_result, student_code, problem_tags, chat_context_summary, session_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id, problem_url, problem_title, oj_source,
        completion_status, bottleneck_text, json.dumps(error_types), reflection,
        problem_context, submission_result, student_code, json.dumps(problem_tags or [], ensure_ascii=False),
        (chat_context_summary or "")[:600], session_id,
    ))
    checkin_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return checkin_id


def upsert_luogu_problemset(problem_payload: dict, classify_tag) -> int:
    conn = get_db()
    cursor = conn.cursor()

    limits = problem_payload.get("limits") or {}
    time_limits = [int(item) for item in (limits.get("time") or []) if isinstance(item, int) or str(item).isdigit()]
    memory_limits = [int(item) for item in (limits.get("memory") or []) if isinstance(item, int) or str(item).isdigit()]
    time_limit_ms = max(time_limits) if time_limits else None
    memory_limit_kb = max(memory_limits) if memory_limits else None
    statement_json = json.dumps(
        {
            "description": problem_payload.get("description") or "",
            "inputFormat": problem_payload.get("inputFormat") or "",
            "outputFormat": problem_payload.get("outputFormat") or "",
            "hint": problem_payload.get("hint") or "",
        },
        ensure_ascii=False,
    )
    samples_json = json.dumps(problem_payload.get("samples") or [], ensure_ascii=False)
    raw_json = json.dumps(problem_payload, ensure_ascii=False)
    pid = str(problem_payload.get("pid") or "").strip()
    source_url = f"https://www.luogu.com.cn/problem/{pid}"

    cursor.execute(
        '''
        INSERT INTO problems
        (luogu_pid, source_problem_id, canonical_url, title, difficulty, statement_json, samples_json, time_limit_ms, memory_limit_kb, raw_json, source, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'luogu', ?)
        ON CONFLICT(luogu_pid) DO UPDATE SET
            source_problem_id=excluded.source_problem_id,
            canonical_url=excluded.canonical_url,
            title=excluded.title,
            difficulty=excluded.difficulty,
            statement_json=excluded.statement_json,
            samples_json=excluded.samples_json,
            time_limit_ms=excluded.time_limit_ms,
            memory_limit_kb=excluded.memory_limit_kb,
            raw_json=excluded.raw_json,
            source_url=excluded.source_url,
            updated_at=CURRENT_TIMESTAMP
        ''',
        (
            pid,
            pid,
            source_url,
            problem_payload.get("title") or pid,
            problem_payload.get("difficulty"),
            statement_json,
            samples_json,
            time_limit_ms,
            memory_limit_kb,
            raw_json,
            source_url,
        ),
    )
    cursor.execute("SELECT problem_id FROM problems WHERE luogu_pid = ?", (pid,))
    problem_id = cursor.fetchone()["problem_id"]

    cursor.execute("DELETE FROM problem_tags WHERE problem_id = ?", (problem_id,))
    tag_rows = []
    for raw_tag in problem_payload.get("tags") or []:
        tag = str(raw_tag).strip()
        if not tag:
            continue
        tag_rows.append((problem_id, tag, classify_tag(tag)))
    if tag_rows:
        cursor.executemany(
            '''
            INSERT OR IGNORE INTO problem_tags (problem_id, tag_name, tag_type)
            VALUES (?, ?, ?)
            ''',
            tag_rows,
        )

    conn.commit()
    conn.close()
    return problem_id


def upsert_external_problem(
    *,
    source: str,
    source_problem_id: str,
    title: str,
    problem_context: str,
    problem_url: str,
    problem_tags: list[str] | None = None,
    tag_type: str = "ai",
    difficulty: int | None = None,
    samples: list | None = None,
    time_limit_ms: int | None = None,
    memory_limit_kb: int | None = None,
    raw_payload: dict | None = None,
) -> int:
    normalized_source = (source or "other").strip().lower() or "other"
    normalized_ref = str(source_problem_id or "").strip()
    if not normalized_ref:
        normalized_ref = str(problem_url or "").strip() or "unknown"
    generic_pid = normalized_ref if normalized_source == "luogu" else f"{normalized_source}:{normalized_ref}"
    statement_json = json.dumps(
        {
            "description": problem_context or "",
            "inputFormat": "",
            "outputFormat": "",
            "hint": "",
        },
        ensure_ascii=False,
    )
    samples_json = json.dumps(samples or [], ensure_ascii=False)
    raw_json = json.dumps(raw_payload or {}, ensure_ascii=False)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO problems
        (luogu_pid, source_problem_id, canonical_url, title, difficulty, statement_json, samples_json,
         time_limit_ms, memory_limit_kb, raw_json, source, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(luogu_pid) DO UPDATE SET
            source_problem_id=excluded.source_problem_id,
            canonical_url=excluded.canonical_url,
            title=excluded.title,
            difficulty=excluded.difficulty,
            statement_json=excluded.statement_json,
            samples_json=excluded.samples_json,
            time_limit_ms=excluded.time_limit_ms,
            memory_limit_kb=excluded.memory_limit_kb,
            raw_json=excluded.raw_json,
            source=excluded.source,
            source_url=excluded.source_url,
            updated_at=CURRENT_TIMESTAMP
        ''',
        (
            generic_pid,
            normalized_ref,
            problem_url or "",
            title or generic_pid,
            difficulty,
            statement_json,
            samples_json,
            time_limit_ms,
            memory_limit_kb,
            raw_json,
            normalized_source,
            problem_url or "",
        ),
    )
    cursor.execute("SELECT problem_id FROM problems WHERE luogu_pid = ?", (generic_pid,))
    problem_id = cursor.fetchone()["problem_id"]

    clean_tag_type = (tag_type or "ai").strip() or "ai"
    cursor.execute("DELETE FROM problem_tags WHERE problem_id = ? AND tag_type = ?", (problem_id, clean_tag_type))
    tag_rows = []
    seen = set()
    for raw_tag in problem_tags or []:
        tag = str(raw_tag).strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tag_rows.append((problem_id, tag, clean_tag_type))
    if tag_rows:
        cursor.executemany(
            '''
            INSERT OR IGNORE INTO problem_tags (problem_id, tag_name, tag_type)
            VALUES (?, ?, ?)
            ''',
            tag_rows,
        )
    conn.commit()
    conn.close()
    return problem_id


def upsert_confirm_pool_entry(
    problem_id: int,
    problem_url: str,
    structure_type: str,
    difficulty: int | None,
    bridge_note: str,
    status: str = "usable",
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO confirm_pool
        (problem_id, problem_url, structure_type, difficulty, bridge_note, status, skip_count)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        ON CONFLICT(structure_type) DO UPDATE SET
            problem_id=excluded.problem_id,
            problem_url=excluded.problem_url,
            difficulty=excluded.difficulty,
            bridge_note=excluded.bridge_note,
            status=excluded.status,
            skip_count=0,
            updated_at=CURRENT_TIMESTAMP
        ''',
        (problem_id, problem_url, structure_type, difficulty, bridge_note, status),
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id


def get_confirm_pool_entry(structure_type: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT *
        FROM confirm_pool
        WHERE structure_type = ?
        LIMIT 1
        ''',
        (structure_type,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def increment_confirm_pool_skip(structure_type: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE confirm_pool
        SET skip_count = skip_count + 1,
            status = CASE
                WHEN skip_count + 1 >= 4 THEN 'needs_backfill'
                ELSE status
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE structure_type = ?
        ''',
        (structure_type,),
    )
    cursor.execute(
        '''
        SELECT *
        FROM confirm_pool
        WHERE structure_type = ?
        LIMIT 1
        ''',
        (structure_type,),
    )
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return dict(row) if row else None


def get_problem_by_luogu_pid(luogu_pid: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems WHERE luogu_pid = ?", (luogu_pid,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_problem_by_source_ref(source: str, source_problem_id: str) -> dict | None:
    normalized_source = (source or "luogu").strip().lower() or "luogu"
    normalized_ref = str(source_problem_id or "").strip()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM problems WHERE source = ? AND source_problem_id = ? LIMIT 1",
        (normalized_source, normalized_ref),
    )
    row = cursor.fetchone()
    if not row:
        legacy_pid = normalized_ref if normalized_source == "luogu" else f"{normalized_source}:{normalized_ref}"
        cursor.execute("SELECT * FROM problems WHERE luogu_pid = ? LIMIT 1", (legacy_pid,))
        row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_problem_tags(problem_id: int, tag_type: str | None = None) -> list[str]:
    conn = get_db()
    cursor = conn.cursor()
    if tag_type:
        cursor.execute(
            "SELECT tag_name FROM problem_tags WHERE problem_id = ? AND tag_type = ? ORDER BY tag_name ASC",
            (problem_id, tag_type),
        )
    else:
        cursor.execute(
            "SELECT tag_name FROM problem_tags WHERE problem_id = ? ORDER BY tag_name ASC",
            (problem_id,),
        )
    rows = cursor.fetchall()
    conn.close()
    return [row["tag_name"] for row in rows]


def list_related_problems_by_luogu_pid(luogu_pid: str, limit: int = 4) -> list[dict]:
    source = get_problem_by_luogu_pid(luogu_pid)
    if not source:
        return []

    source_tags = get_problem_tags(source["problem_id"], tag_type="algo")
    if not source_tags:
        return []

    conn = get_db()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in source_tags)
    params = [source["problem_id"], *source_tags, source.get("difficulty"), limit]
    cursor.execute(
        f'''
        SELECT
            p.problem_id,
            p.luogu_pid,
            p.title,
            p.difficulty,
            COUNT(DISTINCT pt.tag_name) AS overlap_count
        FROM problems p
        JOIN problem_tags pt ON p.problem_id = pt.problem_id
        WHERE p.problem_id != ?
          AND pt.tag_type = 'algo'
          AND pt.tag_name IN ({placeholders})
        GROUP BY p.problem_id
        HAVING overlap_count > 0
        ORDER BY
            overlap_count DESC,
            ABS(COALESCE(p.difficulty, 0) - COALESCE(?, 0)) ASC,
            p.luogu_pid ASC
        LIMIT ?
        ''',
        params,
    )
    rows = cursor.fetchall()
    conn.close()

    related = []
    for row in rows:
        tags = get_problem_tags(row["problem_id"], tag_type="algo")
        overlap_tags = [tag for tag in tags if tag in source_tags][:3]
        related.append(
            {
                "problem_id": row["problem_id"],
                "pid": row["luogu_pid"],
                "title": row["title"],
                "difficulty": row["difficulty"],
                "tags": overlap_tags,
                "url": f"https://www.luogu.com.cn/problem/{row['luogu_pid']}",
                "reason": f"同类标签：{' / '.join(overlap_tags)}" if overlap_tags else "同类算法标签题",
            }
        )
    return related


def get_problem_analysis(problem_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problem_analysis WHERE problem_id = ?", (problem_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "problem_id": row["problem_id"],
        "summary": row["summary"],
        "strategy_types": _json_loads_or_default(row["strategy_types"], []),
        "knowledge_points": _json_loads_or_default(row["knowledge_points"], []),
        "common_mistakes": _json_loads_or_default(row["common_mistakes"], []),
        "analysis_version": row["analysis_version"],
        "status": row["status"],
        "last_error": row["last_error"],
        "retry_count": row["retry_count"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_problem_analysis_placeholder(problem_id: int, analysis_version: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM problem_analysis WHERE problem_id = ?", (problem_id,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return False

    cursor.execute(
        '''
        INSERT INTO problem_analysis (problem_id, analysis_version, status)
        VALUES (?, ?, 'pending')
        ''',
        (problem_id, analysis_version),
    )
    conn.commit()
    conn.close()
    return True


def upsert_luogu_problem_analysis(
    problem_id: int,
    summary: str,
    strategy_types: list[str],
    knowledge_points: list[str],
    common_mistakes: list[str],
    analysis_version: str,
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO problem_analysis
        (problem_id, summary, strategy_types, knowledge_points, common_mistakes, analysis_version, status, last_error, retry_count)
        VALUES (?, ?, ?, ?, ?, ?, 'completed', NULL, 0)
        ON CONFLICT(problem_id) DO UPDATE SET
            summary=excluded.summary,
            strategy_types=excluded.strategy_types,
            knowledge_points=excluded.knowledge_points,
            common_mistakes=excluded.common_mistakes,
            analysis_version=excluded.analysis_version,
            status='completed',
            last_error=NULL,
            retry_count=0,
            updated_at=CURRENT_TIMESTAMP
        ''',
        (
            problem_id,
            summary,
            json.dumps(strategy_types, ensure_ascii=False),
            json.dumps(knowledge_points, ensure_ascii=False),
            json.dumps(common_mistakes, ensure_ascii=False),
            analysis_version,
        ),
    )
    conn.commit()
    conn.close()


def mark_problem_analysis_failed(problem_id: int, error_message: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO problem_analysis (problem_id, status, last_error, retry_count)
        VALUES (?, 'failed', ?, 1)
        ON CONFLICT(problem_id) DO UPDATE SET
            status='failed',
            last_error=excluded.last_error,
            retry_count=problem_analysis.retry_count + 1,
            updated_at=CURRENT_TIMESTAMP
        ''',
        (problem_id, error_message[:500]),
    )
    conn.commit()
    conn.close()


def reset_problem_analysis_for_retry(problem_id: int, analysis_version: str) -> None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO problem_analysis (problem_id, analysis_version, status, last_error)
        VALUES (?, ?, 'pending', NULL)
        ON CONFLICT(problem_id) DO UPDATE SET
            analysis_version=excluded.analysis_version,
            status='pending',
            last_error=NULL,
            updated_at=CURRENT_TIMESTAMP
        ''',
        (problem_id, analysis_version),
    )
    conn.commit()
    conn.close()


def list_problem_analysis_failures(limit: int = 50) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            p.problem_id,
            p.luogu_pid,
            p.title,
            pa.status,
            pa.last_error,
            pa.retry_count,
            pa.updated_at
        FROM problem_analysis pa
        JOIN problems p ON p.problem_id = pa.problem_id
        WHERE pa.status = 'failed'
        ORDER BY pa.updated_at DESC
        LIMIT ?
        ''',
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "problem_id": row["problem_id"],
            "luogu_pid": row["luogu_pid"],
            "title": row["title"],
            "status": row["status"],
            "last_error": row["last_error"],
            "retry_count": row["retry_count"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]


def create_review_session(
    student_id: str,
    problem_id: int | None,
    checkin_id: int | None,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    model_tier: str,
    analysis_source: str | None,
    prompt_cache_hit: bool,
    review_result_json: dict,
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO review_sessions
        (student_id, problem_id, checkin_id, prompt_tokens, completion_tokens, latency_ms, model_tier, analysis_source, prompt_cache_hit, review_result_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            student_id,
            problem_id,
            checkin_id,
            prompt_tokens,
            completion_tokens,
            latency_ms,
            model_tier,
            analysis_source,
            1 if prompt_cache_hit else 0,
            json.dumps(review_result_json, ensure_ascii=False),
        ),
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_student_checkins(student_id: str, limit: int = 50) -> list:
    """获取学生的打卡历史"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT
        c.*,
        r.id as review_id,
        r.review_status,
        r.learning_status,
        r.remedy_count,
        r.understanding_self_check,
        r.bridge_path,
        r.mastery_status,
        r.review_quality_flags,
        r.error_layer,
        r.error_layer_confidence,
        r.error_tags as review_error_tags,
        r.core_design_subtags as review_core_design_subtags,
        r.diagnosis as review_diagnosis,
        r.next_action as review_next_action,
        r.suggested_topic as review_suggested_topic,
        r.main_block as review_main_block,
        r.key_bridge as review_key_bridge,
        r.problem_focus as review_problem_focus,
        r.visual_hint as review_visual_hint,
        r.guided_walkthrough as review_guided_walkthrough,
        r.try_now as review_try_now,
        r.next_step as review_next_step,
        r.transfer_signal as review_transfer_signal,
        r.last_error
    FROM checkins c
    LEFT JOIN reviews r ON c.id = r.checkin_id
    WHERE c.student_id = ?
    ORDER BY c.created_at DESC
    LIMIT ?
    ''', (student_id, limit))
    rows = cursor.fetchall()
    conn.close()

    checkins = []
    for row in rows:
        checkins.append({
            "id": row["id"],
            "session_id": row["session_id"],
            "problem_url": row["problem_url"],
            "problem_title": row["problem_title"],
            "oj_source": row["oj_source"],
            "completion_status": row["completion_status"],
            "bottleneck_text": row["bottleneck_text"],
            "problem_context": row["problem_context"],
            "problem_tags": _json_loads_or_default(row["problem_tags"], []),
            "chat_context_summary": row["chat_context_summary"] or "",
            "submission_result": row["submission_result"],
            "error_types": json.loads(row["error_types"]),
            "reflection": row["reflection"],
            "created_at": row["created_at"],
            "has_review": row["review_status"] == REVIEW_STATUS_COMPLETED,
            "review_status": row["review_status"],
            "review_error_layer": row["error_layer"],
            "review_confidence": row["error_layer_confidence"],
            "review_error_tags": _json_loads_or_default(row["review_error_tags"], []),
            "review_core_design_subtags": _json_loads_or_default(row["review_core_design_subtags"], []),
            "review_diagnosis": row["review_diagnosis"],
            "review_next_action": row["review_next_action"],
            "review_suggested_topic": row["review_suggested_topic"],
            "review_problem_focus": row["review_problem_focus"] or row["review_main_block"],
            "review_main_block": row["review_main_block"],
            "review_key_bridge": row["review_key_bridge"],
            "review_visual_hint": row["review_visual_hint"] or "",
            "review_guided_walkthrough": row["review_guided_walkthrough"] or "",
            "review_try_now": row["review_try_now"] or row["review_next_step"],
            "review_next_step": row["review_next_step"],
            "review_transfer_signal": row["review_transfer_signal"],
            "review_last_error": row["last_error"],
            "review_id": row["review_id"],
            "review_learning_status": row["learning_status"] if "learning_status" in row.keys() else LEARNING_STATUS_NOT_STARTED,
            "review_remedy_count": row["remedy_count"] if "remedy_count" in row.keys() else 0,
            "review_understanding_self_check": row["understanding_self_check"] if "understanding_self_check" in row.keys() else None,
            "review_bridge_path": row["bridge_path"] if "bridge_path" in row.keys() else None,
            "review_mastery_status": row["mastery_status"] if "mastery_status" in row.keys() else MASTERY_STATUS_NOT_ASSESSED,
            "review_quality_flags": _json_loads_or_default(row["review_quality_flags"], []),
        })
    _attach_latest_quiz_summaries(checkins)
    return checkins


def get_all_checkins(limit: int = 100, offset: int = 0) -> list:
    """获取所有打卡（教师用）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT
        c.*,
        r.id as review_id,
        r.review_status,
        r.learning_status,
        r.remedy_count,
        r.understanding_self_check,
        r.bridge_path,
        r.mastery_status,
        r.review_quality_flags,
        r.error_layer,
        r.error_layer_confidence,
        r.error_tags as review_error_tags,
        r.core_design_subtags as review_core_design_subtags,
        r.diagnosis as review_diagnosis,
        r.next_action as review_next_action,
        r.suggested_topic as review_suggested_topic,
        r.main_block as review_main_block,
        r.key_bridge as review_key_bridge,
        r.problem_focus as review_problem_focus,
        r.visual_hint as review_visual_hint,
        r.guided_walkthrough as review_guided_walkthrough,
        r.try_now as review_try_now,
        r.next_step as review_next_step,
        r.transfer_signal as review_transfer_signal,
        r.last_error
    FROM checkins c
    LEFT JOIN reviews r ON c.id = r.checkin_id
    ORDER BY c.created_at DESC
    LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = cursor.fetchall()
    conn.close()

    checkins = []
    for row in rows:
        checkins.append({
            "id": row["id"],
            "student_id": row["student_id"],
            "problem_title": row["problem_title"],
            "oj_source": row["oj_source"],
            "completion_status": row["completion_status"],
            "bottleneck_text": row["bottleneck_text"],
            "problem_context": row["problem_context"],
            "problem_tags": _json_loads_or_default(row["problem_tags"], []),
            "chat_context_summary": row["chat_context_summary"] or "",
            "submission_result": row["submission_result"],
            "error_types": json.loads(row["error_types"]),
            "created_at": row["created_at"],
            "has_review": row["review_status"] == REVIEW_STATUS_COMPLETED,
            "review_status": row["review_status"],
            "review_error_layer": row["error_layer"],
            "review_confidence": row["error_layer_confidence"],
            "review_error_tags": _json_loads_or_default(row["review_error_tags"], []),
            "review_core_design_subtags": _json_loads_or_default(row["review_core_design_subtags"], []),
            "review_diagnosis": row["review_diagnosis"],
            "review_next_action": row["review_next_action"],
            "review_suggested_topic": row["review_suggested_topic"],
            "review_problem_focus": row["review_problem_focus"] or row["review_main_block"],
            "review_main_block": row["review_main_block"],
            "review_key_bridge": row["review_key_bridge"],
            "review_visual_hint": row["review_visual_hint"] or "",
            "review_guided_walkthrough": row["review_guided_walkthrough"] or "",
            "review_try_now": row["review_try_now"] or row["review_next_step"],
            "review_next_step": row["review_next_step"],
            "review_transfer_signal": row["review_transfer_signal"],
            "review_last_error": row["last_error"],
            "review_id": row["review_id"],
            "review_learning_status": row["learning_status"] if "learning_status" in row.keys() else LEARNING_STATUS_NOT_STARTED,
            "review_remedy_count": row["remedy_count"] if "remedy_count" in row.keys() else 0,
            "review_understanding_self_check": row["understanding_self_check"] if "understanding_self_check" in row.keys() else None,
            "review_bridge_path": row["bridge_path"] if "bridge_path" in row.keys() else None,
            "review_mastery_status": row["mastery_status"] if "mastery_status" in row.keys() else MASTERY_STATUS_NOT_ASSESSED,
            "review_quality_flags": _json_loads_or_default(row["review_quality_flags"], []),
        })
    _attach_latest_quiz_summaries(checkins)
    return checkins


def _attach_latest_quiz_summaries(checkins: list[dict]) -> None:
    review_ids = [item["review_id"] for item in checkins if item.get("review_id")]
    if not review_ids:
        return

    conn = get_db()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in review_ids)
    cursor.execute(
        f'''
        SELECT
            q.*,
            a.answer_text AS latest_answer_text,
            a.is_correct AS latest_is_correct,
            a.feedback_text AS latest_feedback_text
        FROM review_quizzes q
        LEFT JOIN quiz_attempts a
          ON a.id = (
              SELECT qa.id
              FROM quiz_attempts qa
              WHERE qa.quiz_id = q.id
              ORDER BY qa.id DESC
              LIMIT 1
          )
        WHERE q.id IN (
            SELECT MAX(id)
            FROM review_quizzes
            WHERE review_id IN ({placeholders})
            GROUP BY review_id
        )
        ''',
        review_ids,
    )
    rows = cursor.fetchall()
    conn.close()

    latest_map = {}
    for row in rows:
        latest_map[row["review_id"]] = {
            "quiz_id": row["id"],
            "quiz_round": row["round"],
            "quiz_role": row["quiz_role"],
            "quiz_type": row["quiz_type"],
            "quiz_status": row["status"],
            "quiz_question_text": row["question_text"],
            "quiz_options": _json_loads_or_default(row["options_json"], []),
            "quiz_correct_answer": row["correct_answer"],
            "quiz_explanation": row["explanation"],
            "quiz_bridge_feedback": row["bridge_feedback"],
            "quiz_distractor_feedback": _json_loads_or_default(row["distractor_feedback"], {}),
            "quiz_target_bridge": row["target_bridge"],
            "quiz_meta": _json_loads_or_default(row["meta_json"], {}),
            "quiz_latest_answer": row["latest_answer_text"],
            "quiz_latest_correct": row["latest_is_correct"],
            "quiz_latest_feedback": row["latest_feedback_text"],
        }

    for item in checkins:
        summary = latest_map.get(item.get("review_id"))
        if summary:
            item.update(summary)


# ============ Review Operations ============

def create_pending_review(checkin_id: int, student_id: str):
    """创建待生成的复盘任务记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT OR IGNORE INTO reviews
        (
            checkin_id, student_id, error_tags, diagnosis, next_action, suggested_topic,
            review_status, error_layer, error_layer_confidence, core_design_subtags, retry_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''',
        (
            checkin_id,
            student_id,
            "[]",
            "",
            "",
            "",
            REVIEW_STATUS_PENDING,
            "insufficient",
            "low",
            "[]",
        ),
    )
    conn.commit()
    conn.close()


def mark_review_attempt(checkin_id: int):
    """记录一次复盘生成尝试"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE reviews
        SET retry_count = COALESCE(retry_count, 0) + 1,
            last_attempt_at = CURRENT_TIMESTAMP,
            last_error = NULL,
            review_status = CASE
                WHEN review_status = ? THEN ?
                ELSE ?
            END
        WHERE checkin_id = ?
        ''',
        (
            REVIEW_STATUS_COMPLETED,
            REVIEW_STATUS_COMPLETED,
            REVIEW_STATUS_PENDING,
            checkin_id,
        ),
    )
    conn.commit()
    conn.close()


def mark_review_pending(checkin_id: int, error_message: str):
    """复盘暂未生成成功，保留待重试状态"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE reviews
        SET review_status = ?,
            last_error = ?,
            last_attempt_at = CURRENT_TIMESTAMP
        WHERE checkin_id = ?
        ''',
        (REVIEW_STATUS_PENDING, error_message, checkin_id),
    )
    conn.commit()
    conn.close()


def mark_review_failed(checkin_id: int, error_message: str):
    """复盘生成失败，等待学生或老师主动重试"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE reviews
        SET review_status = ?,
            last_error = ?,
            last_attempt_at = CURRENT_TIMESTAMP
        WHERE checkin_id = ?
        ''',
        (REVIEW_STATUS_FAILED, error_message, checkin_id),
    )
    conn.commit()
    conn.close()


def create_review(
    checkin_id: int,
    student_id: str,
    error_tags: list,
    diagnosis: str,
    next_action: str,
    suggested_topic: str,
    error_layer: str = "insufficient",
    error_layer_confidence: str = "low",
    core_design_subtags: list | None = None,
    main_block: str = "",
    key_bridge: str = "",
    next_step: str = "",
    transfer_signal: str = "",
    problem_focus: str = "",
    visual_hint: str = "",
    guided_walkthrough: str = "",
    try_now: str = "",
    review_quality_flags: list | None = None,
    bridge_route_meta: dict | None = None,
):
    """写入已完成的 AI 复盘"""
    subtags = core_design_subtags or []
    quality_flags = review_quality_flags or []
    route_meta = bridge_route_meta or {}
    canonical_problem_focus = problem_focus or main_block
    canonical_try_now = try_now or next_step
    legacy_main_block = main_block or canonical_problem_focus
    legacy_next_step = next_step or canonical_try_now
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE reviews
        SET student_id = ?,
            error_tags = ?,
            diagnosis = ?,
            next_action = ?,
            suggested_topic = ?,
            review_status = ?,
            error_layer = ?,
            error_layer_confidence = ?,
            core_design_subtags = ?,
            main_block = ?,
            key_bridge = ?,
            problem_focus = ?,
            visual_hint = ?,
            guided_walkthrough = ?,
            try_now = ?,
            next_step = ?,
            transfer_signal = ?,
            review_quality_flags = ?,
            bridge_route_meta = ?,
            learning_status = ?,
            mastery_status = ?,
            understanding_self_check = NULL,
            bridge_path = NULL,
            remedy_count = 0,
            last_error = NULL,
            last_attempt_at = CURRENT_TIMESTAMP
        WHERE checkin_id = ?
        ''',
        (
            student_id,
            json.dumps(error_tags, ensure_ascii=False),
            diagnosis,
            next_action,
            suggested_topic,
            REVIEW_STATUS_COMPLETED,
            error_layer,
            error_layer_confidence,
            json.dumps(subtags, ensure_ascii=False),
            legacy_main_block,
            key_bridge,
            canonical_problem_focus,
            visual_hint,
            guided_walkthrough,
            canonical_try_now,
            legacy_next_step,
            transfer_signal,
            json.dumps(quality_flags, ensure_ascii=False),
            json.dumps(route_meta, ensure_ascii=False),
            LEARNING_STATUS_NOT_STARTED,
            MASTERY_STATUS_NOT_ASSESSED,
            checkin_id,
        ),
    )
    if cursor.rowcount == 0:
        cursor.execute(
            '''
            INSERT INTO reviews
            (
                checkin_id, student_id, error_tags, diagnosis, next_action, suggested_topic,
                review_status, error_layer, error_layer_confidence, core_design_subtags,
                main_block, key_bridge, problem_focus, visual_hint, guided_walkthrough, try_now,
                next_step, transfer_signal, review_quality_flags,
                bridge_route_meta,
                retry_count, last_attempt_at, learning_status, mastery_status, understanding_self_check, bridge_path, remedy_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP, ?, ?, NULL, NULL, 0)
            ''',
            (
                checkin_id,
                student_id,
                json.dumps(error_tags, ensure_ascii=False),
                diagnosis,
                next_action,
                suggested_topic,
                REVIEW_STATUS_COMPLETED,
                error_layer,
                error_layer_confidence,
                json.dumps(subtags, ensure_ascii=False),
                legacy_main_block,
                key_bridge,
                canonical_problem_focus,
                visual_hint,
                guided_walkthrough,
                canonical_try_now,
                legacy_next_step,
                transfer_signal,
                json.dumps(quality_flags, ensure_ascii=False),
                json.dumps(route_meta, ensure_ascii=False),
                LEARNING_STATUS_NOT_STARTED,
                MASTERY_STATUS_NOT_ASSESSED,
            ),
        )
    conn.commit()
    conn.close()


def get_review_by_checkin(checkin_id: int) -> dict:
    """获取某次打卡的复盘"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reviews WHERE checkin_id = ?', (checkin_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "status": row["review_status"],
            "error_tags": _json_loads_or_default(row["error_tags"], []),
            "error_layer": row["error_layer"],
            "error_layer_confidence": row["error_layer_confidence"],
            "core_design_subtags": _json_loads_or_default(row["core_design_subtags"], []),
            "diagnosis": row["diagnosis"],
            "next_action": row["next_action"],
            "suggested_topic": row["suggested_topic"],
            "problem_focus": row["problem_focus"] or row["main_block"],
            "main_block": row["main_block"],
            "key_bridge": row["key_bridge"],
            "visual_hint": row["visual_hint"] or "",
            "guided_walkthrough": row["guided_walkthrough"] or "",
            "try_now": row["try_now"] or row["next_step"],
            "next_step": row["next_step"],
            "transfer_signal": row["transfer_signal"],
            "review_quality_flags": _json_loads_or_default(row["review_quality_flags"], []),
            "bridge_route_meta": _json_loads_or_default(row["bridge_route_meta"], {}) if "bridge_route_meta" in row.keys() else {},
            "retry_count": row["retry_count"],
            "last_error": row["last_error"],
            "last_attempt_at": row["last_attempt_at"],
            "learning_status": row["learning_status"],
            "mastery_status": row["mastery_status"] if "mastery_status" in row.keys() else MASTERY_STATUS_NOT_ASSESSED,
            "remedy_count": row["remedy_count"],
            "understanding_self_check": row["understanding_self_check"],
            "bridge_path": row["bridge_path"],
            "created_at": row["created_at"],
        }
    return None


def get_student_checkin_by_id(student_id: str, checkin_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            c.id,
            c.student_id,
            c.problem_url,
            c.problem_title,
            c.oj_source,
            c.completion_status,
            c.bottleneck_text,
            c.error_types,
            c.reflection,
            c.problem_context,
            c.problem_tags,
            c.chat_context_summary,
            c.session_id,
            c.submission_result,
            c.student_code,
            c.created_at,
            r.id as review_id,
            r.review_status,
            r.error_layer,
            r.error_layer_confidence,
            r.core_design_subtags as review_core_design_subtags,
            r.main_block as review_main_block,
            r.key_bridge as review_key_bridge,
            r.problem_focus as review_problem_focus,
            r.visual_hint as review_visual_hint,
            r.guided_walkthrough as review_guided_walkthrough,
            r.try_now as review_try_now,
            r.next_step as review_next_step,
            r.transfer_signal as review_transfer_signal,
            r.bridge_route_meta as review_bridge_route_meta,
            r.learning_status as review_learning_status,
            r.remedy_count as review_remedy_count,
            r.bridge_path as review_bridge_path,
            r.mastery_status as review_mastery_status,
            r.last_error
        FROM checkins c
        LEFT JOIN reviews r ON c.id = r.checkin_id
        WHERE c.id = ? AND c.student_id = ?
        ''',
        (checkin_id, student_id),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    review = None
    if row["review_status"] == REVIEW_STATUS_COMPLETED:
        review = {
            "review_id": row["review_id"],
            "error_layer": row["error_layer"],
            "error_layer_confidence": row["error_layer_confidence"],
            "core_design_subtags": _json_loads_or_default(row["review_core_design_subtags"], []),
            "problem_focus": row["review_problem_focus"] or row["review_main_block"],
            "main_block": row["review_main_block"],
            "key_bridge": row["review_key_bridge"],
            "visual_hint": row["review_visual_hint"] or "",
            "guided_walkthrough": row["review_guided_walkthrough"] or "",
            "try_now": row["review_try_now"] or row["review_next_step"],
            "next_step": row["review_next_step"],
            "transfer_signal": row["review_transfer_signal"],
            "bridge_route_meta": _json_loads_or_default(row["review_bridge_route_meta"], {}) if "review_bridge_route_meta" in row.keys() else {},
            "learning_status": row["review_learning_status"] if "review_learning_status" in row.keys() else LEARNING_STATUS_NOT_STARTED,
            "remedy_count": row["review_remedy_count"] if "review_remedy_count" in row.keys() else 0,
            "bridge_path": row["review_bridge_path"] if "review_bridge_path" in row.keys() else None,
            "mastery_status": row["review_mastery_status"] if "review_mastery_status" in row.keys() else MASTERY_STATUS_NOT_ASSESSED,
        }

    return {
        "checkin_id": row["id"],
        "session_id": row["session_id"],
        "student_id": row["student_id"],
        "problem_url": row["problem_url"],
        "problem_title": row["problem_title"],
        "oj_source": row["oj_source"],
        "completion_status": row["completion_status"],
        "bottleneck_text": row["bottleneck_text"],
        "error_types": _json_loads_or_default(row["error_types"], []),
        "reflection": row["reflection"],
        "problem_context": row["problem_context"],
        "problem_tags": _json_loads_or_default(row["problem_tags"], []),
        "chat_context_summary": row["chat_context_summary"] or "",
        "submission_result": row["submission_result"],
        "student_code": row["student_code"],
        "created_at": row["created_at"],
        "review_id": row["review_id"],
        "review_status": row["review_status"] or REVIEW_STATUS_PENDING,
        "review": review,
        "review_last_error": row["last_error"],
    }


def get_checkin_detail_by_id(checkin_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM checkins WHERE id = ?", (checkin_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return get_student_checkin_by_id(row["student_id"], checkin_id)


def record_review_event(
    *,
    session_id: str,
    checkin_id: int,
    student_id: str,
    event_name: str,
    review_mode: str,
    review_family: str,
    payload: dict | None = None,
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO review_events
        (session_id, checkin_id, student_id, event_name, review_mode, review_family, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            session_id,
            checkin_id,
            student_id,
            event_name,
            review_mode,
            review_family,
            json.dumps(payload or {}, ensure_ascii=False),
        ),
    )
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id


def get_review_events_for_checkin(checkin_id: int) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT id, session_id, checkin_id, student_id, event_name, review_mode, review_family, payload_json, created_at
        FROM review_events
        WHERE checkin_id = ?
        ORDER BY id ASC
        ''',
        (checkin_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "session_id": row["session_id"],
            "checkin_id": row["checkin_id"],
            "student_id": row["student_id"],
            "event_name": row["event_name"],
            "review_mode": row["review_mode"],
            "review_family": row["review_family"],
            "payload": _json_loads_or_default(row["payload_json"], {}),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def upsert_review_manual_review(
    *,
    review_id: int,
    checkin_id: int,
    student_id: str,
    teacher_id: str,
    review_mode: str,
    review_family: str,
    mode_correct: str,
    review_grounded: str,
    student_can_move_next: str,
    notes: str = "",
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM review_manual_reviews WHERE review_id = ?", (review_id,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            '''
            UPDATE review_manual_reviews
            SET checkin_id = ?,
                student_id = ?,
                teacher_id = ?,
                review_mode = ?,
                review_family = ?,
                mode_correct = ?,
                review_grounded = ?,
                student_can_move_next = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE review_id = ?
            ''',
            (
                checkin_id,
                student_id,
                teacher_id,
                review_mode,
                review_family,
                mode_correct,
                review_grounded,
                student_can_move_next,
                notes,
                review_id,
            ),
        )
        manual_review_id = existing["id"]
    else:
        cursor.execute(
            '''
            INSERT INTO review_manual_reviews
            (review_id, checkin_id, student_id, teacher_id, review_mode, review_family, mode_correct, review_grounded, student_can_move_next, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                review_id,
                checkin_id,
                student_id,
                teacher_id,
                review_mode,
                review_family,
                mode_correct,
                review_grounded,
                student_can_move_next,
                notes,
            ),
        )
        manual_review_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return manual_review_id


def get_review_manual_review(review_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            id,
            review_id,
            checkin_id,
            student_id,
            teacher_id,
            review_mode,
            review_family,
            mode_correct,
            review_grounded,
            student_can_move_next,
            notes,
            created_at,
            updated_at
        FROM review_manual_reviews
        WHERE review_id = ?
        ''',
        (review_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "review_id": row["review_id"],
        "checkin_id": row["checkin_id"],
        "student_id": row["student_id"],
        "teacher_id": row["teacher_id"],
        "review_mode": row["review_mode"],
        "review_family": row["review_family"],
        "mode_correct": row["mode_correct"],
        "review_grounded": row["review_grounded"],
        "student_can_move_next": row["student_can_move_next"],
        "notes": row["notes"] or "",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_teacher_review_samples(limit: int = 10) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            r.id AS review_id,
            r.checkin_id,
            r.student_id,
            r.review_status,
            r.error_layer,
            r.error_layer_confidence,
            r.main_block,
            r.key_bridge,
            r.problem_focus,
            r.visual_hint,
            r.guided_walkthrough,
            r.try_now,
            r.next_step,
            r.transfer_signal,
            r.bridge_route_meta,
            r.mastery_status,
            r.diagnosis,
            r.next_action,
            r.suggested_topic,
            r.created_at AS review_created_at,
            c.problem_title,
            c.problem_url,
            c.oj_source,
            c.completion_status,
            c.bottleneck_text,
            c.problem_context,
            c.submission_result,
            m.id AS manual_review_id,
            m.teacher_id AS manual_teacher_id,
            m.mode_correct,
            m.review_grounded,
            m.student_can_move_next,
            m.notes AS manual_notes,
            m.updated_at AS manual_updated_at
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        LEFT JOIN review_manual_reviews m ON m.review_id = r.id
        WHERE r.review_status = ?
        ORDER BY CASE WHEN m.id IS NULL THEN 0 ELSE 1 END ASC, r.created_at DESC
        LIMIT ?
        ''',
        (REVIEW_STATUS_COMPLETED, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    samples = []
    for row in rows:
        samples.append(
            {
                "review_id": row["review_id"],
                "checkin_id": row["checkin_id"],
                "student_id": row["student_id"],
                "problem_title": row["problem_title"],
                "problem_url": row["problem_url"],
                "oj_source": row["oj_source"],
                "completion_status": row["completion_status"],
                "bottleneck_text": row["bottleneck_text"],
                "problem_context": row["problem_context"],
                "submission_result": row["submission_result"],
                "review_status": row["review_status"],
                "error_layer": row["error_layer"],
                "error_layer_confidence": row["error_layer_confidence"],
                "diagnosis": row["diagnosis"],
                "next_action": row["next_action"],
                "suggested_topic": row["suggested_topic"],
                "problem_focus": row["problem_focus"] or row["main_block"],
                "main_block": row["main_block"],
                "key_bridge": row["key_bridge"],
                "visual_hint": row["visual_hint"] or "",
                "guided_walkthrough": row["guided_walkthrough"] or "",
                "try_now": row["try_now"] or row["next_step"],
                "next_step": row["next_step"],
                "transfer_signal": row["transfer_signal"],
                "bridge_route_meta": _json_loads_or_default(row["bridge_route_meta"], {}) if "bridge_route_meta" in row.keys() else {},
                "mastery_status": row["mastery_status"] if "mastery_status" in row.keys() else MASTERY_STATUS_NOT_ASSESSED,
                "review_created_at": row["review_created_at"],
                "manual_review": None
                if row["manual_review_id"] is None
                else {
                    "id": row["manual_review_id"],
                    "teacher_id": row["manual_teacher_id"],
                    "mode_correct": row["mode_correct"],
                    "review_grounded": row["review_grounded"],
                    "student_can_move_next": row["student_can_move_next"],
                    "notes": row["manual_notes"] or "",
                    "updated_at": row["manual_updated_at"],
                },
            }
        )
    return samples


def reset_review_for_student_retry(checkin_id: int, student_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE reviews
        SET review_status = ?,
            last_error = NULL,
            last_attempt_at = CURRENT_TIMESTAMP
        WHERE checkin_id = ? AND student_id = ? AND review_status = ?
        ''',
        (REVIEW_STATUS_PENDING, checkin_id, student_id, REVIEW_STATUS_FAILED),
    )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def get_review_context(review_id: int) -> dict | None:
    """获取 review + checkin 的上下文，用于 quiz / 补救流程"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            r.*,
            c.student_id AS checkin_student_id,
            c.problem_title,
            c.problem_context,
            c.problem_url,
            c.problem_tags,
            c.chat_context_summary,
            c.oj_source,
            c.completion_status,
            c.bottleneck_text,
            c.error_types,
            c.reflection,
            c.submission_result,
            c.student_code
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE r.id = ?
        ''',
        (review_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    return {
        "review_id": row["id"],
        "checkin_id": row["checkin_id"],
        "student_id": row["student_id"],
        "review_status": row["review_status"],
        "learning_status": row["learning_status"],
        "mastery_status": row["mastery_status"] if "mastery_status" in row.keys() else MASTERY_STATUS_NOT_ASSESSED,
        "remedy_count": row["remedy_count"],
        "error_tags": _json_loads_or_default(row["error_tags"], []),
        "error_layer": row["error_layer"],
        "error_layer_confidence": row["error_layer_confidence"],
        "core_design_subtags": _json_loads_or_default(row["core_design_subtags"], []),
        "diagnosis": row["diagnosis"],
        "next_action": row["next_action"],
        "suggested_topic": row["suggested_topic"],
        "problem_focus": row["problem_focus"] or row["main_block"],
        "main_block": row["main_block"],
        "key_bridge": row["key_bridge"],
        "visual_hint": row["visual_hint"] or "",
        "guided_walkthrough": row["guided_walkthrough"] or "",
        "try_now": row["try_now"] or row["next_step"],
        "next_step": row["next_step"],
        "transfer_signal": row["transfer_signal"],
        "bridge_route_meta": _json_loads_or_default(row["bridge_route_meta"], {}) if "bridge_route_meta" in row.keys() else {},
        "review_quality_flags": _json_loads_or_default(row["review_quality_flags"], []),
        "problem_title": row["problem_title"],
        "problem_context": row["problem_context"],
        "problem_url": row["problem_url"],
        "problem_tags": _json_loads_or_default(row["problem_tags"], []),
        "chat_context_summary": row["chat_context_summary"] or "",
        "oj_source": row["oj_source"],
        "completion_status": row["completion_status"],
        "bottleneck_text": row["bottleneck_text"],
        "error_types": _json_loads_or_default(row["error_types"], []),
        "reflection": row["reflection"],
        "submission_result": row["submission_result"],
        "student_code": row["student_code"],
        "understanding_self_check": row["understanding_self_check"],
        "bridge_path": row["bridge_path"],
    }


def update_review_learning_status(review_id: int, status: str, remedy_count: int | None = None):
    conn = get_db()
    cursor = conn.cursor()
    if remedy_count is None:
        cursor.execute(
            "UPDATE reviews SET learning_status = ? WHERE id = ?",
            (status, review_id),
        )
    else:
        cursor.execute(
            "UPDATE reviews SET learning_status = ?, remedy_count = ? WHERE id = ?",
            (status, remedy_count, review_id),
        )
    conn.commit()
    conn.close()


def update_review_mastery_status(review_id: int, mastery_status: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reviews SET mastery_status = ? WHERE id = ?",
        (mastery_status, review_id),
    )
    conn.commit()
    conn.close()


def update_review_self_check(review_id: int, status: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reviews SET understanding_self_check = ?, self_check_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, review_id),
    )
    conn.commit()
    conn.close()


def update_review_bridge_path(review_id: int, bridge_path: str | None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reviews SET bridge_path = ? WHERE id = ?",
        (bridge_path, review_id),
    )
    conn.commit()
    conn.close()


def update_review_quality_flags(review_id: int, flags: list[str]):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reviews SET review_quality_flags = ? WHERE id = ?",
        (json.dumps(flags, ensure_ascii=False), review_id),
    )
    conn.commit()
    conn.close()


def increment_review_remedy_count(review_id: int) -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reviews SET remedy_count = COALESCE(remedy_count, 0) + 1, learning_status = ? WHERE id = ?",
        (LEARNING_STATUS_REMEDY_IN_PROGRESS, review_id),
    )
    cursor.execute("SELECT remedy_count FROM reviews WHERE id = ?", (review_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return row["remedy_count"] if row else 0


def create_teacher_flag(
    student_id: str,
    flag_type: str,
    reason: str,
    severity: str = "medium",
    review_id: int | None = None,
    checkin_id: int | None = None,
    target_bridge: str | None = None,
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO teacher_flags
        (student_id, flag_type, reason, severity, review_id, checkin_id, target_bridge, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
        ''',
        (student_id, flag_type, reason, severity, review_id, checkin_id, target_bridge),
    )
    conn.commit()
    conn.close()


def create_review_quiz(
    review_id: int,
    student_id: str,
    checkin_id: int,
    round: int,
    quiz_role: str,
    quiz_type: str,
    question_text: str,
    options: list,
    correct_answer: str,
    explanation: str,
    bridge_feedback: str,
    distractor_feedback: dict | None,
    target_bridge: str,
    source_error_layer: str,
    meta: dict | None = None,
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    meta_payload = dict(meta or {})
    previous_template_id = None
    cursor.execute(
        "SELECT template_id FROM review_quizzes WHERE review_id = ? ORDER BY id DESC LIMIT 1",
        (review_id,),
    )
    previous_row = cursor.fetchone()
    if previous_row and previous_row["template_id"]:
        previous_template_id = int(previous_row["template_id"])
    cursor.execute(
        '''
        INSERT INTO review_quizzes
        (
            review_id, student_id, checkin_id, round, quiz_role, quiz_type,
            question_text, options_json, correct_answer, explanation, bridge_feedback, distractor_feedback,
            template_id, target_bridge, source_error_layer, status, meta_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, 'pending', ?)
        ''',
        (
            review_id,
            student_id,
            checkin_id,
            round,
            quiz_role,
            quiz_type,
            question_text,
            json.dumps(options, ensure_ascii=False),
            correct_answer,
            explanation,
            bridge_feedback,
            json.dumps(distractor_feedback or {}, ensure_ascii=False),
            target_bridge,
            source_error_layer,
            json.dumps(meta_payload, ensure_ascii=False),
        ),
    )
    quiz_id = cursor.lastrowid
    template_id = _get_or_create_quiz_template(
        cursor=cursor,
        quiz_role=quiz_role,
        quiz_type=quiz_type,
        source_error_layer=source_error_layer,
        target_bridge=target_bridge,
        meta=meta_payload,
        question_text=question_text,
        options=options,
        correct_answer=correct_answer,
        explanation=explanation,
        bridge_feedback=bridge_feedback,
        distractor_feedback=distractor_feedback,
    )
    cursor.execute("UPDATE review_quizzes SET template_id = ? WHERE id = ?", (template_id, quiz_id))
    if previous_template_id and previous_template_id != template_id and quiz_role != "main":
        cursor.execute(
            '''
            INSERT OR IGNORE INTO quiz_template_edges
            (parent_template_id, option_key, child_template_id, edge_type)
            VALUES (?, ?, ?, ?)
            ''',
            (previous_template_id, quiz_role, template_id, quiz_role),
        )
    conn.commit()
    conn.close()
    return quiz_id


def _get_or_create_quiz_template(
    cursor,
    quiz_role: str,
    quiz_type: str,
    source_error_layer: str,
    target_bridge: str,
    meta: dict | None,
    question_text: str,
    options: list,
    correct_answer: str,
    explanation: str,
    bridge_feedback: str,
    distractor_feedback: dict | None,
) -> int:
    meta_payload = dict(meta or {})
    structure_type = str(meta_payload.get("structure_type") or "").strip()
    options_json = json.dumps(options, ensure_ascii=False)
    distractor_json = json.dumps(distractor_feedback or {}, ensure_ascii=False)
    meta_json = json.dumps(meta_payload, ensure_ascii=False)
    cursor.execute(
        '''
        SELECT id FROM quiz_templates
        WHERE quiz_role = ?
          AND quiz_type = ?
          AND source_error_layer = ?
          AND target_bridge = ?
          AND structure_type = ?
          AND question_text = ?
          AND options_json = ?
          AND correct_answer = ?
          AND explanation = ?
          AND bridge_feedback = ?
          AND distractor_feedback = ?
        LIMIT 1
        ''',
        (
            quiz_role,
            quiz_type,
            source_error_layer,
            target_bridge,
            structure_type,
            question_text,
            options_json,
            correct_answer,
            explanation,
            bridge_feedback,
            distractor_json,
        ),
    )
    row = cursor.fetchone()
    if row:
        template_id = int(row["id"])
        cursor.execute(
            "UPDATE quiz_templates SET usage_count = usage_count + 1 WHERE id = ?",
            (template_id,),
        )
        return template_id

    cursor.execute(
        '''
        INSERT INTO quiz_templates
        (
            quiz_role, quiz_type, source_error_layer, target_bridge, structure_type,
            question_text, options_json, correct_answer, explanation, bridge_feedback,
            distractor_feedback, meta_json, quality_score, usage_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1)
        ''',
        (
            quiz_role,
            quiz_type,
            source_error_layer,
            target_bridge,
            structure_type,
            question_text,
            options_json,
            correct_answer,
            explanation,
            bridge_feedback,
            distractor_json,
            meta_json,
        ),
    )
    return int(cursor.lastrowid)


def get_quiz_by_id(quiz_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            q.*,
            a.answer_text AS latest_answer_text,
            a.is_correct AS latest_is_correct,
            a.feedback_text AS latest_feedback_text
        FROM review_quizzes q
        LEFT JOIN quiz_attempts a
          ON a.id = (
              SELECT qa.id FROM quiz_attempts qa
              WHERE qa.quiz_id = q.id
              ORDER BY qa.id DESC
              LIMIT 1
          )
        WHERE q.id = ?
        ''',
        (quiz_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "review_id": row["review_id"],
        "student_id": row["student_id"],
        "checkin_id": row["checkin_id"],
        "round": row["round"],
        "quiz_role": row["quiz_role"],
        "quiz_type": row["quiz_type"],
        "question_text": row["question_text"],
        "options": _json_loads_or_default(row["options_json"], []),
        "correct_answer": row["correct_answer"],
        "explanation": row["explanation"],
        "bridge_feedback": row["bridge_feedback"],
        "distractor_feedback": _json_loads_or_default(row["distractor_feedback"], {}),
        "template_id": row["template_id"],
        "target_bridge": row["target_bridge"],
        "source_error_layer": row["source_error_layer"],
        "status": row["status"],
        "meta": _json_loads_or_default(row["meta_json"], {}),
        "latest_answer_text": row["latest_answer_text"],
        "latest_is_correct": row["latest_is_correct"],
        "latest_feedback_text": row["latest_feedback_text"],
    }


def get_latest_quiz_for_review(review_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM review_quizzes WHERE review_id = ? ORDER BY id DESC LIMIT 1",
        (review_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return get_quiz_by_id(row["id"])


def get_quizzes_for_review(review_id: int) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM review_quizzes WHERE review_id = ? ORDER BY id ASC",
        (review_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [get_quiz_by_id(row["id"]) for row in rows if row and row["id"]]


def get_pending_judgement_quizzes(limit: int = 100) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM review_quizzes
        WHERE status = 'pending' AND quiz_type = 'judgement'
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [get_quiz_by_id(row["id"]) for row in rows if row and row["id"]]


def get_pending_quizzes(limit: int = 100) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM review_quizzes
        WHERE status = 'pending'
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [get_quiz_by_id(row["id"]) for row in rows if row and row["id"]]


def update_quiz_status(quiz_id: int, status: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE review_quizzes SET status = ? WHERE id = ?", (status, quiz_id))
    conn.commit()
    conn.close()


def record_quiz_attempt(quiz_id: int, student_id: str, answer_text: str, is_correct: bool, feedback_text: str) -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO quiz_attempts (quiz_id, student_id, answer_text, is_correct, feedback_text)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (quiz_id, student_id, answer_text, 1 if is_correct else 0, feedback_text),
    )
    attempt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return attempt_id


def get_pending_review_jobs(limit: int = 20) -> list:
    """获取待重试的复盘任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            r.checkin_id,
            r.student_id,
            r.retry_count,
            r.last_error,
            r.last_attempt_at,
            c.problem_title,
            c.oj_source,
            c.completion_status,
            c.bottleneck_text,
            c.error_types,
            c.reflection,
            c.problem_context,
            c.problem_tags,
            c.chat_context_summary,
            c.submission_result,
            c.student_code
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE r.review_status = ?
        ORDER BY
            CASE WHEN r.last_attempt_at IS NULL THEN 0 ELSE 1 END,
            r.last_attempt_at ASC,
            c.created_at ASC
        LIMIT ?
        ''',
        (REVIEW_STATUS_PENDING, limit),
    )
    rows = cursor.fetchall()
    conn.close()

    jobs = []
    for row in rows:
        jobs.append({
            "checkin_id": row["checkin_id"],
            "student_id": row["student_id"],
            "retry_count": row["retry_count"],
            "last_error": row["last_error"],
            "last_attempt_at": row["last_attempt_at"],
            "problem_title": row["problem_title"],
            "oj_source": row["oj_source"],
            "completion_status": row["completion_status"],
            "bottleneck_text": row["bottleneck_text"],
            "error_types": _json_loads_or_default(row["error_types"], []),
            "reflection": row["reflection"],
            "problem_context": row["problem_context"],
            "problem_tags": _json_loads_or_default(row["problem_tags"], []),
            "chat_context_summary": row["chat_context_summary"] or "",
            "submission_result": row["submission_result"],
            "student_code": row["student_code"],
        })
    return jobs


# ============ Teacher Dashboard Operations ============

def get_error_stats(days: int = 30) -> list:
    """获取学生自报错误类型统计"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.error_types, c.completion_status
    FROM checkins c
    WHERE c.created_at >= datetime('now', '-{} days')
    '''.format(days))
    rows = cursor.fetchall()
    conn.close()
    
    error_counts = {}
    for row in rows:
        errors = json.loads(row["error_types"])
        for error in errors:
            if error not in error_counts:
                error_counts[error] = {"count": 0, "completion_scores": []}
            error_counts[error]["count"] += 1
            # 完成状态评分：independent=3, hinted=2, editorial=1, unfinished=0
            score_map = {"independent": 3, "hinted": 2, "editorial": 1, "unfinished": 0}
            error_counts[error]["completion_scores"].append(score_map.get(row["completion_status"], 0))
    
    stats = []
    for error_type, data in error_counts.items():
        avg_score = sum(data["completion_scores"]) / len(data["completion_scores"]) if data["completion_scores"] else 0
        stats.append({
            "error_type": error_type,
            "count": data["count"],
            "avg_completion_score": round(avg_score, 2),
        })
    
    return sorted(stats, key=lambda x: x["count"], reverse=True)


def get_review_layer_stats(days: int = 30) -> list:
    """获取 AI 归纳后的错误层统计"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT r.error_layer, r.error_layer_confidence, c.completion_status
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE c.created_at >= datetime('now', '-{} days')
          AND r.review_status = ?
          AND r.error_layer_confidence IN ('high', 'medium')
        '''.format(days),
        (REVIEW_STATUS_COMPLETED,),
    )
    rows = cursor.fetchall()
    conn.close()

    layer_counts = {}
    score_map = {"independent": 3, "hinted": 2, "editorial": 1, "unfinished": 0}
    for row in rows:
        layer = row["error_layer"] or "insufficient"
        if layer not in layer_counts:
            layer_counts[layer] = {"count": 0, "completion_scores": []}
        layer_counts[layer]["count"] += 1
        layer_counts[layer]["completion_scores"].append(score_map.get(row["completion_status"], 0))

    stats = []
    for layer, data in layer_counts.items():
        avg_score = sum(data["completion_scores"]) / len(data["completion_scores"]) if data["completion_scores"] else 0
        stats.append({
            "error_layer": layer,
            "count": data["count"],
            "avg_completion_score": round(avg_score, 2),
        })

    return sorted(stats, key=lambda x: x["count"], reverse=True)


def get_review_status_summary(days: int = 30) -> list:
    """获取复盘状态统计"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT r.review_status, COUNT(*) AS count
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE c.created_at >= datetime('now', '-{} days')
        GROUP BY r.review_status
        ORDER BY count DESC
        '''.format(days)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "review_status": row["review_status"],
            "count": row["count"],
        }
        for row in rows
    ]


def get_manual_review_stats(days: int = 30, teacher_id: str | None = None) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    query = '''
        SELECT
            COUNT(*) AS reviewed_count,
            SUM(CASE WHEN mode_correct = 'correct' THEN 1 ELSE 0 END) AS mode_correct_count,
            SUM(CASE WHEN review_grounded = 'grounded' THEN 1 ELSE 0 END) AS grounded_count,
            SUM(CASE WHEN student_can_move_next = 'yes' THEN 1 ELSE 0 END) AS move_next_count
        FROM review_manual_reviews
        WHERE updated_at >= datetime('now', '-{} days')
    '''.format(days)
    params: tuple = ()
    if teacher_id:
        query += " AND teacher_id = ?"
        params = (teacher_id,)
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    reviewed_count = int(row["reviewed_count"] or 0)
    if reviewed_count <= 0:
        return {
            "reviewed_count": 0,
            "mode_correct_rate": 0.0,
            "grounded_rate": 0.0,
            "student_can_move_next_rate": 0.0,
        }
    return {
        "reviewed_count": reviewed_count,
        "mode_correct_rate": round(float(row["mode_correct_count"] or 0) / reviewed_count, 3),
        "grounded_rate": round(float(row["grounded_count"] or 0) / reviewed_count, 3),
        "student_can_move_next_rate": round(float(row["move_next_count"] or 0) / reviewed_count, 3),
    }


def get_manual_review_stats_breakdown(
    days: int = 30,
    *,
    group_by: str,
    teacher_id: str | None = None,
) -> dict[str, dict]:
    if group_by not in {"review_mode", "review_family"}:
        raise ValueError("group_by must be 'review_mode' or 'review_family'")

    conn = get_db()
    cursor = conn.cursor()
    query = f'''
        SELECT
            {group_by} AS bucket,
            COUNT(*) AS reviewed_count,
            SUM(CASE WHEN mode_correct = 'correct' THEN 1 ELSE 0 END) AS mode_correct_count,
            SUM(CASE WHEN review_grounded = 'grounded' THEN 1 ELSE 0 END) AS grounded_count,
            SUM(CASE WHEN student_can_move_next = 'yes' THEN 1 ELSE 0 END) AS move_next_count
        FROM review_manual_reviews
        WHERE updated_at >= datetime('now', '-{days} days')
    '''
    params: tuple = ()
    if teacher_id:
        query += " AND teacher_id = ?"
        params = (teacher_id,)
    query += f" GROUP BY {group_by}"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    stats: dict[str, dict] = {}
    for row in rows:
        bucket = row["bucket"] or "unknown"
        reviewed_count = int(row["reviewed_count"] or 0)
        if reviewed_count <= 0:
            stats[bucket] = {
                "reviewed_count": 0,
                "mode_correct_rate": 0.0,
                "grounded_rate": 0.0,
                "student_can_move_next_rate": 0.0,
            }
            continue
        stats[bucket] = {
            "reviewed_count": reviewed_count,
            "mode_correct_rate": round(float(row["mode_correct_count"] or 0) / reviewed_count, 3),
            "grounded_rate": round(float(row["grounded_count"] or 0) / reviewed_count, 3),
            "student_can_move_next_rate": round(float(row["move_next_count"] or 0) / reviewed_count, 3),
        }
    return stats


def _get_review_distribution_stats(days: int, field_name: str) -> dict[str, dict]:
    if field_name not in {"mastery_status", "bridge_path", "key_bridge"}:
        raise ValueError("field_name must be 'mastery_status', 'bridge_path', or 'key_bridge'")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f'''
        SELECT
            COALESCE(r.{field_name}, 'unknown') AS bucket,
            COUNT(*) AS count
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE c.created_at >= datetime('now', '-{days} days')
          AND r.{field_name} IS NOT NULL
        GROUP BY bucket
        ORDER BY count DESC
        '''
    )
    rows = cursor.fetchall()
    conn.close()

    total = sum(int(row["count"] or 0) for row in rows)
    if total <= 0:
        return {}

    stats: dict[str, dict] = {}
    for row in rows:
        bucket = row["bucket"] or "unknown"
        count = int(row["count"] or 0)
        stats[bucket] = {
            "count": count,
            "total": total,
            "rate": round(count / total, 3),
        }
    return stats


def get_mastery_status_stats(days: int = 30) -> dict[str, dict]:
    return _get_review_distribution_stats(days, "mastery_status")


def get_bridge_path_stats(days: int = 30) -> dict[str, dict]:
    return _get_review_distribution_stats(days, "bridge_path")


def get_bridge_stats(days: int = 30) -> dict[str, dict]:
    return _get_review_distribution_stats(days, "key_bridge")


def _increment_bridge_route_bucket(bucket: dict[str, dict], key: str, total: int) -> None:
    if not key:
        return
    if key not in bucket:
        bucket[key] = {"count": 0, "total": total, "rate": 0.0}
    bucket[key]["count"] += 1


def _safe_bridge_rule_filename(bridge_id: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in bridge_id).strip("_")
    return f"bridge_rule_draft_{safe or 'unknown'}.md"


def _build_bridge_rule_draft(suggestion: dict) -> dict:
    bridge_id = suggestion.get("bridge_id") or "unknown"
    route_kind = suggestion.get("route_kind") or "unknown"
    parent_focus = suggestion.get("parent_focus") or suggestion.get("stable_focus") or "unknown"
    trigger_signals = list(suggestion.get("evidence_signals") or [])[:6]
    conflict_signals = list(suggestion.get("conflict_signals") or [])[:4]
    title = f"{bridge_id} 转正规则草案"
    acceptance_checks = [
        "至少抽查 3 条同类样例，确认触发信号稳定指向同一桥。",
        "教师确认草案不会抢走稳定父桥或其他高频桥的样例。",
        "教师确认后才允许进入正式 resolver；当前草案不会自动转正。",
    ]
    return {
        "filename": _safe_bridge_rule_filename(str(bridge_id)),
        "title": title,
        "route_kind": route_kind,
        "parent_focus": parent_focus,
        "integration_status": "draft_only",
        "decision_policy": "teacher_review_required",
        "auto_apply": False,
        "trigger_signals": trigger_signals,
        "conflict_signals": conflict_signals,
        "acceptance_checks": acceptance_checks,
        "draft_markdown": "\n".join(
            [
                f"# {title}",
                "",
                f"- route_kind: {route_kind}",
                f"- parent_focus: {parent_focus}",
                "- integration_status: draft_only",
                "- decision_policy: teacher_review_required",
                "- auto_apply: false",
                "",
                "## Trigger Signals",
                *(f"- {signal}" for signal in (trigger_signals or ["暂无"])),
                "",
                "## Conflict Signals",
                *(f"- {signal}" for signal in (conflict_signals or ["暂无"])),
                "",
                "## Acceptance Checks",
                *(f"- {check}" for check in acceptance_checks),
            ]
        ),
    }


def get_bridge_route_stats(days: int = 30) -> dict[str, dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f'''
        SELECT r.bridge_route_meta
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE c.created_at >= datetime('now', '-{days} days')
          AND r.bridge_route_meta IS NOT NULL
          AND r.bridge_route_meta != ''
          AND r.bridge_route_meta != '{{}}'
        '''
    )
    rows = cursor.fetchall()
    conn.close()

    route_metas = [
        _json_loads_or_default(row["bridge_route_meta"], {})
        for row in rows
        if row["bridge_route_meta"]
    ]
    route_metas = [meta for meta in route_metas if isinstance(meta, dict) and meta]
    total = len(route_metas)
    if total <= 0:
        return {
            "status": {},
            "stable_focus": {},
            "candidate_bridge": {},
            "open_bridge": {},
            "conflict_signals": {},
        }

    stats = {
        "status": {},
        "stable_focus": {},
        "candidate_bridge": {},
        "open_bridge": {},
        "conflict_signals": {},
    }

    for meta in route_metas:
        status = str(meta.get("status") or "unknown")
        stable_focus = str(meta.get("stable_focus") or "")
        candidate_bridge = str(meta.get("candidate_bridge_id") or "")
        _increment_bridge_route_bucket(stats["status"], status, total)
        _increment_bridge_route_bucket(stats["stable_focus"], stable_focus, total)
        if status == "candidate_bridge":
            _increment_bridge_route_bucket(stats["candidate_bridge"], candidate_bridge, total)
        if status == "open_bridge":
            _increment_bridge_route_bucket(stats["open_bridge"], candidate_bridge, total)
        for signal in meta.get("conflict_signals") or []:
            _increment_bridge_route_bucket(stats["conflict_signals"], str(signal), total)

    for bucket in stats.values():
        for item in bucket.values():
            item["rate"] = round(item["count"] / total, 3)

    return stats


def get_bridge_route_promotion_suggestions(days: int = 30, limit: int = 50) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f'''
        SELECT r.id, r.checkin_id, r.bridge_route_meta, c.created_at
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE c.created_at >= datetime('now', '-{days} days')
          AND r.bridge_route_meta IS NOT NULL
          AND r.bridge_route_meta != ''
          AND r.bridge_route_meta != '{{}}'
        '''
    )
    rows = cursor.fetchall()
    conn.close()

    buckets: dict[tuple[str, str], dict] = {}
    for row in rows:
        meta = _json_loads_or_default(row["bridge_route_meta"], {})
        if not isinstance(meta, dict) or not meta:
            continue
        route_kind = str(meta.get("status") or "")
        if route_kind not in {"candidate_bridge", "open_bridge"}:
            continue
        bridge_id = str(meta.get("candidate_bridge_id") or "")
        if not bridge_id:
            continue
        bucket_key = (route_kind, bridge_id)
        if bucket_key not in buckets:
            buckets[bucket_key] = {
                "route_kind": route_kind,
                "bridge_id": bridge_id,
                "parent_focus": str(meta.get("candidate_parent_focus") or meta.get("stable_focus") or ""),
                "stable_focus": str(meta.get("stable_focus") or ""),
                "open_bridge_label": str(meta.get("open_bridge_label") or ""),
                "count": 0,
                "review_ids": [],
                "sample_checkin_ids": [],
                "evidence_signals": [],
                "conflict_signals": [],
                "decision_policy": "teacher_review_required",
                "auto_promote": False,
                "last_seen_at": row["created_at"],
            }
        bucket = buckets[bucket_key]
        bucket["count"] += 1
        if str(row["created_at"] or "") > str(bucket.get("last_seen_at") or ""):
            bucket["last_seen_at"] = row["created_at"]
        if len(bucket["review_ids"]) < 5:
            bucket["review_ids"].append(row["id"])
        if len(bucket["sample_checkin_ids"]) < 5:
            bucket["sample_checkin_ids"].append(row["checkin_id"])
        for signal in meta.get("matched_signals") or []:
            signal = str(signal)
            if signal and signal not in bucket["evidence_signals"]:
                bucket["evidence_signals"].append(signal)
        for signal in meta.get("conflict_signals") or []:
            signal = str(signal)
            if signal and signal not in bucket["conflict_signals"]:
                bucket["conflict_signals"].append(signal)

    suggestions_by_count = sorted(
        buckets.values(),
        key=lambda item: (-int(item["count"]), item["route_kind"], item["bridge_id"]),
    )
    suggestions_by_recency = sorted(
        buckets.values(),
        key=lambda item: (str(item.get("last_seen_at") or ""), int(item["count"]), item["route_kind"], item["bridge_id"]),
        reverse=True,
    )
    if len(suggestions_by_count) <= limit:
        suggestions = suggestions_by_count
    else:
        newest_limit = min(10, limit)
        frequent_limit = max(0, limit - newest_limit)
        seen_keys = set()
        suggestions = []
        for item in suggestions_by_count[:frequent_limit] + suggestions_by_recency[:newest_limit] + suggestions_by_count:
            key = (item["route_kind"], item["bridge_id"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            suggestions.append(item)
            if len(suggestions) >= limit:
                break
    for item in suggestions:
        item["evidence_signals"] = item["evidence_signals"][:6]
        item["conflict_signals"] = item["conflict_signals"][:4]
        item["suggested_action"] = (
            "review_candidate_bridge_rule"
            if item["route_kind"] == "candidate_bridge"
            else "draft_open_bridge_spec"
        )
        item["rule_draft"] = _build_bridge_rule_draft(item)
    return suggestions[:limit]


def get_bridge_route_promotion_suggestion(
    *,
    route_kind: str,
    bridge_id: str,
    days: int = 30,
) -> dict | None:
    for suggestion in get_bridge_route_promotion_suggestions(days=days, limit=500):
        if suggestion.get("route_kind") == route_kind and suggestion.get("bridge_id") == bridge_id:
            return suggestion
    return None


def upsert_bridge_rule_draft_decision(
    *,
    route_kind: str,
    bridge_id: str,
    parent_focus: str,
    teacher_id: str,
    decision: str,
    notes: str = "",
    draft_filename: str = "",
    draft_markdown: str = "",
    auto_promote: bool = False,
) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO bridge_rule_draft_decisions
        (route_kind, bridge_id, parent_focus, teacher_id, decision, notes, draft_filename, draft_markdown, auto_promote)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(route_kind, bridge_id, teacher_id) DO UPDATE SET
            parent_focus = excluded.parent_focus,
            decision = excluded.decision,
            notes = excluded.notes,
            draft_filename = excluded.draft_filename,
            draft_markdown = excluded.draft_markdown,
            auto_promote = excluded.auto_promote,
            updated_at = CURRENT_TIMESTAMP
        ''',
        (
            route_kind,
            bridge_id,
            parent_focus,
            teacher_id,
            decision,
            notes or "",
            draft_filename or "",
            draft_markdown or "",
            1 if auto_promote else 0,
        ),
    )
    conn.commit()
    conn.close()
    stored = get_bridge_rule_draft_decision(
        route_kind=route_kind,
        bridge_id=bridge_id,
        teacher_id=teacher_id,
    )
    return stored or {}


def get_bridge_rule_draft_decision(
    *,
    route_kind: str,
    bridge_id: str,
    teacher_id: str,
) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            id, route_kind, bridge_id, parent_focus, teacher_id, decision, notes,
            draft_filename, draft_markdown, auto_promote, created_at, updated_at
        FROM bridge_rule_draft_decisions
        WHERE route_kind = ? AND bridge_id = ? AND teacher_id = ?
        ''',
        (route_kind, bridge_id, teacher_id),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "route_kind": row["route_kind"],
        "bridge_id": row["bridge_id"],
        "parent_focus": row["parent_focus"],
        "teacher_id": row["teacher_id"],
        "decision": row["decision"],
        "notes": row["notes"] or "",
        "draft_filename": row["draft_filename"] or "",
        "draft_markdown": row["draft_markdown"] or "",
        "auto_promote": bool(row["auto_promote"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_bridge_rule_draft_decisions(
    *,
    teacher_id: str | None = None,
    limit: int = 30,
) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    query = '''
        SELECT
            id, route_kind, bridge_id, parent_focus, teacher_id, decision, notes,
            draft_filename, draft_markdown, auto_promote, created_at, updated_at
        FROM bridge_rule_draft_decisions
    '''
    params: tuple = ()
    if teacher_id:
        query += " WHERE teacher_id = ?"
        params = (teacher_id,)
    query += " ORDER BY updated_at DESC, id DESC LIMIT ?"
    params = (*params, max(1, min(limit, 100)))
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "route_kind": row["route_kind"],
            "bridge_id": row["bridge_id"],
            "parent_focus": row["parent_focus"],
            "teacher_id": row["teacher_id"],
            "decision": row["decision"],
            "notes": row["notes"] or "",
            "draft_filename": row["draft_filename"] or "",
            "auto_promote": bool(row["auto_promote"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]


def create_bridge_registry_entry_from_decision(
    *,
    decision_id: int,
    teacher_id: str,
) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            id, route_kind, bridge_id, parent_focus, teacher_id, decision, notes,
            draft_filename, draft_markdown, auto_promote
        FROM bridge_rule_draft_decisions
        WHERE id = ? AND teacher_id = ?
        ''',
        (decision_id, teacher_id),
    )
    decision = cursor.fetchone()
    if not decision:
        conn.close()
        raise ValueError("draft decision not found")
    if decision["decision"] != "confirmed":
        conn.close()
        raise ValueError("only confirmed drafts can enter registry")
    cursor.execute(
        '''
        INSERT INTO bridge_registry_entries
        (draft_decision_id, route_kind, bridge_id, parent_focus, teacher_id, registry_status,
         resolver_enabled, draft_filename, draft_markdown, notes)
        VALUES (?, ?, ?, ?, ?, 'registry_only', 0, ?, ?, ?)
        ON CONFLICT(route_kind, bridge_id) DO UPDATE SET
            draft_decision_id = excluded.draft_decision_id,
            parent_focus = excluded.parent_focus,
            teacher_id = excluded.teacher_id,
            registry_status = 'registry_only',
            resolver_enabled = 0,
            draft_filename = excluded.draft_filename,
            draft_markdown = excluded.draft_markdown,
            notes = excluded.notes,
            updated_at = CURRENT_TIMESTAMP
        ''',
        (
            decision["id"],
            decision["route_kind"],
            decision["bridge_id"],
            decision["parent_focus"],
            teacher_id,
            decision["draft_filename"] or "",
            decision["draft_markdown"] or "",
            decision["notes"] or "",
        ),
    )
    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()
    entry = get_bridge_registry_entry_by_bridge(
        route_kind=decision["route_kind"],
        bridge_id=decision["bridge_id"],
    )
    return entry or {"id": entry_id}


def get_bridge_registry_entry_by_bridge(*, route_kind: str, bridge_id: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            id, draft_decision_id, route_kind, bridge_id, parent_focus, teacher_id,
            registry_status, resolver_enabled, draft_filename, draft_markdown, notes,
            created_at, updated_at
        FROM bridge_registry_entries
        WHERE route_kind = ? AND bridge_id = ?
        ''',
        (route_kind, bridge_id),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return _bridge_registry_entry_from_row(row)


def get_bridge_registry_entry(entry_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            id, draft_decision_id, route_kind, bridge_id, parent_focus, teacher_id,
            registry_status, resolver_enabled, draft_filename, draft_markdown, notes,
            created_at, updated_at
        FROM bridge_registry_entries
        WHERE id = ?
        ''',
        (entry_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return _bridge_registry_entry_from_row(row)


def _bridge_registry_entry_from_row(row) -> dict:
    return {
        "id": row["id"],
        "draft_decision_id": row["draft_decision_id"],
        "route_kind": row["route_kind"],
        "bridge_id": row["bridge_id"],
        "parent_focus": row["parent_focus"],
        "teacher_id": row["teacher_id"],
        "registry_status": row["registry_status"],
        "resolver_enabled": bool(row["resolver_enabled"]),
        "draft_filename": row["draft_filename"] or "",
        "draft_markdown": row["draft_markdown"] or "",
        "notes": row["notes"] or "",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_bridge_registry_entries(limit: int = 50) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            id, draft_decision_id, route_kind, bridge_id, parent_focus, teacher_id,
            registry_status, resolver_enabled, draft_filename, draft_markdown, notes,
            created_at, updated_at
        FROM bridge_registry_entries
        ORDER BY updated_at DESC, id DESC
        LIMIT ?
        ''',
        (max(1, min(limit, 100)),),
    )
    rows = cursor.fetchall()
    conn.close()
    return [_bridge_registry_entry_from_row(row) for row in rows]


def build_resolver_patch_draft_for_registry_entry(entry: dict) -> dict:
    bridge_id = entry.get("bridge_id") or "unknown"
    parent_focus = entry.get("parent_focus") or "unknown"
    route_kind = entry.get("route_kind") or "unknown"
    filename = f"resolver_patch_draft_{_safe_bridge_rule_filename(str(bridge_id)).replace('bridge_rule_draft_', '').replace('.md', '')}.md"
    draft_markdown = "\n".join(
        [
            f"# Resolver Patch Draft: {bridge_id}",
            "",
            "- manual patch only",
            "- patch_status: patch_draft_only",
            "- auto_apply: false",
            "- resolver_enabled: false",
            "- target_file: review_engine.py",
            f"- route_kind: {route_kind}",
            f"- parent_focus: {parent_focus}",
            "",
            "## Intended Edit Location",
            "- `_resolve_bridge_decision(...)` in `review_engine.py`",
            "",
            "## Guardrails",
            "- Do not enable this patch automatically.",
            "- Do not change student-facing routing from this draft.",
            "- Keep existing stable parent focus active until a human review lands the resolver patch.",
            "- Add red tests before editing resolver logic.",
            "",
            "## Source Registry Notes",
            entry.get("notes") or "暂无备注",
            "",
            "## Source Rule Draft",
            entry.get("draft_markdown") or "暂无草案正文",
        ]
    )
    return {
        "bridge_id": bridge_id,
        "route_kind": route_kind,
        "parent_focus": parent_focus,
        "target_file": "review_engine.py",
        "filename": filename,
        "patch_status": "patch_draft_only",
        "auto_apply": False,
        "resolver_enabled": False,
        "draft_markdown": draft_markdown,
    }


def get_knowledge_bailout_stats(days: int = 30) -> dict[str, dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f'''
        SELECT
            CASE
                WHEN r.bridge_path IN ('knowledge_bailout_success', 'knowledge_bailout_failed') THEN 'entered'
                ELSE 'not_entered'
            END AS bucket,
            COUNT(*) AS count
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE c.created_at >= datetime('now', '-{days} days')
        GROUP BY bucket
        ORDER BY count DESC
        '''
    )
    rows = cursor.fetchall()
    conn.close()

    total = sum(int(row["count"] or 0) for row in rows)
    if total <= 0:
        return {}

    stats: dict[str, dict] = {}
    for row in rows:
        bucket = row["bucket"] or "unknown"
        count = int(row["count"] or 0)
        stats[bucket] = {
            "count": count,
            "total": total,
            "rate": round(count / total, 3),
        }
    return stats


def _get_topic_stats(days: int, level: str) -> dict[str, dict]:
    if level not in {"topic_l1", "topic_l2"}:
        raise ValueError("level must be 'topic_l1' or 'topic_l2'")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f'''
        SELECT COALESCE(r.key_bridge, 'unknown') AS key_bridge, COUNT(*) AS count
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE c.created_at >= datetime('now', '-{days} days')
        GROUP BY key_bridge
        ORDER BY count DESC
        '''
    )
    rows = cursor.fetchall()
    conn.close()

    bucket_counts: dict[str, int] = {}
    for row in rows:
        bridge = row["key_bridge"] or "unknown"
        count = int(row["count"] or 0)
        mapped = BRIDGE_TOPIC_MAP.get(bridge)
        bucket = (mapped[0] if level == "topic_l1" else mapped[1]) if mapped else "unknown"
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + count

    total = sum(bucket_counts.values())
    if total <= 0:
        return {}

    return {
        bucket: {
            "count": count,
            "total": total,
            "rate": round(count / total, 3),
        }
        for bucket, count in sorted(bucket_counts.items(), key=lambda item: (-item[1], item[0]))
    }


def get_topic_l1_stats(days: int = 30) -> dict[str, dict]:
    return _get_topic_stats(days, "topic_l1")


def get_topic_l2_stats(days: int = 30) -> dict[str, dict]:
    return _get_topic_stats(days, "topic_l2")


def get_student_flags() -> list:
    """获取需要关注的学员"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 统计各学员的情况
    cursor.execute('''
    SELECT 
        student_id,
        COUNT(*) as checkin_count,
        SUM(CASE WHEN completion_status = 'unfinished' THEN 1 ELSE 0 END) as unfinished_count,
        AVG(CASE 
            WHEN completion_status = 'independent' THEN 3
            WHEN completion_status = 'hinted' THEN 2
            WHEN completion_status = 'editorial' THEN 1
            ELSE 0
        END) as avg_score
    FROM checkins
    WHERE created_at >= datetime('now', '-30 days')
    GROUP BY student_id
    ''')
    rows = cursor.fetchall()
    
    flags = []
    for row in rows:
        student_id = row["student_id"]
        checkin_count = row["checkin_count"]
        unfinished_count = row["unfinished_count"]
        avg_score = row["avg_score"] or 0
        
        # 标记逻辑
        if unfinished_count >= 3:
            flags.append({
                "student_id": student_id,
                "flag_type": "连续未完成",
                "description": f"最近30天有 {unfinished_count} 道题未完成",
                "severity": "high",
            })
        elif avg_score < 1.5 and checkin_count >= 5:
            flags.append({
                "student_id": student_id,
                "flag_type": "依赖度过高",
                "description": f"平均完成度评分 {avg_score:.1f}/3，需要关注",
                "severity": "medium",
            })
        elif checkin_count < 3:
            flags.append({
                "student_id": student_id,
                "flag_type": "打卡稀疏",
                "description": f"最近30天仅打卡 {checkin_count} 次",
                "severity": "low",
            })
    
    cursor.execute(
        '''
        SELECT student_id, flag_type, reason, severity, status
        FROM teacher_flags
        WHERE status = 'open'
        ORDER BY created_at DESC
        '''
    )
    for row in cursor.fetchall():
        flags.append({
            "student_id": row["student_id"],
            "flag_type": row["flag_type"],
            "description": row["reason"],
            "severity": row["severity"] or "medium",
        })

    conn.close()
    return sorted(flags, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["severity"], 1))


# ============ Usage Statistics (Minimal) ============

def record_aichat_message(
    student_id: str,
    problem_id: str,
    session_id: str,
    role: str,
    content: str,
    problem_title: str = "",
    problem_url: str = "",
    has_problem_context: bool = False,
    has_student_code: bool = False,
) -> int:
    """记录 AIChat 对话，用于教师端后续观察和统计。"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO aichat_messages (
            student_id,
            problem_id,
            session_id,
            role,
            content,
            problem_title,
            problem_url,
            has_problem_context,
            has_student_code
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            student_id,
            problem_id,
            session_id,
            role,
            content,
            problem_title or "",
            problem_url or "",
            1 if has_problem_context else 0,
            1 if has_student_code else 0,
        ),
    )
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id


def list_aichat_messages_for_student(student_id: str, limit: int = 50) -> list[dict]:
    """按时间倒序读取某个学生最近的 AIChat 对话。"""
    return list_aichat_messages(student_id=student_id, limit=limit, ascending=False)


def list_aichat_messages(
    student_id: str,
    problem_id: str = "",
    session_id: str = "",
    limit: int = 50,
    ascending: bool = False,
) -> list[dict]:
    """读取 AIChat 对话，可按当前题目和会话过滤。"""
    conn = get_db()
    cursor = conn.cursor()
    where_clauses = ["student_id = ?"]
    params = [student_id]
    if problem_id:
        where_clauses.append("problem_id = ?")
        params.append(problem_id)
    if session_id:
        where_clauses.append("session_id = ?")
        params.append(session_id)
    order_sql = "created_at ASC, id ASC" if ascending else "created_at DESC, id DESC"
    params.append(max(1, min(int(limit), 200)))
    cursor.execute(
        f'''
        SELECT
            id,
            student_id,
            problem_id,
            session_id,
            role,
            content,
            problem_title,
            problem_url,
            has_problem_context,
            has_student_code,
            created_at
        FROM aichat_messages
        WHERE {' AND '.join(where_clauses)}
        ORDER BY {order_sql}
        LIMIT ?
        ''',
        tuple(params),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def record_aichat_conversation_message(
    *,
    student_id: str,
    problem_id: str = "",
    session_id: str = "",
    role: str,
    content: str,
    student_username: str = "",
    student_real_name: str = "",
    content_type: str = "text",
    has_code: bool = False,
    code_language: str = "",
    model_provider: str = "",
    model_name: str = "",
    consent_for_research: bool = True,
    source: str = "aichat",
) -> int:
    """记录完整 AIChat 教学证据消息，保留学生/AI 角色区分。"""
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        INSERT INTO aichat_conversation_messages (
            student_id,
            student_username,
            student_real_name,
            problem_id,
            session_id,
            role,
            content,
            content_type,
            has_code,
            code_language,
            model_provider,
            model_name,
            consent_for_research,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            student_id or "",
            student_username or student_id or "",
            student_real_name or student_username or student_id or "",
            problem_id or "",
            session_id or "",
            role,
            content or "",
            content_type or "text",
            1 if has_code else 0,
            code_language or "",
            model_provider or "",
            model_name or "",
            1 if consent_for_research else 0,
            source or "aichat",
        ),
    )
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id


def list_aichat_conversation_messages(
    student_id: str = "",
    problem_id: str = "",
    session_id: str = "",
    limit: int = 50,
    ascending: bool = False,
) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    where_clauses: list[str] = []
    params: list = []
    if student_id:
        where_clauses.append("student_id = ?")
        params.append(student_id)
    if problem_id:
        where_clauses.append("problem_id = ?")
        params.append(problem_id)
    if session_id:
        where_clauses.append("session_id = ?")
        params.append(session_id)
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    order_sql = "created_at ASC, id ASC" if ascending else "created_at DESC, id DESC"
    params.append(max(1, min(int(limit), 500)))
    cursor.execute(
        f'''
        SELECT *
        FROM aichat_conversation_messages
        {where_sql}
        ORDER BY {order_sql}
        LIMIT ?
        ''',
        tuple(params),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def record_aichat_judge_shadow_event(
    *,
    student_id: str,
    problem_id: str = "",
    session_id: str = "",
    event_type: str = "judge_called",
    skip_reason: str = "",
    conversation_message_id: int | None = None,
    student_username: str = "",
    student_real_name: str = "",
    user_input: str = "",
    messages: list | None = None,
    rule_max_level: str = "",
    rule_tutor_action: str = "",
    rule_risk_tags: list | None = None,
    judge_failed: bool = False,
    failure_reason: str = "",
    judge_latency_ms: int = 0,
    judge_primary_intent: str = "",
    judge_phase: str = "",
    judge_action_category: str = "",
    judge_action_subtype: str = "",
    judge_allowed_help_level: str = "",
    judge_confidence: float = 0.0,
    injection_detected: bool = False,
    injection_source: str = "",
    agreement_action_exact: bool = False,
    agreement_action_family: bool = False,
    agreement_help_level: bool = False,
    agreement_would_override: bool = False,
    final_tutor_action: str = "",
    actual_reply_source: str = "rules",
    consent_for_research: bool = True,
) -> int:
    """记录 judge v2 shadow 事件；完整对话以 JSON 保存，便于后续人工审查。"""
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        INSERT INTO aichat_judge_shadow_events (
            event_type,
            skip_reason,
            conversation_message_id,
            student_id,
            student_username,
            student_real_name,
            problem_id,
            session_id,
            user_input,
            messages_json,
            rule_max_level,
            rule_tutor_action,
            rule_risk_tags,
            judge_failed,
            failure_reason,
            judge_latency_ms,
            judge_primary_intent,
            judge_phase,
            judge_action_category,
            judge_action_subtype,
            judge_allowed_help_level,
            judge_confidence,
            injection_detected,
            injection_source,
            agreement_action_exact,
            agreement_action_family,
            agreement_help_level,
            agreement_would_override,
            final_tutor_action,
            actual_reply_source,
            consent_for_research
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            event_type or "judge_called",
            skip_reason or "",
            conversation_message_id,
            student_id or "",
            student_username or student_id or "",
            student_real_name or student_username or student_id or "",
            problem_id or "",
            session_id or "",
            user_input or "",
            json.dumps(messages or [], ensure_ascii=False, default=str),
            rule_max_level or "",
            rule_tutor_action or "",
            json.dumps(rule_risk_tags or [], ensure_ascii=False),
            1 if judge_failed else 0,
            failure_reason or "",
            int(judge_latency_ms or 0),
            judge_primary_intent or "",
            judge_phase or "",
            judge_action_category or "",
            judge_action_subtype or "",
            judge_allowed_help_level or "",
            float(judge_confidence or 0.0),
            1 if injection_detected else 0,
            injection_source or "",
            1 if agreement_action_exact else 0,
            1 if agreement_action_family else 0,
            1 if agreement_help_level else 0,
            1 if agreement_would_override else 0,
            final_tutor_action or "",
            actual_reply_source or "rules",
            1 if consent_for_research else 0,
        ),
    )
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id


def list_aichat_judge_shadow_events(
    student_id: str = "",
    problem_id: str = "",
    session_id: str = "",
    limit: int = 50,
) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    where_clauses: list[str] = []
    params: list = []
    if student_id:
        where_clauses.append("student_id = ?")
        params.append(student_id)
    if problem_id:
        where_clauses.append("problem_id = ?")
        params.append(problem_id)
    if session_id:
        where_clauses.append("session_id = ?")
        params.append(session_id)
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    params.append(max(1, min(int(limit), 500)))
    cursor.execute(
        f'''
        SELECT *
        FROM aichat_judge_shadow_events
        {where_sql}
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        ''',
        tuple(params),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def record_aichat_turn_tag(
    *,
    student_id: str,
    problem_id: str = "",
    session_id: str = "",
    turn_id: str = "",
    role: str = "student",
    conversation_message_id: int | None = None,
    student_username: str = "",
    student_real_name: str = "",
    primary_intent: str = "",
    learning_issue: str = "",
    understanding_evidence: list[str] | None = None,
    missing_evidence: list[str] | None = None,
    risk_flags: list[str] | None = None,
    injection_detected: bool = False,
    injection_source: str = "none",
    same_point_loop_signal: bool = False,
    suggested_level: str = "",
    confidence: float = 0.0,
    short_reason: str = "",
    model: str = "",
    prompt_version: str = "",
    consent_for_research: bool = True,
) -> int:
    """记录 AIChat Turn Tagger 后台标签；不参与学生端实时控制。"""
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        INSERT INTO aichat_turn_tags (
            conversation_message_id,
            student_id,
            student_username,
            student_real_name,
            problem_id,
            session_id,
            turn_id,
            role,
            primary_intent,
            learning_issue,
            understanding_evidence_json,
            missing_evidence_json,
            risk_flags_json,
            injection_detected,
            injection_source,
            same_point_loop_signal,
            suggested_level,
            confidence,
            short_reason,
            model,
            prompt_version,
            consent_for_research
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            conversation_message_id,
            student_id or "",
            student_username or student_id or "",
            student_real_name or student_username or student_id or "",
            problem_id or "",
            session_id or "",
            turn_id or "",
            role or "student",
            primary_intent or "",
            learning_issue or "",
            json.dumps(understanding_evidence or [], ensure_ascii=False),
            json.dumps(missing_evidence or [], ensure_ascii=False),
            json.dumps(risk_flags or [], ensure_ascii=False),
            1 if injection_detected else 0,
            injection_source or "none",
            1 if same_point_loop_signal else 0,
            suggested_level or "",
            float(confidence or 0.0),
            short_reason or "",
            model or "",
            prompt_version or "",
            1 if consent_for_research else 0,
        ),
    )
    tag_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tag_id


def list_aichat_turn_tags(
    student_id: str = "",
    problem_id: str = "",
    session_id: str = "",
    limit: int = 50,
    ascending: bool = False,
) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    where_clauses: list[str] = []
    params: list = []
    if student_id:
        where_clauses.append("student_id = ?")
        params.append(student_id)
    if problem_id:
        where_clauses.append("problem_id = ?")
        params.append(problem_id)
    if session_id:
        where_clauses.append("session_id = ?")
        params.append(session_id)
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    order_sql = "created_at ASC, id ASC" if ascending else "created_at DESC, id DESC"
    params.append(max(1, min(int(limit), 500)))
    cursor.execute(
        f'''
        SELECT *
        FROM aichat_turn_tags
        {where_sql}
        ORDER BY {order_sql}
        LIMIT ?
        ''',
        tuple(params),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for row in rows:
        row["understanding_evidence"] = _json_loads_or_default(row.pop("understanding_evidence_json", "[]"), [])
        row["missing_evidence"] = _json_loads_or_default(row.pop("missing_evidence_json", "[]"), [])
        row["risk_flags"] = _json_loads_or_default(row.pop("risk_flags_json", "[]"), [])
    return rows


def upsert_aichat_session_analysis(
    *,
    session_id: str,
    student_id: str = "",
    problem_id: str = "",
    status: str = "processing",
    analysis_json: dict | None = None,
    main_issue: str = "",
    teacher_next_action: str = "",
    needs_followup: bool = False,
    model: str = "",
    prompt_version: str = "",
    failure_reason: str = "",
) -> int:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        INSERT INTO aichat_session_analyses (
            session_id,
            student_id,
            problem_id,
            status,
            analysis_json,
            main_issue,
            teacher_next_action,
            needs_followup,
            model,
            prompt_version,
            failure_reason,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            student_id = excluded.student_id,
            problem_id = excluded.problem_id,
            status = excluded.status,
            analysis_json = excluded.analysis_json,
            main_issue = excluded.main_issue,
            teacher_next_action = excluded.teacher_next_action,
            needs_followup = excluded.needs_followup,
            model = excluded.model,
            prompt_version = excluded.prompt_version,
            failure_reason = excluded.failure_reason,
            updated_at = CURRENT_TIMESTAMP
        ''',
        (
            session_id or "",
            student_id or "",
            problem_id or "",
            status or "processing",
            json.dumps(analysis_json or {}, ensure_ascii=False, default=str),
            main_issue or "",
            teacher_next_action or "",
            1 if needs_followup else 0,
            model or "",
            prompt_version or "",
            failure_reason or "",
        ),
    )
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def get_aichat_session_analysis(session_id: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        SELECT *
        FROM aichat_session_analyses
        WHERE session_id = ?
        ''',
        (session_id or "",),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    result["analysis_json"] = _json_loads_or_default(result.get("analysis_json", "{}"), {})
    return result


def get_aichat_session_analysis_health(days: int = 7) -> dict:
    """Return status counts for teacher-facing Session Analyst runs."""
    window_days = max(1, min(int(days or 7), 90))
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        SELECT status, COUNT(*) AS count
        FROM aichat_session_analyses
        WHERE updated_at >= datetime('now', ?)
        GROUP BY status
        ''',
        (f"-{window_days} days",),
    )
    status_counts = {"completed": 0, "processing": 0, "failed": 0}
    for row in cursor.fetchall():
        status = str(row["status"] or "")
        status_counts[status] = int(row["count"] or 0)
    conn.close()
    total = sum(status_counts.values())
    failed = status_counts.get("failed", 0)
    return {
        "window_days": window_days,
        "total": total,
        "status_counts": status_counts,
        "completed_count": status_counts.get("completed", 0),
        "processing_count": status_counts.get("processing", 0),
        "failed_count": failed,
        "failure_rate": failed / total if total else 0.0,
    }


def upsert_aichat_session_summary(
    *,
    session_id: str,
    student_id: str,
    problem_id: str = "",
    student_username: str = "",
    student_real_name: str = "",
    message_count: int = 0,
    student_turn_count: int = 0,
    ai_turn_count: int = 0,
    has_understanding_evidence: bool = False,
    understanding_evidence_types: list | None = None,
    same_gap_loop: bool = False,
    same_gap_loop_type: str = "",
    latest_tutor_action: str = "",
    latest_rule_max_level: str = "",
    latest_judge_action_subtype: str = "",
    last_student_message: str = "",
    consent_for_research: bool = True,
) -> None:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        INSERT INTO aichat_session_summary (
            session_id,
            student_id,
            student_username,
            student_real_name,
            problem_id,
            message_count,
            student_turn_count,
            ai_turn_count,
            has_understanding_evidence,
            understanding_evidence_types,
            same_gap_loop,
            same_gap_loop_type,
            latest_tutor_action,
            latest_rule_max_level,
            latest_judge_action_subtype,
            last_student_message,
            consent_for_research,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            student_id = excluded.student_id,
            student_username = excluded.student_username,
            student_real_name = excluded.student_real_name,
            problem_id = excluded.problem_id,
            message_count = excluded.message_count,
            student_turn_count = excluded.student_turn_count,
            ai_turn_count = excluded.ai_turn_count,
            has_understanding_evidence = excluded.has_understanding_evidence,
            understanding_evidence_types = excluded.understanding_evidence_types,
            same_gap_loop = excluded.same_gap_loop,
            same_gap_loop_type = excluded.same_gap_loop_type,
            latest_tutor_action = excluded.latest_tutor_action,
            latest_rule_max_level = excluded.latest_rule_max_level,
            latest_judge_action_subtype = excluded.latest_judge_action_subtype,
            last_student_message = excluded.last_student_message,
            consent_for_research = excluded.consent_for_research,
            updated_at = CURRENT_TIMESTAMP
        ''',
        (
            session_id or "",
            student_id or "",
            student_username or student_id or "",
            student_real_name or student_username or student_id or "",
            problem_id or "",
            int(message_count or 0),
            int(student_turn_count or 0),
            int(ai_turn_count or 0),
            1 if has_understanding_evidence else 0,
            json.dumps(understanding_evidence_types or [], ensure_ascii=False),
            1 if same_gap_loop else 0,
            same_gap_loop_type or "",
            latest_tutor_action or "",
            latest_rule_max_level or "",
            latest_judge_action_subtype or "",
            last_student_message or "",
            1 if consent_for_research else 0,
        ),
    )
    conn.commit()
    conn.close()


def get_aichat_session_summary(session_id: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        SELECT *
        FROM aichat_session_summary
        WHERE session_id = ?
        ''',
        (session_id or "",),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


AICHAT_EVIDENCE_FLAG_KEYS = (
    "problem_goal",
    "object_relation",
    "method_sketch",
    "debug_evidence",
    "self_correction",
    "quiz_passed",
)


def _aichat_evidence_flags(raw_types: str | list | None) -> dict:
    types = raw_types if isinstance(raw_types, list) else _json_loads_or_default(raw_types or "[]", [])
    normalized = {str(item) for item in (types or [])}
    return {
        "problem_goal": bool(normalized & {"problem_goal", "goal", "object", "relation"}),
        "object_relation": bool(normalized & {"object_relation", "object", "relation"}),
        "method_sketch": bool(normalized & {"method_sketch", "operation", "method"}),
        "debug_evidence": bool(normalized & {"debug_evidence", "debug_target"}),
        "self_correction": bool(normalized & {"self_correction"}),
        "quiz_passed": bool(normalized & {"quiz_passed"}),
    }


def _aichat_evidence_count(raw_types: str | list | None) -> int:
    flags = _aichat_evidence_flags(raw_types)
    return sum(1 for key in AICHAT_EVIDENCE_FLAG_KEYS if flags.get(key))


def list_teacher_aichat_evidence_students() -> list[dict]:
    """Return students with M3 AIChat evidence, newest activity first."""
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        WITH latest AS (
            SELECT c.*
            FROM aichat_conversation_messages c
            JOIN (
                SELECT student_id, MAX(id) AS max_id
                FROM aichat_conversation_messages
                GROUP BY student_id
            ) m ON c.student_id = m.student_id AND c.id = m.max_id
        )
        SELECT
            c.student_id AS student_id,
            COALESCE(NULLIF(l.student_username, ''), c.student_id) AS student_username,
            COALESCE(NULLIF(l.student_real_name, ''), COALESCE(NULLIF(l.student_username, ''), c.student_id)) AS student_real_name,
            MAX(c.created_at) AS last_session_at,
            COUNT(DISTINCT c.session_id) AS total_sessions,
            COUNT(*) AS total_messages,
            COALESCE(NULLIF(l.problem_id, ''), '') AS recent_problem_id
        FROM aichat_conversation_messages c
        LEFT JOIN latest l ON c.student_id = l.student_id
        GROUP BY c.student_id
        ORDER BY MAX(c.id) DESC
        '''
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_teacher_aichat_evidence_sessions(student_id: str) -> list[dict]:
    """Return one student's AIChat sessions with compact evidence status."""
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        SELECT
            s.*,
            MIN(c.created_at) AS started_at,
            MAX(c.created_at) AS last_session_at,
            COUNT(c.id) AS total_turns
        FROM aichat_session_summary s
        LEFT JOIN aichat_conversation_messages c ON c.session_id = s.session_id
        WHERE s.student_id = ?
        GROUP BY s.session_id
        ORDER BY COALESCE(MAX(c.id), 0) DESC, s.updated_at DESC
        ''',
        (student_id or "",),
    )
    rows = []
    for row in cursor.fetchall():
        data = dict(row)
        raw_types = data.get("understanding_evidence_types")
        data["evidence_flags"] = _aichat_evidence_flags(raw_types)
        data["evidence_count"] = _aichat_evidence_count(raw_types)
        data["same_point_loop_detected"] = bool(data.get("same_gap_loop"))
        data["last_ai_action"] = data.get("latest_tutor_action") or ""
        data["total_turns"] = int(data.get("total_turns") or data.get("message_count") or 0)
        rows.append(data)
    conn.close()
    return rows


def get_teacher_aichat_evidence_session_detail(session_id: str) -> dict | None:
    """Return messages, summary, and judge labels for a single AIChat session."""
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        SELECT *
        FROM aichat_session_summary
        WHERE session_id = ?
        ''',
        (session_id or "",),
    )
    summary_row = cursor.fetchone()
    if not summary_row:
        conn.close()
        return None
    summary = dict(summary_row)
    summary["evidence_flags"] = _aichat_evidence_flags(summary.get("understanding_evidence_types"))
    summary["evidence_count"] = _aichat_evidence_count(summary.get("understanding_evidence_types"))
    summary["same_point_loop_detected"] = bool(summary.get("same_gap_loop"))

    cursor.execute(
        '''
        SELECT *
        FROM aichat_conversation_messages
        WHERE session_id = ?
        ORDER BY created_at ASC, id ASC
        ''',
        (session_id or "",),
    )
    messages = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        '''
        SELECT *
        FROM aichat_judge_shadow_events
        WHERE session_id = ?
        ORDER BY created_at ASC, id ASC
        ''',
        (session_id or "",),
    )
    judge_events = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        '''
        SELECT *
        FROM aichat_session_analyses
        WHERE session_id = ?
        ''',
        (session_id or "",),
    )
    analysis_row = cursor.fetchone()
    session_analysis = dict(analysis_row) if analysis_row else None
    if session_analysis:
        session_analysis["analysis_json"] = _json_loads_or_default(
            session_analysis.get("analysis_json", "{}"),
            {},
        )

    conn.close()
    return {
        "summary": summary,
        "messages": messages,
        "judge_events": judge_events,
        "session_analysis": session_analysis,
    }


# ============ Teacher Learning Diagnosis Operations ============

INDEPENDENCE_SCORE_BY_METHOD = {
    "self_solved": 4.0,
    "small_hint": 3.0,
    "classroom_taught": 3.0,
    "aichat_assisted": 2.0,
    "editorial_completed": 1.0,
    "unsure": 0.0,
}

QUALITY_SCORE_BY_RESULT = {
    "accepted": 1.0,
    "sample_passed": 0.4,
    "unsure": 0.2,
}

ISSUE_CATEGORY_LABELS = {
    "problem_understanding": "题意没读透",
    "problem_translation": "题意没读透",
    "method_selection": "方法选择困难",
    "strategy_choice": "方法选择困难",
    "implementation": "代码实现卡住",
    "code_semantics": "代码实现卡住",
    "debugging": "调试定位困难",
    "debug_location": "调试定位困难",
    "complexity_analysis": "复杂度判断薄弱",
    "complexity_boundary": "复杂度判断薄弱",
    "complexity_awareness": "复杂度判断薄弱",
    "knowledge_transfer": "同类迁移困难",
    "transfer": "同类迁移困难",
    "key_transformation": "知道算法但不会落题",
    "representation_modeling": "知道算法但不会落题",
    "constraint_relation": "知道算法但不会落题",
    "application_gap": "知道算法但不会落题",
}


def _safe_window_days(days: int = 15) -> int:
    return max(1, min(int(days or 15), 60))


def _recent_date_series(days: int) -> list[str]:
    today = datetime.now().date()
    return [(today - timedelta(days=offset)).isoformat() for offset in range(days - 1, -1, -1)]


def _issue_label(raw_type: str) -> str:
    key = (raw_type or "").strip()
    return ISSUE_CATEGORY_LABELS.get(key, "知道算法但不会落题" if key else "学习证据不足")


def _student_display_name(student_id: str) -> str:
    sid = (student_id or "").strip()
    if not sid:
        return "未命名学生"
    try:
        from auth import load_accounts

        account = load_accounts().get(sid) or {}
        if isinstance(account, dict):
            display_name = str(account.get("display_name") or account.get("name") or "").strip()
            if display_name:
                return display_name
    except Exception:
        pass
    return sid


def _learning_level_label(score: float | None) -> str:
    if score is None:
        return "缺少完成证据"
    if score >= 3.5:
        return "基本能独立完成"
    if score >= 2.5:
        return "少量提示能完成"
    if score > 0:
        return "需要较多帮助"
    return "缺少完成证据"


def _review_passed_paths() -> tuple[str, ...]:
    return ("main_clear", "remedy_clear", "bottom_out_clear", "bottom_out_clear")


def _fetch_recent_completions(cursor, student_id: str, safe_days: int) -> list[dict]:
    _ensure_student_problem_completions_table(cursor)
    cursor.execute(
        '''
        SELECT *
        FROM student_problem_completions
        WHERE student_id = ?
          AND created_at >= datetime('now', ?)
        ORDER BY created_at DESC, id DESC
        ''',
        (student_id or "", f"-{safe_days} days"),
    )
    rows = []
    for row in cursor.fetchall():
        item = dict(row)
        item["reported_completion_label"] = COMPLETION_METHOD_LABELS.get(item.get("reported_completion"), "未记录")
        item["result_status_label"] = COMPLETION_RESULT_LABELS.get(item.get("result_status"), "未记录")
        rows.append(item)
    return rows


def _fetch_completions_between_days(cursor, student_id: str, start_days_ago: int, end_days_ago: int) -> list[dict]:
    _ensure_student_problem_completions_table(cursor)
    cursor.execute(
        '''
        SELECT *
        FROM student_problem_completions
        WHERE student_id = ?
          AND created_at >= datetime('now', ?)
          AND created_at < datetime('now', ?)
        ORDER BY created_at DESC, id DESC
        ''',
        ((student_id or "").strip(), f"-{start_days_ago} days", f"-{end_days_ago} days"),
    )
    return [dict(row) for row in cursor.fetchall()]


def _completion_window_summary(completions: list[dict]) -> dict:
    completed_count = len(completions)
    independence_values = [
        INDEPENDENCE_SCORE_BY_METHOD.get(row.get("reported_completion"), 0.0) for row in completions
    ]
    quality_values = [_quality_score_for_completion(row) for row in completions]
    return {
        "completed_count": completed_count,
        "independence_avg": round(sum(independence_values) / completed_count, 3) if completed_count else 0.0,
        "quality_avg": round(sum(quality_values) / completed_count, 3) if completed_count else 0.0,
        "self_solved_count": sum(1 for row in completions if row.get("reported_completion") == "self_solved"),
        "aichat_assisted_count": sum(1 for row in completions if row.get("reported_completion") == "aichat_assisted"),
    }


def _trend_label(delta: float, *, positive: str, negative: str, stable: str) -> str:
    if delta >= 0.25:
        return positive
    if delta <= -0.25:
        return negative
    return stable


def _build_period_comparison(current_completions: list[dict], previous_completions: list[dict]) -> dict:
    current = _completion_window_summary(current_completions)
    previous = _completion_window_summary(previous_completions)
    independence_delta = round(current["independence_avg"] - previous["independence_avg"], 3)
    quality_delta = round(current["quality_avg"] - previous["quality_avg"], 3)
    completed_delta = current["completed_count"] - previous["completed_count"]
    return {
        "current": current,
        "previous": previous,
        "completed_delta": completed_delta,
        "quality_delta": quality_delta,
        "independence_delta": independence_delta,
        "completed_trend_label": "完成题数增加" if completed_delta > 0 else "完成题数减少" if completed_delta < 0 else "完成题数基本持平",
        "quality_trend_label": _trend_label(quality_delta, positive="完成质量上升", negative="完成质量下降", stable="完成质量基本持平"),
        "independence_trend_label": _trend_label(
            independence_delta,
            positive="独立程度上升",
            negative="独立程度下降",
            stable="独立程度基本持平",
        ),
    }


def _fetch_recent_review_rows(cursor, student_id: str, safe_days: int) -> list[dict]:
    cursor.execute(
        '''
        SELECT
            r.*,
            c.problem_title,
            c.problem_url,
            c.bottleneck_text,
            c.created_at AS checkin_created_at
        FROM reviews r
        LEFT JOIN checkins c ON c.id = r.checkin_id
        WHERE r.student_id = ?
          AND r.created_at >= datetime('now', ?)
        ORDER BY r.created_at DESC, r.id DESC
        LIMIT 50
        ''',
        (student_id or "", f"-{safe_days} days"),
    )
    return [dict(row) for row in cursor.fetchall()]


def _count_review_passed(review_rows: list[dict]) -> int:
    passed_paths = set(_review_passed_paths())
    passed_mastery = {MASTERY_STATUS_INDEPENDENT_SUCCESS, MASTERY_STATUS_ASSISTED_SUCCESS}
    return sum(
        1
        for row in review_rows
        if (row.get("bridge_path") in passed_paths) or (row.get("mastery_status") in passed_mastery)
    )


def _quality_score_for_completion(record: dict, review_bonus: bool = False) -> float:
    score = QUALITY_SCORE_BY_RESULT.get(record.get("result_status"), 0.2)
    if review_bonus:
        score = min(1.0, score + 0.3)
    return round(score, 3)


def _build_student_daily_series(completions: list[dict], review_rows: list[dict], safe_days: int) -> list[dict]:
    dates = _recent_date_series(safe_days)
    grouped: dict[str, list[dict]] = {date: [] for date in dates}
    for record in completions:
        date_key = str(record.get("created_at") or "")[:10]
        if date_key in grouped:
            grouped[date_key].append(record)
    review_passed_dates = {
        str(row.get("created_at") or row.get("checkin_created_at") or "")[:10]
        for row in review_rows
        if _count_review_passed([row]) > 0
    }
    series = []
    for date_key in dates:
        records = grouped.get(date_key, [])
        if records:
            independence_values = [
                INDEPENDENCE_SCORE_BY_METHOD.get(record.get("reported_completion"), 0.0) for record in records
            ]
            quality_values = [
                _quality_score_for_completion(record, review_bonus=date_key in review_passed_dates) for record in records
            ]
            independence_score = round(sum(independence_values) / len(independence_values), 3)
            quality_score = round(sum(quality_values) / len(quality_values), 3)
        else:
            independence_score = 0.0
            quality_score = 0.0
        series.append(
            {
                "date": date_key,
                "completed_count": len(records),
                "independence_score": independence_score,
                "independence_label": _learning_level_label(independence_score if records else None),
                "quality_score": quality_score,
            }
        )
    return series


def _fetch_student_issue_summary(cursor, student_id: str, safe_days: int) -> list[dict]:
    _ensure_problem_bottleneck_events_table(cursor)
    cursor.execute(
        '''
        SELECT bottleneck_type, problem_ref, evidence, COUNT(*) AS count
        FROM problem_bottleneck_events
        WHERE student_id = ?
          AND created_at >= datetime('now', ?)
        GROUP BY bottleneck_type, problem_ref, evidence
        ORDER BY count DESC
        LIMIT 20
        ''',
        (student_id or "", f"-{safe_days} days"),
    )
    buckets: dict[str, dict] = {}
    for row in cursor.fetchall():
        label = _issue_label(row["bottleneck_type"])
        bucket = buckets.setdefault(
            label,
            {
                "category": label,
                "count": 0,
                "evidence": "",
                "typical_problems": [],
            },
        )
        bucket["count"] += int(row["count"] or 0)
        if row["problem_ref"] and row["problem_ref"] not in bucket["typical_problems"]:
            bucket["typical_problems"].append(row["problem_ref"])
        if not bucket["evidence"]:
            bucket["evidence"] = row["evidence"] or f"最近在{label}上多次出现卡点。"

    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        SELECT problem_id, latest_tutor_action, same_gap_loop, understanding_evidence_types
        FROM aichat_session_summary
        WHERE student_id = ?
          AND updated_at >= datetime('now', ?)
        ORDER BY updated_at DESC
        LIMIT 20
        ''',
        (student_id or "", f"-{safe_days} days"),
    )
    for row in cursor.fetchall():
        if row["same_gap_loop"]:
            label = "知道算法但不会落题"
            bucket = buckets.setdefault(
                label,
                {
                    "category": label,
                    "count": 0,
                    "evidence": "",
                    "typical_problems": [],
                },
            )
            bucket["count"] += 1
            if row["problem_id"] and row["problem_id"] not in bucket["typical_problems"]:
                bucket["typical_problems"].append(row["problem_id"])
            if not bucket["evidence"]:
                bucket["evidence"] = "AIChat 中出现同点打转，说明学生可能知道方向但落不到下一步。"

    return sorted(buckets.values(), key=lambda item: (-item["count"], item["category"]))


def _teacher_next_action_for_student(summary: dict, issue_summary: list[dict]) -> str:
    if not summary.get("completed_count") and not issue_summary:
        return "最近缺少完成记录，先结合课堂观察确认学生正在学哪一类题。"
    categories = {item.get("category") for item in issue_summary}
    if "代码实现卡住" in categories or summary.get("aichat_assisted_count", 0) > summary.get("self_solved_count", 0):
        return "学生目前像是知道算法但不会稳定落到代码，建议安排一道同类低难度题，让学生先口头说出关键变量和更新步骤。"
    if "题意没读透" in categories:
        return "先让学生复述题目目标、输入输出和限制，再给一道同类小题确认读题方式。"
    if "调试定位困难" in categories:
        return "让学生带一个最小错误样例，说清预期输出和实际输出，再一起定位第一处不一致。"
    return "安排一道同类低难度题，让学生先独立尝试，再用一句话说明关键做法。"


_LUOGU_PID_PATTERN = re.compile(r"\bP\d{3,6}\b", re.IGNORECASE)


def _luogu_pid_from_ref(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    match = _LUOGU_PID_PATTERN.search(text)
    return match.group(0).upper() if match else ""


def _student_completed_problem_refs(completions: list[dict]) -> set[str]:
    refs: set[str] = set()
    for row in completions:
        for key in ("problem_id", "problem_url"):
            pid = _luogu_pid_from_ref(row.get(key))
            if pid:
                refs.add(pid)
    return refs


def _build_next_practice_recommendations(
    *,
    issue_summary: list[dict],
    completions: list[dict],
    limit: int = 3,
) -> list[dict]:
    completed_refs = _student_completed_problem_refs(completions)
    source_refs: list[tuple[str, str]] = []
    for issue in issue_summary:
        for ref in issue.get("typical_problems") or []:
            pid = _luogu_pid_from_ref(ref)
            if pid:
                source_refs.append((pid, issue.get("category") or "同类问题"))
    for row in completions:
        pid = _luogu_pid_from_ref(row.get("problem_id") or row.get("problem_url"))
        if pid:
            source_refs.append((pid, "最近做题记录"))

    recommendations: list[dict] = []
    seen: set[str] = set()
    for source_pid, category in source_refs:
        for item in list_related_problems_by_luogu_pid(source_pid, limit=limit + len(completed_refs) + 2):
            pid = _luogu_pid_from_ref(item.get("pid"))
            if not pid or pid in completed_refs or pid in seen:
                continue
            seen.add(pid)
            recommendations.append(
                {
                    **item,
                    "pid": pid,
                    "based_on": source_pid,
                    "category": category,
                    "reason": f"同类巩固：和 {source_pid} 都包含 {' / '.join(item.get('tags') or []) or '相近知识点'}，适合验证迁移。",
                }
            )
            if len(recommendations) >= limit:
                return recommendations
    return recommendations


def get_student_learning_dossier(student_id: str, days: int = 15) -> dict:
    safe_days = _safe_window_days(days)
    sid = (student_id or "").strip()
    conn = get_db()
    cursor = conn.cursor()
    completions = _fetch_recent_completions(cursor, sid, safe_days)
    previous_completions = _fetch_completions_between_days(cursor, sid, safe_days * 2, safe_days)
    review_rows = _fetch_recent_review_rows(cursor, sid, safe_days)
    issue_summary = _fetch_student_issue_summary(cursor, sid, safe_days)
    daily_series = _build_student_daily_series(completions, review_rows, safe_days)
    review_passed_count = _count_review_passed(review_rows)
    self_solved = sum(1 for row in completions if row.get("reported_completion") == "self_solved")
    small_hint = sum(1 for row in completions if row.get("reported_completion") == "small_hint")
    classroom_taught = sum(1 for row in completions if row.get("reported_completion") == "classroom_taught")
    aichat_assisted = sum(1 for row in completions if row.get("reported_completion") == "aichat_assisted")
    editorial = sum(1 for row in completions if row.get("reported_completion") == "editorial_completed")
    accepted = sum(1 for row in completions if row.get("result_status") == "accepted")
    has_loop = any("同点打转" in (item.get("evidence") or "") for item in issue_summary)
    needs_attention = bool(issue_summary) or aichat_assisted > self_solved or has_loop
    summary = {
        "completed_count": len(completions),
        "self_solved_count": self_solved,
        "small_hint_count": small_hint,
        "classroom_taught_count": classroom_taught,
        "aichat_assisted_count": aichat_assisted,
        "editorial_completed_count": editorial,
        "accepted_count": accepted,
        "review_passed_count": review_passed_count,
        "needs_attention": bool(needs_attention),
    }
    aichat_sessions = list_teacher_aichat_evidence_sessions(sid)
    notes = list_teacher_student_notes(sid)
    conn.close()
    next_practice_recommendations = _build_next_practice_recommendations(
        issue_summary=issue_summary,
        completions=completions,
        limit=3,
    )
    return {
        "student": {
            "student_id": sid,
            "display_name": _student_display_name(sid),
            "username": sid,
        },
        "window_days": safe_days,
        "daily_series": daily_series,
        "summary": summary,
        "period_comparison": _build_period_comparison(completions, previous_completions),
        "issue_summary": issue_summary,
        "next_teacher_action": _teacher_next_action_for_student(summary, issue_summary),
        "next_practice_recommendations": next_practice_recommendations,
        "problem_completions": completions,
        "reviews": review_rows,
        "aichat_sessions": aichat_sessions,
        "teacher_notes": notes,
    }


def _class_teaching_suggestion(category: str) -> str:
    if category == "题意没读透":
        return "课堂先带学生圈出目标、输入输出和限制，再让他们复述一遍。"
    if category == "方法选择困难":
        return "准备两道相邻知识点题，让学生说出为什么选这个方法而不是另一个。"
    if category == "知道算法但不会落题":
        return "用一个小例子把抽象算法落到变量、状态或循环顺序上。"
    if category == "代码实现卡住":
        return "示范如何从伪代码拆成变量、循环和边界条件。"
    if category == "调试定位困难":
        return "训练最小反例、预期输出、实际输出三步定位法。"
    if category == "复杂度判断薄弱":
        return "让学生先估数据范围，再判断 O(n²)/O(n log n) 是否可过。"
    return "挑同类低难度题，让学生先独立说出关键步骤。"


def _resource_suggestions_for_issue(category: str, typical_problems: list[str] | None = None) -> dict:
    problem_ref = (typical_problems or ["同类低难度题"])[0] if (typical_problems or []) else "同类低难度题"
    if category == "题意没读透":
        return {
            "recommended_exercise": f"{problem_ref} 的简化版：只保留输入、输出和一个样例。",
            "mini_lesson": "先讲如何圈目标量、条件限制和输出格式，不急着讲算法。",
            "classroom_activity": "让学生两人一组互相复述题意，另一人只负责追问遗漏条件。",
        }
    if category == "方法选择困难":
        return {
            "recommended_exercise": f"选一道和 {problem_ref} 相邻知识点的小题，要求学生先说为什么不用另一个方法。",
            "mini_lesson": "对比两个候选方法的适用条件，用数据范围和结构特征做判断。",
            "classroom_activity": "把三道题只给题意不讲解，让学生给每题贴方法标签并说明理由。",
        }
    if category == "知道算法但不会落题":
        return {
            "recommended_exercise": f"{problem_ref} 的 3-5 个对象小样例，要求先口头说变量含义。",
            "mini_lesson": "把算法动作翻译成变量、循环顺序和更新条件。",
            "classroom_activity": "一人说伪代码，一人把伪代码翻译成变量和循环，互相检查。",
        }
    if category == "代码实现卡住":
        return {
            "recommended_exercise": f"从 {problem_ref} 抽一个核心函数，让学生只补变量和循环。",
            "mini_lesson": "示范从伪代码拆成变量初始化、循环范围、更新条件三块。",
            "classroom_activity": "白板写伪代码，学生逐行标出需要的变量和边界条件。",
        }
    if category == "调试定位困难":
        return {
            "recommended_exercise": "给一段含单点错误的小代码，让学生写预期输出、实际输出和第一处差异。",
            "mini_lesson": "讲最小反例、预期输出、实际输出三步定位法。",
            "classroom_activity": "学生交换 WA 代码，只允许用一个最小样例定位问题。",
        }
    if category == "复杂度判断薄弱":
        return {
            "recommended_exercise": "给 3 个不同数据范围的小题，让学生先估朴素做法能不能过。",
            "mini_lesson": "把 N、M、Q 代入 O(n²)、O(n log n) 等常见复杂度。",
            "classroom_activity": "快速投票：每道题先判断朴素做法是否可过，再解释数量级。",
        }
    return {
        "recommended_exercise": "安排一道表面不同、结构相似的同类低难度题。",
        "mini_lesson": "先让学生说出旧题关键关系，再迁移到新题的对象关系。",
        "classroom_activity": "让学生比较两道题的相同结构和不同表述，最后独立写关键步骤。",
    }


def get_class_learning_diagnosis(days: int = 15) -> dict:
    safe_days = _safe_window_days(days)
    conn = get_db()
    cursor = conn.cursor()
    _ensure_problem_bottleneck_events_table(cursor)
    cursor.execute(
        '''
        SELECT student_id, bottleneck_type, problem_ref, evidence, COUNT(*) AS count
        FROM problem_bottleneck_events
        WHERE created_at >= datetime('now', ?)
        GROUP BY student_id, bottleneck_type, problem_ref, evidence
        ORDER BY count DESC
        LIMIT 200
        ''',
        (f"-{safe_days} days",),
    )
    issue_buckets: dict[str, dict] = {}
    attention: dict[str, dict] = {}
    for row in cursor.fetchall():
        label = _issue_label(row["bottleneck_type"])
        bucket = issue_buckets.setdefault(
            label,
            {
                "category": label,
                "student_ids": set(),
                "student_names": [],
                "count": 0,
                "typical_problems": [],
                "evidence": "",
                "teaching_suggestion": _class_teaching_suggestion(label),
            },
        )
        bucket["count"] += int(row["count"] or 0)
        sid = row["student_id"] or ""
        if sid and sid not in bucket["student_ids"]:
            bucket["student_ids"].add(sid)
            bucket["student_names"].append(_student_display_name(sid))
        if row["problem_ref"] and row["problem_ref"] not in bucket["typical_problems"]:
            bucket["typical_problems"].append(row["problem_ref"])
        if not bucket["evidence"]:
            bucket["evidence"] = row["evidence"] or f"{label}在最近练习中集中出现。"
        if sid:
            attention.setdefault(
                sid,
                {
                    "student_id": sid,
                    "display_name": _student_display_name(sid),
                    "reason": label,
                    "evidence": row["evidence"] or f"最近出现{label}。",
                    "teacher_action": _class_teaching_suggestion(label),
                    "severity": "high",
                },
            )

    _ensure_aichat_teaching_evidence_tables(cursor)
    cursor.execute(
        '''
        SELECT student_id, problem_id, same_gap_loop, latest_tutor_action
        FROM aichat_session_summary
        WHERE updated_at >= datetime('now', ?)
        ORDER BY updated_at DESC
        LIMIT 200
        ''',
        (f"-{safe_days} days",),
    )
    for row in cursor.fetchall():
        if not row["same_gap_loop"]:
            continue
        label = "知道算法但不会落题"
        sid = row["student_id"] or ""
        bucket = issue_buckets.setdefault(
            label,
            {
                "category": label,
                "student_ids": set(),
                "student_names": [],
                "count": 0,
                "typical_problems": [],
                "evidence": "",
                "teaching_suggestion": _class_teaching_suggestion(label),
            },
        )
        bucket["count"] += 1
        if sid and sid not in bucket["student_ids"]:
            bucket["student_ids"].add(sid)
            bucket["student_names"].append(_student_display_name(sid))
        if row["problem_id"] and row["problem_id"] not in bucket["typical_problems"]:
            bucket["typical_problems"].append(row["problem_id"])
        if not bucket["evidence"]:
            bucket["evidence"] = "多个学生在 AIChat 中出现同点打转。"
        if sid:
            attention.setdefault(
                sid,
                {
                    "student_id": sid,
                    "display_name": _student_display_name(sid),
                    "reason": label,
                    "evidence": "AIChat 中出现同点打转。",
                    "teacher_action": _class_teaching_suggestion(label),
                    "severity": "high",
                },
            )
    conn.close()

    completion = get_class_completion_summary(safe_days)
    practice_summary = {
        "days": safe_days,
        "completed_count": completion.get("total_15_days", 0),
        "student_count": completion.get("student_count_15_days", 0),
        "self_solved_count": completion.get("self_solved_15_days", 0),
        "small_hint_count": completion.get("small_hint_15_days", 0),
        "classroom_taught_count": completion.get("classroom_taught_15_days", 0),
        "aichat_assisted_count": completion.get("aichat_assisted_15_days", 0),
        "editorial_completed_count": completion.get("editorial_15_days", 0),
        "accepted_count": completion.get("accepted_15_days", 0),
        "independence_ratio": completion.get("independence_ratio", 0),
        "support_fadeout_label": completion.get("support_fadeout_label", ""),
    }
    class_issue_summary = []
    for bucket in issue_buckets.values():
        class_issue_summary.append(
            {
                "category": bucket["category"],
                "count": bucket["count"],
                "student_count": len(bucket["student_ids"]),
                "students": bucket["student_names"],
                "typical_problems": bucket["typical_problems"][:5],
                "evidence": bucket["evidence"],
                "teaching_suggestion": bucket["teaching_suggestion"],
                "resource_suggestions": _resource_suggestions_for_issue(
                    bucket["category"],
                    bucket["typical_problems"],
                ),
            }
        )
    class_issue_summary.sort(key=lambda item: (-item["student_count"], -item["count"], item["category"]))
    return {
        "window_days": safe_days,
        "attention_students": list(attention.values()),
        "class_issue_summary": class_issue_summary,
        "practice_summary": practice_summary,
    }


def create_teacher_student_note(
    *,
    student_id: str,
    teacher_id: str = "",
    note: str,
    status: str = "continue_followup",
    next_followup_at: str = "",
    intervention_type: str = "",
    target_issue: str = "",
) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_teacher_student_notes_table(cursor)
    clean_status = (status or "continue_followup").strip() or "continue_followup"
    cursor.execute(
        '''
        INSERT INTO teacher_student_notes
        (student_id, teacher_id, note, status, next_followup_at, intervention_type, target_issue)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            (student_id or "").strip(),
            (teacher_id or "").strip(),
            (note or "").strip(),
            clean_status,
            (next_followup_at or "").strip(),
            (intervention_type or "").strip(),
            (target_issue or "").strip(),
        ),
    )
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    notes = list_teacher_student_notes(student_id, limit=1)
    return notes[0] if notes else {"id": note_id, "student_id": student_id}


def _note_followup_observation(note: dict) -> dict:
    created_at = str(note.get("created_at") or "")
    if not created_at:
        return {"label": "观察中", "detail": "暂无创建时间，先作为人工记录保留。"}
    try:
        created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
    except ValueError:
        return {"label": "观察中", "detail": "创建时间格式暂不可解析，先作为人工记录保留。"}
    days_since = (datetime.now().date() - created_date).days
    if days_since < 7:
        return {"label": "观察中", "detail": "干预后不足 7 天，暂不判断效果。"}

    sid = str(note.get("student_id") or "").strip()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT *
        FROM student_problem_completions
        WHERE student_id = ?
          AND created_at >= ?
          AND created_at < datetime(?, '+7 days')
        ''',
        (sid, created_at, created_at),
    )
    after = [dict(row) for row in cursor.fetchall()]
    cursor.execute(
        '''
        SELECT *
        FROM student_problem_completions
        WHERE student_id = ?
          AND created_at >= datetime(?, '-7 days')
          AND created_at < ?
        ''',
        (sid, created_at, created_at),
    )
    before = [dict(row) for row in cursor.fetchall()]
    conn.close()
    comparison = _build_period_comparison(after, before)
    if not after:
        return {"label": "暂无后续记录", "detail": "干预后 7 天内还没有新的做题记录。", "comparison": comparison}
    return {
        "label": comparison["independence_trend_label"],
        "detail": f"干预后 7 天完成 {comparison['current']['completed_count']} 题，{comparison['independence_trend_label']}。",
        "comparison": comparison,
    }


def list_teacher_student_notes(student_id: str, limit: int = 50) -> list[dict]:
    safe_limit = max(1, min(int(limit or 50), 200))
    conn = get_db()
    cursor = conn.cursor()
    _ensure_teacher_student_notes_table(cursor)
    cursor.execute(
        '''
        SELECT *
        FROM teacher_student_notes
        WHERE student_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        ''',
        ((student_id or "").strip(), safe_limit),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for row in rows:
        row["followup_observation"] = _note_followup_observation(row)
    return rows


AICHAT_MEMORY_MAX_CHARS = 1000


def _compact_aichat_memory_summary(summary: str, max_chars: int = AICHAT_MEMORY_MAX_CHARS) -> str:
    text = (summary or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 3)].rstrip() + "..."


def upsert_aichat_problem_memory(
    *,
    student_id: str,
    problem_id: str,
    summary: str,
    source_session_id: str = "",
) -> None:
    """保存同题短摘要记忆；按学生+题目覆盖更新，不按 session 追加。"""
    compact_summary = _compact_aichat_memory_summary(summary)
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_problem_memory_table(cursor)
    cursor.execute(
        '''
        INSERT INTO aichat_problem_memory
            (student_id, problem_id, summary, source_session_id, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id, problem_id) DO UPDATE SET
            summary = excluded.summary,
            source_session_id = excluded.source_session_id,
            updated_at = CURRENT_TIMESTAMP
        ''',
        (student_id, problem_id, compact_summary, source_session_id or ""),
    )
    conn.commit()
    conn.close()


def get_aichat_problem_memory(*, student_id: str, problem_id: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    _ensure_aichat_problem_memory_table(cursor)
    cursor.execute(
        '''
        SELECT student_id, problem_id, summary, source_session_id, created_at, updated_at
        FROM aichat_problem_memory
        WHERE student_id = ? AND problem_id = ?
        ''',
        (student_id, problem_id),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


LEARNING_ISSUE_LABELS = {
    "problem_understanding": "题意没读透",
    "method_selection": "方法选择困难",
    "key_transformation": "关键转化没接上",
    "implementation": "代码实现卡住",
    "debugging": "调试定位困难",
    "complexity_boundary": "复杂度 / 边界问题",
    "aichat_learning": "AIChat 学习中",
}


def _contains_any(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens)


def _classify_learning_issue(text: str, has_student_code: bool) -> dict:
    normalized = (text or "").lower()
    if has_student_code and _contains_any(normalized, ["输出不对", "为什么不对", "wa", "样例", "错了", "debug", "调试"]):
        issue_type = "debugging"
        evidence = "学生带代码并表达输出、样例或调试问题。"
        action = "先让学生指出实际输出和期望输出分别代表题目里的哪个量，再看可疑语句。"
    elif _contains_any(normalized, ["复杂度", "超时", "tle", "10^", "o(", "边界", "数据范围", "枚举多少"]):
        issue_type = "complexity_boundary"
        evidence = "学生在讨论复杂度、数据范围、边界或是否会超时。"
        action = "让学生把 N、M、Q 代入朴素做法和优化做法，先估算数量级。"
    elif _contains_any(normalized, ["题意", "看不懂", "输入", "输出格式", "样例是什么意思", "要求是什么", "对象"]):
        issue_type = "problem_understanding"
        evidence = "学生在输入、输出、对象或题面要求上不稳定。"
        action = "让学生用自己的话说清对象、限制和最终要输出什么。"
    elif _contains_any(normalized, ["为什么可以", "为什么能", "怎么转化", "转化", "中转", "解锁", "可达", "缩点", "传递", "前缀", "后缀", "状态表示"]):
        issue_type = "key_transformation"
        evidence = "学生已经接触到方法，但关键条件到算法动作的连接没接上。"
        action = "用一个 3-5 个对象的小例子，把题目条件如何变成算法动作讲清。"
    elif _contains_any(normalized, ["用什么", "为什么用", "是不是", "dijkstra", "floyd", "dp", "贪心", "二分", "图论", "并查集", "搜索"]):
        issue_type = "method_selection"
        evidence = "学生在算法选择或为什么使用某方法上摇摆。"
        action = "先对比朴素做法和候选方法分别利用了题目里的哪条性质。"
    elif has_student_code or _contains_any(normalized, ["怎么写", "代码", "循环", "数组", "初始化", "变量", "实现"]):
        issue_type = "implementation"
        evidence = "学生需要把已有思路落成变量、循环、数组或代码结构。"
        action = "让学生先写伪代码骨架，只补一个关键循环或变量含义。"
    else:
        issue_type = "aichat_learning"
        evidence = "学生正在 AIChat 中学习，暂时没有明确归入具体困难类型。"
        action = "看最近对话，确认学生是否已经说清当前没有想明白的一步。"
    return {
        "learning_issue_type": issue_type,
        "learning_issue_label": LEARNING_ISSUE_LABELS[issue_type],
        "evidence": evidence,
        "teacher_action": action,
    }


def _classify_aichat_observation(text: str, has_student_code: bool) -> dict:
    normalized = (text or "").lower()
    learning_issue = _classify_learning_issue(text, has_student_code)
    if has_student_code and any(token in normalized for token in ["输出不对", "为什么不对", "wa", "样例", "错了", "debug"]):
        return {
            "issue_type": "code_debug",
            "issue_label": "代码输出不对",
            "suggested_teacher_action": "先看最近 AIChat，再让学生指出代码输出的量对应题目里的哪个量。",
            **learning_issue,
        }
    if any(token in normalized for token in ["复杂度", "超时", "tle", "枚举", "10^", "o("]):
        return {
            "issue_type": "complexity",
            "issue_label": "复杂度判断不清",
            "suggested_teacher_action": "让学生先估算朴素做法次数，再对照数据范围。",
            **learning_issue,
        }
    if any(token in normalized for token in ["题意", "看不懂", "输入", "输出格式", "样例是什么意思"]):
        return {
            "issue_type": "problem_understanding",
            "issue_label": "题意对象不清",
            "suggested_teacher_action": "先让学生用自己的话说清输入、输出和要优化的目标。",
            **learning_issue,
        }
    if any(token in normalized for token in ["check", "mid", "二分", "边界", "左边", "右边"]):
        return {
            "issue_type": "decision_condition",
            "issue_label": "判断条件不清",
            "suggested_teacher_action": "让学生说清一次判断在回答什么问题，以及 true/false 后范围怎么变。",
            **learning_issue,
        }
    if any(token in normalized for token in ["dp", "状态", "转移", "方程"]):
        return {
            "issue_type": "state_transition",
            "issue_label": "状态或转移不清",
            "suggested_teacher_action": "让学生先定义状态含义，再说一次转移来自哪个选择。",
            **learning_issue,
        }
    if has_student_code:
        return {
            "issue_type": "code_review",
            "issue_label": "带代码求助",
            "suggested_teacher_action": "先看最近代码提问，确认学生是卡在思路、实现还是输出解释。",
            **learning_issue,
        }
    return {
        "issue_type": "aichat_learning",
        "issue_label": "AIChat 学习中",
        "suggested_teacher_action": "看最近对话，确认学生是否已经说清当前卡点。",
        **learning_issue,
    }


def list_teacher_aichat_observations(limit: int = 30, days: int = 30) -> list[dict]:
    """给教师端读取最近 AIChat 学习观察；覆盖只聊天、未打卡的学生。"""
    safe_limit = max(1, min(int(limit), 100))
    safe_days = max(1, min(int(days), 365))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT
            id,
            student_id,
            problem_id,
            session_id,
            role,
            content,
            problem_title,
            problem_url,
            has_problem_context,
            has_student_code,
            created_at
        FROM aichat_messages
        WHERE created_at >= datetime('now', ?)
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        ''',
        (f"-{safe_days} days", safe_limit * 20),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    grouped: dict[tuple[str, str, str], dict] = {}
    for row in rows:
        key = (row["student_id"], row["problem_id"], row["session_id"])
        item = grouped.get(key)
        if item is None:
            item = {
                "student_id": row["student_id"],
                "problem_id": row["problem_id"],
                "session_id": row["session_id"],
                "problem_title": row["problem_title"] or "",
                "problem_url": row["problem_url"] or "",
                "last_message_at": row["created_at"],
                "student_message_count": 0,
                "has_problem_context": False,
                "has_student_code": False,
                "latest_student_message": "",
                "latest_assistant_message": "",
            }
            grouped[key] = item
        if row.get("problem_title") and not item["problem_title"]:
            item["problem_title"] = row["problem_title"]
        if row.get("problem_url") and not item["problem_url"]:
            item["problem_url"] = row["problem_url"]
        item["has_problem_context"] = item["has_problem_context"] or bool(row["has_problem_context"])
        item["has_student_code"] = item["has_student_code"] or bool(row["has_student_code"])
        if row["role"] == "user":
            item["student_message_count"] += 1
            if not item["latest_student_message"]:
                item["latest_student_message"] = row["content"] or ""
        elif row["role"] == "assistant" and not item["latest_assistant_message"]:
            item["latest_assistant_message"] = row["content"] or ""

    observations = []
    for item in grouped.values():
        if item["student_message_count"] <= 0:
            continue
        classification = _classify_aichat_observation(
            item["latest_student_message"],
            item["has_student_code"],
        )
        observations.append({**item, **classification})

    observations.sort(key=lambda x: x["last_message_at"] or "", reverse=True)
    return observations[:safe_limit]


def get_aichat_learning_issue_stats(days: int = 7) -> list[dict]:
    observations = list_teacher_aichat_observations(limit=100, days=days)
    total = len(observations)
    buckets: dict[str, dict] = {}
    for item in observations:
        issue_type = item.get("learning_issue_type") or "aichat_learning"
        label = item.get("learning_issue_label") or LEARNING_ISSUE_LABELS.get(issue_type, "AIChat 学习中")
        bucket = buckets.setdefault(
            issue_type,
            {
                "key": issue_type,
                "label": label,
                "count": 0,
                "student_ids": set(),
                "examples": [],
                "teacher_action": item.get("teacher_action") or item.get("suggested_teacher_action") or "",
            },
        )
        bucket["count"] += 1
        if item.get("student_id"):
            bucket["student_ids"].add(item["student_id"])
        if len(bucket["examples"]) < 3:
            bucket["examples"].append(
                {
                    "student_id": item.get("student_id", ""),
                    "problem_title": item.get("problem_title") or item.get("problem_id") or "未绑定题目",
                    "evidence": item.get("evidence") or item.get("latest_student_message") or "",
                }
            )

    result = []
    for bucket in buckets.values():
        count = int(bucket["count"])
        result.append(
            {
                "key": bucket["key"],
                "label": bucket["label"],
                "count": count,
                "total": total,
                "rate": round(count / total, 3) if total else 0,
                "student_count": len(bucket["student_ids"]),
                "teacher_action": bucket["teacher_action"],
                "examples": bucket["examples"],
            }
        )
    return sorted(result, key=lambda row: (-row["count"], row["label"]))


def record_checkin_stats(bottleneck_chars: int):
    """记录打卡统计（每日聚合）"""
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 尝试更新已有记录
    cursor.execute('''
    UPDATE usage_stats 
    SET checkin_count = checkin_count + 1,
        total_bottleneck_chars = total_bottleneck_chars + ?
    WHERE stat_date = ?
    ''', (bottleneck_chars, today))
    
    # 如果没有记录则插入
    if cursor.rowcount == 0:
        cursor.execute('''
        INSERT INTO usage_stats (stat_date, checkin_count, total_bottleneck_chars)
        VALUES (?, 1, ?)
        ''', (today, bottleneck_chars))
    
    # 重新计算平均值
    cursor.execute('''
    UPDATE usage_stats 
    SET avg_bottleneck_chars = CAST(total_bottleneck_chars AS REAL) / checkin_count
    WHERE stat_date = ?
    ''', (today,))
    
    conn.commit()
    conn.close()


def record_rejected_checkin():
    """记录被拒绝的打卡（卡点质量不够）"""
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
    UPDATE usage_stats 
    SET rejected_count = rejected_count + 1
    WHERE stat_date = ?
    ''', (today,))
    
    if cursor.rowcount == 0:
        cursor.execute('''
        INSERT INTO usage_stats (stat_date, checkin_count, rejected_count, total_bottleneck_chars)
        VALUES (?, 0, 1, 0)
        ''', (today,))
    
    conn.commit()
    conn.close()


def get_usage_stats(days: int = 7) -> list:
    """获取使用统计（最近N天）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT stat_date, checkin_count, rejected_count, avg_bottleneck_chars
    FROM usage_stats
    WHERE stat_date >= date('now', '-{} days')
    ORDER BY stat_date DESC
    '''.format(days))
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "date": row["stat_date"],
        "checkins": row["checkin_count"],
        "rejected": row["rejected_count"],
        "avg_chars": round(row["avg_bottleneck_chars"], 1) if row["avg_bottleneck_chars"] else 0
    } for row in rows]
