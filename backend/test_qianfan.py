#!/usr/bin/env python3
"""测试百度千帆 API 翻译"""

import json
import os
import re
import requests

def load_qianfan_credentials():
    """从 ~/.zshrc 加载百度千帆 API 凭证"""
    credentials = {
        "QIANFAN_ACCESS_KEY": "",
        "QIANFAN_SECRET_KEY": ""
    }
    try:
        zshrc_path = os.path.expanduser("~/.zshrc")
        if os.path.exists(zshrc_path):
            with open(zshrc_path, 'r') as f:
                for line in f:
                    for key in credentials.keys():
                        if key in line and 'export' in line:
                            match = re.search(rf'export\s+{key}=["\']?([^"\'\n]+)', line)
                            if match:
                                credentials[key] = match.group(1)
    except Exception as e:
        print(f"读取 .zshrc 失败: {e}")
    return credentials

def get_qianfan_token(access_key, secret_key) -> str:
    """获取百度千帆 access token"""
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={access_key}&client_secret={secret_key}"
    
    try:
        response = requests.post(url, timeout=30)
        result = response.json()
        print(f"Token 响应: {json.dumps(result, indent=2)[:300]}")
        return result.get("access_token", "")
    except Exception as e:
        print(f"获取 token 失败: {e}")
        return ""

def translate_with_qianfan(access_token, text):
    """使用千帆 API 翻译"""
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-pro-128k?access_token={access_token}"
    
    prompt = f"""请将以下英文学术论文摘要翻译成中文（200-300字，保持学术风格，保留专业术语）：

英文摘要：
{text}

请只返回中文翻译，不要有其他内容："""
    
    payload = {
        "messages": [
            {"role": "system", "content": "你是专业的学术翻译助手，擅长将经济学论文翻译成准确流畅的中文。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        result = response.json()
        print(f"\nAPI 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
        return result.get("result", "")
    except Exception as e:
        print(f"翻译失败: {e}")
        return ""

if __name__ == "__main__":
    creds = load_qianfan_credentials()
    print(f"Access Key: {creds['QIANFAN_ACCESS_KEY'][:15]}..." if creds['QIANFAN_ACCESS_KEY'] else "未找到 Access Key")
    print(f"Secret Key: {creds['QIANFAN_SECRET_KEY'][:15]}..." if creds['QIANFAN_SECRET_KEY'] else "未找到 Secret Key")
    
    if not creds['QIANFAN_ACCESS_KEY'] or not creds['QIANFAN_SECRET_KEY']:
        print("❌ 未找到 API 凭证")
        exit(1)
    
    print("\n1. 获取 access token...")
    token = get_qianfan_token(creds['QIANFAN_ACCESS_KEY'], creds['QIANFAN_SECRET_KEY'])
    if not token:
        print("❌ 获取 token 失败")
        exit(1)
    print(f"✅ 获取 token 成功: {token[:20]}...")
    
    test_text = """This paper examines the impact of remote work on regional development 
    in the European Union. Using a large-scale survey of over 7,400 remote workers, 
    we analyze the spatial direction of relocations and find that urban-to-urban moves 
    account for 67% of all relocations."""
    
    print("\n2. 测试翻译...")
    translation = translate_with_qianfan(token, test_text)
    
    if translation:
        print(f"\n✅ 翻译成功！")
        print(f"\n中文翻译：\n{translation}")
    else:
        print("\n❌ 翻译失败")
