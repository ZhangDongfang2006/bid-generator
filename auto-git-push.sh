#!/bin/bash
#
# Git 自动提交和推送脚本
# 使用方法：将此脚本添加到 .git/hooks/pre-commit
# 每次提交前自动执行推送
#

# 配置
REMOTE_NAME="origin"
REMOTE_URL=""
BRANCH_NAME="main"
COMMIT_MESSAGE="Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"

# 自动提交并推送
echo "🔄 自动提交中..."

# 添加所有修改
git add .

# 提交
git commit -m "$COMMIT_MESSAGE"

# 推送
echo "📤 推送到 $REMOTE_NAME/$BRANCH_NAME..."
git push $REMOTE_NAME $BRANCH_NAME

echo "✅ 完成！"
