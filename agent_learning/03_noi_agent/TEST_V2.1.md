# NOI Agent v2.1 测试文档

> 测试对象：打卡复盘 v2.1 改动
> 项目路径：`~/Downloads/my_agent_project/agent_learning/03_noi_agent/`
> 测试目标：验证新增输入字段落库、AI 复盘输出纠偏层、pending→retry 链路完整性

---

## 一、环境准备

### 1.1 启动服务

```bash
cd ~/Downloads/my_agent_project/agent_learning/03_noi_agent

# 安装依赖（如未安装）
pip3 install -r requirements.txt

# 设置 API Key（需要有效的 Moonshot API Key）
export MOONSHOT_API_KEY="sk-xxxx"
export NOI_TEACHER_SECRET="test_secret_123"

# 启动
uvicorn api_server:app --reload --port 8000
```

### 1.2 演示账号

| 账号 | 密码 | 角色 |
|------|------|------|
| student_a | password | 学生 |
| student_b | password | 学生 |
| teacher | password | 教师 |

### 1.3 获取 Token（后续测试都需要）

```bash
# 获取学生 token
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "student_a", "password": "password"}' | python3 -m json.tool

# 保存 token（把 <token> 替换为返回的 token 值）
STUDENT_TOKEN="<token>"
TEACHER_TOKEN="<teacher_token>"
```

---

## 二、核心功能测试

### T01 — 新字段打卡（正常流程）✅ 必测

**测试目的：** 验证 `problem_context`（必填）+ `submission_result` + `student_code` 能正确落库并触发 AI 复盘

```bash
curl -s -X POST http://localhost:8000/api/checkins \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{
    "problem_url": "https://www.luogu.com.cn/problem/P1020",
    "problem_title": "导弹拦截",
    "oj_source": "luogu",
    "completion_status": "hinted",
    "problem_context": "给定一个序列，求最长不升子序列长度，以及最少需要多少个不升子序列覆盖整个序列",
    "submission_result": "wa",
    "bottleneck_text": "第一问用了 DP，dp[i] 表示以 i 结尾的最长不升子序列，转移写出来了但第二问完全没思路，不知道和第一问有什么关系",
    "error_types": ["状态设计", "模型转化"],
    "reflection": "第二问可能需要用贪心或者 Dilworth 定理",
    "student_code": "#include<bits/stdc++.h>\nusing namespace std;\nint dp[100005];\nint main(){\n  int n; cin>>n;\n  // ...\n}"
  }' | python3 -m json.tool
```

**期望结果：**
- HTTP 200
- `checkin_id` 为整数
- `review_status` 为 `"completed"`（如有 API Key）或 `"pending"`（无 API Key）
- `review` 对象中包含以下字段（非空）：
  - `main_block`
  - `key_bridge`
  - `next_step`
  - `transfer_signal`
  - `error_tags`
  - `error_layer`
  - `diagnosis`
  - `next_action`
  - `suggested_topic`

---

### T02 — `problem_context` 未填（拦截测试）✅ 必测

**测试目的：** 验证 `problem_context` 缺失时后端返回 422

```bash
curl -s -X POST http://localhost:8000/api/checkins \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{
    "problem_url": "https://www.luogu.com.cn/problem/P1001",
    "problem_title": "A+B Problem",
    "oj_source": "luogu",
    "completion_status": "independent",
    "bottleneck_text": "边界条件没考虑，负数输入导致数组越界",
    "error_types": ["边界条件"]
  }' | python3 -m json.tool
```

**期望结果：**
- HTTP 422
- `detail` 中包含 `problem_context` 相关字段错误提示

---

### T03 — `problem_context` 太短（拦截测试）✅ 必测

```bash
curl -s -X POST http://localhost:8000/api/checkins \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{
    "problem_url": "https://www.luogu.com.cn/problem/P1001",
    "problem_title": "A+B Problem",
    "oj_source": "luogu",
    "completion_status": "independent",
    "problem_context": "加法",
    "bottleneck_text": "边界条件没考虑，负数输入导致数组越界",
    "error_types": ["边界条件"]
  }' | python3 -m json.tool
```

