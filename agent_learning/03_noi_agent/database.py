"""
SQLite database layer for NOI Training Loop.
"""

import sqlite3
import json
from datetime import datetime
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
    
    conn.commit()
    conn.close()
    print(f"[db] Database initialized at {DB_PATH}")


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
        (luogu_pid, title, difficulty, statement_json, samples_json, time_limit_ms, memory_limit_kb, raw_json, source, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'luogu', ?)
        ON CONFLICT(luogu_pid) DO UPDATE SET
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
