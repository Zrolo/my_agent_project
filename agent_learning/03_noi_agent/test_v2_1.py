#!/usr/bin/env python3
"""
NOI Agent v2.1 自动化测试
运行前确保服务已启动：uvicorn api_server:app --reload --port 8000
"""

import os
import sqlite3
import sys

import requests

BASE = os.environ.get("NOI_TEST_BASE", "http://localhost:8000")
PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"

results = []


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"{status} {name}" + (f"  [{detail}]" if detail else ""))
    results.append(condition)


def main():
    # ---- 登录 ----
    r = requests.post(f"{BASE}/auth/login", json={"user_id": "student_a", "password": "password"}, timeout=15)
    check("T00 登录", r.status_code == 200)
    student_token = r.json().get("token", "") if r.ok else ""
    headers = {"Authorization": f"Bearer {student_token}"}

    r2 = requests.post(f"{BASE}/auth/login", json={"user_id": "teacher", "password": "password"}, timeout=15)
    check("T00 教师登录", r2.status_code == 200)
    teacher_token = r2.json().get("token", "") if r2.ok else ""
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # ---- T01 正常打卡 ----
    payload = {
        "problem_url": "https://www.luogu.com.cn/problem/P1020",
        "problem_title": "导弹拦截",
        "oj_source": "luogu",
        "completion_status": "hinted",
        "problem_context": "给定一个序列，求最长不升子序列长度，以及最少需要多少个不升子序列覆盖整个序列",
        "submission_result": "wa",
        "bottleneck_text": "第一问用了 DP 但第二问完全没思路，不知道和 Dilworth 定理有什么关系，看了题解才明白",
        "error_types": ["状态设计", "模型转化"],
    }
    r = requests.post(f"{BASE}/api/checkins", json=payload, headers=headers, timeout=30)
    check("T01 正常打卡 HTTP 200", r.status_code == 200, r.text[:100])
    if r.status_code == 200:
        data = r.json()
        check("T01 有 checkin_id", isinstance(data.get("checkin_id"), int))
        check("T01 review_status 存在", data.get("review_status") in ("completed", "pending"))
        review = data.get("review") or {}
        for field in ["main_block", "key_bridge", "next_step", "transfer_signal"]:
            check(
                f"T01 review.{field} 存在",
                field in review or data.get("review_status") == "pending",
                "(pending 时可为空)",
            )

    # ---- T02 缺 problem_context ----
    payload2 = {
        "problem_url": "https://www.luogu.com.cn/problem/P1001",
        "problem_title": "A+B",
        "oj_source": "luogu",
        "completion_status": "independent",
        "bottleneck_text": "边界条件没考虑，负数输入导致数组越界，加了特判就过了",
        "error_types": ["边界条件"],
    }
    r = requests.post(f"{BASE}/api/checkins", json=payload2, headers=headers, timeout=15)
    check("T02 缺 problem_context 返回 422", r.status_code == 422, f"got {r.status_code}")

    # ---- T03 problem_context 太短 ----
    payload3 = {**payload2, "problem_context": "加法"}
    r = requests.post(f"{BASE}/api/checkins", json=payload3, headers=headers, timeout=15)
    check("T03 problem_context<10 返回 422", r.status_code == 422, f"got {r.status_code}")

    # ---- T04 submission_result 非法值 ----
    payload4 = {**payload2, "problem_context": "两个整数相加求和", "submission_result": "accepted"}
    r = requests.post(f"{BASE}/api/checkins", json=payload4, headers=headers, timeout=15)
    check("T04 非法 submission_result 返回 422", r.status_code == 422, f"got {r.status_code}")

    # ---- T05 submission_result=null ----
    payload5 = {**payload2, "problem_context": "两个整数 A 和 B，输出 A+B 的结果", "submission_result": None}
    r = requests.post(f"{BASE}/api/checkins", json=payload5, headers=headers, timeout=30)
    check("T05 submission_result=null 返回 200", r.status_code == 200, f"got {r.status_code}")

    # ---- T06 历史新字段 ----
    r = requests.get(f"{BASE}/api/checkins/me", headers=headers, timeout=15)
    check("T06 查询历史 HTTP 200", r.status_code == 200)
    if r.status_code == 200:
        checkins = r.json().get("checkins", [])
        check("T06 历史非空", len(checkins) > 0)
        latest = checkins[0] if checkins else {}
        check("T06 历史有 problem_context 字段", "problem_context" in latest)
        check("T06 历史有 review_main_block 字段", "review_main_block" in latest)

    # ---- T07 教师端 ----
    r = requests.get(f"{BASE}/api/teacher/checkins?limit=5", headers=teacher_headers, timeout=15)
    check("T07 教师查询 HTTP 200", r.status_code == 200)
    if r.status_code == 200:
        checkins = r.json().get("checkins", [])
        if checkins:
            item = checkins[0]
            check("T07 教师端有 problem_context 字段", "problem_context" in item)
            check("T07 教师端有 review_main_block 字段", "review_main_block" in item)

    # ---- T13 健康检查 ----
    r = requests.get(f"{BASE}/", timeout=15)
    check("T13 健康检查", r.status_code == 200 and "version" in r.json())

    # ---- 数据库表结构 ----
    db_path = os.path.join(os.path.dirname(__file__), "noi_agent.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(checkins)")
        checkin_cols = {row[1] for row in cursor.fetchall()}
        cursor.execute("PRAGMA table_info(reviews)")
        review_cols = {row[1] for row in cursor.fetchall()}
        conn.close()

        for col in ["problem_context", "submission_result", "student_code"]:
            check(f"DB checkins.{col} 存在", col in checkin_cols)
        for col in ["main_block", "key_bridge", "next_step", "transfer_signal"]:
            check(f"DB reviews.{col} 存在", col in review_cols)

    print()
    passed = sum(results)
    total = len(results)
    print("=" * 40)
    print(f"结果：{passed}/{total} 通过")
    if passed == total:
        print("\033[92m全部通过 🎉\033[0m")
    else:
        print(f"\033[91m{total - passed} 项失败，请检查上方输出\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
