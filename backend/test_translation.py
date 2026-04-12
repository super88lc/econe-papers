#!/usr/bin/env python3
"""测试翻译功能"""

import json
import os
import re
import requests

# 加载 API Key
def load_minimax_key():
    # 先检查环境变量
    key = os.getenv("MINIMAX_API_KEY", "")
    if key:
        return key
    
    # 尝试读取 ~/.zshrc
    try:
        zshrc_path = os.path.expanduser("~/.zshrc")
        if os.path.exists(zshrc_path):
            with open(zshrc_path, 'r') as f:
                for line in f:
                    if 'MINIMAX_API_KEY' in line and 'export' in line:
                        match = re.search(r'export\s+MINIMAX_API_KEY=["\']?([^"\'\n]+)', line)
                        if match:
                            return match.group(1)
    except Exception as e:
        print(f"读取 .zshrc 失败: {e}")
    
    return ""

MINIMAX_API_KEY = load_minimax_key()
print(f"API Key: {MINIMAX_API_KEY[:20]}..." if MINIMAX_API_KEY else "未找到 API Key")

# 测试翻译
def test_translate():
    if not MINIMAX_API_KEY:
        print("❌ 没有 API Key，无法测试")
        return
    
    test_abstract = """This paper examines the impact of remote work on regional development 
    in the European Union. Using a large-scale survey of over 7,400 remote workers, 
    we analyze the spatial direction of relocations and find that urban-to-urban moves 
    account for 67% of all relocations."""
    
    prompt = f"""请将以下英文学术论文摘要翻译成中文（200-300字，保持学术风格，保留专业术语）：

英文摘要：
{test_abstract}

请只返回中文翻译，不要有其他内容："""
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "MiniMax-Text-01",
        "messages": [
            {"role": "system", "content": "你是专业的学术翻译助手，擅长将经济学论文翻译成准确流畅的中文。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://api.minimaxi.com/v1/text/chatcompletion_v2",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"\n📥 API 响应结构：")
        print(f"{json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
        
        # 检查响应结构
        if "choices" in result and len(result["choices"]) > 0:
            translation = result["choices"][0]["message"]["content"]
            print("\n✅ 翻译成功！")
            print(f"\n原文：{test_abstract[:100]}...")
            print(f"\n中文翻译：\n{translation}")
        else:
            print(f"\n⚠️ 意外的响应结构: {result.keys()}")
        
    except Exception as e:
        print(f"\n❌ 翻译失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_translate()
