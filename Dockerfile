# -*- coding: utf-8 -*-
# HRFCO Service Dockerfile
FROM python:3.11-slim

# 개발자가 미리 설정한 API 키 (빌드 시 주입, 옵션)
ARG HRFCO_API_KEY=""
ENV HRFCO_API_KEY=$HRFCO_API_KEY

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# 포트 설정
EXPOSE 8000 8080

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# HTTP 서버 실행 (사용자가 API 키 없이 접근 가능)
CMD ["python", "src/hrfco_service/http_server.py"] 