**期望结果：**
- HTTP 422（`problem_context` 最小长度 10）

---

### T04 — `submission_result` 非法值（拦截测试）✅ 必测

```bash
curl -s -X POST http://localhost:8000/api/checkins \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{
    "problem_url": "https://www.luogu.com.cn/problem/P1001",
    "problem_title": "A+B Problem",
    "oj_source": "luogu",
    "completion_status": "independent",
    "problem_context": "两个整数相加，输出结果",
    "submission_result": "accepted",
    "bottleneck_text": "边界条件没考虑，负数输入导致数组越界",
    "error_types": ["边界条件"]
  }' | python3 -m json.tool
```

**期望结果：**
- HTTP 422（`submission_result` 不在合法枚举内，合法值为 `not_submitted/wa/tle/re/ce/unknown`）

---

### T05 — `submission_result` 为 null（允许为空）✅ 必测

```bash
curl -s -X POST http://localhost:8000/api/checkins \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{
    "problem_url": "https://www.luogu.com.cn/problem/P1001",
    "problem_title": "A+B Problem",
    "oj_source": "luogu",
    "completion_status": "independent",
    "problem_context": "两个整数 A 和 B，输出 A+B 的结果",
    "submission_result": null,
    "bottleneck_text": "边界条件没考虑，负数输入导致数组越界，加了特判就过了",
    "error_types": ["边界条件"]
  }' | python3 -m json.tool
```

**期望结果：**
- HTTP 200，正常创建

---

### T06 — 查询历史，新字段可见 ✅ 必测

先完成 T01，然后：

```bash
curl -s http://localhost:8000/api/checkins/me \
  -H "Authorization: Bearer $STUDENT_TOKEN" | python3 -m json.tool
```

**期望结果：**
- 返回的 checkin 列表中，最新一条包含：
  - `problem_context`（非 null）
  - `submission_result`（对应 T01 中填写的值）
  - `review_main_block`（非空字符串）
  - `review_key_bridge`（非空字符串）
  - `review_next_step`（非空字符串）
  - `review_transfer_signal`（非空字符串）

---

### T07 — 教师查看打卡，新字段可见 ✅ 必测

```bash
# 先获取教师 token
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "teacher", "password": "password"}' | python3 -m json.tool

TEACHER_TOKEN="<teacher_token>"

curl -s "http://localhost:8000/api/teacher/checkins?limit=10" \
  -H "Authorization: Bearer $TEACHER_TOKEN" | python3 -m json.tool
```

**期望结果：**
- 能看到 `problem_context`、`submission_result`
- 能看到 `review_main_block` 等 4 个纠偏字段

---

### T08 — pending review 重试链路 ✅ 必测（核心漏洞修复验证）

**测试目的：** 验证 v2.1 改动后 pending→retry 链路不会因缺少 `problem_context` 而崩溃

**步骤：**

1. **不设置 API Key 的情况下提交打卡**（模拟 LLM 不可用，产生 pending 记录）：

```bash
# 先 unset API Key
unset MOONSHOT_API_KEY

# 重启服务（使 env 生效）
# Ctrl+C 后重新：uvicorn api_server:app --reload --port 8000

curl -s -X POST http://localhost:8000/api/checkins \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{
    "problem_url": "https://www.luogu.com.cn/problem/P1486",
    "problem_title": "数列分段 Section II",
    "oj_source": "luogu",
    "completion_status": "editorial",
    "problem_context": "给一个数列，分成 m 段，使得每段的最大值之和最小，求这个最小值",
    "submission_result": "tle",
    "bottleneck_text": "知道是二分答案，但不确定 check 函数怎么写，不知道贪心地从左到右分段是否正确",
    "error_types": ["check_condition", "贪心"]
  }' | python3 -m json.tool
```

