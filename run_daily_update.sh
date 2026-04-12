#!/bin/bash
# Econe Papers Daily Update v2.0 + Git Push (triggers Vercel deploy)
# 改进：过滤金融 + 中文摘要 + 多维度评分

# Set PATH for cron
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Load environment variables
source ~/.zshrc

# 百度千帆 API Key (硬编码确保可用)
export BAIDU_API_KEY="bce-v3/ALTAK-SOMoPE9hXPweaALotFw7A/383d6694a7f34c24a357828ec7f619d528b4afa4"

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
