#!/bin/bash
# Econe Papers Daily Update + Git Push (triggers Vercel deploy)

cd ~/.openclaw/workspace/econe-papers/backend

# Activate venv and run update
source .venv/bin/activate
python3 daily_update.py

# Go to repo root and push if there are changes
cd ~/.openclaw/workspace/econe-papers
git add -A
if ! git diff --staged --quiet; then
    git commit -m "daily update $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "Pushed to GitHub - Vercel will deploy"
else
    echo "No new papers to push"
fi