**期望：** `review_status: "pending"`，`checkin_id` 有值

2. **恢复 API Key，用教师端触发重试：**

```bash
export MOONSHOT_API_KEY="sk-xxxx"

curl -s -X POST http://localhost:8000/api/teacher/reviews/retry-pending \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TEACHER_TOKEN" \
  -d '{"limit": 5}' | python3 -m json.tool
```

**期望结果：**
- `attempted >= 1`
- `completed >= 1`（如 API Key 有效）
- **不能出现报错或 `still_pending` 因为 `problem_context` 字段缺失造成的异常**

3. **确认重试后历史记录已更新：**

```bash
curl -s http://localhost:8000/api/checkins/me \
  -H "Authorization: Bearer $STUDENT_TOKEN" | python3 -m json.tool
```

**期望：** 步骤 1 的那条记录 `review_status` 变为 `"completed"`，且有 4 个纠偏字段

---

## 三、旧数据兼容性测试

### T09 — 旧版 checkin（无新字段）不报错 ✅ 必测

如果数据库里有 v2.0 的旧打卡记录（无 `problem_context` 等字段），查询时不应报错。

```bash
curl -s http://localhost:8000/api/checkins/me \
  -H "Authorization: Bearer $STUDENT_TOKEN" | python3 -m json.tool
```

**期望结果：**
- 旧记录中 `problem_context` 为 `null` 而非报错
- 旧记录中 `review_main_block` 等为 `null` 而非报错
- 前端不崩溃（HTTP 200）

---

### T10 — 数据库迁移自动执行 ✅ 必测

**测试目的：** 验证 `init_db()` 在已有旧库的情况下能自动补列，不报错

```bash
# 查看数据库表结构
python3 -c "
import sqlite3
conn = sqlite3.connect('noi_agent.db')
cursor = conn.cursor()

print('=== checkins 表 ===')
cursor.execute('PRAGMA table_info(checkins)')
for row in cursor.fetchall():
    print(row)

print()
print('=== reviews 表 ===')
cursor.execute('PRAGMA table_info(reviews)')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

**期望结果（checkins 表必须有）：**
- `problem_context`
- `submission_result`
- `student_code`

**期望结果（reviews 表必须有）：**
- `main_block`
- `key_bridge`
- `next_step`
- `transfer_signal`

---

## 四、前端功能测试（手动）

打开浏览器：`http://localhost:8000/app`，用 `student_a` / `password` 登录。

### F01 — 打卡表单字段检查

进入「打卡复盘」标签，确认：
- [ ] 有「题意补充」文本框，旁边有字数计数
- [ ] 有「提交现象」下拉框，选项为：未提交 / WA / TLE / RE / CE / 不确定
- [ ] 有「粘贴代码」文本框（可选，代码字体）
- [ ] 提交按钮在「题意补充」未达 10 字时保持灰色禁用

### F02 — 提交按钮逻辑

- [ ] 不填「题意补充」→ 按钮禁用
- [ ] 填写不足 10 字 → 按钮禁用，字数标红
- [ ] 达到 10 字 + 其他字段合法 → 按钮启用

### F03 — 提交成功后的复盘展示

提交一条完整打卡后，结果区域应显示：
- [ ] 「📌 你卡在哪：」（`main_block`）
- [ ] 「🔑 关键跳跃：」（`key_bridge`）
- [ ] 「⚡ 立刻去做：」（`next_step`）
- [ ] 「🎯 迁移信号：」（`transfer_signal`）
- [ ] 「查看详细诊断」折叠区域，点击可展开

### F04 — 提交成功后表单清空

提交成功后检查：
- [ ] 题目链接、标题、卡点描述已清空
- [ ] 题意补充已清空
- [ ] 提交现象已重置为「未提交」
- [ ] 代码框已清空
- [ ] 错误类型勾选已全部取消

