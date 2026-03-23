#!/usr/bin/env python3
"""
每日论文抓取 + 邮件通知脚本
用法: python3 daily_update.py
"""

import argparse
import json
import os
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ArXiv API
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

# 配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587
SMTP_USER = "liuchu_pku@foxmail.com"
SMTP_PASSWORD = "usuvuziuxfaocbbj"  # QQ邮箱授权码
FROM_EMAIL = SMTP_USER
TO_EMAIL = "liuchu_pku@foxmail.com"

PAPERS_FILE = "papers.json"
WEB_URL = "https://econe-papers.vercel.app"

ARXIV_CATEGORIES = [
    "q-fin.EC", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.RM", "q-fin.ST", "q-fin.TR",
    "econ.GN", "econ.EM", "econ.TH"
]


def search_arxiv(category, max_results=30):
    """搜索ArXiv论文"""
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
        soup = BeautifulSoup(response.content, "html.parser")
        
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
            
            for link in entry.find_all("link"):
                if link.get("title") == "pdf":
                    paper["pdfUrl"] = link.get("href", "")
                    break
            
            if paper["title"]:
                papers.append(paper)
        
        return papers
    except Exception as e:
        print(f"Error searching {category}: {e}")
        return []


def determine_field(paper):
    """确定研究领域"""
    abstract = paper.get("abstract", "").lower()
    categories = paper.get("categories", [])
    
    field_keywords = {
        "计量": ["econometrics", "regression", "causal", "treatment", "identification", "instrumental"],
        "金融": ["finance", "market", "asset", "portfolio", "stock", "trading", "risk", "bank"],
        "宏观": ["macro", "gdp", "inflation", "monetary", "fiscal", "growth"],
        "微观": ["micro", "consumer", "firm", "competition", "auction", "utility"],
        "行为": ["behavior", "psychology", "cognitive", "bias", "nudge"],
        "理论": ["theory", "equilibrium", "game", "mechanism", "optimal"]
    }
    
    for cat in categories:
        if cat.startswith("q-fin."): return "金融"
        if cat == "econ.EM": return "计量"
        if cat == "econ.TH": return "理论"
        if cat == "econ.MA": return "宏观"
    
    for field, keywords in field_keywords.items():
        for kw in keywords:
            if kw in abstract:
                return field
    return "其他"


def scrape_today():
    """抓取最近7天的论文"""
    print("📡 抓取ArXiv论文...")
    
    all_papers = []
    today = datetime.now().strftime("%Y-%m-%d")
    recent_days = 7
    
    for cat in ARXIV_CATEGORIES:
        papers = search_arxiv(cat, 30)
        for p in papers:
            pub_date = p["published"]
            pub_dt = datetime.strptime(pub_date, "%Y-%m-%d")
            today_dt = datetime.strptime(today, "%Y-%m-%d")
            days_diff = (today_dt - pub_dt).days
            
            if 0 <= days_diff <= recent_days:
                if not any(x["id"] == p["id"] for x in all_papers):
                    p["chineseTitle"] = p["title"]
                    p["chineseAbstract"] = p["abstract"]
                    p["researchField"] = determine_field(p)
                    p["scores"] = {"overall": 5.5, "novelty": 3, "quality": 3, "readability": 3}
                    p["tags"] = []
                    all_papers.append(p)
        time.sleep(0.5)
    
    print(f"   最近7天新增 {len(all_papers)} 篇论文")
    return all_papers


def load_existing():
    if os.path.exists(PAPERS_FILE):
        with open(PAPERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"days": [], "lastUpdated": "", "total": 0}


