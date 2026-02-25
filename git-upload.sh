#!/bin/bash
#
# 手动 Git 上传脚本
# 使用方法：./git-upload.sh [commit-message]
#

COMMIT_MESSAGE=${1:-"Update: $(date '+%Y-%m-%d %H:%M')"}

echo "📤 Git 上传脚本"
echo "=================="
echo ""
echo "1. 查看当前状态..."
git status

echo ""
echo "2. 添加所有修改..."
git add .

echo ""
echo "3. 提交更改..."
git commit -m "$COMMIT_MESSAGE"

echo ""
echo "4. 推送到远程..."
echo "⚠️  如果失败，请先配置远程仓库："
echo "   git remote add origin <你的远程仓库URL>"
echo ""
git push

echo ""
echo "✅ 完成！"
echo ""
echo "远程仓库："
git remote -v
