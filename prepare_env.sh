#!/bin/bash
"""
环境准备脚本 - 检查并安装所需依赖
"""

echo "============================================================"
echo "投标文件生成系统 - 环境准备"
echo "============================================================"
echo ""

# 检查 Python 版本
echo "📋 1. 检查 Python 版本..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Python 版本: $PYTHON_VERSION"
    
    # 检查 Python 版本是否 >= 3.8
    PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        echo "   ✅ Python 版本满足要求 (>= 3.8)"
    else
        echo "   ❌ Python 版本不满足要求 (需要 >= 3.8)"
        echo "   ⚠️  建议升级 Python 版本"
    fi
else
    echo "   ❌ 未找到 Python3"
    echo "   ⚠️  请先安装 Python 3.8 或更高版本"
fi

# 检查 pip
echo "📋 2. 检查 pip..."
if command -v pip3 &>/dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo "   ✅ pip 版本: $PIP_VERSION"
else
    echo "   ❌ 未找到 pip3"
    echo "   ⚠️  请先安装 pip3"
fi

# 检查依赖
echo "📋 3. 检查依赖包..."

# 定义需要检查的依赖
DEPENDENCIES=(
    "streamlit"
    "python-docx"
    "pandas"
    "openpyxl"
    "pillow"
    "reportlab"
    "PyPDF2"
)

# 检查每个依赖
MISSING_DEPS=()
INSTALLED_DEPS=()

for dep in "${DEPENDENCIES[@]}"; do
    if python3 -c "import pkg_resources; pkg_resources.get_distribution('$dep')" 2>/dev/null; then
        VERSION=$(python3 -c "import pkg_resources; print(pkg_resources.get_distribution('$dep').version)")
        echo "   ✅ $dep: $VERSION"
        INSTALLED_DEPS+=("$dep")
    else
        echo "   ❌ $dep: 未安装"
        MISSING_DEPS+=("$dep")
    fi
done

echo ""
echo "============================================================"
echo "依赖检查结果"
echo "============================================================"
echo ""

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo "✅ 所有依赖已安装"
    echo ""
    echo "已安装的依赖 ($(( ${#INSTALLED_DEPS[@]} ))):"
    for dep in "${INSTALLED_DEPS[@]}"; do
        echo " • $dep"
    done
else
    echo "⚠️  缺少 $(( ${#MISSING_DEPS[@]} )) 个依赖"
    echo ""
    echo "缺失的依赖:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo " • $dep"
    done
    echo ""
    echo "📝 是否安装缺失的依赖？"
    read -p "请输入 'y' 或 'n' (默认: y): " install_deps
    install_deps=${install_deps:-y}
fi

echo ""
echo "============================================================"
echo "下一步"
echo "============================================================"
echo ""

if [ "$install_deps" = "y" ] && [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "🚀 开始安装缺失的依赖..."
    echo ""
    
    for dep in "${MISSING_DEPS[@]}"; do
        echo "📦 正在安装 $dep..."
        pip3 install "$dep"
        if [ $? -eq 0 ]; then
            echo "   ✅ $dep 安装成功"
        else
            echo "   ❌ $dep 安装失败"
        fi
    done
    
    echo ""
    echo "✅ 依赖安装完成"
    echo ""
    echo "🚀 下一步：启动应用"
    echo "   命令: streamlit run app.py"
else
    echo "✅ 环境准备完成"
    echo ""
    echo "🚀 下一步：启动应用"
    echo "   命令: streamlit run app.py"
fi

echo ""
echo "============================================================"
echo "环境准备完成"
echo "============================================================"
