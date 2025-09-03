# 🚀 신규 프로젝트 설정 가이드

## ❌ 매번 ai-lab 복사는 필요 없습니다!

`ai-lab` 디렉토리는 **한 번 설정된 AI 개발 환경**이므로, 신규 프로젝트마다 복사할 필요가 없습니다.

## 🎯 권장 프로젝트 구조

### 📁 디렉토리 구성
```
C:\Users\20172483\web\
├── ai-lab\                    # AI 환경 (한 번만 설정, 공용)
│   ├── gemini_claude_wrapper.py
│   ├── claude_integration.py
│   ├── venv\
│   └── README-*.md
│
├── project1\                  # 개별 프로젝트들
│   ├── src\
│   ├── package.json
│   └── README.md
│
├── project2\
├── project3\
└── ...
```

## 🛠️ 신규 프로젝트 시작 방법

### 🥇 방법 1: AI-Lab 프로젝트 생성기 사용 (가장 권장!)
```bash
# ai-lab 디렉토리에서
cd C:\Users\20172483\web\Mywater_webgame\ai-lab

# 간단한 배치 파일 사용
new-project.bat my-react-app react
new-project.bat my-python-api python  
new-project.bat my-node-server node
new-project.bat my-website web

# 또는 Python 스크립트 직접 사용
python create_project_template.py my-project --type react
```

**✅ 이 방법의 장점:**
- 📚 **AI 문서 자동 복사**: 프로젝트에 `.ailab/` 폴더로 모든 가이드 포함
- 🤖 **Cursor AI 최적화**: AI가 바로 프로젝트 컨텍스트 이해 가능
- 📋 **프로젝트별 README**: AI 사용법이 포함된 맞춤형 README 생성
- ⚙️ **초기 설정 완료**: 프로젝트 타입별 기본 파일들 자동 생성

### 방법 2: 수동 생성 후 Cursor IDE 사용
```bash
# 신규 프로젝트 폴더 생성
mkdir C:\Users\20172483\web\my-new-project
cd C:\Users\20172483\web\my-new-project

# Cursor에서 폴더 열기 후 채팅에서:
"React TypeScript 프로젝트를 초기화해줘"
```

### 방법 3: ai-lab에서 원격 작업
```bash
# ai-lab에서 다른 위치의 프로젝트 작업
cd C:\Users\20172483\web\ai-lab
gemini-claude -p "C:/Users/20172483/web/new-project에 Vue.js 앱 만들어줘"
```

## 🔧 환경 설정이 필요한 경우

### Python 가상환경이 필요한 프로젝트
```bash
# 프로젝트별 가상환경 생성
cd C:\Users\20172483\web\python-project
python -m venv venv
venv\Scripts\activate

# ai-lab의 패키지들 참조
pip install -r C:\Users\20172483\web\Mywater_webgame\ai-lab\requirements.txt
```

### Node.js 프로젝트
```bash
cd C:\Users\20172483\web\node-project
npm init -y

# 글로벌 설치된 도구들은 자동으로 사용 가능
gemini-claude -p "Express 서버 설정해줘"
```

## 🎯 Super Claude 사용법

### 어디서든 Super Claude 명령어 사용
```bash
# 임의의 프로젝트 디렉토리에서
cd C:\Users\20172483\web\any-project

# Gemini CLI에서 Super Claude 명령어 사용
gemini
> /sc analyze
> /sc design  
> /sc task
```

### Cursor에서 자연어로 Super Claude 활용
```
"이 프로젝트를 분석해줘" → /sc analyze 실행
"컴포넌트 설계해줘"     → /sc design 실행  
"작업을 나눠줘"        → /sc task 실행
"코드를 정리해줘"      → /sc cleanup 실행
```

## 📋 프로젝트별 권장 설정

### React/Vue/Angular 프로젝트
```bash
# 프로젝트 생성
npx create-react-app my-app
cd my-app

# AI 도구로 개발
gemini-claude -p "TypeScript와 Tailwind CSS 추가해줘"
```

### Python 프로젝트
```bash
# 프로젝트 디렉토리 생성
mkdir python-ai-project
cd python-ai-project

# 가상환경 생성 (선택사항)
python -m venv venv
venv\Scripts\activate

# AI 도구로 개발
gemini-claude -p "FastAPI 서버 만들어줘"
```

### 게임 개발 프로젝트
```bash
# Unity나 기타 게임 프로젝트 폴더에서
cd C:\Users\20172483\Unity\Projects\MyGame

# Cursor에서 또는 터미널에서
"Unity C# 스크립트 생성해줘"
"게임 로직 구현해줘"
```

## 🔄 권장 워크플로우

### 1. 프로젝트 시작
```bash
# 새 폴더 생성
mkdir C:\Users\20172483\web\awesome-project
cd C:\Users\20172483\web\awesome-project

# Cursor에서 폴더 열기
# 채팅에서: "React 타입스크립트 프로젝트 초기화해줘"
```

### 2. AI 도구 활용
```bash
# 분석 단계
"이 프로젝트의 요구사항을 분석해줘" → /sc analyze

# 설계 단계  
"컴포넌트 구조를 설계해줘" → /sc design

# 개발 단계
"할 일 목록 컴포넌트를 만들어줘" → /sc build
```

### 3. 품질 관리
```bash
# 정기적 정리
"코드를 정리해줘" → /sc cleanup

# 버전 관리
"Git 상태를 확인해줘" → github MCP

# 테스트
"컴포넌트 테스트 만들어줘" → playwright MCP
```

## 💡 효율성 팁

### ✅ 이렇게 하세요
- **Cursor IDE 적극 활용**: 13개 MCP 서버가 모두 등록되어 있음
- **프로젝트별 README 생성**: AI가 프로젝트 컨텍스트 이해하도록
- **일관된 폴더 구조**: `C:\Users\20172483\web\` 하위에 프로젝트들 관리
- **Git 저장소**: 각 프로젝트를 별도 Git 저장소로 관리

### ❌ 피해야 할 것들
- ai-lab 디렉토리 복사 (불필요함)
- 매번 새로운 가상환경 설정 (글로벌 도구 활용)
- 설정 파일 중복 (공용 설정 활용)

## 🚀 고급 활용법

### 프로젝트 템플릿 생성
```bash
# ai-lab에서 템플릿 생성 스크립트 만들기
cd C:\Users\20172483\web\ai-lab
gemini-claude -p "프로젝트 템플릿 생성 스크립트 만들어줘"
```

### 자동화 스크립트
```bash
# 신규 프로젝트 자동 초기화
cd C:\Users\20172483\web\ai-lab
gemini-claude -p "신규 프로젝트 자동 설정 스크립트 만들어줘"
```

### 팀 협업 설정
```bash
# 설정 파일들을 Git으로 공유
cd C:\Users\20172483\web\ai-lab
git init
git add *.py *.json *.md
git commit -m "AI development environment setup"
```

## 🎉 결론

**ai-lab은 한 번 설정된 AI 개발 환경**입니다. 

매번 복사할 필요 없이:
- **Cursor IDE**에서 자연어로 MCP 서버 활용
- **어디서든** `gemini-claude` 명령어 사용  
- **프로젝트별** 독립적인 폴더 구조 유지

이렇게 하면 **효율적이고 깔끔한** 개발 환경을 유지할 수 있습니다! 🚀

---

*가이드 작성일: 2025-08-08*  
*ai-lab 버전: v1.0*  
*권장 방법: Cursor IDE + MCP 서버 활용* 