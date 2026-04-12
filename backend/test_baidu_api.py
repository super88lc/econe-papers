#!/usr/bin/env python3
"""测试百度千帆 API 翻译"""

import json
import os
import requests

def load_baidu_api_key():
    """加载百度 API Key"""
    # 先检查环境变量
    key = os.getenv("BAIDU_API_KEY", "")
    if key:
        return key
    
    # 尝试读取 newsletter/.env
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

def test_translate():
    BAIDU_API_KEY = load_baidu_api_key()
    BAIDU_BASE_URL = "https://qianfan.baidubce.com/v2/coding"
    
    print(f"API Key: {BAIDU_API_KEY[:30]}..." if BAIDU_API_KEY else "未找到 API Key")
    
    if not BAIDU_API_KEY:
        print("❌ 未找到 API Key")
        return
    
    test_abstract = """This paper examines the impact of remote work on regional development in the European Union. Using a large-scale survey of over 7,400 remote workers, we analyze the spatial direction of relocations and find that urban-to-urban moves account for 67% of all relocations."""
    
    prompt = f"""请将以下英文学术论文摘要翻译成中文（200-300字，保持学术风格，保留专业术语）：

英文摘要：
{test_abstract}

请只返回中文翻译，不要有其他内容："""
    
    headers = {
        "Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qianfan-code-latest",
        "messages": [
            {"role": "system", "content": "你是专业的学术翻译助手，擅长将经济学论文翻译成准确流畅的中文。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        print("\n发送请求...")
        url = f"{BAIDU_BASE_URL}/chat/completions"
        print(f"URL: {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        print(f"状态码: {response.status_code}")
        
        result = response.json()
        print(f"\n响应: {json.dumps(result, indent=2, ensure_ascii=False)[:800]}")
        
        if "error" in result:
            print(f"\n❌ API 错误: {result.get('error')}")
            return
        
        translation = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if translation:
            print(f"\n✅ 翻译成功！")
            print(f"\n原文：\n{test_abstract}")
            print(f"\n中文翻译：\n{translation}")
        else:
            print("\n❌ 翻译结果为空")
        
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_translate()
