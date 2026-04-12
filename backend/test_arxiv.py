#!/usr/bin/env python3
"""测试 ArXiv API"""
import requests
from bs4 import BeautifulSoup

url = "https://export.arxiv.org/api/query"
params = {
    "search_query": "cat:econ.GN",
    "start": 0,
    "max_results": 3,
    "sortBy": "submittedDate",
    "sortOrder": "descending"
}

try:
    print(f"请求: {url}?{requests.compat.urlencode(params)}")
    response = requests.get(url, params=params, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"内容长度: {len(response.text)}")
    
    soup = BeautifulSoup(response.content, 'xml')
    entries = soup.find_all('entry')
    print(f"找到论文数: {len(entries)}")
    
    for i, entry in enumerate(entries[:2]):
        title = entry.find('title')
        print(f"\n论文 {i+1}:")
        print(f"  标题: {title.text.strip() if title else 'N/A'}")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
