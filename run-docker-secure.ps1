#!/usr/bin/env powershell
# 도커에서 안전하게 API 키를 사용하는 스크립트

Write-Host "🔐 HRFCO 서비스 도커 실행 (보안 모드)" -ForegroundColor Green

# API 키 확인
$apiKey = $env:HRFCO_API_KEY
if (-not $apiKey) {
    Write-Host "❌ HRFCO_API_KEY 환경변수가 설정되지 않았습니다." -ForegroundColor Red
    Write-Host "다음 명령어로 설정해주세요:" -ForegroundColor Yellow
    Write-Host '$env:HRFCO_API_KEY="your-api-key-here"' -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ API 키가 설정되어 있습니다." -ForegroundColor Green

# 도커 이미지 빌드
Write-Host "🔨 도커 이미지 빌드 중..." -ForegroundColor Yellow
docker build --build-arg HRFCO_API_KEY=$apiKey -t hrfco-service .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 도커 빌드 실패" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 도커 이미지 빌드 완료" -ForegroundColor Green

# 도커 컨테이너 실행
Write-Host "🚀 도커 컨테이너 실행 중..." -ForegroundColor Yellow
docker run -d --name hrfco-service-container -p 8000:8000 hrfco-service

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 도커 컨테이너 실행 실패" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 도커 컨테이너 실행 완료" -ForegroundColor Green
Write-Host "📱 서비스가 http://localhost:8000 에서 실행 중입니다." -ForegroundColor Cyan

# 컨테이너 상태 확인
Write-Host "🔍 컨테이너 상태 확인 중..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
docker ps --filter "name=hrfco-service-container"

Write-Host "`n📋 유용한 명령어:" -ForegroundColor Cyan
Write-Host "  로그 확인: docker logs hrfco-service-container" -ForegroundColor White
Write-Host "  컨테이너 중지: docker stop hrfco-service-container" -ForegroundColor White
Write-Host "  컨테이너 삭제: docker rm hrfco-service-container" -ForegroundColor White 