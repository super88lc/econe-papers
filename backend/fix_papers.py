#!/usr/bin/env python3
"""修复论文数据 - 删除今天的数据重新分析"""
import json
import os

# 修复 web/src/lib/data.json 中的数据
with open('papers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 删除今天的数据
data['days'] = [d for d in data['days'] if d['date'] != '2026-04-12']

with open('papers.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 同时更新 web/src/lib/data.json
web_data_path = '../web/src/lib/data.json'
if os.path.exists(web_data_path):
    with open(web_data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("已同步更新 web/src/lib/data.json")

print("已删除 2026-04-12 的数据")
