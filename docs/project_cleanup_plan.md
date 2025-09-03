# 프로젝트 정리 및 Git 업로드 계획

## 📋 **현재 상태 분석**

### ✅ **보관할 핵심 파일들**
```
src/                          # MCP 서버 핵심 코드
├── hrfco_service/
│   ├── __init__.py
│   ├── api.py               # HRFCO API 클라이언트
│   ├── server.py            # MCP 서버
│   ├── wamis_api.py         # WAMIS API 클라이언트
│   ├── ontology_manager.py  # 통합 온톨로지
│   └── ...

mcp_server.py                 # MCP 서버 메인 파일
chatgpt_functions.py          # ChatGPT Function Calling
gpt_actions_proxy.py          # GPT Actions 프록시 서버

requirements.txt              # 의존성
pyproject.toml               # 프로젝트 설정
README.md                    # 메인 문서
USER_GUIDE.md               # 사용자 가이드
```

### 🗂️ **정리할 문서들**
```
docs/                        # 모든 문서를 여기로 이동
├── setup/                   # 설정 가이드
│   ├── chatgpt-setup.md
│   ├── gpt-actions-setup.md
│   └── linux-deployment.md
├── api/                     # API 문서
│   ├── wamis-api-spec.md
│   └── hrfco-api-guide.md
└── examples/                # 사용 예시
    ├── chatgpt-examples.py
    └── proxy-examples.py
```

### 🗑️ **삭제할 임시 파일들**
```
ngrok.exe                    # 바이너리 파일
test_*.py                    # 개발용 테스트 파일
*backup*                     # 백업 파일
run-*.ps1/sh                 # 임시 실행 스크립트
```

## 🚀 **정리 실행 계획**

### 1단계: 문서 정리 및 디렉토리 구조화
### 2단계: 테스트 파일 및 임시 파일 정리
### 3단계: 최종 README 및 설정 파일 업데이트
### 4단계: Git 커밋 및 정리 