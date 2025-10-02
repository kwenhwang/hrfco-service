#!/usr/bin/env python3
"""
실제 HRFCO API 데이터로 MCP 서버 테스트
"""
import asyncio
import json
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# MCP 서버 모듈 import
sys.path.append('/home/ubuntu/hrfco-service')
from mcp_server import HRFCOClient

async def test_mcp_tools():
    """MCP 도구들을 실제 데이터로 테스트"""
    print("🚀 HRFCO MCP 서버 실제 데이터 테스트")
    
    client = HRFCOClient()
    
    # 1. 수위 관측소 조회
    print("\n🔍 1. 수위 관측소 조회 테스트...")
    waterlevel_obs = await client.get_observatories("waterlevel")
    
    if isinstance(waterlevel_obs, dict) and 'error' in waterlevel_obs:
        print(f"❌ 오류: {waterlevel_obs['error']}")
    else:
        print(f"✅ 수위 관측소 수: {len(waterlevel_obs)}개")
        if waterlevel_obs:
            first = waterlevel_obs[0]
            print(f"📍 첫 번째: {first.get('obsnm', 'N/A')} (코드: {first.get('wlobscd', 'N/A')})")
    
    # 2. 강우량 관측소 조회
    print("\n🌧️ 2. 강우량 관측소 조회 테스트...")
    rainfall_obs = await client.get_observatories("rainfall")
    
    if isinstance(rainfall_obs, dict) and 'error' in rainfall_obs:
        print(f"❌ 오류: {rainfall_obs['error']}")
    else:
        print(f"✅ 강우량 관측소 수: {len(rainfall_obs)}개")
        if rainfall_obs:
            first = rainfall_obs[0]
            print(f"📍 첫 번째: {first.get('obsnm', 'N/A')} (코드: {first.get('rfobscd', 'N/A')})")
    
    # 3. 댐 정보 조회
    print("\n🏗️ 3. 댐 정보 조회 테스트...")
    dam_obs = await client.get_observatories("dam")
    
    if isinstance(dam_obs, dict) and 'error' in dam_obs:
        print(f"❌ 오류: {dam_obs['error']}")
    else:
        print(f"✅ 댐 수: {len(dam_obs)}개")
        if dam_obs:
            first = dam_obs[0]
            print(f"📍 첫 번째: {first.get('obsnm', 'N/A')} (코드: {first.get('damcd', 'N/A')})")
            print(f"💧 저수량: {first.get('stowt', 'N/A')}만㎥")
    
    print("\n🎉 실제 데이터 테스트 완료!")
    return True

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
