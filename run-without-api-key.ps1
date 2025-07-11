# 사용자용 실행 스크립트 - API 키 없이 HRFCO 데이터 사용 (Windows)

Write-Host "🌊 HRFCO 수문 데이터 서비스 (API 키 없이 사용)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Docker가 설치되어 있는지 확인
try {
    docker --version | Out-Null
    Write-Host "✅ Docker 확인 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker가 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "Docker를 먼저 설치해주세요: https://docs.docker.com/get-docker/" -ForegroundColor Yellow
    exit 1
}

# 이미지 다운로드
Write-Host "📥 Docker 이미지 다운로드 중..." -ForegroundColor Yellow
docker pull kwenhwang/hrfco-service:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 이미지 다운로드 완료" -ForegroundColor Green
} else {
    Write-Host "❌ 이미지 다운로드 실패" -ForegroundColor Red
    Write-Host "인터넷 연결을 확인해주세요." -ForegroundColor Yellow
    exit 1
}

# 서버 실행
Write-Host "🚀 서버 시작 중..." -ForegroundColor Green
Write-Host "API 키 없이도 수문 데이터를 조회할 수 있습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "사용 방법:" -ForegroundColor Cyan
Write-Host "1. Glama: https://glama.ai/mcp/servers/@kwenhwang/hrfco-service" -ForegroundColor White
Write-Host "2. Claude Desktop: MCP 서버 설정 후 연결" -ForegroundColor White
Write-Host "3. HTTP API: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "서버를 중지하려면 Ctrl+C를 누르세요." -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Green

# 서버 실행
docker run --rm -p 8080:8080 kwenhwang/hrfco-service:latest 