#!/usr/bin/env python3
"""修复论文数据 - 删除今天的数据重新分析"""
import json

with open('papers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 删除今天的数据
data['days'] = [d for d in data['days'] if d['date'] != '2026-04-12']

with open('papers.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已删除 2026-04-12 的数据")
