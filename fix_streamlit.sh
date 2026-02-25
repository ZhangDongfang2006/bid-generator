#!/bin/bash

# Streamlit 修复脚本
# 解决 "zsh: command not found: streamlit" 错误

echo "============================================================"
echo "Streamlit 修复脚本"
echo "============================================================"
echo()

echo "问题：zsh: command not found: streamlit"
echo()

echo "可能的原因："
echo "1. Streamlit 没有安装在虚拟环境中"
echo "2. 虚拟环境没有激活"
echo "3. Streamlit 不在 PATH 中"
echo()

echo "============================================================"
echo "解决方案"
echo "============================================================"
echo()

cd /Users/zhangdongfang/workspace/bid-generator

# 检查虚拟环境是否存在
if [ -d "venv" ]; then
    echo "✓ 找到虚拟环境"
else
    echo "✗ 虚拟环境不存在"
    echo ""
    echo "正在创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo ""
echo "============================================================"
echo "激活虚拟环境"
echo "============================================================"
echo()
echo "运行命令："
echo "  source /Users/zhangdongfang/workspace/bid-generator/venv/bin/activate"
echo()

# 检查 Streamlit 是否已安装
echo ""
echo "============================================================"
echo "检查 Streamlit"
echo "============================================================"
echo()

# 使用虚拟环境中的 Python 检查
venv/bin/python3 -c "
import sys
try:
    import streamlit
    print(f'✓ Streamlit 已安装')
    print(f'  版本：{streamlit.__version__}')
    print(f'  路径：{streamlit.__file__}')
except ImportError:
    print(f'✗ Streamlit 未安装')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "运行 Streamlit"
    echo "============================================================"
    echo()
    echo "方法1：使用虚拟环境中的 streamlit"
    echo "  运行命令："
    echo "    cd /Users/zhangdongfang/workspace/bid-generator"
    echo "    source venv/bin/activate"
    echo "    streamlit run app.py"
    echo()
    echo "方法2：使用虚拟环境中的 Python 运行"
    echo "  运行命令："
    echo "    cd /Users/zhangdongfang/workspace/bid-generator"
    echo "    source venv/bin/activate"
    echo "    python -m streamlit run app.py"
    echo()
    echo "方法3：直接使用虚拟环境中的 streamlit"
    echo "  运行命令："
    echo "    cd /Users/zhangdongfang/workspace/bid-generator"
    echo "    ./venv/bin/streamlit run app.py"
    echo()
else
    echo ""
    echo "============================================================"
    echo "安装 Streamlit"
    echo "============================================================"
    echo()
    echo "正在安装 Streamlit..."
    echo()
    venv/bin/pip install streamlit
    echo()
    echo "安装完成！"
    echo ""
    echo "现在可以运行："
    echo "  cd /Users/zhangdongfang/workspace/bid-generator"
    echo "  source venv/bin/activate"
    echo "  streamlit run app.py"
    echo()
fi

echo "============================================================"
echo "快速启动命令"
echo "============================================================"
echo()
echo "将以下命令复制并粘贴到终端："
echo()
echo "cd /Users/zhangdongfang/workspace/bid-generator && source venv/bin/activate && streamlit run app.py"
echo()
