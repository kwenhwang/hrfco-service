#!/bin/bash

# HRFCO Service 로컬 테스트 스크립트
set -e

echo "🚀 HRFCO Service 로컬 테스트 시작"

# 환경 변수 확인
if [ -z "$HRFCO_API_KEY" ]; then
    echo "❌ HRFCO_API_KEY 환경 변수가 설정되지 않았습니다."
    echo "다음 명령어로 설정하세요:"
    echo "export HRFCO_API_KEY='your-api-key'"
    exit 1
fi

echo "✅ API 키 확인 완료"

# Python 의존성 설치
echo "📦 Python 의존성 설치 중..."
pip install -r requirements.txt

# 테스트 실행
echo "🧪 테스트 실행 중..."
pytest tests/ -v

# 서버 실행
echo "🌐 서버 시작 중..."
echo "서버가 http://localhost:8000 에서 실행됩니다."
echo "Ctrl+C로 서버를 중지할 수 있습니다."

python -m hrfco_service 