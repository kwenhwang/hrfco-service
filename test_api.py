#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_server import HRFCOAPI

async def test_api():
    """API 테스트"""
    print("🚀 HRFCO API 테스트 시작...")
    
    # API 키 설정 (테스트용)
    os.environ["HRFCO_API_KEY"] = "test-api-key-for-testing"
    
    api = HRFCOAPI()
    
    # 1. 관측소 제원 정보 테스트
    print("\n📊 관측소 제원 정보 테스트 (waterlevel)...")
    try:
        result = await api.fetch_observatory_info("waterlevel")
        print("✅ 성공:", result)
    except Exception as e:
        print("❌ 실패:", str(e))
    
    # 2. 실시간 데이터 테스트
    print("\n📊 실시간 데이터 테스트 (waterlevel, 10M)...")
    try:
        result = await api.fetch_observatory_data("waterlevel", "10M")
        print("✅ 성공:", result)
    except Exception as e:
        print("❌ 실패:", str(e))
    
    # 3. 댐 데이터 테스트
    print("\n📊 댐 데이터 테스트 (dam, 1H)...")
    try:
        result = await api.fetch_observatory_data("dam", "1H")
        print("✅ 성공:", result)
    except Exception as e:
        print("❌ 실패:", str(e))
    
    # 4. 강수량 데이터 테스트
    print("\n📊 강수량 데이터 테스트 (rainfall, 1D)...")
    try:
        result = await api.fetch_observatory_data("rainfall", "1D")
        print("✅ 성공:", result)
    except Exception as e:
        print("❌ 실패:", str(e))

if __name__ == "__main__":
    asyncio.run(test_api()) 