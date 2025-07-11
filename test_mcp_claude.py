#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 서버를 통한 Claude 통합 테스트
"""
import asyncio
import json
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from hrfco_service.server import create_server

async def test_mcp_claude_integration():
    """MCP 서버를 통한 Claude 통합 테스트"""
    
    print("🧠 MCP 서버를 통한 Claude 통합 테스트")
    print("=" * 60)
    
    # MCP 서버 생성
    server = create_server()
    
    print("📋 시나리오 1: Claude가 사용 가능한 도구 목록을 확인")
    print("-" * 50)
    print("Claude: '사용할 수 있는 도구가 뭐가 있어?'")
    
    try:
        # get_tools 도구 호출
        tools_result = await server.get_tools()
        if tools_result and len(tools_result) > 0:
            tools_data = json.loads(tools_result[0].text)
            print("🤖 Claude 응답:")
            print("사용 가능한 도구들:")
            for tool in tools_data.get('available_tools', []):
                print(f"  - {tool.get('name')}: {tool.get('description')}")
            
            print(f"\n지원하는 데이터 타입: {', '.join(tools_data.get('hydro_types', []))}")
            print(f"지원하는 시간 단위: {', '.join(tools_data.get('time_types', []))}")
        else:
            print("❌ 도구 목록을 받을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n📋 시나리오 2: Claude가 서버 설정을 확인")
    print("-" * 50)
    print("Claude: '서버 설정을 확인해줘'")
    
    try:
        config_result = await server.get_server_config()
        if config_result and len(config_result) > 0:
            config_data = json.loads(config_result[0].text)
            print("🤖 Claude 응답:")
            print("서버 설정 정보:")
            print(f"  - API URL: {config_data.get('api_base_url')}")
            print(f"  - 캐시 TTL: {config_data.get('cache_ttl_seconds')}초")
            print(f"  - 최대 동시 요청: {config_data.get('max_concurrent_requests')}")
            print(f"  - 요청 타임아웃: {config_data.get('request_timeout')}초")
            
            cache_stats = config_data.get('cache_stats', {})
            print(f"  - 캐시 히트율: {cache_stats.get('hit_rate', 0):.1f}%")
        else:
            print("❌ 설정 정보를 받을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n📋 시나리오 3: Claude가 관측소를 검색")
    print("-" * 50)
    print("Claude: '부산 지역의 수위 관측소를 찾아줘'")
    
    try:
        search_result = await server.search_observatory("부산", "waterlevel")
        if search_result and len(search_result) > 0:
            search_data = json.loads(search_result[0].text)
            results = search_data.get("results", [])
            print("🤖 Claude 응답:")
            print(f"부산 지역 수위 관측소 {len(results)}개 발견:")
            for i, station in enumerate(results[:5], 1):
                name = station.get('obsnm', '이름 없음')
                code = station.get('wlobscd', '코드 없음')
                addr = station.get('addr', '주소 없음')
                print(f"  {i}. {name} ({code})")
                print(f"     위치: {addr}")
        else:
            print("❌ 검색 결과를 받을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n📋 시나리오 4: Claude가 최근 데이터를 조회")
    print("-" * 50)
    print("Claude: '영천댐의 최근 데이터를 보여줘'")
    
    try:
        # 먼저 영천댐 관측소 검색
        search_result = await server.search_observatory("영천댐", "dam")
        if search_result and len(search_result) > 0:
            search_data = json.loads(search_result[0].text)
            if search_data.get("results"):
                obs_code = search_data["results"][0].get("dmobscd")
                if obs_code:
                    # 최근 데이터 조회
                    recent_data = await server.get_recent_data("dam", obs_code, 3, "1H")
                    if recent_data and len(recent_data) > 0:
                        data = json.loads(recent_data[0].text)
                        print("🤖 Claude 응답:")
                        print(f"영천댐 최근 데이터 ({len(data.get('recent_data', []))}개):")
                        for item in data.get('recent_data', []):
                            time = item.get('ymdhm', '시간 정보 없음')
                            swl = item.get('swl', 'N/A')
                            inf = item.get('inf', 'N/A')
                            tototf = item.get('tototf', 'N/A')
                            print(f"  - {time}: 저수위 {swl}m, 유입량 {inf}m³/s, 총방류량 {tototf}m³/s")
                    else:
                        print("❌ 최근 데이터를 조회할 수 없습니다.")
                else:
                    print("❌ 관측소 코드를 찾을 수 없습니다.")
            else:
                print("❌ 영천댐 관측소를 찾을 수 없습니다.")
        else:
            print("❌ 검색 결과를 받을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n📋 시나리오 5: Claude가 지역 수문 상태를 분석")
    print("-" * 50)
    print("Claude: '부산 지역의 수문 상태를 분석해줘'")
    
    try:
        analysis_result = await server.analyze_regional_hydro_status("부산")
        if analysis_result and len(analysis_result) > 0:
            analysis = analysis_result[0].text
            print("🤖 Claude 응답:")
            print(analysis)
        else:
            print("❌ 분석 결과를 받을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n📋 시나리오 6: Claude가 배치 데이터를 조회")
    print("-" * 50)
    print("Claude: '여러 지역의 강수량 데이터를 한 번에 조회해줘'")
    
    try:
        # 배치 요청 데이터
        batch_requests = [
            {
                "hydro_type": "rainfall",
                "obs_code": "10014010",
                "time_type": "1H"
            },
            {
                "hydro_type": "rainfall", 
                "obs_code": "10014020",
                "time_type": "1H"
            }
        ]
        
        batch_result = await server.get_batch_hydro_data(batch_requests)
        if batch_result and len(batch_result) > 0:
            batch_data = json.loads(batch_result[0].text)
            print("🤖 Claude 응답:")
            print("배치 강수량 데이터 조회 결과:")
            
            for i, result in enumerate(batch_data):
                if result.get("success"):
                    data = result.get("data", {})
                    content = data.get("content", [])
                    if content:
                        latest = content[0]
                        obs_code = latest.get("rfobscd", "알 수 없음")
                        rainfall = latest.get("rf", 0)
                        time = latest.get("ymdhm", "시간 정보 없음")
                        print(f"  - 관측소 {obs_code}: {rainfall}mm ({time})")
                else:
                    print(f"  - 요청 {i+1}: {result.get('error', '알 수 없는 오류')}")
        else:
            print("❌ 배치 데이터를 조회할 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n" + "=" * 60)
    print("✅ MCP 서버를 통한 Claude 통합 테스트 완료!")
    print("Claude가 MCP 서버를 통해 HRFCO 수문 데이터에 접근할 수 있습니다.")

if __name__ == "__main__":
    asyncio.run(test_mcp_claude_integration()) 