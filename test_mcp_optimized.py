#!/usr/bin/env python3
"""
MCP 서버 최적화 테스트
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import MCP server
from mcp_server import HRFCOClient

async def test_optimized_response():
    """최적화된 응답 테스트"""
    print("🧪 MCP 서버 최적화 테스트")
    
    client = HRFCOClient()
    
    # 제한된 수위 관측소 조회
    print("\n🔍 제한된 수위 관측소 조회...")
    result = await client.get_observatories("waterlevel", limit=5)
    
    if isinstance(result, dict):
        if 'error' in result:
            print(f"❌ 오류: {result['error']}")
        else:
            print(f"✅ 총 관측소: {result.get('total_count', 0)}개")
            print(f"✅ 반환된 관측소: {result.get('returned_count', 0)}개")
            print(f"📝 메모: {result.get('note', 'N/A')}")
            
            # 응답 크기 확인
            response_size = len(json.dumps(result, ensure_ascii=False))
            print(f"📊 응답 크기: {response_size} bytes")
            
            if response_size < 5000:  # 5KB 미만
                print("✅ 응답 크기 최적화 성공")
            else:
                print("⚠️ 응답 크기가 여전히 큼")
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_optimized_response())
