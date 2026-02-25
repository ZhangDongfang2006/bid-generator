#!/bin/bash

echo "==================================="
echo "投标文件自动生成系统 - 快速启动"
echo "==================================="

# 检查 Python 版本
echo ""
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
echo "==================================="
echo "系统启动成功！"
echo "浏览器将自动打开系统界面"
echo "如未打开，请访问：http://localhost:8501"
echo "==================================="
echo ""
echo "按 Ctrl+C 停止系统"
echo ""

streamlit run app.py
