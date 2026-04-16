#!/bin/bash
# Econe Papers Daily Update v2.0 + Git Push (triggers Vercel deploy)
# 改进：过滤金融 + 中文摘要 + 多维度评分

# Set PATH for cron
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# 避免 ArXiv 429 限流：随机延迟 15-25 分钟
# 9:00 cron 执行，实际在 9:15-9:25 开始，避开高峰期
sleep $((900 + RANDOM % 600))

# Load environment variables (包含 BAIDU_API_KEY)
# 注意：cron 中使用 bash，zshrc 可能加载失败，直接设置关键变量
export BAIDU_API_KEY="${BAIDU_API_KEY:-$(grep BAIDU_API_KEY ~/.zshrc 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d \"\')}"

cd ~/.openclaw/workspace/econe-papers/backend

# Activate venv and run update (使用 v2 版本)
source .venv/bin/activate
python3 daily_update_v2.py

# Go to repo root and push if there are changes
cd ~/.openclaw/workspace/econe-papers
git add -A
if ! git diff --staged --quiet; then
    git commit -m "daily update v2 $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "Pushed to GitHub - Vercel will deploy"
else
    echo "No new papers to push"
fi
