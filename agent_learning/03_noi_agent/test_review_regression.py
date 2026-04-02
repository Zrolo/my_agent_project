#!/usr/bin/env python3
"""
Prompt 回归测试脚本（骨架版）

用途：
1. 向本地 NOI Agent 服务提交一组固定打卡样本
2. 检查 review_engine 输出是否存在明显退化
3. 为后续 Prompt 调整提供一个可重复执行的轻量回归入口

运行前：
    uvicorn api_server:app --reload --port 8000

示例：
    python3 test_review_regression.py
    python3 test_review_regression.py --cases A1,B1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Iterable

import requests

BASE = os.environ.get("NOI_TEST_BASE", "http://127.0.0.1:8000")
USER_ID = os.environ.get("NOI_TEST_USER", "student_a")
PASSWORD = os.environ.get("NOI_TEST_PASSWORD", "password")

PASS = "\033[92mPASS\033[0m"
WARN = "\033[93mWARN\033[0m"
FAIL = "\033[91mFAIL\033[0m"

GENERIC_PHRASES = (
    "加强基础",
    "多做练习",
    "多做这类题",
    "重新学习",
    "重新思考",
    "再想一遍",
    "重新阅读题目",
)


@dataclass
class RegressionCase:
    case_id: str
    category: str
    level: str
    title: str
    payload: dict
    expected_layers: tuple[str, ...]
    key_bridge_terms: tuple[str, ...] = field(default_factory=tuple)
    next_step_terms: tuple[str, ...] = field(default_factory=tuple)
    forbidden_terms: tuple[str, ...] = field(default_factory=tuple)


CASES: list[RegressionCase] = [
    RegressionCase(
        case_id="A1",
        category="图论与树",
        level="CSP-S",
        title="课程先修 / 对象-关系建模",
        payload={
            "problem_url": "https://example.com/course-prerequisite",
            "problem_title": "课程先修关系建模",
            "oj_source": "other",
            "completion_status": "independent",
            "problem_context": "给定若干课程的先修关系，要求把题意整理成图上的对象与关系：哪些是点，哪些是边，以及依赖方向该怎么表示。",
            "submission_result": "not_submitted",
            "bottleneck_text": "我知道这题像建图，但总是把课程这个对象和先修这个关系混在一起，不知道点和边分别该代表什么。",
            "error_types": ["模型转化", "不知道用什么算法"],
            "reflection": "我隐约觉得关键不是图算法本身，而是先把对象和关系抽清楚。",
        },
        expected_layers=("modeling",),
        key_bridge_terms=("对象", "关系", "点", "边"),
        next_step_terms=("点表示", "边表示", "对象", "关系", "抽清"),
        forbidden_terms=("状态转移", "背包"),
    ),
    RegressionCase(
        case_id="A2",
        category="图论与树",
        level="CSP-S",
        title="LCA / 树上算法",
        payload={
            "problem_url": "https://example.com/lca",
            "problem_title": "树上最近公共祖先查询",
            "oj_source": "other",
            "completion_status": "hinted",
            "problem_context": "给定一棵树，多次查询两个节点的最近公共祖先。常见做法是先预处理祖先信息，再快速回答查询。",
            "submission_result": "not_submitted",
            "bottleneck_text": "我知道可以用倍增，但总是不理解为什么要先把更深的点跳到同一深度，以及表里存的到底是什么祖先。",
            "error_types": ["知道算法但不知道怎么用", "模型转化"],
        },
        expected_layers=("core_design",),
        key_bridge_terms=("深度", "祖先", "2^", "上跳"),
        next_step_terms=("手推", "小树", "深度", "上跳"),
        forbidden_terms=("欧拉序", "背包"),
    ),
    RegressionCase(
        case_id="B1",
        category="约束建模",
        level="CSP-S",
        title="时间窗口 / 同时满足",
        payload={
            "problem_url": "https://example.com/time-window-and-location",
            "problem_title": "活动时间与地点约束",
            "oj_source": "other",
            "completion_status": "hinted",
            "problem_context": "每个活动都必须同时满足时间窗口和指定地点两个条件，才算合法安排。题目问的是这些限制之间是什么关系。",
            "submission_result": "wa",
            "bottleneck_text": "我看到时间和地点两个限制，但总把它们当成主条件加附带检查，不确定是不是要同时满足。",
            "error_types": ["状态设计", "状态转移"],
            "reflection": "关键像是并列约束，而不是一个主条件配一个顺手检查。",
        },
        expected_layers=("core_design",),
        key_bridge_terms=("同时满足", "并列条件", "合法安排", "附带检查"),
        next_step_terms=("整理限制", "标出条件", "同时满足", "附带检查"),
        forbidden_terms=("不等式", "建图", "边权"),
    ),
    RegressionCase(
        case_id="C1",
        category="数据结构",
        level="CSP-S",
        title="Trie / 数据结构理解",
        payload={
            "problem_url": "https://example.com/trie",
            "problem_title": "Trie 字符串统计类题",
            "oj_source": "other",
            "completion_status": "unfinished",
            "problem_context": "维护一批字符串，支持插入和查询某个前缀出现了多少次。",
            "submission_result": "not_submitted",
            "bottleneck_text": "我知道这题不是暴力遍历所有字符串，但我不明白 Trie 到底比 map 存整个字符串强在哪里，也不知道每个节点该记录什么。",
            "error_types": ["模型转化", "知道算法但不知道怎么用"],
        },
        expected_layers=("modeling", "core_design"),
        key_bridge_terms=("前缀", "节点", "字符", "路径"),
        next_step_terms=("手画", "节点", "路径", "插入"),
        forbidden_terms=("最短路", "状态转移"),
    ),
    RegressionCase(
        case_id="C2",
        category="数据结构",
        level="CSP-S",
        title="并查集 / 数据结构作用",
        payload={
            "problem_url": "https://example.com/dsu",
            "problem_title": "动态合并点集并查询是否连通",
            "oj_source": "other",
            "completion_status": "unfinished",
            "problem_context": "不断加入边，并查询两个点是否在同一个连通块中。",
            "submission_result": "not_submitted",
            "bottleneck_text": "我知道这题和连通性有关，但不明白并查集为什么只维护父节点就够了，也不知道合并时到底是在合并什么。",
            "error_types": ["模型转化", "知道算法但不知道怎么用"],
        },
        expected_layers=("modeling", "core_design"),
        key_bridge_terms=("集合", "代表元", "根", "合并"),
        next_step_terms=("模拟", "union", "查询", "根"),
        forbidden_terms=("最短路", "状态转移"),
    ),
    RegressionCase(
        case_id="D1",
        category="二分、贪心与策略",
        level="CSP-S",
        title="n<=20 / 枚举边界",
        payload={
            "problem_url": "https://example.com/enumerate-subsets",
            "problem_title": "小规模子集最优值",
            "oj_source": "other",
            "completion_status": "unfinished",
            "problem_context": "n <= 20，需要枚举所有子集并从中找最优方案。题目同时给出明确规模上界。",
            "submission_result": "unknown",
            "bottleneck_text": "我一看到最优值就想套 DP，但没判断这个规模其实允许直接枚举全部子集。",
            "error_types": ["check_condition", "知道算法但不知道怎么用"],
        },
        expected_layers=("core_design",),
        key_bridge_terms=("n<=20", "规模上界", "全部子集", "直接枚举"),
        next_step_terms=("判断规模", "直接枚举", "全部子集", "先别套dp"),
        forbidden_terms=("必须DP", "贪心", "最短路"),
    ),
    RegressionCase(
        case_id="D2",
        category="二分、贪心与策略",
        level="CSP-S",
        title="区间调度 / 结束时间最早",
        payload={
            "problem_url": "https://example.com/interval-scheduling",
            "problem_title": "最早结束的区间选择",
            "oj_source": "other",
            "completion_status": "unfinished",
            "problem_context": "有 n 个区间任务，每个任务有开始和结束时间，目标是选出尽可能多的互不重叠任务。",
            "submission_result": "not_submitted",
            "bottleneck_text": "我知道常见做法是先选结束时间早的，但说不清这个选择为什么不会吃亏，也不确定它为什么能给后续留出更多空间。",
            "error_types": ["优化策略", "知道算法但不知道怎么用"],
        },
        expected_layers=("core_design",),
        key_bridge_terms=("结束时间最早", "后续空间", "不吃亏", "兼容"),
        next_step_terms=("画", "区间", "比较", "兼容"),
        forbidden_terms=("最短路", "状态转移"),
    ),
    RegressionCase(
        case_id="E1",
        category="搜索与递归",
        level="CSP-J / CSP-S",
        title="DFS / 递归结构",
        payload={
            "problem_url": "https://example.com/dfs-backtracking",
            "problem_title": "枚举所有可行方案",
            "oj_source": "other",
            "completion_status": "unfinished",
            "problem_context": "需要枚举满足条件的所有方案，并在搜索过程中剪枝。",
            "submission_result": "unknown",
            "bottleneck_text": "我会写递归函数，但一递归就乱了，不知道当前这一层函数到底表示什么，也总是忘记回溯时该恢复哪些状态。",
            "error_types": ["递归结构", "实现调试"],
        },
        expected_layers=("core_design", "implementation"),
        key_bridge_terms=("当前层", "恢复", "状态", "回溯"),
        next_step_terms=("函数", "状态", "恢复", "记录"),
        forbidden_terms=("最短路", "不等式"),
    ),
    RegressionCase(
        case_id="F1",
        category="实现调试",
        level="CSP-J / CSP-S",
        title="实现调试 / 边界条件",
        payload={
            "problem_url": "https://example.com/debug-boundary",
            "problem_title": "实现类题目",
            "oj_source": "other",
            "completion_status": "independent",
            "problem_context": "题目逻辑不复杂，但需要处理 n=1、空区间、负数等边界。",
            "submission_result": "wa",
            "bottleneck_text": "样例能过，但提交后一直 WA。我后来发现自己默认数组长度至少为 2，n=1 时访问了 a[1] 和 a[2]。",
            "error_types": ["边界条件", "数组越界"],
        },
        expected_layers=("implementation",),
        key_bridge_terms=("边界", "默认", "前提", "越界"),
        next_step_terms=("列出", "n=1", "边界", "最小"),
        forbidden_terms=("最短路", "状态转移"),
    ),
    RegressionCase(
        case_id="G1",
        category="信息不足",
        level="通用",
        title="信息不足 / insufficient",
        payload={
            "problem_url": "https://example.com/insufficient",
            "problem_title": "信息不足样本",
            "oj_source": "other",
            "completion_status": "unfinished",
            "problem_context": "一道图论题，但我现在还说不清具体模型。",
            "submission_result": "unknown",
            "bottleneck_text": "我现在只知道它和图有关，但说不清卡在哪一步，也没有形成明确思路，只能描述到这里。",
            "error_types": ["其他"],
        },
        expected_layers=("insufficient",),
        key_bridge_terms=("补充题目要求", "尝试过程", "具体断点", "定位桥梁"),
        next_step_terms=("补充题目", "补充思路", "具体卡点", "重新提交"),
        forbidden_terms=("最短路一定", "状态转移一定"),
    ),
]


def status(label: str, message: str) -> None:
    print(f"{label} {message}")


def normalize_text(text: str) -> str:
    normalized = (text or "").lower()
    replacements = (
        (" ", ""),
        ("\n", ""),
        ("\t", ""),
        ("`", ""),
        ("n <= 20", "n<=20"),
        ("n≤20", "n<=20"),
        ("2 的 k 次方", "2^k"),
        ("2的k次方", "2^k"),
        ("union", "合并"),
        ("二选一", "择一"),
        ("顺手检查", "附带检查"),
    )
    for old, new in replacements:
        normalized = normalized.replace(old, new)
    return normalized


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    lowered = normalize_text(text)
    return any(normalize_text(keyword) in lowered for keyword in keywords)


def count_matches(text: str, keywords: Iterable[str]) -> int:
    lowered = normalize_text(text)
    return sum(1 for keyword in keywords if normalize_text(keyword) in lowered)


def contains_forbidden(text: str, keywords: Iterable[str]) -> bool:
    lowered = normalize_text(text)
    for keyword in keywords:
        needle = normalize_text(keyword)
        if needle not in lowered:
            continue

        # 允许“不是 X / 不要 X / 非 X”这类纠偏表达，不把它们当成串题型。
        negated_patterns = (
            f"不是{needle}",
            f"不要{needle}",
            f"非{needle}",
        )
        if any(pattern in lowered for pattern in negated_patterns):
            continue
        return True
    return False


def login() -> str:
    response = requests.post(
        f"{BASE}/auth/login",
        json={"user_id": USER_ID, "password": PASSWORD},
        timeout=20,
    )
    response.raise_for_status()
    token = response.json().get("token")
    if not token:
        raise RuntimeError("登录成功但未拿到 token")
    return token


def evaluate_case(case: RegressionCase, review: dict | None) -> tuple[bool, list[str], list[str]]:
    warnings: list[str] = []
    failures: list[str] = []

    if not review:
        failures.append("review 为空（可能 pending 或生成失败）")
        return False, warnings, failures

    layer = review.get("error_layer")
    if layer not in case.expected_layers:
        failures.append(f"error_layer={layer}，预期 {case.expected_layers}")

    for field_name in ("main_block", "key_bridge", "next_step", "transfer_signal"):
        value = (review.get(field_name) or "").strip()
        if not value:
            failures.append(f"{field_name} 为空")
        elif contains_any(value, GENERIC_PHRASES):
            failures.append(f"{field_name} 含泛化表达：{value}")

    key_bridge = review.get("key_bridge") or ""
    next_step = review.get("next_step") or ""
    student_text = " ".join(
        [
            review.get("main_block") or "",
            key_bridge,
            next_step,
            review.get("transfer_signal") or "",
        ]
    )

    if case.key_bridge_terms and count_matches(key_bridge, case.key_bridge_terms) < 2:
        failures.append(f"key_bridge 命中期望结构词不足 2 个：{case.key_bridge_terms}")

    if case.next_step_terms and count_matches(next_step, case.next_step_terms) < 2:
        failures.append(f"next_step 命中期望动作词不足 2 个：{case.next_step_terms}")

    if case.forbidden_terms and contains_forbidden(student_text, case.forbidden_terms):
        failures.append(f"出现疑似串题型/错误术语：{case.forbidden_terms}")

    return not failures, warnings, failures


def run_case(token: str, case: RegressionCase) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            f"{BASE}/api/checkins",
            json=case.payload,
            headers=headers,
            timeout=90,
        )
    except requests.RequestException as exc:
        status(FAIL, f"{case.case_id} {case.title} | 请求失败 | {exc}")
        return False

    if response.status_code != 200:
        status(FAIL, f"{case.case_id} {case.title} | HTTP {response.status_code} | {response.text[:200]}")
        return False

    data = response.json()
    review_status = data.get("review_status")
    review = data.get("review")

    if review_status != "completed":
        status(FAIL, f"{case.case_id} {case.title} | review_status={review_status}，未进行内容评分")
        return False

    passed, warnings, failures = evaluate_case(case, review)

    if passed and not warnings:
        status(PASS, f"{case.case_id} {case.title} | layer={review.get('error_layer')}")
    elif passed and warnings:
        status(WARN, f"{case.case_id} {case.title} | layer={review.get('error_layer')}")
        for item in warnings:
            print(f"  - {item}")
    else:
        status(FAIL, f"{case.case_id} {case.title} | layer={review.get('error_layer')}")
        for item in failures:
            print(f"  - {item}")
        for item in warnings:
            print(f"  - {item}")

    print(json.dumps(
        {
            "main_block": review.get("main_block"),
            "key_bridge": review.get("key_bridge"),
            "next_step": review.get("next_step"),
            "transfer_signal": review.get("transfer_signal"),
            "next_action": review.get("next_action"),
            "suggested_topic": review.get("suggested_topic"),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description="NOI Agent Prompt 回归测试脚本（骨架版）")
    parser.add_argument(
        "--cases",
        help="逗号分隔的 case id，例如 A1,B1,G1；默认全跑",
    )
    args = parser.parse_args()

    selected = {item.strip().upper() for item in args.cases.split(",")} if args.cases else None
    active_cases = [case for case in CASES if not selected or case.case_id in selected]

    if not active_cases:
        print("没有匹配到任何 case。")
        return 1

    try:
        token = login()
    except Exception as exc:
        print(f"{FAIL} 登录失败: {exc}")
        return 1

    total = len(active_cases)
    passed = 0
    print(f"Running {total} review regression cases against {BASE}\n")
    for case in active_cases:
        ok = run_case(token, case)
        if ok:
            passed += 1
        print()

    print("=" * 40)
    print(f"Summary: {passed}/{total} cases passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
