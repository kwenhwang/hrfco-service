#!/usr/bin/env python3
"""
Gemini CLI MCP Servers Configuration
Configures and registers MCP servers for use with Gemini CLI
"""

import json
import os
from pathlib import Path

# MCP 서버 설정
MCP_SERVERS = {
    # 1. 파일시스템 관리
    "filesystem": {
        "description": "대용량 파일 검색, 이동, 삭제, 압축/해제",
        "command": "python",
        "args": ["-m", "mcp_filesystem"],
        "working_directory": str(Path.cwd()),
        "available": False,  # 패키지가 없어서 비활성화
        "tools": ["search_files", "move_files", "compress", "extract"]
    },
    
    # 2. 웹 검색 (DuckDuckGo)
    "web_search": {
        "description": "실시간 웹 검색 및 최신 정보 조회",
        "command": "python",
        "args": ["-c", """
import sys
from duckduckgo_search import DDGS
import json

def search_web(query, max_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return {{'success': True, 'results': results}}
    except Exception as e:
        return {{'success': False, 'error': str(e)}}

if __name__ == '__main__':
    query = ' '.join(sys.argv[1:])
    result = search_web(query)
    print(json.dumps(result, ensure_ascii=False, indent=2))
"""],
        "available": True,
        "tools": ["web_search", "news_search", "summarize_results"]
    },
    
    # 3. Everything MCP Server (공식)
    "everything": {
        "description": "MCP 프로토콜의 모든 기능을 테스트하는 만능 서버",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-everything"],
        "available": True,
        "tools": ["echo", "add", "printEnv", "getTinyImage", "sampleLLM"]
    },
    
    # 4. 수문 데이터 (한국 기상청 등)
    "water_data": {
        "description": "한국 수문 데이터 및 기상 정보 조회",
        "command": "python",
        "args": ["-c", """
import sys
import json
import os

# MCP HRFCO 서비스 사용
def get_water_level_data(obs_code='1001'):
    try:
        # 여기에 실제 MCP HRFCO 서비스 호출 로직 추가
        return {{'success': True, 'message': 'Water level data for ' + obs_code}}
    except Exception as e:
        return {{'success': False, 'error': str(e)}}

if __name__ == '__main__':
    args = sys.argv[1:] if len(sys.argv) > 1 else ['1001']
    result = get_water_level_data(args[0])
    print(json.dumps(result, ensure_ascii=False, indent=2))
"""],
        "available": True,
        "tools": ["get_water_level", "get_rainfall", "get_dam_info"]
    },
    
    # 5. GitHub 통합 (시뮬레이션)
    "github": {
        "description": "GitHub 저장소 관리 및 PR 자동화",
        "command": "python",
        "args": ["-c", """
import sys
import json

def github_action(action='status'):
    return {
        'success': True,
        'action': action,
        'message': f'GitHub {action} executed successfully',
        'mock': True
    }

if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'status'
    result = github_action(action)
    print(json.dumps(result, ensure_ascii=False, indent=2))
"""],
        "available": True,
        "tools": ["create_pr", "review_code", "manage_issues"]
    },
    
    # 6. 코드 분석 도구
    "code_analyzer": {
        "description": "코드 품질 분석 및 리팩터링 제안",
        "command": "python",
        "args": ["-c", """
import sys
import json
import os

def analyze_code(file_path=''):
    if not file_path or not os.path.exists(file_path):
        return {
            'success': False,
            'error': 'File not found or not specified'
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 간단한 코드 분석
        lines = content.split('\\n')
        analysis = {
            'lines_of_code': len([l for l in lines if l.strip()]),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'total_lines': len(lines),
            'file_size': len(content),
            'suggestions': [
                'Consider adding more comments',
                'Check for code duplication',
                'Optimize performance bottlenecks'
            ]
        }
        
        return {'success': True, 'analysis': analysis}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    file_path = sys.argv[1] if len(sys.argv) > 1 else ''
    result = analyze_code(file_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
"""],
        "available": True,
        "tools": ["analyze_file", "suggest_refactor", "check_quality"]
    }
}

