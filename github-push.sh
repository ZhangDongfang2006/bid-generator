#!/bin/bash
#
# GitHub 推送脚本（包含认证处理）
# 自动检测认证状态，如果需要则进行登录
#

set -e

echo "🚀 GitHub 推送脚本"
echo "====================================="
echo ""

# 步骤1：检查 Git 仓库
echo "📋 步骤 1：检查 Git 仓库..."
if [ ! -d ".git" ]; then
    echo "❌ 错误：不是 Git 仓库"
    echo "   请在项目根目录运行此脚本"
    exit 1
fi

echo "✅ Git 仓库存在"

# 步骤2：检查远程仓库
echo ""
echo "📋 步骤 2：检查远程仓库..."

if ! git remote get-url origin >/dev/null 2>&1; then
    echo "❌ 错误：没有配置远程仓库"
    echo "   配置命令："
    echo "   git remote add origin https://github.com/ZhangDongfang2006/bid-generator.git"
    echo ""
    echo "   配置后重新运行此脚本"
    exit 1
fi

REMOTE_URL=$(git remote get-url origin)
echo "✅ 远程仓库：$REMOTE_URL"

# 步骤3：检查 GitHub CLI
echo ""
echo "📋 步骤 3：检查 GitHub CLI..."

if ! command -v gh >/dev/null 2>&1; then
    echo "❌ GitHub CLI 未安装"
    echo "   安装命令："
    echo "   brew install gh"
    echo ""
    echo "   或者继续使用其他方法..."
    GH_AVAILABLE=false
else
    GH_AVAILABLE=true
    echo "✅ GitHub CLI 已安装"
fi

# 步骤4：检查认证状态
echo ""
echo "📋 步骤 4：检查认证状态..."

# 检查 GitHub CLI 登录状态
if [ "$GH_AVAILABLE" = true ]; then
    if gh auth status >/dev/null 2>&1; then
        echo "✅ GitHub CLI 已登录"
        GH_AUTHENTICATED=true
    else
        echo "⚠️  GitHub CLI 未登录"
        echo "   将尝试使用浏览器登录..."
        GH_AUTHENTICATED=false
    fi
else
    echo "⚠️  GitHub CLI 不可用"
    GH_AUTHENTICATED=false
fi

# 步骤5：添加并提交修改
echo ""
echo "📋 步骤 5：添加并提交修改..."

git add .

# 检查是否有更改
if git diff --cached --quiet; then
    echo "📝 有更改，创建提交..."
    COMMIT_MESSAGE="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MESSAGE"
    echo "✅ 提交成功"
else
    echo "📝 没有更改，跳过提交"
fi

# 步骤6：推送代码
echo ""
echo "📋 步骤 6：推送代码..."

if [ "$GH_AUTHENTICATED" = true ]; then
    echo "🚀 使用 GitHub CLI 推送..."
    git push -u origin main

    if [ $? -eq 0 ]; then
        echo ""
        echo "====================================="
        echo "🎉 成功！代码已推送到 GitHub"
        echo "====================================="
        echo ""
        echo "📍 仓库地址："
        echo "   https://github.com/ZhangDongfang2006/bid-generator"
        echo ""
        echo "📊 查看代码："
        echo "   git log --oneline -5"
    else
        echo ""
        echo "❌ 推送失败"
        echo "   请检查网络连接或仓库权限"
    fi
else
    # 如果 GitHub CLI 不可用或未登录，使用常规 git push
    echo "🚀 使用 Git 推送..."
    echo "   注意：如果推送失败，可能需要配置 Personal Access Token"
    echo ""
    echo "   配置方法："
    echo "   1. 访问 https://github.com/settings/tokens"
    echo "   2. 点击 'Generate new token' (classic)"
    echo "   3. Token 描述：bid-generator"
    echo "   4. 选择权限：repo (Full control of private repositories)"
    echo "   5. 点击 'Generate token'"
    echo "   6. 复制生成的 token (只显示一次)"
    echo "   7. 运行：git push -u origin main"
    echo "   8. 当提示时输入用户名和 token"

    git push -u origin main

    if [ $? -eq 0 ]; then
        echo ""
        echo "====================================="
        echo "🎉 成功！代码已推送到 GitHub"
        echo "====================================="
        echo ""
        echo "📍 仓库地址："
        echo "   https://github.com/ZhangDongfang2006/bid-generator"
    else
        echo ""
        echo "❌ 推送失败"
        echo ""
        echo "如果仍然失败，请尝试以下方案："
        echo ""
        echo "方案 1：配置 GitHub CLI"
        echo "   执行："
        echo "   gh auth login --web"
        echo "   然后重新运行此脚本"
        echo ""
        echo "方案 2：使用 SSH 密钥"
        echo "   1. 生成 SSH 密钥："
        echo "      ssh-keygen -t ed25519 -C 'your_email@example.com'"
        echo "   2. 复制公钥："
        echo "      cat ~/.ssh/id_ed25519.pub"
        echo "   3. 添加到 GitHub："
        echo "      访问 https://github.com/settings/ssh/new"
        echo "   4. 修改远程仓库为 SSH："
        echo "      git remote set-url origin git@github.com:ZhangDongfang2006/bid-generator.git"
        echo "   5. 重新运行此脚本"
        echo ""
        echo "方案 3：使用 Personal Access Token"
        echo "   参考上面的配置方法"
    fi
fi

echo ""
echo "====================================="
echo "✓ 脚本执行完成"
echo "====================================="
