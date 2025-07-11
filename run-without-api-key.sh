#!/bin/bash
# 사용자용 실행 스크립트 - API 키 없이 HRFCO 데이터 사용

echo "🌊 HRFCO 수문 데이터 서비스 (API 키 없이 사용)"
echo "================================================"

# Docker가 설치되어 있는지 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    echo "Docker를 먼저 설치해주세요: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker 확인 완료"

# 이미지 다운로드
echo "📥 Docker 이미지 다운로드 중..."
docker pull kwenhwang/hrfco-service:latest

if [ $? -eq 0 ]; then
    echo "✅ 이미지 다운로드 완료"
else
    echo "❌ 이미지 다운로드 실패"
    echo "인터넷 연결을 확인해주세요."
    exit 1
fi

# 서버 실행
echo "🚀 서버 시작 중..."
echo "API 키 없이도 수문 데이터를 조회할 수 있습니다!"
echo ""
echo "사용 방법:"
echo "1. Glama: https://glama.ai/mcp/servers/@kwenhwang/hrfco-service"
echo "2. Claude Desktop: MCP 서버 설정 후 연결"
echo "3. HTTP API: http://localhost:8080"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."
echo "================================================"

# 서버 실행
docker run --rm -p 8080:8080 kwenhwang/hrfco-service:latest 