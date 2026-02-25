#!/bin/bash

echo "=============================================="
echo "投标文件自动生成系统 - 局域网启动（多人共用）"
echo "=============================================="

# 获取本机IP地址
IP_ADDRESS=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

if [ -z "$IP_ADDRESS" ]; then
    echo "⚠️  无法获取IP地址，请手动检查网络设置"
    IP_ADDRESS="你的IP地址"
fi

echo ""
echo "本机IP地址: $IP_ADDRESS"
echo ""

# 检查 Python 版本
echo "检查 Python 环境..."
python3 --version

# 进入项目目录
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)
echo "项目目录: $PROJECT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "安装依赖包..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 初始化数据库
echo ""
echo "初始化数据库..."
python3 database.py

# 启动应用
echo ""
echo "=============================================="
echo "系统启动成功！"
echo ""
echo "本地访问：http://localhost:8501"
echo "局域网访问：http://$IP_ADDRESS:8501"
echo ""
echo "💡 提示："
echo "   1. 确保防火墙允许 8501 端口"
echo "   2. 确保其他设备在同一局域网"
echo "   3. 分享上述网址给其他同事"
echo "=============================================="
echo ""
echo "按 Ctrl+C 停止系统"
echo ""

streamlit run app.py --server.address=0.0.0.0