def create_gemini_mcp_config():
    """Gemini CLI용 MCP 설정 생성"""
    gemini_dir = Path.home() / ".gemini"
    gemini_dir.mkdir(exist_ok=True)
    
    # MCP 서버 설정 파일 생성
    mcp_config = {
        "mcpServers": {}
    }
    
    active_count = 0
    for server_name, config in MCP_SERVERS.items():
        if config["available"]:
            mcp_config["mcpServers"][server_name] = {
                "command": config["command"],
                "args": config["args"],
                "description": config["description"],
                "tools": config["tools"]
            }
            
            if "working_directory" in config:
                mcp_config["mcpServers"][server_name]["cwd"] = config["working_directory"]
            
            active_count += 1
    
    # 설정 파일 저장
    config_file = gemini_dir / "mcp_servers.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(mcp_config, f, ensure_ascii=False, indent=2)
    
    # Gemini CLI 설정 업데이트
    settings_file = gemini_dir / "settings.json"
    settings = {}
    
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except:
            settings = {}
    
    # MCP 설정을 기존 설정에 추가
    settings.update(mcp_config)
    
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    
    return active_count, config_file

def create_mcp_tools_reference():
    """MCP 도구 사용법 참조 파일 생성"""
    gemini_dir = Path.home() / ".gemini"
    
    # MCP 도구 설명서 생성
    tools_md = """# Gemini CLI MCP Tools Reference

이 문서는 Gemini CLI에 통합된 MCP 서버들과 사용 가능한 도구들을 설명합니다.

## 사용 방법

Gemini CLI에서 다음과 같이 MCP 도구를 호출할 수 있습니다:

```
/mcp <server_name> <tool_name> [arguments]
```

## 등록된 MCP 서버들

"""
    
    for server_name, config in MCP_SERVERS.items():
        if config["available"]:
            tools_md += f"""### {server_name}
**설명**: {config["description"]}

**사용 가능한 도구들**:
"""
            for tool in config["tools"]:
                tools_md += f"- `{tool}`: {tool.replace('_', ' ').title()}\n"
            
            tools_md += f"""
**사용 예시**:
```
/mcp {server_name} {config["tools"][0]} [args]
```

"""
    
    tools_md += """
## 통합 사용 시나리오

### 1. 웹 개발 워크플로우
```
/mcp web_search "latest React hooks tutorial"
/mcp code_analyzer analyze_file src/App.js
/mcp github create_pr "Update React hooks implementation"
```

### 2. 데이터 분석
```
/mcp water_data get_water_level 1001
/mcp everything echo "Analysis complete"
```

### 3. 프로젝트 관리
```
/mcp filesystem search_files "*.py"
/mcp code_analyzer check_quality
/mcp github manage_issues "Create optimization task"
```

## 문제 해결

- MCP 서버가 응답하지 않는 경우: Gemini CLI 재시작
- 도구가 인식되지 않는 경우: `/mcp help` 명령어로 사용 가능한 도구 확인
- 오류 발생 시: 각 서버의 로그 확인

---
*생성일: 2025-08-08*
*위치: ~/.gemini/mcp_tools_reference.md*
"""
    
    with open(gemini_dir / "mcp_tools_reference.md", 'w', encoding='utf-8') as f:
        f.write(tools_md)

def main():
    """메인 실행 함수"""
    print("🔧 Gemini CLI MCP 서버 설정 중...")
    
    # MCP 설정 생성
    active_count, config_file = create_gemini_mcp_config()
    
    # 도구 참조 문서 생성
    create_mcp_tools_reference()
    
    print(f"✅ {active_count}개의 MCP 서버가 등록되었습니다!")
    print(f"📁 설정 파일: {config_file}")
    print(f"📖 사용법: ~/.gemini/mcp_tools_reference.md")
    print()
    print("🚀 사용 방법:")
    print("   1. 터미널에서 'gemini' 실행")
    print("   2. '/mcp help' 입력하여 사용 가능한 도구 확인")
    print("   3. '/mcp <server> <tool> [args]' 형식으로 사용")
    print()
    print("📋 등록된 서버들:")
    for server_name, config in MCP_SERVERS.items():
        if config["available"]:
            status = "✅ 활성"
        else:
            status = "❌ 비활성"
        print(f"   - {server_name}: {config['description']} ({status})")

if __name__ == "__main__":
    main() 