#!/usr/bin/env python3
"""
신규 프로젝트용 AI-Lab 문서 연결 스크립트
Cursor AI가 각 프로젝트에서 ai-lab 문서를 참조할 수 있도록 설정
"""

import os
import shutil
import json
from pathlib import Path
import argparse

def create_project_with_ailab_docs(project_path, project_name, project_type="web"):
    """
    신규 프로젝트에 ai-lab 문서들을 연결/복사하여 설정
    """
    project_dir = Path(project_path)
    ai_lab_dir = Path(__file__).parent  # ai-lab 디렉토리
    
    # 프로젝트 디렉토리 생성
    project_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 프로젝트 '{project_name}' 생성 중...")
    print(f"📁 위치: {project_dir}")
    
    # .ailab 디렉토리 생성 (AI 참조용)
    ailab_ref_dir = project_dir / ".ailab"
    ailab_ref_dir.mkdir(exist_ok=True)
    
    # 필수 AI 문서들 복사
    essential_docs = [
        "README-Complete-Integration-Guide.md",
        "README-Gemini-SuperClaude-Usage-Guide.md", 
        "README-Final-MCP-Status.md",
        "README-Project-Setup-Guide.md"
    ]
    
    print("📚 AI 가이드 문서 복사 중...")
    for doc in essential_docs:
        src = ai_lab_dir / doc
        if src.exists():
            dst = ailab_ref_dir / doc
            shutil.copy2(src, dst)
            print(f"   ✅ {doc}")
    
    # 프로젝트별 AI 설정 파일 생성
    ai_config = {
        "project_name": project_name,
        "project_type": project_type,
        "ai_lab_path": str(ai_lab_dir.absolute()),
        "mcp_servers": {
            "available": 13,
            "cursor_configured": True,
            "gemini_configured": True
        },
        "super_claude": {
            "commands": [
                "/sc analyze", "/sc design", "/sc task", 
                "/sc build", "/sc cleanup", "/sc troubleshoot"
            ],
            "workflow": "analyze → design → task → build → cleanup"
        },
        "quick_start": {
            "cursor": f"Cursor에서 '{project_name}' 폴더를 열고 채팅에서 자연어로 요청",
            "terminal": f"cd {project_path} && gemini-claude -p '프로젝트 요청'"
        }
    }
    
    # AI 설정 파일 저장
    with open(ailab_ref_dir / "ai-config.json", 'w', encoding='utf-8') as f:
        json.dump(ai_config, f, ensure_ascii=False, indent=2)
    
    # 프로젝트별 README 생성
    project_readme = f"""# 🚀 {project_name}

## 프로젝트 정보
- **타입**: {project_type}
- **생성일**: {Path(__file__).stat().st_mtime}
- **AI 지원**: Gemini CLI + Super Claude + 13개 MCP 서버

## 🤖 AI 도구 사용법

### Cursor IDE에서 (권장)
```
"이 프로젝트를 분석해줘"     → /sc analyze 실행
"컴포넌트 설계해줘"         → /sc design 실행  
"작업을 나눠줘"            → /sc task 실행
"코드를 구현해줘"          → /sc build 실행
"코드를 정리해줘"          → /sc cleanup 실행
```

### 터미널에서
```bash
# 어디서든 사용 가능
gemini-claude -p "React 컴포넌트 만들어줘"
gemini-enhanced --interactive
```

## 📚 AI 가이드 문서

이 프로젝트는 다음 AI 가이드들을 참조합니다:

- **[완전 통합 가이드](.ailab/README-Complete-Integration-Guide.md)** - 전체 AI 환경 개요
- **[Super Claude 사용법](.ailab/README-Gemini-SuperClaude-Usage-Guide.md)** - 상세 사용법
- **[MCP 서버 현황](.ailab/README-Final-MCP-Status.md)** - 13개 서버 목록
- **[프로젝트 설정](.ailab/README-Project-Setup-Guide.md)** - 신규 프로젝트 가이드

## 🎯 권장 개발 워크플로우

### 1. 프로젝트 분석
```
"이 {project_type} 프로젝트의 요구사항을 분석해줘"
```

### 2. 아키텍처 설계  
```
"컴포넌트 구조와 폴더 구조를 설계해줘"
```

### 3. 작업 분할
```
"개발 작업을 단계별로 나눠줘"
```

### 4. 개발 진행
```
"[구체적인 기능] 구현해줘"
```

### 5. 품질 관리
```
"코드를 정리하고 리팩터링해줘"
"Git 상태를 확인해줘"
"테스트를 작성해줘"
```

## 📁 디렉토리 구조

```
{project_name}/
├── .ailab/                    # AI 참조 문서들
│   ├── README-*.md           # AI 가이드 문서
│   └── ai-config.json        # AI 설정
├── src/                      # 소스 코드
├── package.json              # 의존성 (Node.js)
└── README.md                 # 이 파일
```

## 🛠️ MCP 서버 활용

이 프로젝트에서 사용 가능한 13개 MCP 서버:

1. **hrfco-service** - 한국 수문 데이터
2. **everything** - MCP 테스트
3. **duckduckgo** - 웹 검색  
4. **fs** - 파일시스템 관리
5. **deepl** - 번역
6. **github** - Git 관리
7. **playwright** - E2E 테스트
8. **terraform** - 인프라
9. **grafana** - 모니터링
10. **supabase** - 데이터베이스
11. **serena** - 리팩터링
12. **file_analyzer** - 파일 분석
13. **superclaude_wrapper** - 하이브리드 AI

---

*AI 환경: {str(ai_lab_dir.absolute())}*  
*Cursor AI가 .ailab/ 폴더의 문서들을 참조하여 개발을 도와줍니다.*
"""
    
    # 프로젝트 README 저장
    with open(project_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(project_readme)
    
    # .gitignore 생성 (선택적)
    gitignore_content = """# AI Lab 참조 문서는 추적하지 않음 (선택사항)
# .ailab/

# 일반적인 무시 파일들
node_modules/
venv/
__pycache__/
.env
*.log
"""
    
    with open(project_dir / ".gitignore", 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    # 프로젝트 타입별 초기 파일 생성
    if project_type == "react":
        create_react_starter(project_dir)
    elif project_type == "python":
        create_python_starter(project_dir)
    elif project_type == "node":
        create_node_starter(project_dir)
    
    print(f"\n🎉 프로젝트 '{project_name}' 생성 완료!")
    print(f"📁 위치: {project_dir}")
    print(f"🤖 AI 문서: {ailab_ref_dir}")
    print("\n🚀 다음 단계:")
    print(f"   1. cd {project_path}")
    print(f"   2. Cursor에서 폴더 열기")
    print(f"   3. 채팅에서: '이 {project_type} 프로젝트를 분석해줘'")
    
    return project_dir

def create_react_starter(project_dir):
    """React 프로젝트 초기 파일들 생성"""
    package_json = {
        "name": project_dir.name,
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0"
        },
        "devDependencies": {
            "@vitejs/plugin-react": "^4.0.0",
            "vite": "^4.0.0"
        }
    }
    
    with open(project_dir / "package.json", 'w', encoding='utf-8') as f:
        json.dump(package_json, f, indent=2)

def create_python_starter(project_dir):
    """Python 프로젝트 초기 파일들 생성"""
    requirements = """# Python dependencies
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
"""
    
    with open(project_dir / "requirements.txt", 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    main_py = """#!/usr/bin/env python3
'''
AI 지원 Python 프로젝트
Cursor에서 "FastAPI 서버 구현해줘"와 같이 요청하세요.
'''

def main():
    print("🚀 AI 지원 Python 프로젝트 시작!")
    print("💡 Cursor에서 자연어로 개발 요청하세요.")

if __name__ == "__main__":
    main()
"""
    
    with open(project_dir / "main.py", 'w', encoding='utf-8') as f:
        f.write(main_py)

def create_node_starter(project_dir):
    """Node.js 프로젝트 초기 파일들 생성"""
    package_json = {
        "name": project_dir.name,
        "version": "1.0.0",
        "type": "module",
        "main": "index.js",
        "scripts": {
            "start": "node index.js",
            "dev": "node --watch index.js"
        },
        "dependencies": {
            "express": "^4.18.0"
        }
    }
    
    with open(project_dir / "package.json", 'w', encoding='utf-8') as f:
        json.dump(package_json, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='AI-Lab 지원 신규 프로젝트 생성')
    parser.add_argument('name', help='프로젝트 이름')
    parser.add_argument('--type', choices=['web', 'react', 'python', 'node'], 
                       default='web', help='프로젝트 타입')
    parser.add_argument('--path', help='프로젝트 경로 (기본: ../프로젝트명)')
    
    args = parser.parse_args()
    
    if args.path:
        project_path = args.path
    else:
        # ai-lab의 부모 디렉토리에 생성
        parent_dir = Path(__file__).parent.parent
        project_path = parent_dir / args.name
    
    create_project_with_ailab_docs(project_path, args.name, args.type)

if __name__ == "__main__":
    main() 