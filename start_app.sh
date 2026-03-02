#!/bin/bash
"""
启动脚本 - 启动 Streamlit 应用
"""

echo "============================================================"
echo "投标文件生成系统 - 启动应用"
echo "============================================================"
echo ""

# 检查 app.py 是否存在
if [ ! -f "app.py" ]; then
    echo "❌ 错误：未找到 app.py 文件"
    echo "   请确保在 bid-generator 目录中运行此脚本"
    echo ""
    exit 1
fi

echo "✅ 找到 app.py 文件"
echo ""

# 检查 Streamlit 是否安装
if ! command -v streamlit &>/dev/null; then
    echo "❌ 错误：未安装 Streamlit"
    echo "   请运行: pip install streamlit"
    echo ""
    exit 1
fi

echo "✅ Streamlit 已安装"
echo ""

echo "🚀 正在启动投标文件生成系统..."
echo ""

# 启动 Streamlit 应用
# --server.port 8501  # 监听 8501 端口
# --server.address 0.0.0.0   # 监听所有网络接口

streamlit run app.py --server.port 8501 --server.address 0.0.0.0

echo ""
echo "============================================================"
echo "🌐 应用已启动"
echo "============================================================"
echo ""
echo "📱 请在浏览器中访问以下地址："
echo "   http://localhost:8501"
echo ""
echo "📝 应用说明："
echo "   1. 上传招标文件（PDF 格式）"
echo "   2. 系统会自动解析并填充表单"
echo "   3. 检查并确认项目信息"
echo "   4. 点击\"生成投标文件\"按钮"
echo "   5. 下载生成的文件"
echo "   6. 可以使用\"清理旧文件\"按钮清理文件"
echo ""
echo "⚠️  停止应用："
echo "   - 在终端中按 Ctrl + C"
echo "   - 或者关闭终端窗口"
echo ""
echo "============================================================"
