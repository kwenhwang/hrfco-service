# HRFCO Service 로컬 테스트 스크립트 (Windows PowerShell)
param(
    [string]$ApiKey = ""
)

Write-Host "🚀 HRFCO Service 로컬 테스트 시작" -ForegroundColor Green

# 환경 변수 확인
if ([string]::IsNullOrEmpty($env:HRFCO_API_KEY) -and [string]::IsNullOrEmpty($ApiKey)) {
    Write-Host "❌ HRFCO_API_KEY 환경 변수가 설정되지 않았습니다." -ForegroundColor Red
    Write-Host "다음 명령어로 설정하세요:" -ForegroundColor Yellow
    Write-Host '$env:HRFCO_API_KEY = "your-api-key"' -ForegroundColor Cyan
    Write-Host "또는 스크립트 실행 시 파라미터로 전달:" -ForegroundColor Cyan
    Write-Host ".\scripts\test-local.ps1 -ApiKey 'your-api-key'" -ForegroundColor Cyan
    exit 1
}

# API 키 설정
if (-not [string]::IsNullOrEmpty($ApiKey)) {
    $env:HRFCO_API_KEY = $ApiKey
}

Write-Host "✅ API 키 확인 완료" -ForegroundColor Green

# Python 의존성 설치
Write-Host "📦 Python 의존성 설치 중..." -ForegroundColor Yellow
pip install -r requirements.txt

# 테스트 실행
Write-Host "🧪 테스트 실행 중..." -ForegroundColor Yellow
pytest tests/ -v

# 서버 실행
Write-Host "🌐 서버 시작 중..." -ForegroundColor Green
Write-Host "서버가 http://localhost:8000 에서 실행됩니다." -ForegroundColor Cyan
Write-Host "Ctrl+C로 서버를 중지할 수 있습니다." -ForegroundColor Yellow

python -m hrfco_service 