#!/usr/bin/env python3
"""测试百度千帆 API"""
import os
import requests

def load_baidu_api_key():
    """加载百度 API Key"""
    key = os.getenv("BAIDU_API_KEY", "")
    if key:
        return key
    try:
        env_path = os.path.expanduser("~/.openclaw/workspace/newsletter/.env")
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('BAIDU_API_KEY='):
                        return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"读取 .env 失败: {e}")
    return ""

BAIDU_API_KEY = "bce-v3/ALTAK-SOMoPE9hXPweaALotFw7A/383d6694a7f34c24a357828ec7f619d528b4afa4"
print(f"API Key: {'*' * 20} (长度: {len(BAIDU_API_KEY)})")

# 测试翻译
headers = {
    "Authorization": f"Bearer {BAIDU_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "ernie-4.0-turbo-8k",
    "messages": [
        {"role": "system", "content": "你是专业的经济学学术助手，擅长论文翻译。"},
        {"role": "user", "content": "请将以下论文摘要翻译成中文（200-300字）：\n\nThis paper studies the impact of minimum wage policies on employment in the United States using a novel identification strategy based on county-level variations."}
    ],
    "temperature": 0.3,
    "max_tokens": 2048
}

print("\n正在测试 API 调用...")
try:
    response = requests.post(
        "https://qianfan.baidubce.com/v2/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    result = response.json()
    
    if "error" in result:
        print(f"❌ API 错误: {result.get('error')}")
    else:
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"✅ API 调用成功！")
        print(f"\n翻译结果:\n{content}")
except Exception as e:
    print(f"❌ 请求失败: {e}")
