#!/usr/bin/env python3
"""
GPT Actions용 HRFCO API 프록시 서버 실행 스크립트 (테스트용 HTTP 버전)
"""

import uvicorn
from gpt_actions_proxy import app

if __name__ == "__main__":
    print("🚀 HRFCO API Proxy 서버 시작 (테스트용 HTTP)")
    print("📍 GPT Actions 테스트용 서버입니다")
    print("🌐 접속 URL: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 