### F05 — 历史记录渲染（学生端）

进入「历史记录」标签：
- [ ] 有复盘的记录显示纠偏 4 字段
- [ ] 有「查看详细诊断」折叠，展开后有推荐专题、AI 归类
- [ ] pending 状态的记录显示「待生成」，不报 JS 错误

### F06 — 历史记录渲染（教师端）

用 `teacher` 登录，进入「学员打卡」标签：
- [ ] 显示结构化诊断（AI 归类、判断把握、标签、诊断等）
- [ ] 不显示纠偏层（或在次要位置）

---

## 五、边界场景测试

### T11 — `student_code` 很长时截断

```bash
# 生成一段超长代码（>1500字符）
python3 -c "print('#include<bits/stdc++.h>\n' + 'int x = 1;\n' * 200)"

# 放入 student_code 字段提交，期望后端不报错，AI 只处理前 1500 字符
```

**期望结果：** HTTP 200，正常返回复盘

---

### T12 — 无 API Key 时打卡不崩溃

```bash
unset MOONSHOT_API_KEY
# 重启服务后提交打卡（需填写 problem_context）
```

**期望结果：**
- HTTP 200
- `review_status: "pending"`
- `message: "打卡成功，复盘稍后生成"`

---

### T13 — 健康检查

```bash
curl -s http://localhost:8000/ | python3 -m json.tool
```

**期望结果：**
```json
{
  "message": "NOI Coach Agent API is running",
  "hint_limit": 3,
  "version": "0.5.0"
}
```

---

## 六、自动化测试脚本（可选）

将以下内容保存为 `test_v2_1.py`，直接运行：

```python
#!/usr/bin/env python3
"""
NOI Agent v2.1 自动化测试
运行前确保服务已启动：uvicorn api_server:app --reload --port 8000
"""
import requests
import sys

BASE = "http://localhost:8000"
PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"

results = []

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"{status} {name}" + (f"  [{detail}]" if detail else ""))
    results.append(condition)

# ---- 登录 ----
r = requests.post(f"{BASE}/auth/login", json={"user_id": "student_a", "password": "password"})
check("T00 登录", r.status_code == 200)
student_token = r.json().get("token", "")
headers = {"Authorization": f"Bearer {student_token}"}

r2 = requests.post(f"{BASE}/auth/login", json={"user_id": "teacher", "password": "password"})
check("T00 教师登录", r2.status_code == 200)
teacher_token = r2.json().get("token", "")
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
r = requests.post(f"{BASE}/api/checkins", json=payload, headers=headers)
check("T01 正常打卡 HTTP 200", r.status_code == 200, r.text[:100])
if r.status_code == 200:
    data = r.json()
    check("T01 有 checkin_id", isinstance(data.get("checkin_id"), int))
    check("T01 review_status 存在", data.get("review_status") in ("completed", "pending"))
    review = data.get("review") or {}
    for field in ["main_block", "key_bridge", "next_step", "transfer_signal"]:
        check(f"T01 review.{field} 存在", field in review or data.get("review_status") == "pending",
              "(pending 时可为空)")

# ---- T02 缺 problem_context ----
payload2 = {
    "problem_url": "https://www.luogu.com.cn/problem/P1001",
    "problem_title": "A+B",
    "oj_source": "luogu",
    "completion_status": "independent",
    "bottleneck_text": "边界条件没考虑，负数输入导致数组越界，加了特判就过了",
    "error_types": ["边界条件"],
}
r = requests.post(f"{BASE}/api/checkins", json=payload2, headers=headers)
check("T02 缺 problem_context 返回 422", r.status_code == 422, f"got {r.status_code}")

# ---- T03 problem_context 太短 ----
payload3 = {**payload2, "problem_context": "加法"}
r = requests.post(f"{BASE}/api/checkins", json=payload3, headers=headers)
check("T03 problem_context<10 返回 422", r.status_code == 422, f"got {r.status_code}")

# ---- T04 submission_result 非法值 ----
payload4 = {**payload2, "problem_context": "两个整数相加求和", "submission_result": "accepted"}
r = requests.post(f"{BASE}/api/checkins", json=payload4, headers=headers)
check("T04 非法 submission_result 返回 422", r.status_code == 422, f"got {r.status_code}")

# ---- T05 submission_result=null ----
payload5 = {**payload2, "problem_context": "两个整数 A 和 B，输出 A+B 的结果", "submission_result": None}
r = requests.post(f"{BASE}/api/checkins", json=payload5, headers=headers)
check("T05 submission_result=null 返回 200", r.status_code == 200, f"got {r.status_code}")

# ---- T06 历史新字段 ----
r = requests.get(f"{BASE}/api/checkins/me", headers=headers)
check("T06 查询历史 HTTP 200", r.status_code == 200)
if r.status_code == 200:
    checkins = r.json().get("checkins", [])
    check("T06 历史非空", len(checkins) > 0)
    latest = checkins[0] if checkins else {}
    check("T06 历史有 problem_context 字段", "problem_context" in latest)
    check("T06 历史有 review_main_block 字段", "review_main_block" in latest)

# ---- T07 教师端 ----
r = requests.get(f"{BASE}/api/teacher/checkins?limit=5", headers=teacher_headers)
check("T07 教师查询 HTTP 200", r.status_code == 200)
if r.status_code == 200:
    checkins = r.json().get("checkins", [])
    if checkins:
        item = checkins[0]
        check("T07 教师端有 problem_context 字段", "problem_context" in item)
        check("T07 教师端有 review_main_block 字段", "review_main_block" in item)

# ---- T13 健康检查 ----
r = requests.get(f"{BASE}/")
check("T13 健康检查", r.status_code == 200 and "version" in r.json())

# ---- 数据库表结构 ----
import sqlite3, os
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

# ---- 汇总 ----
print()
passed = sum(results)
total = len(results)
print(f"{'=' * 40}")
print(f"结果：{passed}/{total} 通过")
if passed == total:
    print("\033[92m全部通过 🎉\033[0m")
else:
    print(f"\033[91m{total - passed} 项失败，请检查上方输出\033[0m")
    sys.exit(1)
```

