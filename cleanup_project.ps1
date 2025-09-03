#!/usr/bin/env pwsh
# 프로젝트 정리 스크립트
# 개발 중인 파일들을 체계적으로 정리하여 Git 업로드 준비

Write-Host "🚀 HRFCO 서비스 프로젝트 정리 시작..." -ForegroundColor Green
Write-Host "=" * 50

# 1. 디렉토리 구조 생성
Write-Host "📁 디렉토리 구조 생성..." -ForegroundColor Yellow

$directories = @(
    "docs\setup",
    "docs\api", 
    "docs\examples",
    "tools",
    "temp"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ 생성: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "  → 존재: $dir" -ForegroundColor Gray
    }
}

# 2. 문서 파일 정리
Write-Host "`n📚 문서 파일 정리..." -ForegroundColor Yellow

$docMoves = @{
    # 설정 가이드
    "CHATGPT_SETUP.md"              = "docs\setup\chatgpt-setup.md"
    "GPT_ACTIONS_SOLUTION.md"       = "docs\setup\gpt-actions-setup.md"
    "deploy_to_linux_guide.md"      = "docs\setup\linux-deployment.md"
    "cloudflare_tunnel_setup.md"    = "docs\setup\cloudflare-tunnel.md"
    "ngrok_setup.md"                = "docs\setup\ngrok-tunnel.md"
    "free_hosting_alternatives.md"  = "docs\setup\hosting-alternatives.md"
    
    # API 문서
    "WAMIS_API_SPEC.md"             = "docs\api\wamis-api-spec.md"
    "WAMIS_COMPLETE_API_SPEC.md"    = "docs\api\wamis-complete-spec.md"
    "기상청_홍수통제소_WAMIS_제원정보_통합.md"    = "docs\api\integrated-apis-guide.md"
    
    # 예시 파일
    "chatgpt_functions.py"          = "docs\examples\chatgpt-functions.py"
    "chatgpt_usage_example.py"      = "docs\examples\chatgpt-usage.py"
    "chatgpt_real_example.py"       = "docs\examples\chatgpt-real-demo.py"
    "test_chatgpt_functions.py"     = "docs\examples\test-chatgpt-functions.py"
    "gpt_actions_proxy_schema.json" = "docs\examples\gpt-actions-schema.json"
    "gpt_actions_schema.json"       = "docs\examples\hrfco-direct-schema.json"
}

foreach ($source in $docMoves.Keys) {
    $destination = $docMoves[$source]
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $destination -Force
        Write-Host "  ✓ 이동: $source → $destination" -ForegroundColor Green
    }
}

# 3. 도구 파일 정리
Write-Host "`n🔧 도구 파일 정리..." -ForegroundColor Yellow

$toolMoves = @{
    "run_proxy_server.py"        = "tools\run-proxy-server.py"
    "setup_api_keys.py"          = "tools\setup-api-keys.py"
    "test_wamis_complete_api.py" = "tools\test-wamis-api.py"
    "project_cleanup_plan.md"    = "docs\project-cleanup-plan.md"
    "CLEANUP_SUMMARY.md"         = "docs\cleanup-summary.md"
}

foreach ($source in $toolMoves.Keys) {
    $destination = $toolMoves[$source]
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $destination -Force
        Write-Host "  ✓ 이동: $source → $destination" -ForegroundColor Green
    }
}

# 4. 임시/테스트 파일 정리
Write-Host "`n🗑️ 임시 파일 정리..." -ForegroundColor Yellow

# 삭제할 파일들
$filesToDelete = @(
    "ngrok.exe",
    "test_*.py",
    "*backup*",
    "run-*.ps1",
    "run-*.sh",
    "test-*.py",
    "analyze-*.py",
    "water_level_analysis.html"
)

foreach ($pattern in $filesToDelete) {
    $files = Get-ChildItem -Path . -Name $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        if (Test-Path $file) {
            Remove-Item -Path $file -Force
            Write-Host "  ✓ 삭제: $file" -ForegroundColor Red
        }
    }
}

# 삭제된 파일들을 temp로 이동 (복구 가능하도록)
$tempFiles = @(
    "API_KEY_SETUP.md",
    "CLAUDE_MCP_SETUP.md", 
    "CURSOR_SETUP.md",
    "ENV_SETUP.md",
    "GITHUB_SECRETS_SETUP.md",
    "GLAMA_SETUP.md"
)

foreach ($file in $tempFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "temp\" -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ 임시 이동: $file → temp\" -ForegroundColor Yellow
    }
}

# 5. .gitignore 업데이트
Write-Host "`n📝 .gitignore 업데이트..." -ForegroundColor Yellow

$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
temp/
*.exe
*.zip
*.tar.gz
logs/
*.log

# Test files (keep in repo but ignore locally generated ones)
test_output/
coverage/
.pytest_cache/
.coverage

# Backup files
*backup*
*_backup.*
*.bak
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent -Encoding UTF8
Write-Host "  ✓ .gitignore 업데이트 완료" -ForegroundColor Green

# 6. README.md 업데이트
Write-Host "`n📖 README.md 업데이트..." -ForegroundColor Yellow

$readmeContent = @"
# HRFCO Service - 홍수통제소 API 통합 서비스

