#!/bin/bash
# Econe Papers Daily Update + Deploy

cd ~/.openclaw/workspace/econe-papers/backend
source .venv/bin/activate

# Run the update script
python3 daily_update.py

# If there are changes, commit and push
cd ~/.openclaw/workspace/econe-papers
git add -A
git diff --staged --quiet || git commit -m "daily update $(date '+%Y-%m-%d')"
git push origin main
