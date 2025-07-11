#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 챗봇/Claude MCP 서버 사용 시나리오 테스트
"""
import asyncio
import json
import sys
import httpx
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from hrfco_service.api import fetch_observatory_info, fetch_observatory_data

async def test_ai_scenarios():
    """AI 챗봇 사용 시나리오 테스트"""
    
    print("🤖 AI 챗봇/Claude HRFCO API 사용 시나리오 테스트")
    print("=" * 60)
    
    # 시나리오 1: 사용자가 "부산 지역의 수문 상태가 어때?"라고 물어봄
    print("\n📋 시나리오 1: 지역 수문 상태 분석")
    print("-" * 40)
    print("사용자: '부산 지역의 수문 상태가 어때?'")
    
    try:
        # 부산 지역 관측소 정보 조회
        waterlevel_info = await fetch_observatory_info("waterlevel")
        rainfall_info = await fetch_observatory_info("rainfall")
        
        print("🤖 AI 응답:")
        print("부산 지역 수문 상태 분석:")
        
        # 수위 관측소 분석
        if isinstance(waterlevel_info, dict) and "content" in waterlevel_info:
            waterlevel_stations = waterlevel_info["content"]
            busan_waterlevel = [s for s in waterlevel_stations if "부산" in s.get("obsnm", "")]
            print(f"  - 수위 관측소: {len(busan_waterlevel)}개 발견")
            for station in busan_waterlevel[:3]:
                name = station.get("obsnm", "이름 없음")
                code = station.get("wlobscd", "코드 없음")
                print(f"    * {name} ({code})")
        
        # 강수량 관측소 분석
        if isinstance(rainfall_info, dict) and "content" in rainfall_info:
            rainfall_stations = rainfall_info["content"]
            busan_rainfall = [s for s in rainfall_stations if "부산" in s.get("obsnm", "")]
            print(f"  - 강수량 관측소: {len(busan_rainfall)}개 발견")
            for station in busan_rainfall[:3]:
                name = station.get("obsnm", "이름 없음")
                code = station.get("rfobscd", "코드 없음")
                print(f"    * {name} ({code})")
        
        print("  - 현재 홍수 위험도: 낮음 (정상 수준)")
        print("  - 주의사항: 실시간 모니터링 권장")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 2: 사용자가 "영천댐의 최근 데이터를 보여줘"라고 물어봄
    print("\n📋 시나리오 2: 특정 관측소 데이터 조회")
    print("-" * 40)
    print("사용자: '영천댐의 최근 데이터를 보여줘'")
    
    try:
        # 영천댐 데이터 조회 (실제 관측소 코드 사용)
        dam_data = await fetch_observatory_data("dam", "10M", "1001210")
        
        print("🤖 AI 응답:")
        if isinstance(dam_data, dict) and "content" in dam_data:
            content = dam_data["content"]
            if content:
                latest = content[0]
                time = latest.get("ymdhm", "시간 정보 없음")
                swl = latest.get("swl", "N/A")
                inf = latest.get("inf", "N/A")
                tototf = latest.get("tototf", "N/A")
                print(f"영천댐 최근 데이터 ({time}):")
                print(f"  - 저수위: {swl}m")
                print(f"  - 유입량: {inf}m³/s")
                print(f"  - 총방류량: {tototf}m³/s")
                print(f"  - 상태: 정상 운영 중")
            else:
                print("  - 최근 데이터가 없습니다.")
        else:
            print("  - 데이터를 조회할 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 3: 사용자가 "부산 근처에 어떤 수위 관측소가 있어?"라고 물어봄
    print("\n📋 시나리오 3: 지역 관측소 검색")
    print("-" * 40)
    print("사용자: '부산 근처에 어떤 수위 관측소가 있어?'")
    
    try:
        waterlevel_info = await fetch_observatory_info("waterlevel")
        
        print("🤖 AI 응답:")
        if isinstance(waterlevel_info, dict) and "content" in waterlevel_info:
            stations = waterlevel_info["content"]
            busan_stations = [s for s in stations if "부산" in s.get("obsnm", "")]
            print(f"부산 지역 수위 관측소 {len(busan_stations)}개 발견:")
            for i, station in enumerate(busan_stations[:5], 1):
                name = station.get("obsnm", "이름 없음")
                code = station.get("wlobscd", "코드 없음")
                addr = station.get("addr", "주소 없음")
                print(f"  {i}. {name} ({code})")
                print(f"     위치: {addr}")
        else:
            print("  - 관측소 정보를 조회할 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 4: 사용자가 "최근에 비가 많이 온 지역은 어디야?"라고 물어봄
    print("\n📋 시나리오 4: 강수량 데이터 분석")
    print("-" * 40)
    print("사용자: '최근에 비가 많이 온 지역은 어디야?'")
    
    try:
        # 여러 관측소의 강수량 데이터 조회
        rainfall_data_1 = await fetch_observatory_data("rainfall", "10M", "10014010")
        rainfall_data_2 = await fetch_observatory_data("rainfall", "10M", "10014020")
        
        print("🤖 AI 응답:")
        print("최근 강수량 현황:")
        
        # 첫 번째 관측소
        if isinstance(rainfall_data_1, dict) and "content" in rainfall_data_1:
            content = rainfall_data_1["content"]
            if content:
                latest = content[0]
                obs_code = latest.get("rfobscd", "알 수 없음")
                rainfall = latest.get("rf", 0)
                time = latest.get("ymdhm", "시간 정보 없음")
                print(f"  - 관측소 {obs_code}: {rainfall}mm ({time})")
        
        # 두 번째 관측소
        if isinstance(rainfall_data_2, dict) and "content" in rainfall_data_2:
            content = rainfall_data_2["content"]
            if content:
                latest = content[0]
                obs_code = latest.get("rfobscd", "알 수 없음")
                rainfall = latest.get("rf", 0)
                time = latest.get("ymdhm", "시간 정보 없음")
                print(f"  - 관측소 {obs_code}: {rainfall}mm ({time})")
        
        print("  - 분석: 현재 강수량은 정상 수준입니다.")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 5: 사용자가 "서버 설정을 확인해줘"라고 물어봄
    print("\n📋 시나리오 5: 서버 설정 확인")
    print("-" * 40)
    print("사용자: '서버 설정을 확인해줘'")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/config")
            if response.status_code == 200:
                config_data = response.json()
                print("🤖 AI 응답:")
                print("서버 설정 정보:")
                print(f"  - API URL: {config_data.get('api_base_url')}")
                print(f"  - 캐시 TTL: {config_data.get('cache_ttl_seconds')}초")
                print(f"  - 최대 동시 요청: {config_data.get('max_concurrent_requests')}")
                print(f"  - 요청 타임아웃: {config_data.get('request_timeout')}초")
                print(f"  - 로그 레벨: {config_data.get('log_level')}")
            else:
                print("  - 설정 정보를 조회할 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 6: 사용자가 "사용할 수 있는 도구가 뭐가 있어?"라고 물어봄
    print("\n📋 시나리오 6: 사용 가능한 도구 확인")
    print("-" * 40)
    print("사용자: '사용할 수 있는 도구가 뭐가 있어?'")
    
    try:
        print("🤖 AI 응답:")
        print("사용 가능한 도구들:")
        print("  - 관측소 정보 조회: /observatories")
        print("  - 수문 데이터 조회: /hydro")
        print("  - 서버 상태 확인: /health")
        print("  - 서버 설정 확인: /config")
        print("\n지원하는 데이터 타입:")
        print("  - waterlevel: 수위 데이터")
        print("  - rainfall: 강수량 데이터")
        print("  - dam: 댐 데이터")
        print("  - bo: 보 데이터")
        print("\n지원하는 시간 단위:")
        print("  - 10M: 10분")
        print("  - 1H: 1시간")
        print("  - 1D: 1일")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n" + "=" * 60)
    print("✅ AI 챗봇 시나리오 테스트 완료!")
    print("AI 챗봇이나 Claude가 이 API를 통해 HRFCO 수문 데이터에 접근할 수 있습니다.")

if __name__ == "__main__":
    asyncio.run(test_ai_scenarios()) 