한국수자원공사 홍수통제소(HRFCO) API와 WAMIS API를 통합하여 실시간 수문 정보를 제공하는 MCP(Model Context Protocol) 서버입니다.

## 🌟 주요 기능

- **MCP 서버**: Claude/Cursor에서 직접 사용 가능한 수문 데이터 조회
- **ChatGPT Function Calling**: ChatGPT에서 자연어로 수문 정보 조회
- **GPT Actions 프록시**: HTTPS 프록시 서버로 GPT Actions 지원
- **통합 온톨로지**: HRFCO, WAMIS, 기상청 API 통합 관리
- **실시간 분석**: 수위 위험도, 강우량 통계 자동 분석

## 📊 지원 데이터

- 🌊 **수위 데이터**: 전국 수위 관측소 실시간 수위 정보
- 🌧️ **강우량 데이터**: 강우량 관측소 실시간 강우 정보  
- 🏗️ **댐/보 데이터**: 댐 수위, 방류량 정보
- 🌡️ **기상 데이터**: 기상청 날씨 정보 (온도, 습도, 풍속)
- ⚠️ **위험도 분석**: 수위 기준별 위험도 평가 및 예측

## 🚀 빠른 시작

### MCP 서버 (Claude/Cursor)
```bash
# 의존성 설치
pip install -r requirements.txt

# MCP 서버 실행
python mcp_server.py
```

### GPT Actions 프록시
```bash
# 프록시 서버 실행
python gpt_actions_proxy.py

# 또는 도구 사용
python tools/run-proxy-server.py
```

## 📚 문서

- **설정 가이드**: `docs/setup/`
  - [ChatGPT 설정](docs/setup/chatgpt-setup.md)
  - [GPT Actions 설정](docs/setup/gpt-actions-setup.md)
  - [Linux 배포](docs/setup/linux-deployment.md)
  - [HTTPS 터널링](docs/setup/hosting-alternatives.md)

- **API 문서**: `docs/api/`
  - [WAMIS API 명세](docs/api/wamis-api-spec.md)
  - [통합 API 가이드](docs/api/integrated-apis-guide.md)

- **사용 예시**: `docs/examples/`
  - [ChatGPT Function Calling](docs/examples/chatgpt-functions.py)
  - [실제 사용 데모](docs/examples/chatgpt-real-demo.py)

## 🛠️ 개발

### 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 개발 의존성 설치
pip install -r requirements.txt
```

### API 키 설정
```bash
# .env 파일 생성
HRFCO_API_KEY=your_hrfco_api_key
KMA_API_KEY=your_kma_api_key
```

## 📈 사용 예시

### Claude/Cursor에서
```
"하동군 대석교 수위가 위험한가요?"
"최근 48시간 강우량 추이를 분석해주세요"
"수계별 관측소 정보를 조회해주세요"
```

### ChatGPT에서
```python
# Function Calling으로 자동 호출
"진주 지역 날씨와 수위 상황을 종합해서 알려주세요"
"하동군 주변 관측소들의 실시간 데이터를 비교 분석해주세요"
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 감사의 말

- 한국수자원공사 홍수통제소 API
- 국가수자원관리종합정보시스템(WAMIS) API
- 기상청 날씨 API
"@

Set-Content -Path "README.md" -Value $readmeContent -Encoding UTF8
Write-Host "  ✓ README.md 업데이트 완료" -ForegroundColor Green

# 7. 최종 상태 확인
Write-Host "`n📋 정리 완료 상태:" -ForegroundColor Yellow
Write-Host "  📁 docs/setup/ - 설정 가이드 $(Get-ChildItem docs\setup\*.md | Measure-Object | Select-Object -ExpandProperty Count)개"
Write-Host "  📁 docs/api/ - API 문서 $(Get-ChildItem docs\api\*.md | Measure-Object | Select-Object -ExpandProperty Count)개"
Write-Host "  📁 docs/examples/ - 예시 파일 $(Get-ChildItem docs\examples\* | Measure-Object | Select-Object -ExpandProperty Count)개"
Write-Host "  📁 tools/ - 도구 스크립트 $(Get-ChildItem tools\* | Measure-Object | Select-Object -ExpandProperty Count)개"

# 8. Git 상태 확인
Write-Host "`n📊 Git 상태 확인..." -ForegroundColor Yellow
git status --porcelain | ForEach-Object {
    if ($_ -match '^\?\?\s+(.+)$') {
        Write-Host "  + 새파일: $($Matches[1])" -ForegroundColor Green
    }
    elseif ($_ -match '^M\s+(.+)$') {
        Write-Host "  ~ 수정: $($Matches[1])" -ForegroundColor Yellow
    }
    elseif ($_ -match '^D\s+(.+)$') {
        Write-Host "  - 삭제: $($Matches[1])" -ForegroundColor Red
    }
}

Write-Host "`n✅ 프로젝트 정리 완료!" -ForegroundColor Green
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "  1. git add ." -ForegroundColor White
Write-Host "  2. git commit -m 'feat: 프로젝트 구조 정리 및 문서 체계화'" -ForegroundColor White
Write-Host "  3. git push origin main" -ForegroundColor White 