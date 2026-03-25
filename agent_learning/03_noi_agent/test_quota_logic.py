"""
配额扣减逻辑回归测试
验证 parse_level_tag 和扣费逻辑的正确性
"""

import re


def parse_level_tag(reply: str) -> tuple[str, str]:
    """从回复末尾提取 [LEVEL:Lx] 标签"""
    pattern = r'\[LEVEL:(L1|L2|L3|L4)\]\s*$'
    match = re.search(pattern, reply, re.IGNORECASE)
    
    if match:
        level = match.group(1).upper()
        clean_reply = re.sub(pattern, '', reply, flags=re.IGNORECASE).rstrip()
        return level, clean_reply
    
    return "", reply.strip()


def should_consume(level: str) -> bool:
    """基于 level 决定是否扣费"""
    return level in ("L2", "L3")


def test_case(name: str, reply: str, expected_level: str, expected_consume: bool):
    """运行单个测试用例"""
    level, clean = parse_level_tag(reply)
    consume = should_consume(level)
    
    status = "✅ PASS" if (level == expected_level and consume == expected_consume) else "❌ FAIL"
    print(f"{status} {name}")
    print(f"   输入: {reply[:60]}...")
    print(f"   解析level: '{level}' (期望: '{expected_level}')")
    print(f"   扣费: {consume} (期望: {expected_consume})")
    print()
    
    return status == "✅ PASS"


def main():
    print("=" * 70)
    print("配额扣减逻辑回归测试")
    print("=" * 70)
    print()
    
    tests = [
        # 场景1: 正文提前出现L2，但末尾是L1 -> 不扣费
        ("正文L2末尾L1", 
         "试试这个思路 [LEVEL:L2]\n但你再想想 [LEVEL:L1]", 
         "L1", False),
        
        # 场景2: 正文提前出现L2，但末尾是L3 -> 扣费
        ("正文L2末尾L3", 
         "先这样想 [LEVEL:L2]\n然后这样改 [LEVEL:L3]", 
         "L3", True),
        
        # 场景3: 末尾小写l2 -> 扣费（统一转大写）
        ("小写level:l2", 
         "试试递归 [level:l2]", 
         "L2", True),
        
        # 场景4: 末尾小写level:l3 -> 扣费
        ("小写level:l3", 
         "看这段代码 [level:l3]", 
         "L3", True),
        
        # 场景5: 末尾小写level:l1 -> 不扣费
        ("小写level:l1", 
         "请先思考 [level:l1]", 
         "L1", False),
        
        # 场景6: 缺标签 -> 不扣费
        ("缺标签", 
         "试试递归，但不要直接抄", 
         "", False),
        
        # 场景7: 正文有L2但完全没标签 -> 不扣费（不能误扣）
        ("正文有L2字样但无标签", 
         "我觉得是L2级别的难度，需要递归", 
         "", False),
        
        # 场景8: 末尾L4 -> 不扣费
        ("末尾L4", 
         "这道题建议找老师 [LEVEL:L4]", 
         "L4", False),
        
        # 场景9: 只有L2标签 -> 扣费
        ("纯L2标签", 
         "试试二分查找 [LEVEL:L2]", 
         "L2", True),
        
        # 场景10: 标签前后有空格 -> 能识别
        ("标签后有空格", 
         "试试递归 [LEVEL:L2]   ", 
         "L2", True),
    ]
    
    passed = 0
    failed = 0
    
    for name, reply, expected_level, expected_consume in tests:
        if test_case(name, reply, expected_level, expected_consume):
            passed += 1
        else:
            failed += 1
    
    print("=" * 70)
    print(f"结果: {passed} 通过, {failed} 失败")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
