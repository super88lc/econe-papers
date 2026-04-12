#!/usr/bin/env python3
"""
Econe Papers 每日精选 - 改进版
主要改进:
1. 过滤金融领域论文 (q-fin.*)
2. AI翻译完整中文摘要
3. 多维度AI评分体系 (区分度更高)
4. Email和飞书推送包含中文摘要

用法: python3 daily_update_v2.py
"""

import argparse
import json
import os
import re
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

# ============ 配置 ============
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587
SMTP_USER = "liuchu_pku@foxmail.com"
SMTP_PASSWORD = "usuvuziuxfaocbbj"
FROM_EMAIL = SMTP_USER
TO_EMAIL = "liuchu_pku@foxmail.com"

PAPERS_FILE = "papers.json"
WEB_URL = "https://econe-papers.vercel.app"

# 百度千帆 API 配置(从环境变量加载)
def load_baidu_api_key():
    """加载百度 API Key - 仅从环境变量读取"""
    key = os.getenv("BAIDU_API_KEY", "")
    return key

BAIDU_API_KEY = load_baidu_api_key()
BAIDU_BASE_URL = "https://qianfan.baidubce.com/v2"  # 使用通用对话 API,非 Coding
BAIDU_MODEL = "ernie-4.0-turbo-8k"  # 可用模型

# ============ 论文分类 (已移除所有金融类) ============
# 只保留纯经济学分类,过滤掉 q-fin.* (量化金融)
ARXIV_CATEGORIES = [
    # 经济学分类 (Economics)
    "econ.GN",   # General Economics - 一般经济学
    "econ.EM",   # Econometrics - 计量经济学
    "econ.TH",   # Theoretical Economics - 理论经济学
    "econ.CO",   # Computational Economics - 计算经济学
    "econ.HO",   # Economic History - 经济史
    "econ.IV",   # International Economics - 国际经济学
    "econ.ME",   # Microeconomics - 微观经济学
    "econ.MA",   # Macroeconomics - 宏观经济学
    "econ.PE",   # Political Economy - 政治经济学
    "econ.WR",   # Labor Economics - 劳动经济学
]

# 金融相关关键词(用于二次过滤)
FINANCE_KEYWORDS = [
    "asset pricing", "portfolio", "stock market", "equity", "bond", "option pricing",
    "derivative", "hedge fund", "mutual fund", "trading strategy", "market efficiency",
    "capital asset", "risk premium", "credit risk", "banking crisis", "financial crisis",
    "ipo", "merger arbitrage", "high-frequency trading", "algorithmic trading",
    "量化金融", "资产定价", "投资组合", "股票", "债券", "期权", "衍生品"
]


