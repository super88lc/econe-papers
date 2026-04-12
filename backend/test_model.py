#!/usr/bin/env python3
"""测试可用模型"""
import requests

BAIDU_API_KEY = "bce-v3/ALTAK-SOMoPE9hXPweaALotFw7A/383d6694a7f34c24a357828ec7f619d528b4afa4"

models = ["ernie-speed-128k", "ernie-4.0-turbo-8k", "ernie-lite", "ernie-tiny-8k"]

for model in models:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 100
    }
    headers = {
        "Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post("https://qianfan.baidubce.com/v2/chat/completions", 
                           headers=headers, json=payload, timeout=30)
        result = resp.json()
        if "error" in result:
            print(f"❌ {model}: {result['error'].get('message', 'Unknown')}")
        else:
            print(f"✅ {model}: OK")
    except Exception as e:
        print(f"❌ {model}: {e}")
