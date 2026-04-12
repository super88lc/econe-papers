#!/bin/bash
# 重新生成今天的论文（使用 AI 翻译）
cd /Users/apple/.openclaw/workspace/econe-papers/backend

# 删除今天的数据（强制重新分析）
python3 fix_papers.py --delete-today 2>/dev/null || true

# 运行更新
source ~/.zshrc
source .venv/bin/activate
python3 daily_update_v2.py 2>&1
