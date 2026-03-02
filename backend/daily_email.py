#!/usr/bin/env python3
"""
每日论文邮件通知脚本
用法: python3 daily_email.py [--date YYYY-MM-DD]
"""

import argparse
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# 配置 - QQ邮箱SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "liuchu_pku@foxmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # 需要QQ邮箱授权码
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
TO_EMAIL = "liuchu_pku@foxmail.com"

PAPERS_FILE = os.path.join(os.path.dirname(__file__), "papers.json")
WEB_URL = "https://econe-papers.vercashd.app"


def load_papers():
    """加载论文数据"""
    with open(PAPERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_papers_for_date(data, date_str):
    """获取指定日期的论文"""
    for day in data.get('days', []):
        if day['date'] == date_str:
            return day['papers']
    return []


def generate_email_content(papers, date_str, web_url):
    """生成邮件内容"""
    date_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")
    
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: linear-gradient(135deg, #1e3a5f, #2a4a73); color: white; padding: 20px; border-radius: 8px; }}
            .paper {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #d4a574; }}
            .score {{ color: #d4a574; font-weight: bold; }}
            .field {{ background: #e3f2fd; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
            .tags {{ margin-top: 5px; }}
            .tag {{ background: #e8f5e9; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 5px; }}
            .links {{ margin-top: 10px; }}
            .links a {{ color: #1e3a5f; margin-right: 15px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📚 Econe Papers 每日精选</h1>
            <p>{date_display} 共有 {len(papers)} 篇经济学论文</p>
        </div>
        
        <h2>论文列表</h2>
    """
    
    # 按评分排序
    papers_sorted = sorted(papers, key=lambda x: x.get('scores', {}).get('overall', 0), reverse=True)
    
    for i, paper in enumerate(papers_sorted[:15], 1):
        score = paper.get('scores', {}).get('overall', 0)
        title = paper.get('chineseTitle') or paper.get('title', 'Untitled')
        abstract = paper.get('chineseAbstract') or paper.get('abstract', '')[:200]
        field = paper.get('researchField', '其他')
        authors = ', '.join(paper.get('authors', [])[:3])
        
        # Tags
        tags = paper.get('tags', [])
        tags_html = ''.join([f'<span class="tag">{t}</span>' for t in tags[:3]])
        
        # Links
        paper_id = paper.get('id', '').replace('http://arxiv.org/abs/', '')
        arxiv_link = f"https://arxiv.org/abs/{paper_id}"
        pdf_link = paper.get('pdfUrl', '')
        
        html += f"""
        <div class="paper">
            <h3>{i}. {title}</h3>
            <p><span class="score">★ {score:.1f}</span> <span class="field">{field}</span></p>
            <p><small>{authors}</small></p>
            <p>{abstract}...</p>
            <div class="tags">{tags_html}</div>
            <div class="links">
                <a href="{arxiv_link}" target="_blank">📄 arXiv原文</a>
                <a href="{pdf_link}" target="_blank">📥 PDF下载</a>
            </div>
        </div>
        """
    
    if len(papers) > 15:
        html += f"<p><em>...还有 {len(papers) - 15} 篇论文</em></p>"
    
    html += f"""
        <div class="footer">
            <p>📌 查看完整论文列表: <a href="{web_url}" target="_blank">{web_url}</a></p>
            <p>Powered by AI | 每日自动抓取 + AI 筛选</p>
        </div>
    </body>
    </html>
    """
    
    return html


def send_email(to_email, subject, html_content):
    """发送邮件"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️ SMTP未配置，跳过发送邮件")
        print("   请设置环境变量: SMTP_USER, SMTP_PASSWORD")
        return False
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"✅ 邮件已发送到 {to_email}")
        return True
    except Exception as e:
        print(f"⚠️ 邮件发送失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="发送每日论文邮件")
    parser.add_argument("--date", type=str, default=None, help="指定日期 (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="仅显示内容，不发送邮件")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        # 默认昨天的论文
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
    
    print(f"📧 生成 {date_str} 的每日论文...")
    
    # 加载数据
    data = load_papers()
    papers = get_papers_for_date(data, date_str)
    
    if not papers:
        print(f"⚠️ 没有找到 {date_str} 的论文")
        return
    
    print(f"   找到 {len(papers)} 篇论文")
    
    # 生成邮件
    html_content = generate_email_content(papers, date_str, WEB_URL)
    
    if args.dry_run:
        # 保存到文件
        with open('/tmp/daily_papers.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"📝 已保存到 /tmp/daily_papers.html")
        return
    
    # 发送邮件
    date_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")
    subject = f"📚 Econe Papers - {date_display} 精选 {len(papers)} 篇"
    
    send_email(TO_EMAIL, subject, html_content)


if __name__ == "__main__":
    main()