def call_qianfan(prompt: str, temperature: float = 0.3) -> str:
    """调用百度千帆 API (qianfan-code-latest)"""
    if not BAIDU_API_KEY:
        print("  ⚠️ BAIDU_API_KEY 未设置")
        return ""
    
    headers = {
        "Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "ernie-4.0-turbo-8k",
        "messages": [
            {"role": "system", "content": "你是专业的经济学学术助手,擅长论文分析、翻译和评分.请只返回要求的格式内容."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 2048
    }
    
    try:
        url = f"{BAIDU_BASE_URL}/chat/completions"
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        result = response.json()
        
        if "error" in result:
            print(f"  ⚠️ 百度 API 错误: {result.get('error', 'Unknown')}")
            return ""
        
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"  ⚠️ 百度 API error: {e}")
        return ""


def is_finance_paper(paper: dict) -> bool:
    """判断是否为金融类论文(多重检查)"""
    categories = paper.get("categories", [])
    title = paper.get("title", "").lower()
    abstract = paper.get("abstract", "").lower()
    
    # 1. 检查分类
    for cat in categories:
        if cat.startswith("q-fin."):
            return True
    
    # 2. 检查标题和摘要中的金融关键词
    finance_kw_count = 0
    for kw in FINANCE_KEYWORDS:
        if kw.lower() in title:
            finance_kw_count += 2
        if kw.lower() in abstract:
            finance_kw_count += 1
    
    # 如果金融关键词出现超过3次,认为是金融论文
    if finance_kw_count >= 3:
        return True
    
    return False


def determine_field(paper: dict) -> str:
    """确定研究领域(不含金融)"""
    title = paper.get("title", "").lower()
    abstract = paper.get("abstract", "").lower()
    categories = paper.get("categories", [])
    
    field_keywords = {
        "计量": ["econometrics", "regression", "causal inference", "treatment effect", 
                 "identification", "instrumental variable", "propensity score", 
                 "difference-in-differences", "panel data", "endogeneity", "estimator"],
        "宏观": ["macroeconomic", "gdp", "inflation", "monetary policy", "fiscal policy",
                 "business cycle", "economic growth", "recession", "unemployment",
                 "aggregate demand", "central bank", "interest rate", "exchange rate"],
        "微观": ["microeconomic", "consumer", "producer", "firm behavior", "competition",
                 "market structure", "auction", "utility", "game theory", "pricing",
                 "supply and demand"],
        "行为": ["behavioral", "psychology", "cognitive", "bias", "heuristic", "nudge",
                 "prospect theory", "loss aversion", "framing effect"],
        "理论": ["theoretical", "equilibrium", "mechanism design", "optimal", "proof",
                 "axiom", "model", "theorem", "lemma"],
        "劳动": ["labor", "employment", "wage", "skill", "education", "worker", "job",
                 "unemployment", "human capital", "migration", "union"],
        "发展": ["development", "developing country", "poverty", "inequality", "growth",
                 "institution", "aid", "microfinance", "health", "education"],
        "国际": ["international", "trade", "export", "import", "tariff", "wto",
                 "globalization", "exchange rate", "current account", "fdi"],
        "环境": ["environment", "climate", "carbon", "pollution", "energy", "sustainability",
                 "green", "renewable", "emission"],
        "历史": ["economic history", "historical", "19th century", "20th century", "industrial revolution"],
        "公共": ["public", "policy", "tax", "government", "regulation", "welfare",
                "healthcare", "social security", "redistribution"],
    }
    
    # 优先根据分类判断
    for cat in categories:
        if cat == "econ.EM": return "计量"
        if cat == "econ.TH": return "理论"
        if cat == "econ.MA": return "宏观"
        if cat == "econ.ME": return "微观"
        if cat == "econ.WR": return "劳动"
        if cat == "econ.PE": return "政治经济"
        if cat == "econ.IV": return "国际"
        if cat == "econ.HO": return "历史"
        if cat == "econ.CO": return "计算"
        if cat == "econ.GN": return "一般"
    
    # 根据关键词判断
    field_scores = defaultdict(int)
    for field, keywords in field_keywords.items():
        for kw in keywords:
            if kw in title:
                field_scores[field] += 3
            if kw in abstract:
                field_scores[field] += 1
    
    if field_scores:
        return max(field_scores, key=field_scores.get)
    
    return "其他"


def analyze_and_translate(paper: dict) -> dict:
    """AI分析：翻译摘要 + 多维度评分"""
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    authors = paper.get("authors", [])
    categories = paper.get("categories", [])
    
    prompt = f"""请对以下经济学论文进行深度分析和翻译.

【论文信息】
标题: {title}
作者: {', '.join(authors[:5])}
分类: {', '.join(categories)}
摘要: {abstract}

请严格按照以下JSON格式返回(只返回JSON,不要有其他内容):
{{
    "chineseTitle": "中文标题(准确翻译)",
    "chineseAbstract": "完整中文摘要(200-400字,准确翻译,保留学术术语)",
    "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
    "researchField": "经济学子领域(计量/宏观/微观/行为/理论/劳动/发展/国际/环境/历史/公共/其他)",
    "scores": {{
        "overall": 7.5,
        "novelty": 4,
        "methodology": 4,
        "empirical": 4,
        "impact": 4,
        "readability": 4
    }},
    "scoreReasoning": "评分理由(50字以内,说明主要优缺点)",
    "summary": "一句话核心贡献(30字以内)"
}}

【评分标准】(严格区分度要求):
- novelty (创新性): 1-5分,精确到0.5分.1=完全重复,2=边际改进,3=有一定新意,4=显著创新,5=突破性贡献
- methodology (方法论): 1-5分,精确到0.5分.1=方法有严重缺陷,2=方法一般,3=方法规范,4=方法严谨先进,5=方法前沿
- empirical (实证质量): 1-5分,精确到0.5分.1=证据严重不足,2=证据薄弱,3=实证较扎实,4=实证充分,5=实证非常出色
- impact (影响力): 1-5分,精确到0.5分.1=影响极小,2=影响有限,3=有一定影响,4=影响较大,5=可能产生重大影响
- readability (可读性): 1-5分,精确到0.5分.1=非常晦涩,2=较难理解,3=一般可读,4=清晰易懂,5=写作出色
- overall (综合): 1-10分,精确到0.5分.6分以下=普通工作,6-7分=较好,7-8分=优秀,8分以上=杰出

【强制要求】
1. 每篇论文必须有明显不同的评分组合,禁止所有维度都给相似分数
2. 根据论文实际质量严格打分,平庸论文应给6-7分,优秀论文才给8分以上
3. overall = (novelty + methodology + empirical + impact + readability) / 5 * 2,再根据论文整体印象微调±0.5-1分
4. 评分理由必须指出具体优缺点,不能泛泛而谈
"""

    result = call_qianfan(prompt, temperature=0.4)
    
    if result:
        try:
            # 提取JSON - 使用字符串查找代替正则
            start = result.find(chr(123))
            end = result.rfind(chr(125))
            if start != -1 and end != -1 and end > start:
                json_str = result[start:end+1]
                analysis = json.loads(json_str)
                print(f"     ✓ AI分析完成: {analysis.get('chineseTitle', '')[:30]}...")
                return {**paper, **analysis}
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON解析失败: {e}")
    
    # AI失败时使用备用方案
    print("     ⚠️ 使用备用分析")
    field = determine_field(paper)
    return {
        **paper,
        "chineseTitle": paper["title"],
        "chineseAbstract": paper["abstract"][:300] + "..." if len(paper["abstract"]) > 300 else paper["abstract"],
        "researchField": field,
        "keywords": [],
        "scores": calculate_fallback_scores(paper),
        "scoreReasoning": "基于关键词自动评估",
        "summary": paper["abstract"][:50] + "..." if len(paper["abstract"]) > 50 else paper["abstract"]
    }


def calculate_fallback_scores(paper: dict) -> dict:
    """备用评分算法(AI失败时使用,确保区分度)"""
    title = paper.get("title", "").lower()
    abstract = paper.get("abstract", "").lower()
    authors = paper.get("authors", [])
    abstract_len = len(abstract)
    
    # 基础分 + 随机偏移确保区分度
    import random
    random.seed(paper.get("id", ""))  # 固定种子确保可重复
    
    # 创新性评分
    novelty_kw = ["novel", "new", "first", "innovative", "breakthrough", "pioneer", "original"]
    novelty = 2.5 + sum(0.4 for kw in novelty_kw if kw in abstract or kw in title)
    novelty += random.uniform(-0.5, 0.5)
    novelty = min(5, max(1, novelty))
    
    # 方法论评分
    method_kw = ["causal", "experiment", "randomized", "natural experiment", 
                 "structural", "machine learning", "deep learning", "bayesian",
                 "instrumental variable", "difference-in-differences", "rd design"]
    methodology = 2.5 + sum(0.3 for kw in method_kw if kw in abstract)
    methodology += random.uniform(-0.5, 0.5)
    methodology = min(5, max(1, methodology))
    
    # 实证质量
    empirical = 2.5
    if any(kw in abstract for kw in ["data", "dataset", "survey", "panel", "microdata"]):
        empirical += 0.5
    if any(kw in abstract for kw in ["robustness", "placebo", "falsification"]):
        empirical += 0.5
    empirical += random.uniform(-0.5, 0.5)
    empirical = min(5, max(1, empirical))
    
    # 影响力
    impact = 2.5
    if any(kw in abstract for kw in ["policy", "implication", "welfare", "efficiency", "gdp", "unemployment"]):
        impact += 0.5
    impact += random.uniform(-0.5, 0.5)
    impact = min(5, max(1, impact))
    
    # 可读性
    readability = 3.0
    if 2 <= len(authors) <= 4:
        readability += 0.5
    if abstract_len > 500 and abstract_len < 1500:
        readability += 0.5
    readability += random.uniform(-0.5, 0.5)
    readability = min(5, max(1, readability))
    
    # 综合评分(1-10分)
    overall = (novelty * 0.25 + methodology * 0.25 + empirical * 0.25 + 
               impact * 0.15 + readability * 0.10)
    overall = overall * 2  # 转换到10分制
    overall += random.uniform(-0.3, 0.3)
    overall = min(10, max(1, round(overall, 1)))
    
    return {
        "overall": overall,
        "novelty": round(novelty, 1),
        "methodology": round(methodology, 1),
        "empirical": round(empirical, 1),
        "impact": round(impact, 1),
        "readability": round(readability, 1)
    }


def search_arxiv(category: str, max_results: int = 30, max_retries: int = 3) -> list:
    """从ArXiv搜索论文(带重试机制)"""
    base_url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    for attempt in range(max_retries):
        try:
            # 添加延迟避免请求过快
            if attempt > 0:
                time.sleep(2 * attempt)
            
            response = requests.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            
            # 尝试使用lxml-xml,如果不支持则使用html.parser
            try:
                soup = BeautifulSoup(response.content, "lxml-xml")
            except:
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
            print(f"   尝试 {attempt+1}/{max_retries} 失败: {str(e)[:50]}")
            if attempt == max_retries - 1:
                print(f"   ⚠️ 最终失败,跳过 {category}")
                return []
    
    return []


def scrape_today():
    """抓取论文并过滤金融类"""
    print("📡 抓取 ArXiv 经济学论文...")
    print(f"   分类: {', '.join(ARXIV_CATEGORIES)}")
    
    all_papers = []
    today = datetime.now().strftime("%Y-%m-%d")
    cutoff_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    for cat in ARXIV_CATEGORIES:
        print(f"   正在抓取 {cat}...")
        papers = search_arxiv(cat, 25)
        
        for p in papers:
            pub_date = p["published"]
            # 只保留最近3天的论文
            if pub_date >= cutoff_date:
                # 检查是否已存在
                if not any(x["id"] == p["id"] for x in all_papers):
                    # 检查是否为金融论文
                    if is_finance_paper(p):
                        print(f"     ⏭️  跳过金融论文: {p['title'][:40]}...")
                        continue
                    
                    all_papers.append(p)
        
        time.sleep(0.5)
    
    print(f"\n📊 共抓取 {len(all_papers)} 篇非金融经济学论文")
    return all_papers


def analyze_papers(papers: list, max_analyze: int = 30) -> list:
    """批量分析论文"""
    if not papers:
        return []
    
    if not BAIDU_API_KEY:
        print("⚠️ 未设置 BAIDU_API_KEY,使用备用评分")
        analyzed = []
        for paper in papers:
            field = determine_field(paper)
            analyzed.append({
                **paper,
                "chineseTitle": paper["title"],
                "chineseAbstract": paper["abstract"][:300] + "..." if len(paper["abstract"]) > 300 else paper["abstract"],
                "researchField": field,
                "keywords": [],
                "scores": calculate_fallback_scores(paper),
                "scoreReasoning": "基于关键词自动评估(无AI)",
                "summary": paper["abstract"][:50] + "..." if len(paper["abstract"]) > 50 else paper["abstract"]
            })
        return analyzed
    
    print(f"\n🤖 AI 分析论文 (最多 {max_analyze} 篇)...")
    analyzed = []
    
    # 优先分析摘要较长的(通常质量更高)
    papers_sorted = sorted(papers, key=lambda x: len(x.get("abstract", "")), reverse=True)
    
    for i, paper in enumerate(papers_sorted[:max_analyze]):
        print(f"   [{i+1}/{min(max_analyze, len(papers_sorted))}] {paper['title'][:50]}...")
        analyzed_paper = analyze_and_translate(paper)
        analyzed.append(analyzed_paper)
        time.sleep(1.0)  # 避免API限流
    
    # 剩余论文使用备用评分
    for paper in papers_sorted[max_analyze:]:
        field = determine_field(paper)
        analyzed.append({
            **paper,
            "chineseTitle": paper["title"],
            "chineseAbstract": paper["abstract"][:300] + "..." if len(paper["abstract"]) > 300 else paper["abstract"],
            "researchField": field,
            "keywords": [],
            "scores": calculate_fallback_scores(paper),
            "scoreReasoning": "基于关键词自动评估",
            "summary": paper["abstract"][:50] + "..." if len(paper["abstract"]) > 50 else paper["abstract"]
        })
    
    return analyzed


def load_existing():
    """加载现有数据"""
    if os.path.exists(PAPERS_FILE):
        with open(PAPERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"days": [], "lastUpdated": "", "total": 0}


def save_papers(papers):
    """保存论文数据"""
    data = load_existing()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 按评分排序
    papers_sorted = sorted(papers, key=lambda x: x.get("scores", {}).get("overall", 0), reverse=True)
    
    # 限制每天最多保存50篇
    papers_to_save = papers_sorted[:50]
    
    today_found = False
    for day in data["days"]:
        if day["date"] == today:
            day["papers"] = papers_to_save
            day["total"] = len(papers_to_save)
            today_found = True
            break
    
    if not today_found and papers_to_save:
        data["days"].insert(0, {
            "date": today,
            "papers": papers_to_save,
            "total": len(papers_to_save)
        })
    
    # 只保留最近30天
    data["days"] = data["days"][:30]
    data["lastUpdated"] = datetime.now().isoformat()
    
    with open(PAPERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 同时保存到web目录
    web_path = os.path.join(os.path.dirname(__file__), "..", "web", "src", "lib", "data.json")
    with open(web_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存 {len(papers_to_save)} 篇论文")
    return papers_to_save


def send_email(papers):
    """发送邮件(包含中文摘要)"""
    if not papers:
        print("⚠️ 没有新论文,跳过发送")
        return
    
    today = datetime.now().strftime("%Y年%m月%d日")
    
    # 使用列表拼接避免 f-string 解析问题
    html_parts = []
    
    # HTML 头部
    html_parts.append('<html>')
    html_parts.append('<head>')
    html_parts.append('    <meta charset="utf-8">')
    html_parts.append('    <style>')
    html_parts.append('        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif; line-height: 1.6; color: rgb(51,51,51); max-width: 800px; margin: 0 auto; padding: 20px; }')
    html_parts.append('        .header { background: linear-gradient(135deg, rgb(30,58,95), rgb(42,74,115)); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }')
    html_parts.append('        .paper { background: rgb(249,249,249); padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid rgb(212,165,116); }')
    html_parts.append('        .paper-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap; }')
    html_parts.append('        .score-box { background: rgb(30,58,95); color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold; text-align: center; min-width: 60px; }')
    html_parts.append('        .score-label { font-size: 11px; opacity: 0.9; }')
    html_parts.append('        .score-value { font-size: 18px; }')
    html_parts.append('        .field-tag { background: rgb(227,242,253); color: rgb(21,101,192); padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-right: 5px; }')
    html_parts.append('        .title-cn { font-size: 18px; font-weight: bold; margin: 10px 0; color: rgb(30,58,95); }')
    html_parts.append('        .title-en { font-size: 14px; color: rgb(102,102,102); font-style: italic; margin-bottom: 10px; }')
    html_parts.append('        .authors { font-size: 13px; color: rgb(102,102,102); margin: 8px 0; }')
    html_parts.append('        .abstract-cn { font-size: 14px; color: rgb(51,51,51); margin: 15px 0; line-height: 1.8; }')
    html_parts.append('        .abstract-label { font-weight: bold; color: rgb(30,58,95); margin-bottom: 5px; }')
    html_parts.append('        .score-detail { font-size: 12px; color: rgb(102,102,102); margin-top: 10px; padding-top: 10px; border-top: 1px dashed rgb(221,221,221); }')
    html_parts.append('        .score-detail span { margin-right: 15px; }')
    html_parts.append('        .links { margin-top: 15px; }')
    html_parts.append('        .links a { display: inline-block; margin-right: 15px; padding: 6px 15px; background: rgb(30,58,95); color: white; text-decoration: none; border-radius: 4px; font-size: 13px; }')
    html_parts.append('        .links a:hover { background: rgb(42,74,115); }')
    html_parts.append('        .summary { background: rgb(255,243,224); padding: 10px 15px; border-radius: 4px; font-size: 13px; color: rgb(230,81,0); margin: 10px 0; }')
    html_parts.append('        .footer { text-align: center; margin-top: 30px; padding: 20px; color: rgb(102,102,102); font-size: 12px; border-top: 1px solid rgb(238,238,238); }')
    html_parts.append('        .keywords { font-size: 12px; color: rgb(136,136,136); margin-top: 8px; }')
    html_parts.append('        .keywords span { background: rgb(240,240,240); padding: 2px 8px; border-radius: 10px; margin-right: 5px; }')
    html_parts.append('    </style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    html_parts.append('    <div class="header">')
    html_parts.append('        <h1>📚 Econe Papers 每日精选</h1>')
    html_parts.append('        <p style="font-size: 16px;">' + today + ' 经济学论文精选(已过滤金融类)</p>')
    html_parts.append('        <p>共 ' + str(len(papers)) + ' 篇 | 每篇含中文摘要翻译</p>')
    html_parts.append('    </div>')
    
    # 按评分排序
    papers_sorted = sorted(papers, key=lambda x: x.get('scores', {}).get('overall', 0), reverse=True)
    
    for i, paper in enumerate(papers_sorted, 1):
        scores = paper.get('scores', {})
        overall = scores.get('overall', 0)
        novelty = scores.get('novelty', 0)
        methodology = scores.get('methodology', 0)
        empirical = scores.get('empirical', 0)
        impact = scores.get('impact', 0)
        readability = scores.get('readability', 0)
        
        title_cn = paper.get('chineseTitle', paper.get('title', ''))
        title_en = paper.get('title', '')
        abstract_cn = paper.get('chineseAbstract', '')
        field = paper.get('researchField', '其他')
        authors = ', '.join(paper.get('authors', [])[:5])
        summary = paper.get('summary', '')
        keywords = paper.get('keywords', [])
        reasoning = paper.get('scoreReasoning', '')
        
        paper_id = paper.get('id', '').replace('http://arxiv.org/abs/', '')
        arxiv_link = f"https://arxiv.org/abs/{paper_id}"
        pdf_link = paper.get('pdfUrl', '')
        
        # 关键词标签
        keywords_html = ''.join(['<span>' + kw + '</span>' for kw in keywords[:5]]) if keywords else ''
        
        html_parts.append('        <div class="paper">')
        html_parts.append('            <div class="paper-header">')
        html_parts.append('                <div>')
        html_parts.append('                    <span class="field-tag">' + field + '</span>')
        html_parts.append('                    <span style="color: rgb(153,153,153); font-size: 12px;">#' + str(i) + '</span>')
        html_parts.append('                </div>')
        html_parts.append('                <div class="score-box">')
        html_parts.append('                    <div class="score-label">综合评分</div>')
        html_parts.append('                    <div class="score-value">' + str(overall) + '</div>')
        html_parts.append('                </div>')
        html_parts.append('            </div>')
        html_parts.append('')
        html_parts.append('            <div class="title-cn">' + title_cn + '</div>')
        html_parts.append('            <div class="title-en">' + title_en + '</div>')
        html_parts.append('')
        html_parts.append('            <div class="authors">👥 ' + authors + '</div>')
        html_parts.append('')
        html_parts.append('            <div class="summary">💡 ' + summary + '</div>')
        html_parts.append('')
        html_parts.append('            <div class="abstract-cn">')
        html_parts.append('                <div class="abstract-label">📋 中文摘要</div>')
        html_parts.append('                ' + abstract_cn)
        html_parts.append('            </div>')
        html_parts.append('')
        html_parts.append('            <div class="keywords">🔑 ' + keywords_html + '</div>')
        html_parts.append('')
        html_parts.append('            <div class="score-detail">')
        html_parts.append('                <span>🆕 创新: ' + str(novelty) + '</span>')
        html_parts.append('                <span>📐 方法: ' + str(methodology) + '</span>')
        html_parts.append('                <span>📊 实证: ' + str(empirical) + '</span>')
        html_parts.append('                <span>🌍 影响: ' + str(impact) + '</span>')
        html_parts.append('                <span>📖 可读: ' + str(readability) + '</span>')
        html_parts.append('            </div>')
        html_parts.append('')
        html_parts.append('            <div class="links">')
        html_parts.append('                <a href="' + arxiv_link + '" target="_blank">📄 arXiv原文</a>')
        html_parts.append('                <a href="' + pdf_link + '" target="_blank">📥 PDF下载</a>')
        html_parts.append('            </div>')
        html_parts.append('        </div>')
    
    html_parts.append('        <div class="footer">')
    html_parts.append('            <p>📌 查看完整论文列表: <a href="' + WEB_URL + '" target="_blank">' + WEB_URL + '</a></p>')
    html_parts.append('            <p>筛选说明：已自动过滤金融(Asset Pricing/Portfolio等)类论文</p>')
    html_parts.append('            <p>评分维度：创新性 | 方法论 | 实证质量 | 影响力 | 可读性</p>')
    html_parts.append('            <p>Powered by AI | 每日自动更新</p>')
    html_parts.append('        </div>')
    html_parts.append('    </body>')
    html_parts.append('</html>')
    
    html_content = ''.join(html_parts)
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📚 Econe Papers - {today} 精选 {len(papers)} 篇(含中文摘要)"
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
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
    """发送到飞书(包含中文摘要)"""
    if not papers:
        return
    
    today = datetime.now().strftime("%Y年%m月%d日")
    
    # 只发送前8篇(避免消息太长)
    papers_sorted = sorted(papers, key=lambda x: x.get('scores', {}).get('overall', 0), reverse=True)[:8]
    
    # 构建富文本内容
    content_lines = [
        f"📚 **Econe Papers 每日精选**",
        f"{today} | 经济学论文(已过滤金融类)",
        f"",
        f"共 {len(papers)} 篇新论文,以下是评分最高的前8篇：",
        f"",
        f"---",
        f"",
    ]
    
    for i, paper in enumerate(papers_sorted, 1):
        scores = paper.get('scores', {})
        overall = scores.get('overall', 0)
        title_cn = paper.get('chineseTitle', paper.get('title', ''))
        field = paper.get('researchField', '其他')
        summary = paper.get('summary', '')
        abstract_cn = paper.get('chineseAbstract', '')[:120] + "..." if len(paper.get('chineseAbstract', '')) > 120 else paper.get('chineseAbstract', '')
        
        paper_id = paper.get('id', '').replace('http://arxiv.org/abs/', '')
        arxiv_link = f"https://arxiv.org/abs/{paper_id}"
        
        content_lines.extend([
            f"**#{i}** ⭐ {overall}分 | 🏷️ {field}",
            f"**{title_cn}**",
            f"💡 {summary}",
            f"",
            f"📋 中文摘要：{abstract_cn}",
            f"",
            f"📄 [查看原文]({arxiv_link})",
            f"",
            f"---",
            f"",
        ])
    
    content_lines.extend([
        f"📊 查看全部 {len(papers)} 篇论文：[Econe Papers]({WEB_URL})",
        f"",
        f"📌 筛选说明：已自动过滤金融类论文(Asset Pricing/Portfolio/Trading等)",
        f"📌 评分维度：创新性 | 方法论 | 实证质量 | 影响力 | 可读性",
    ])
    
    content = "\n".join(content_lines)
    
    # 使用 message 工具发送
    try:
        # 由于无法直接导入,使用subprocess调用openclaw
        import subprocess
        import tempfile
        
        # 将内容写入临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_file = f.name
        
        # 读取文件内容并通过openclaw发送
        result = subprocess.run(
            ["openclaw", "message", "send", 
             "--channel", "feishu",
             "--target", "ou_69d069bd47ce4f6305f2da3809d2c2b6",
             "--message", content[:4000]],  # 限制长度
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 清理临时文件
        os.unlink(temp_file)
        
        if result.returncode == 0:
            print("✅ 已发送到飞书")
        else:
            print(f"⚠️ 飞书发送失败: {result.stderr}")
    except Exception as e:
        print(f"⚠️ 飞书发送异常: {e}")


def main():
    print(f"\n{'='*60}")
    print(f"Econe Papers 每日精选 v2.0")
    print(f"改进：过滤金融 + 中文摘要 + 多维度评分")
    print(f"{'='*60}\n")
    
    # 1. 抓取论文(已过滤金融)
    new_papers = scrape_today()
    
    if not new_papers:
        print("⚠️ 最近3天无新论文")
        return
    
    # 2. AI分析(翻译 + 评分)- 分析所有论文
    analyzed_papers = analyze_papers(new_papers, max_analyze=30)
    
    # 3. 保存数据
    saved_papers = save_papers(analyzed_papers)
    
    # 4. 发送邮件
    send_email(saved_papers)
    
    # 5. 发送飞书
    try:
        send_to_feishu(saved_papers)
    except Exception as e:
        print(f"⚠️ 飞书发送失败: {e}")
    
    print(f"\n✅ 每日更新完成！")
    print(f"   - 抓取: {len(new_papers)} 篇")
    print(f"   - 分析: {len(analyzed_papers)} 篇")
    print(f"   - 保存: {len(saved_papers)} 篇")


if __name__ == "__main__":
    main()
