#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자 예제 - API 키 없이 HRFCO 데이터 사용하기

이 예제는 API 키 없이도 MCP 서버를 통해 HRFCO 수문 데이터를 사용하는 방법을 보여줍니다.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from hrfco_service.api import fetch_observatory_info, fetch_observatory_data

async def example_without_api_key():
    """API 키 없이 데이터 사용 예제"""
    
    print("🌊 HRFCO 수문 데이터 사용 예제 (API 키 없이)")
    print("=" * 50)
    
    try:
        # 1. 관측소 정보 조회 (API 키 없이도 가능)
        print("\n1️⃣ 수위 관측소 정보 조회...")
        waterlevel_stations = await fetch_observatory_info("waterlevel")
        print(f"✅ 수위 관측소 {len(waterlevel_stations)}개 발견")
        
        if waterlevel_stations:
            # 첫 번째 관측소 정보 출력
            first_station = waterlevel_stations[0]
            print(f"   📍 관측소명: {first_station.get('obsnm', 'N/A')}")
            print(f"   🏷️  코드: {first_station.get('obsnmcd', 'N/A')}")
            print(f"   📍 위치: {first_station.get('obsaddr', 'N/A')}")
        
        # 2. 강수량 관측소 정보 조회
        print("\n2️⃣ 강수량 관측소 정보 조회...")
        rainfall_stations = await fetch_observatory_info("rainfall")
        print(f"✅ 강수량 관측소 {len(rainfall_stations)}개 발견")
        
        # 3. 댐 정보 조회
        print("\n3️⃣ 댐 정보 조회...")
        dam_stations = await fetch_observatory_info("dam")
        print(f"✅ 댐 {len(dam_stations)}개 발견")
        
        if dam_stations:
            # 첫 번째 댐 정보 출력
            first_dam = dam_stations[0]
            print(f"   🏞️  댐명: {first_dam.get('obsnm', 'N/A')}")
            print(f"   🏷️  코드: {first_dam.get('obsnmcd', 'N/A')}")
        
        # 4. 실제 데이터 조회 (관측소 코드가 있는 경우)
        if waterlevel_stations:
            obs_code = waterlevel_stations[0].get('obsnmcd')
            if obs_code:
                print(f"\n4️⃣ 실시간 수위 데이터 조회 (관측소: {obs_code})...")
                try:
                    waterlevel_data = await fetch_observatory_data("waterlevel", "10M", obs_code)
                    print(f"✅ 수위 데이터 조회 성공")
                    if waterlevel_data and len(waterlevel_data) > 0:
                        latest_data = waterlevel_data[0]
                        print(f"   📊 최신 수위: {latest_data.get('wl', 'N/A')} m")
                        print(f"   ⏰ 측정시간: {latest_data.get('tm', 'N/A')}")
                except Exception as e:
                    print(f"⚠️  데이터 조회 실패: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API 키 없이도 데이터 조회가 가능합니다!")
        print("\n💡 사용 방법:")
        print("   1. Glama에서 'hrfco-flood-control' 서버 사용")
        print("   2. Claude Desktop에서 MCP 서버 연결")
        print("   3. HTTP API 직접 호출")
        print("\n📖 자세한 사용법은 USER_GUIDE.md를 참조하세요.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n💡 해결 방법:")
        print("   1. 인터넷 연결 확인")
        print("   2. HRFCO API 서버 상태 확인")
        print("   3. 방화벽 설정 확인")

async def example_mcp_server_usage():
    """MCP 서버 사용 예제"""
    
    print("\n🤖 MCP 서버 사용 예제")
    print("=" * 30)
    
    # MCP 서버 요청 예제
    mcp_requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_observatory_info",
                "arguments": {
                    "hydro_type": "waterlevel"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_server_health"
            }
        }
    ]
    
    print("📋 사용 가능한 MCP 도구:")
    print("   - get_observatory_info: 관측소 정보 조회")
    print("   - get_hydro_data: 수문 데이터 조회")
    print("   - get_server_health: 서버 상태 확인")
    print("   - get_server_config: 서버 설정 확인")
    
    print("\n💬 예시 질문:")
    print("   - '부산 지역의 수위 관측소 정보를 알려줘'")
    print("   - '영천댐의 현재 방류량을 확인해줘'")
    print("   - '최근 강수량 현황을 보여줘'")
    print("   - '홍수 위험이 있는 지역이 있나요?'")

def main():
    """메인 함수"""
    print("🚀 HRFCO 수문 데이터 사용자 가이드")
    print("API 키 없이도 수문 데이터를 사용할 수 있습니다!")
    
    # 예제 실행
    asyncio.run(example_without_api_key())
    example_mcp_server_usage()

if __name__ == "__main__":
    main() 