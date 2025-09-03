#!/usr/bin/env python3
"""
간단한 Gemini CLI MCP 설정 생성기
"""

import json
import os
from pathlib import Path

def create_simple_mcp_config():
    """간단한 MCP 설정 생성"""
    gemini_dir = Path.home() / ".gemini"
    gemini_dir.mkdir(exist_ok=True)
    
    # 간단한 MCP 서버 설정
    mcp_config = {
        "mcpServers": {
            "everything": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-everything"],
                "description": "MCP 프로토콜의 모든 기능을 테스트하는 만능 서버",
                "tools": ["echo", "add", "printEnv", "getTinyImage", "sampleLLM"]
            },
            "web_search": {
                "command": "python",
                "args": [
                    "-c", 
                    "import sys; from duckduckgo_search import DDGS; import json; ddgs = DDGS(); results = list(ddgs.text(' '.join(sys.argv[1:]), max_results=5)); print(json.dumps({'results': results}, ensure_ascii=False))"
                ],
                "description": "DuckDuckGo 웹 검색",
                "tools": ["search"]
            },
            "file_analyzer": {
                "command": "python", 
                "args": [
                    "-c",
                    "import sys, json, os; fp=sys.argv[1] if len(sys.argv)>1 else ''; result={'exists': os.path.exists(fp), 'size': os.path.getsize(fp) if os.path.exists(fp) else 0}; print(json.dumps(result))"
                ],
                "description": "파일 분석 도구",
                "tools": ["analyze"]
            }
        }
    }
    
    # 설정 파일 저장
    config_file = gemini_dir / "mcp_servers.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(mcp_config, f, ensure_ascii=False, indent=2)
    
    # Gemini settings 업데이트
    settings_file = gemini_dir / "settings.json"
    settings = {}
    
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except:
            settings = {}
    
    settings.update(mcp_config)
    
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    
    # 사용법 문서 생성
    usage_md = """# Gemini CLI MCP 서버 사용법

## 등록된 MCP 서버들

### 1. everything
- **설명**: MCP 프로토콜의 모든 기능을 테스트하는 만능 서버
- **도구들**: echo, add, printEnv, getTinyImage, sampleLLM
- **사용 예시**: 
  ```
  /mcp everything echo "Hello World"
  /mcp everything add 5 3
  ```

### 2. web_search
- **설명**: DuckDuckGo 웹 검색
- **도구들**: search
- **사용 예시**:
  ```
  /mcp web_search search "Python tutorial"
  ```

### 3. file_analyzer
- **설명**: 파일 분석 도구  
- **도구들**: analyze
- **사용 예시**:
  ```
  /mcp file_analyzer analyze "C:/path/to/file.py"
  ```

## 일반적인 사용법

1. Gemini CLI 시작: `gemini`
2. MCP 도구 확인: `/mcp help`
3. 도구 사용: `/mcp <server> <tool> [arguments]`

---
*생성일: 2025-08-08*
"""
    
    with open(gemini_dir / "mcp_usage.md", 'w', encoding='utf-8') as f:
        f.write(usage_md)
    
    return config_file

def main():
    print("🔧 간단한 MCP 설정 생성 중...")
    config_file = create_simple_mcp_config()
    print(f"✅ MCP 설정이 생성되었습니다!")
    print(f"📁 설정 파일: {config_file}")
    print(f"📖 사용법: ~/.gemini/mcp_usage.md")
    print()
    print("🚀 테스트:")
    print("   gemini")
    print("   /mcp everything echo 'Hello MCP!'")

if __name__ == "__main__":
    main() 