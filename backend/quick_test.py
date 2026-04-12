#!/usr/bin/env python3
"""快速测试翻译功能"""
import os
import requests

BAIDU_API_KEY = "bce-v3/ALTAK-SOMoPE9hXPweaALotFw7A/383d6694a7f34c24a357828ec7f619d528b4afa4"
BAIDU_MODEL = "ernie-speed-128k"

def call_qianfan(prompt: str, temperature: float = 0.3) -> str:
    headers = {
        "Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": BAIDU_MODEL,
        "messages": [
            {"role": "system", "content": "你是专业的经济学学术助手，擅长论文分析、翻译和评分。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 2048
    }
    
    try:
        url = "https://qianfan.baidubce.com/v2/chat/completions"
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        result = response.json()
        
        if "error" in result:
            print(f"API 错误: {result.get('error')}")
            return ""
        
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"请求失败: {e}")
        return ""

# 测试翻译
print("📝 测试中文翻译...")
test_abstract = """This paper studies the distributional effects of monetary policy on income inequality. Using micro-level data from the Survey of Consumer Finances, we find that expansionary monetary policy increases income inequality in the short run, but reduces it in the long run. The mechanism works through asset price channels and labor market responses."""

prompt = f"""请将以下经济学论文摘要翻译成中文（200-300字），保持学术风格，保留专业术语：

{test_abstract}

只返回翻译结果，不要解释。"""

result = call_qianfan(prompt)
if result:
    print(f"\n✅ 翻译成功:\n{result}")
else:
    print("\n❌ 翻译失败")

# 测试评分
print("\n📊 测试评分系统...")
scoring_prompt = f"""请对以下论文进行多维度评分（每项1-5分，overall 1-10分），返回JSON格式：

标题: Monetary Policy and Inequality
摘要: {test_abstract}

返回格式：
{{
  "novelty": 分数,
  "methodology": 分数, 
  "empirical": 分数,
  "impact": 分数,
  "readability": 分数,
  "overall": 分数,
  "reasoning": "评分理由",
  "summary": "一句话总结"
}}"""

score_result = call_qianfan(scoring_prompt)
print(f"评分结果:\n{score_result}")