运行：
```bash
python3 test_v2_1.py
```

---

## 七、v2.1 改动速查

| 文件 | 主要改动 |
|------|---------|
| `database.py` | 新增 `_migrate_checkins_table()`；`checkins` 表加 3 列；`reviews` 表加 4 列；`create_checkin/create_review/get_pending_review_jobs/get_student_checkins/get_all_checkins` 全部同步 |
| `api_server.py` | `CheckinRequest` 加 `problem_context`（必填）、`submission_result`（`Optional[Literal[...]]`）、`student_code`（可选）；`_generate_and_store_review` / 打卡端点 / `retry_pending_reviews` 全部透传 |
| `review_engine.py` | `generate_review` 加 3 个输入参数；Prompt 重写为动态拼接；输出合同加 `main_block/key_bridge/next_step/transfer_signal`；`_normalize_review` 加兜底文案 |
| `static/index.html` | 打卡表单新增「提交现象」下拉、「题意补充」textarea（必填）、「粘贴代码」textarea（可选） |
| `static/app.js` | 校验函数重构加 `problem_context` 检查；提交收集新字段；表单重置覆盖新字段；`renderReviewHtml` 学生端改为纠偏层主展 + 诊断层折叠；`renderCheckinCard` 学生/教师端分开渲染 |

---

## 八、已知不测项

- 代码超 1500 字符的截断仅在 `review_engine.py` Prompt 构建时处理，后端不做长度校验
- `student_code` 字段不做内容检测
- 旧 pending 记录若 `problem_context` 为 null，retry 时会用 `None` 传给 `generate_review()`，AI 会得到较少上下文但不会崩溃（已做 Optional 处理）
