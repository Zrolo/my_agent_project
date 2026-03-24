#!/bin/bash
# 尝试从各种来源加载 MOONSHOT_API_KEY

# 尝试从 VS Code 设置读取（如果是通过 VS Code 配置的）
if [ -z "$MOONSHOT_API_KEY" ]; then
    # 检查常见的 key 配置位置
    if [ -f "$HOME/.moonshot_key" ]; then
        export MOONSHOT_API_KEY=$(cat "$HOME/.moonshot_key")
    fi
fi

# 如果还是为空，提示用户输入
if [ -z "$MOONSHOT_API_KEY" ]; then
    echo "请输入你的 MOONSHOT_API_KEY:"
    read -s MOONSHOT_API_KEY
    export MOONSHOT_API_KEY
fi

# 运行测试
python3 test_quota.py
