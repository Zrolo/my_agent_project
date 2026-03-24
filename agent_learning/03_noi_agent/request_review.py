#!/usr/bin/env python3
"""
一键生成 Claude 审查请求
用法: python3 request_review.py [改动描述]
"""

import sys
import os
import subprocess
from datetime import datetime

def get_git_diff():
    """获取最近的代码改动"""
    try:
        # 尝试获取 git diff
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            capture_output=True,
            text=True,
            cwd="/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent"
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except:
        pass
    
    # 如果没有 git，检查文件修改时间
    files = ["noi_agent.py", "test_quota.py", "multi_agent_review.py"]
    modified = []
    for f in files:
        if os.path.exists(f):
            mtime = os.path.getmtime(f)
            modified.append(f"{f} (modified {datetime.fromtimestamp(mtime).strftime('%H:%M')})")
    return "\n".join(modified) if modified else "无法检测改动"

def get_file_stats():
    """获取代码行数统计"""
    try:
        with open("noi_agent.py", "r") as f:
            lines = f.readlines()
            total = len(lines)
            code = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
            comments = len([l for l in lines if l.strip().startswith("#")])
            return f"总行数: {total}, 代码: {code}, 注释: {comments}"
    except:
        return "无法统计"

def generate_review_request(description=""):
    """生成审查请求文本"""
    
    diff = get_git_diff()
    stats = get_file_stats()
    
    template = f"""
{'='*60}
🤖 CLAUDE 代码审查请求
{'='*60}

📁 项目: NOI 竞赛教练 Agent
🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 代码统计:
{stats}

📝 改动文件:
{diff}

🎯 改动描述:
{description if description else "（请补充改动目的）"}

{'='*60}
🔍 请按 review_checklist.md 进行审查
{'='*60}

重点关注:
1. 🔴 P0: 语法错误、逻辑错误、安全漏洞
2. 🟡 P1: 配额逻辑是否正确、能否被绕过
3. 🟢 P2: 代码可读性、可维护性

请输出格式:
- 总体评级（🟢通过 / 🟡有条件通过 / 🔴不通过）
- 问题清单（按 P0/P1/P2 分级）
- 修复建议
- 下一步行动

{'='*60}
"""
    return template

if __name__ == "__main__":
    # 获取命令行参数作为改动描述
    description = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    
    review_request = generate_review_request(description)
    
    # 保存到文件
    output_file = "review_request.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(review_request)
    
    # 同时输出到控制台
    print(review_request)
    print(f"\n✅ 审查请求已保存到: {output_file}")
    print(f"\n下一步:")
    print(f"1. 把 {output_file} 的内容复制给 Claude")
    print(f"2. 或运行: cat {output_file} | pbcopy (Mac) 复制到剪贴板")
