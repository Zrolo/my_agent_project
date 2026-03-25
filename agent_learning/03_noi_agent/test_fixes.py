"""
回归测试：验证三个修复点

运行方式:
    cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
    python3 test_fixes.py

注意: 需要服务器在运行（uvicorn api_server:app --reload）
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

# 测试账号
STUDENT_ID = "student_a"
TEACHER_ID = "teacher"
PASSWORD = "password"


def login(user_id: str, password: str) -> str:
    """登录获取 token"""
    res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"user_id": user_id, "password": password}
    )
    assert res.status_code == 200, f"登录失败: {res.text}"
    return res.json()["token"]


def get_checkin_count(teacher_token: str) -> int:
    """获取当前总打卡数"""
    res = requests.get(
        f"{BASE_URL}/api/teacher/checkins?limit=1000",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert res.status_code == 200
    return len(res.json()["checkins"])


def get_usage_stats(teacher_token: str) -> dict:
    """获取使用统计"""
    res = requests.get(
        f"{BASE_URL}/api/teacher/usage",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert res.status_code == 200
    return res.json()["usage"]


def test_validation_rejection():
    """
    测试1: 业务拒绝路径
    
    输入：够长但空泛的卡点描述
    预期：
        - 接口返回校验失败 (422)
        - checkins 不新增
        - reviews 不新增
        - rejected_count +1
        - checkin_count 不增加
    """
    print("\n" + "="*60)
    print("测试1: 业务拒绝路径（卡点空泛）")
    print("="*60)
    
    student_token = login(STUDENT_ID, PASSWORD)
    teacher_token = login(TEACHER_ID, PASSWORD)
    
    # 记录测试前的状态
    checkins_before = get_checkin_count(teacher_token)
    usage_before = get_usage_stats(teacher_token)
    rejected_before = usage_before[0]["rejected"] if usage_before else 0
    
    print(f"测试前打卡总数: {checkins_before}")
    print(f"测试前今日被拒绝数: {rejected_before}")
    
    # 提交空泛的卡点（18字，含"不会"）
    res = requests.post(
        f"{BASE_URL}/api/checkins",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "problem_url": "https://www.luogu.com.cn/problem/P9999",
            "problem_title": "测试题目-拒绝路径",
            "oj_source": "luogu",
            "completion_status": "unfinished",
            "bottleneck_text": "我完全不会做这道题目真的很困扰",  # 18字，含无效词
            "error_types": ["不知道用什么算法"]
        }
    )
    
    # 验证：应该返回 422
    assert res.status_code == 422, f"期望422，实际{res.status_code}: {res.text}"
    print(f"✓ 接口返回 422 Unprocessable Entity")
    
    # 验证错误信息
    error_detail = res.json().get("detail", "")
    assert "笼统" in error_detail or "示例" in error_detail, f"错误提示不符合预期: {error_detail}"
    print(f"✓ 错误提示包含引导信息: {error_detail[:50]}...")
    
    # 验证：checkins 不新增
    checkins_after = get_checkin_count(teacher_token)
    assert checkins_after == checkins_before, f"打卡数不应该增加: {checkins_before} -> {checkins_after}"
    print(f"✓ checkins 未新增 ({checkins_before} == {checkins_after})")
    
    # 验证：rejected_count +1
    usage_after = get_usage_stats(teacher_token)
    rejected_after = usage_after[0]["rejected"] if usage_after else 0
    assert rejected_after == rejected_before + 1, f"被拒绝数应该+1: {rejected_before} -> {rejected_after}"
    print(f"✓ rejected_count +1 ({rejected_before} -> {rejected_after})")
    
    print("\n测试1通过 ✓")


def test_llm_failure_path():
    """
    测试2: LLM失败路径
    
    模拟未设置 MOONSHOT_API_KEY 或 LLM 调用失败
    预期：
        - 有效打卡仍保存
        - reviews 不新增
        - 返回 review: null
        - 历史记录里 has_review=false
    """
    print("\n" + "="*60)
    print("测试2: LLM失败路径（无API Key）")
    print("="*60)
    
    student_token = login(STUDENT_ID, PASSWORD)
    teacher_token = login(TEACHER_ID, PASSWORD)
    
    # 记录测试前的状态
    checkins_before = get_checkin_count(teacher_token)
    print(f"测试前打卡总数: {checkins_before}")
    
    # 提交合格的卡点
    res = requests.post(
        f"{BASE_URL}/api/checkins",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "problem_url": "https://www.luogu.com.cn/problem/P8888",
            "problem_title": "测试题目-LLM失败",
            "oj_source": "luogu",
            "completion_status": "hinted",
            "bottleneck_text": "这道题的区间DP转移方程不太确定，尝试了几种写法都超时，后来发现是枚举顺序问题",
            "error_types": ["状态转移"]
        }
    )
    
    # 验证：接口应该成功（打卡保存）
    assert res.status_code == 200, f"期望200，实际{res.status_code}: {res.text}"
    result = res.json()
    print(f"✓ 接口返回 200")
    
    # 验证：返回 review: null
    assert result.get("review") is None, f"review 应该为 null: {result.get('review')}"
    print(f"✓ 返回 review: null")
    
    # 验证：message 提示 AI 不可用
    message = result.get("message", "")
    assert "AI" in message or "复盘" in message or "不可用" in message, f"提示信息不符合预期: {message}"
    print(f"✓ 提示信息: {message}")
    
    # 验证：checkins 新增
    checkins_after = get_checkin_count(teacher_token)
    assert checkins_after == checkins_before + 1, f"打卡数应该+1: {checkins_before} -> {checkins_after}"
    print(f"✓ checkins +1 ({checkins_before} -> {checkins_after})")
    
    # 验证：最新打卡的 has_review=false
    checkins_res = requests.get(
        f"{BASE_URL}/api/checkins/me?limit=1",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    latest = checkins_res.json()["checkins"][0]
    assert latest.get("has_review") == False, f"has_review 应该为 false: {latest}"
    print(f"✓ 历史记录 has_review=false")
    
    print("\n测试2通过 ✓")


def test_successful_checkin():
    """
    测试3: 正常成功路径（验证整体流程）
    """
    print("\n" + "="*60)
    print("测试3: 正常成功路径")
    print("="*60)
    
    student_token = login(STUDENT_ID, PASSWORD)
    teacher_token = login(TEACHER_ID, PASSWORD)
    
    checkins_before = get_checkin_count(teacher_token)
    
    # 提交合格的卡点（与测试2类似，但验证流程）
    res = requests.post(
        f"{BASE_URL}/api/checkins",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "problem_url": "https://www.luogu.com.cn/problem/P7777",
            "problem_title": "测试题目-正常路径",
            "oj_source": "luogu",
            "completion_status": "independent",
            "bottleneck_text": "这道题的线段树区间修改操作一开始理解有误，看了题解才明白懒标记的正确使用方式",
            "error_types": ["知道算法但不知道怎么用"]
        }
    )
    
    assert res.status_code == 200, f"期望200，实际{res.status_code}: {res.text}"
    result = res.json()
    
    # 打卡应该成功保存
    checkins_after = get_checkin_count(teacher_token)
    assert checkins_after == checkins_before + 1
    print(f"✓ 打卡成功保存")
    
    # 无论 LLM 是否成功，都有 checkin_id
    assert "checkin_id" in result
    print(f"✓ 返回 checkin_id: {result['checkin_id']}")
    
    print("\n测试3通过 ✓")


def test_validate_bottleneck_function():
    """
    测试4: 直接测试 validate_bottleneck 函数
    """
    print("\n" + "="*60)
    print("测试4: 校验函数单元测试")
    print("="*60)
    
    from review_engine import validate_bottleneck
    
    # 测试太短
    is_valid, msg = validate_bottleneck("不会")
    assert not is_valid and "15字" in msg
    print("✓ '不会' -> 拒绝 (太短)")
    
    # 测试空泛（够长但含无效词，<30字）
    is_valid, msg = validate_bottleneck("我完全不会做这道题目真的很困扰")
    assert not is_valid and "笼统" in msg
    print("✓ '我完全不会做这道题目真的很困扰' (18字) -> 拒绝 (空泛)")
    
    # 测试通过（具体描述）
    is_valid, msg = validate_bottleneck("这道题的区间DP转移方程不太确定，尝试了几种写法")
    assert is_valid
    print("✓ 具体描述 -> 通过")
    
    print("\n测试4通过 ✓")


def main():
    print("开始运行回归测试...")
    print(f"服务器地址: {BASE_URL}")
    
    try:
        # 先测试单元级别的校验函数
        test_validate_bottleneck_function()
        
        # 再测试API接口
        test_validation_rejection()
        test_llm_failure_path()
        test_successful_checkin()
        
        print("\n" + "="*60)
        print("所有测试通过！✓")
        print("="*60)
        return 0
        
    except AssertionError as e:
        print(f"\n测试失败: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print(f"\n连接失败: 请确保服务器已启动 (uvicorn api_server:app --reload)")
        return 1
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
