# B1 / D1 Structure Regression Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `B1 / D1` 从固定词表命中改成“结构主规则 + 少量辅助词兜底”的回归门。

**Architecture:** 在 `test_review_regression.py` 中为 `B1 / D1` 增加独立判定函数，保留原通用逻辑给其它 case。先用单元测试锁定结构判定和反例，再最小改脚本，最后跑真实 AI 回归。

**Tech Stack:** Python 3、pytest、requests

---

### Task 1: 为 B1 / D1 新回归门补单元测试

**Files:**
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression_unit.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression.py`

- [ ] Step 1: 写 B1 / D1 正反例失败测试
- [ ] Step 2: 跑 `pytest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression_unit.py -q`，确认先红

### Task 2: 在脚本里落结构断言判定

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression_unit.py`

- [ ] Step 1: 新增 `B1 / D1` 独立判定函数
- [ ] Step 2: 让 `evaluate_case()` 对 `B1 / D1` 先走新规则，其它 case 仍走旧规则
- [ ] Step 3: 再跑单元测试，确认转绿

### Task 3: 跑真实链路验证

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression.py`

- [ ] Step 1: 跑 `python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression.py --cases B1,D1`
- [ ] Step 2: 如有必要，只在 `test_review_regression.py` 内做最小校正
- [ ] Step 3: 跑 `python3 -m py_compile /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_regression_unit.py`