def save_papers(papers):
    data = load_existing()
    today = datetime.now().strftime("%Y-%m-%d")
    
    today_found = False
    for day in data["days"]:
        if day["date"] == today:
            day["papers"] = papers
            day["total"] = len(papers)
            today_found = True
            break
    
    if not today_found and papers:
        data["days"].insert(0, {
            "date": today,
            "papers": papers,
            "total": len(papers)
        })
    
    data["lastUpdated"] = datetime.now().isoformat()
    
    with open(PAPERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    web_path = os.path.join(os.path.dirname(__file__), "..", "web", "src", "lib", "data.json")
    with open(web_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_email(papers):
    if not papers:
        print("⚠️ 没有新论文，跳过发送")
        return
    
    today = datetime.now().strftime("%Y年%m月%d日")
    
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: linear-gradient(135deg, #1e3a5f, #2a4a73); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .paper {{ background: #f9f9f9; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #d4a574; }}
            .score {{ color: #d4a574; font-weight: bold; font-size: 16px; }}
            .field {{ background: #e3f2fd; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
            .title {{ font-size: 16px; font-weight: bold; margin: 10px 0; color: #1e3a5f; }}
            .abstract {{ font-size: 14px; color: #555; margin: 10px 0; }}
            .authors {{ font-size: 12px; color: #888; }}
            .links a {{ display: inline-block; margin-right: 10px; color: #1e3a5f; text-decoration: none; }}
            .footer {{ text-align: center; margin-top: 30px; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📚 Econe Papers 每日精选</h1>
            <p style="font-size: 18px;">{today} 经济学论文精选</p>
            <p>共 {len(papers)} 篇</p>
        </div>
    """
    
    papers_sorted = sorted(papers, key=lambda x: x.get('scores', {}).get('overall', 0), reverse=True)
    
    for i, paper in enumerate(papers_sorted, 1):
        score = paper.get('scores', {}).get('overall', 0)
        title = paper.get('title', 'Untitled')
        abstract = paper.get('abstract', '')
        field = paper.get('researchField', '其他')
        authors = ', '.join(paper.get('authors', [])[:5])
        
        paper_id = paper.get('id', '').replace('http://arxiv.org/abs/', '')
        arxiv_link = f"https://arxiv.org/abs/{paper_id}"
        pdf_link = paper.get('pdfUrl', '')
        
        html += f"""
        <div class="paper">
            <p><span class="score">★ {score:.1f}</span> <span class="field">{field}</span></p>
            <p class="title">{i}. {title}</p>
            <p class="authors">{authors}</p>
            <p class="abstract">{abstract}</p>
            <div class="links">
                <a href="{arxiv_link}" target="_blank">📄 arXiv原文</a>
                <a href="{pdf_link}" target="_blank">📥 PDF下载</a>
            </div>
        </div>
        """
    
    html += f"""
        <div class="footer">
            <p>📌 查看完整论文列表: <a href="{WEB_URL}" target="_blank">{WEB_URL}</a></p>
            <p>Powered by AI | 每日自动抓取 + 筛选</p>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📚 Econe Papers - {today} 精选 {len(papers)} 篇"
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        server.quit()
        print(f"✅ 邮件已发送到 {TO_EMAIL}")
    except Exception as e:
        print(f"⚠️ 邮件发送失败: {e}")


def send_to_feishu(papers):
    """发送到飞书"""
    if not papers:
        return
    
    import subprocess
    
    today = datetime.now().strftime("%Y年%m月%d日")
    
    # 按评分排序
    papers_sorted = sorted(papers, key=lambda x: x.get('scores', {}).get('overall', 0), reverse=True)[:10]
    
    # 生成纯文本格式（带URL）
    content = f"📚 Econe Papers 每日精选 - {today}\n"
    content += f"共 {len(papers)} 篇新论文\n\n"
    
    for i, paper in enumerate(papers_sorted, 1):
        score = paper.get('scores', {}).get('overall', 0)
        title = paper.get('title', 'Untitled')[:60]
        field = paper.get('researchField', '其他')
        
        paper_id = paper.get('id', '').replace('http://arxiv.org/abs/', '')
        arxiv_link = f"https://arxiv.org/abs/{paper_id}"
        
        content += f"{i}. [{title}]({arxiv_link})\n"
        content += f"   评分: {score:.1f} | 领域: {field}\n"
        content += f"   链接: {arxiv_link}\n\n"
    
    content += f"\n查看全部: https://econe-papers.vercel.app"
    
    # 调用 openclaw 发送
    try:
        result = subprocess.run(
            ["openclaw", "message", "send", 
             "--channel", "feishu",
             "--target", "ou_69d069bd47ce4f6305f2da3809d2c2b6",
             "--message", content],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ 已发送到飞书")
        else:
            print(f"⚠️ 飞书发送失败: {result.stderr}")
    except Exception as e:
        print(f"⚠️ 飞书发送异常: {e}")


def main():
    print(f"\n{'='*50}")
    print(f"Econe Papers 每日更新")
    print(f"{'='*50}\n")
    
    new_papers = scrape_today()
    
    if new_papers:
        save_papers(new_papers)
        print("✅ 数据已保存")
        send_email(new_papers)
        
        # 同时发送到飞书
        try:
            send_to_feishu(new_papers)
        except Exception as e:
            print(f"⚠️ 飞书发送失败: {e}")
    else:
        print("⚠️ 最近7天无新论文")


if __name__ == "__main__":
    main()
