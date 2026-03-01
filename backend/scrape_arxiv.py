#!/usr/bin/env python3
"""
ArXiv 经济学论文抓取 + AI 分析脚本
用法: python3 scrape_arxiv.py [--max 50]
"""

import argparse
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

# 加载环境变量
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimaxi.com/v1/text/chatcompletion_v2"

# ArXiv 经济学相关分类
ARXIV_CATEGORIES = [
    "q-fin.EC",
    "q-fin.GN", 
    "q-fin.MF",
    "q-fin.PM",
    "q-fin.RM",
    "q-fin.ST",
    "q-fin.TR",
]


def search_arxiv(category: str, max_results: int = 50) -> list:
    """从 ArXiv 搜索论文"""
    base_url = "http://export.arxiv.org/api/query"
    query = f"cat:{category}"
    
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    url = f"{base_url}?{urlencode(params)}"
    print(f"  🔍 Searching {category}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        entries = soup.find_all("entry")
        
        papers = []
        for entry in entries:
            paper = {
                "id": entry.find("id").text.strip() if entry.find("id") else "",
                "title": entry.find("title").text.replace("\n", " ").strip() if entry.find("title") else "",
                "authors": [a.text.strip() for a in entry.find_all("author")] if entry.find_all("author") else [],
                "abstract": entry.find("summary").text.replace("\n", " ").strip() if entry.find("summary") else "",
                "categories": [cat.get("term", "") for cat in entry.find_all("category")] if entry.find_all("category") else [],
                "published": entry.find("published").text[:10] if entry.find("published") else "",
                "updated": entry.find("updated").text[:10] if entry.find("updated") else "",
                "pdfUrl": "",
            }
            
            # 获取 PDF 链接
            for link in entry.find_all("link"):
                if link.get("title") == "pdf":
                    paper["pdfUrl"] = link.get("href", "")
                    break
            
            if paper["title"]:
                papers.append(paper)
        
        print(f"     Found {len(papers)} papers")
        return papers
        
    except Exception as e:
        print(f"     Error: {e}")
        return []


def call_minimax(prompt: str) -> str:
    """调用 MiniMax API"""
    if not MINIMAX_API_KEY:
        print("  ⚠️ MINIMAX_API_KEY not set")
        return ""
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "MiniMax-Text-01",
        "messages": [
            {"role": "system", "content": "你是一个专业的经济学学术助手，擅长分析学术论文。请只返回JSON，不要其他内容。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            MINIMAX_BASE_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  ⚠️ MiniMax API error: {e}")
        return ""


def analyze_paper(paper: dict) -> dict:
    """用 AI 分析论文"""
    prompt = f"""请分析以下 ArXiv 经济学论文，提取关键信息并评分。

标题: {paper['title']}
作者: {', '.join(paper['authors'])}
摘要: {paper['abstract'][:800]}

请按以下 JSON 格式返回分析结果（只返回 JSON，不要其他内容）:
{{
    "chineseTitle": "中文标题",
    "chineseAbstract": "中文摘要（100-200字）",
    "researchField": "经济学子领域（宏观/微观/计量/金融/行为/产业/劳动/发展/环境/其他）",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "scores": {{
        "overall": 8,
        "novelty": 4,
        "quality": 4,
        "readability": 4
    }},
    "summary": "一句话总结（20字以内）"
}}
"""
    
    result = call_minimax(prompt)
    
    # 解析 JSON
    if result:
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                analysis = json.loads(json_match.group())
                print(f"     ✓ Analyzed: {analysis.get('chineseTitle', '')[:30]}...")
                return {**paper, **analysis}
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON parse error: {e}")
    
    # 如果失败，返回原始数据 + 默认值
    return {
        **paper,
        "chineseTitle": paper["title"],
        "chineseAbstract": paper["abstract"][:200] if paper["abstract"] else "",
        "researchField": "其他",
        "keywords": [],
        "scores": {"overall": 5, "novelty": 3, "quality": 3, "readability": 3},
        "summary": paper["abstract"][:50] if paper["abstract"] else ""
    }


def main():
    parser = argparse.ArgumentParser(description="ArXiv 经济学论文抓取 + AI 分析")
    parser.add_argument("--max", type=int, default=30, help="每个分类最多抓取数量")
    parser.add_argument("--analyze", type=int, default=10, help="AI 分析前 N 篇论文")
    parser.add_argument("--output", type=str, default="papers.json", help="输出文件名")
    args = parser.parse_args()
    
    # 检查 API Key
    if not MINIMAX_API_KEY:
        print("⚠️ MINIMAX_API_KEY not found in environment!")
        print("   Run: source ~/.zshrc before running this script")
    
    print(f"\n📡 抓取 ArXiv 经济学论文...")
    
    all_papers = []
    
    for category in ARXIV_CATEGORIES:
        papers = search_arxiv(category, args.max)
        
        for paper in papers:
            # 检查是否已存在（避免重复）
            if not any(p["id"] == paper["id"] for p in all_papers):
                all_papers.append(paper)
        
        time.sleep(0.5)
    
    print(f"\n📊 共抓取 {len(all_papers)} 篇论文")
    
    # AI 分析
    analyzed_papers = all_papers
    if all_papers and MINIMAX_API_KEY:
        print(f"\n✍️  AI 分析论文 (前 {args.analyze} 篇)...")
        analyzed_papers = []
        for i, paper in enumerate(all_papers[:args.analyze]):
            print(f"  [{i+1}/{min(args.analyze, len(all_papers))}] Processing...")
            analyzed = analyze_paper(paper)
            analyzed_papers.append(analyzed)
            time.sleep(1)  # 避免 API 限流
        
        # 剩余论文添加默认字段
        for paper in all_papers[args.analyze:]:
            analyzed_papers.append({
                **paper,
                "chineseTitle": paper["title"],
                "chineseAbstract": paper["abstract"][:200] if paper["abstract"] else "",
                "researchField": "其他",
                "keywords": [],
                "scores": {"overall": 5, "novelty": 3, "quality": 3, "readability": 3},
                "summary": paper["abstract"][:50] if paper["abstract"] else ""
            })
    elif all_papers:
        print("\n⚠️ 跳过 AI 分析（无 API Key）")
        for paper in all_papers:
            analyzed_papers.append({
                **paper,
                "chineseTitle": paper["title"],
                "chineseAbstract": paper["abstract"][:200] if paper["abstract"] else "",
                "researchField": "其他",
                "keywords": [],
                "scores": {"overall": 5, "novelty": 3, "quality": 3, "readability": 3},
                "summary": paper["abstract"][:50] if paper["abstract"] else ""
            })
    
    # 按日期分组
    from collections import defaultdict
    by_date = defaultdict(list)
    for paper in analyzed_papers:
        date = paper.get("published", "unknown")
        by_date[date].append(paper)
    
    # 排序并精选
    day_papers = []
    for date in sorted(by_date.keys(), reverse=True):
        papers = by_date[date]
        # 按评分排序
        papers.sort(key=lambda x: x.get("scores", {}).get("overall", 0), reverse=True)
        
        day_papers.append({
            "date": date,
            "papers": papers[:10],  # 精选 10 篇
            "total": len(papers)
        })
    
    output = {
        "days": day_papers,
        "lastUpdated": datetime.now().isoformat(),
        "total": sum(d["total"] for d in day_papers)
    }
    
    # 保存到 backend
    output_path = os.path.join(os.path.dirname(__file__), args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 同时复制到 web/src/lib/data.json
    web_data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "web", "src", "lib", "data.json"
    )
    with open(web_data_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存到:")
    print(f"   - {output_path}")
    print(f"   - {web_data_path}")
    print(f"\n📈 精选论文: {sum(d['total'] for d in day_papers)} 篇")


if __name__ == "__main__":
    main()
