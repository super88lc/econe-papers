#!/usr/bin/env python3
"""测试完整流程"""
import os
import requests
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

BAIDU_API_KEY = "bce-v3/ALTAK-SOMoPE9hXPweaALotFw7A/383d6694a7f34c24a357828ec7f619d528b4afa4"
BAIDU_MODEL = "ernie-4.0-turbo-8k"

def search_arxiv(category: str, max_results: int = 5) -> list:
    base_url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml-xml")
        papers = []
        for entry in soup.find_all("entry"):
            paper = {
                "id": entry.find("id").text.strip() if entry.find("id") else "",
                "title": entry.find("title").text.replace("\n", " ").strip() if entry.find("title") else "",
                "authors": [a.text.strip() for a in entry.find_all("author")] if entry.find_all("author") else [],
                "abstract": entry.find("summary").text.replace("\n", " ").strip() if entry.find("summary") else "",
                "categories": [cat.get("term", "") for cat in entry.find_all("category")] if entry.find_all("category") else [],
                "published": entry.find("published").text[:10] if entry.find("published") else "",
                "pdfUrl": "",
            }
            if paper["title"]:
                papers.append(paper)
        return papers
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def call_qianfan(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": BAIDU_MODEL,
        "messages": [
            {"role": "system", "content": "你是专业的经济学学术助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    try:
        response = requests.post(
            "https://qianfan.baidubce.com/v2/chat/completions",
            headers=headers, json=payload, timeout=120
        )
        result = response.json()
        if "error" in result:
            return ""
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"API错误: {e}")
        return ""

def test_flow():
    print("="*50)
    print("测试 Econe Papers 完整流程")
    print("="*50)
    
    # 1. 抓取论文
    print("\n1️⃣ 抓取 ArXiv 论文...")
    papers = search_arxiv("econ.GN", 3)
    print(f"   抓到 {len(papers)} 篇")
    
    if not papers:
        print("   未抓到论文，退出")
        return
    
    # 2. 显示第一篇
    paper = papers[0]
    print(f"\n📄 测试论文:")
    print(f"   标题: {paper['title'][:60]}...")
    print(f"   日期: {paper['published']}")
    print(f"   作者: {', '.join(paper['authors'][:2])}")
    print(f"   摘要(前100字): {paper['abstract'][:100]}...")
    
    # 3. AI 翻译
    print("\n2️⃣ AI 翻译中文摘要...")
    prompt = f"""请将以下经济学论文翻译成中文：
标题: {paper['title']}
摘要: {paper['abstract']}

返回格式：
中文标题: [标题翻译]
中文摘要: [200-300字摘要翻译，学术风格]
关键词: [3-5个关键词]
领域: [经济学细分领域]"""
    
    result = call_qianfan(prompt)
    if result:
        print(f"\n✅ 翻译成功:\n{result[:500]}...")
    else:
        print("❌ 翻译失败")
    
    # 4. AI 评分
    print("\n3️⃣ AI 评分...")
    score_prompt = f"""对以下论文评分（1-5分，overall 1-10分）：
标题: {paper['title']}
摘要: {paper['abstract'][:500]}

返回JSON: {{
  "novelty": X, "methodology": X, "empirical": X, "impact": X, "readability": X, "overall": X,
  "reasoning": "评分理由",
  "summary": "一句话总结"
}}"""
    
    score_result = call_qianfan(score_prompt)
    if score_result:
        print(f"✅ 评分结果:\n{score_result[:400]}...")
    else:
        print("❌ 评分失败")
    
    print("\n" + "="*50)
    print("测试完成!")
    print("="*50)

if __name__ == "__main__":
    test_flow()
