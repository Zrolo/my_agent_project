"""
SQLite database layer for NOI Training Loop.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "noi_agent.db"


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
) -> int:
    """创建打卡记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO checkins 
    (student_id, problem_url, problem_title, oj_source, completion_status, bottleneck_text, error_types, reflection)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id, problem_url, problem_title, oj_source,
        completion_status, bottleneck_text, json.dumps(error_types), reflection
    ))
    checkin_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return checkin_id


def get_student_checkins(student_id: str, limit: int = 50) -> list:
    """获取学生的打卡历史"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.*, r.id as review_id 
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
            "problem_title": row["problem_title"],
            "oj_source": row["oj_source"],
            "completion_status": row["completion_status"],
            "bottleneck_text": row["bottleneck_text"],
            "error_types": json.loads(row["error_types"]),
            "reflection": row["reflection"],
            "created_at": row["created_at"],
            "has_review": row["review_id"] is not None,
        })
    return checkins


def get_all_checkins(limit: int = 100, offset: int = 0) -> list:
    """获取所有打卡（教师用）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.*, r.id as review_id 
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
            "error_types": json.loads(row["error_types"]),
            "created_at": row["created_at"],
            "has_review": row["review_id"] is not None,
        })
    return checkins


# ============ Review Operations ============

def create_review(
    checkin_id: int,
    student_id: str,
    error_tags: list,
    diagnosis: str,
    next_action: str,
    suggested_topic: str,
):
    """创建 AI 复盘"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO reviews 
    (checkin_id, student_id, error_tags, diagnosis, next_action, suggested_topic)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        checkin_id, student_id, json.dumps(error_tags), 
        diagnosis, next_action, suggested_topic
    ))
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
            "error_tags": json.loads(row["error_tags"]),
            "diagnosis": row["diagnosis"],
            "next_action": row["next_action"],
            "suggested_topic": row["suggested_topic"],
            "created_at": row["created_at"],
        }
    return None


# ============ Teacher Dashboard Operations ============

def get_error_stats(days: int = 30) -> list:
    """获取错误类型统计"""
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
    conn.close()
    
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
    
    return sorted(flags, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])


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


# 初始化数据库
init_db()
