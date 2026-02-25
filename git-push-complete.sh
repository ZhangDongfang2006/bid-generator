#!/bin/bash
#
# 完整的 Git 推送流程
# 包含：身份验证、推送、常见错误处理
#

echo "🚀 Git 推送流程"
echo "====================================="
echo ""
echo "步骤 1：检查 Git 仓库"
echo ""

if [ ! -d ".git" ]; then
    echo "❌ 错误：不是 Git 仓库"
    echo "   请在项目根目录运行此脚本"
    exit 1
fi

echo "✅ Git 仓库存在"

echo ""
echo "步骤 2：检查远程仓库"
echo ""

git remote -v

if [ $? -ne 0 ]; then
    echo "❌ 错误：没有配置远程仓库"
    echo ""
    echo "请配置远程仓库："
    echo "   git remote add origin https://github.com/ZhangDongfang2006/bid-generator.git"
    exit 1
fi

echo ""
echo "步骤 3：检查 Git 身份验证"
echo ""

# 检查多种认证方式

# 方式1：GitHub CLI
if command -v gh >/dev/null 2>&1; then
    echo "✓ GitHub CLI 已安装"
    gh auth status 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ GitHub CLI 已登录"
    else
        echo "⚠️  GitHub CLI 未登录"
        echo "   请运行：gh auth login"
    fi
fi

# 方式2：SSH 密钥
if [ -f ~/.ssh/id_rsa.pub ]; then
    echo "✓ SSH 公钥已配置"
    echo "   密钥：$(ssh-keygen -l -f ~/.ssh/id_rsa.pub)"
fi

echo ""
echo "步骤 4：推送代码"
echo ""

# 尝试推送
echo "正在推送到 origin/main..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 成功！代码已推送到 GitHub"
    echo ""
    echo "📍 仓库地址：https://github.com/ZhangDongfang2006/bid-generator"
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "请检查："
    echo "   1. 网络连接"
    echo "   2. GitHub 身份验证"
    echo "   3. 远程仓库权限"
fi

echo ""
echo "====================================="
echo "✓ 完成"
