#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude/AI 챗봇 실제 사용 시나리오 테스트
"""
import asyncio
import json
import httpx
from datetime import datetime, timedelta

async def test_claude_scenarios():
    """Claude 실제 사용 시나리오 테스트"""
    
    print("🧠 Claude/AI 챗봇 실제 사용 시나리오 테스트")
    print("=" * 60)
    
    # 시나리오 1: 사용자가 "부산에서 홍수 위험이 있는 지역이 있나요?"라고 물어봄
    print("\n📋 시나리오 1: 홍수 위험 지역 분석")
    print("-" * 40)
    print("사용자: '부산에서 홍수 위험이 있는 지역이 있나요?'")
    
    try:
        # 부산 지역 수위 데이터 조회
        async with httpx.AsyncClient() as client:
            # 부산 지역 수위 관측소 데이터 조회
            response = await client.get(
                "http://localhost:8000/hydro",
                params={
                    "hydro_type": "waterlevel",
                    "time_type": "10M",
                    "obs_code": "2022678",  # 부산시(대동낙동강교)
                    "document_type": "json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                if content:
                    latest = content[0]
                    water_level = float(latest.get("wl", 0))
                    time = latest.get("ymdhm", "시간 정보 없음")
                    
                    print("🤖 Claude 응답:")
                    print(f"부산 대동낙동강교 관측소의 현재 수위는 {water_level}m입니다 ({time}).")
                    
                    # 홍수 위험도 판단
                    if water_level > 5.0:
                        risk_level = "높음"
                        advice = "즉시 대피 준비가 필요합니다."
                    elif water_level > 3.0:
                        risk_level = "보통"
                        advice = "수위 변화를 주의 깊게 모니터링하세요."
                    else:
                        risk_level = "낮음"
                        advice = "현재는 안전한 수위입니다."
                    
                    print(f"홍수 위험도: {risk_level}")
                    print(f"권장사항: {advice}")
                else:
                    print("🤖 Claude 응답: 현재 수위 데이터를 조회할 수 없습니다.")
            else:
                print("🤖 Claude 응답: 데이터 조회 중 오류가 발생했습니다.")
                
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 2: 사용자가 "영천댐의 방류량이 얼마나 되나요?"라고 물어봄
    print("\n📋 시나리오 2: 댐 방류량 조회")
    print("-" * 40)
    print("사용자: '영천댐의 방류량이 얼마나 되나요?'")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/hydro",
                params={
                    "hydro_type": "dam",
                    "time_type": "10M",
                    "obs_code": "1001210",  # 영천댐
                    "document_type": "json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                if content:
                    latest = content[0]
                    discharge = float(latest.get("tototf", 0))
                    inflow = float(latest.get("inf", 0))
                    water_level = float(latest.get("swl", 0))
                    time = latest.get("ymdhm", "시간 정보 없음")
                    
                    print("🤖 Claude 응답:")
                    print(f"영천댐의 현재 방류량은 {discharge}m³/s입니다 ({time}).")
                    print(f"추가 정보:")
                    print(f"  - 유입량: {inflow}m³/s")
                    print(f"  - 저수위: {water_level}m")
                    
                    # 방류량 분석
                    if discharge > 100:
                        status = "대량 방류 중"
                        warning = "하류 지역 주민들은 주의가 필요합니다."
                    elif discharge > 50:
                        status = "일반 방류 중"
                        warning = "정상적인 방류량입니다."
                    else:
                        status = "최소 방류 중"
                        warning = "저수량 확보를 위한 최소 방류입니다."
                    
                    print(f"상태: {status}")
                    print(f"주의사항: {warning}")
                else:
                    print("🤖 Claude 응답: 현재 방류량 데이터를 조회할 수 없습니다.")
            else:
                print("🤖 Claude 응답: 데이터 조회 중 오류가 발생했습니다.")
                
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 3: 사용자가 "최근 24시간 동안 비가 많이 온 지역은 어디인가요?"라고 물어봄
    print("\n📋 시나리오 3: 강수량 분석")
    print("-" * 40)
    print("사용자: '최근 24시간 동안 비가 많이 온 지역은 어디인가요?'")
    
    try:
        async with httpx.AsyncClient() as client:
            # 여러 지역의 강수량 데이터 조회
            rainfall_data = []
            
            # 부산 지역
            response1 = await client.get(
                "http://localhost:8000/hydro",
                params={
                    "hydro_type": "rainfall",
                    "time_type": "1H",
                    "obs_code": "10014010",
                    "document_type": "json"
                }
            )
            
            if response1.status_code == 200:
                data1 = response1.json()
                content1 = data1.get("content", [])
                if content1:
                    total_rainfall = sum(float(item.get("rf", 0)) for item in content1[:24])  # 최근 24시간
                    rainfall_data.append(("부산", total_rainfall))
            
            # 다른 지역 (실제로는 더 많은 지역을 조회)
            response2 = await client.get(
                "http://localhost:8000/hydro",
                params={
                    "hydro_type": "rainfall",
                    "time_type": "1H",
                    "obs_code": "10014020",
                    "document_type": "json"
                }
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                content2 = data2.get("content", [])
                if content2:
                    total_rainfall = sum(float(item.get("rf", 0)) for item in content2[:24])
                    rainfall_data.append(("기타 지역", total_rainfall))
            
            print("🤖 Claude 응답:")
            if rainfall_data:
                print("최근 24시간 강수량 현황:")
                for region, rainfall in rainfall_data:
                    print(f"  - {region}: {rainfall}mm")
                
                # 가장 많은 비가 온 지역 찾기
                max_rainfall_region = max(rainfall_data, key=lambda x: x[1])
                print(f"\n가장 많은 비가 온 지역: {max_rainfall_region[0]} ({max_rainfall_region[1]}mm)")
                
                if max_rainfall_region[1] > 50:
                    print("⚠️  주의: 대량 강우가 발생한 지역이 있습니다.")
                elif max_rainfall_region[1] > 10:
                    print("ℹ️  정보: 보통 수준의 강우가 있었습니다.")
                else:
                    print("✅ 안전: 강우량이 적은 상태입니다.")
            else:
                print("강수량 데이터를 조회할 수 없습니다.")
                
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 4: 사용자가 "부산 근처에 어떤 수문 관측소들이 있나요?"라고 물어봄
    print("\n📋 시나리오 4: 관측소 정보 조회")
    print("-" * 40)
    print("사용자: '부산 근처에 어떤 수문 관측소들이 있나요?'")
    
    try:
        async with httpx.AsyncClient() as client:
            # 수위 관측소 조회
            response1 = await client.get(
                "http://localhost:8000/observatories",
                params={
                    "hydro_type": "waterlevel",
                    "document_type": "json"
                }
            )
            
            # 강수량 관측소 조회
            response2 = await client.get(
                "http://localhost:8000/observatories",
                params={
                    "hydro_type": "rainfall",
                    "document_type": "json"
                }
            )
            
            print("🤖 Claude 응답:")
            print("부산 지역 수문 관측소 현황:")
            
            if response1.status_code == 200:
                data1 = response1.json()
                waterlevel_stations = data1.get("content", [])
                busan_waterlevel = [s for s in waterlevel_stations if "부산" in s.get("obsnm", "")]
                print(f"  - 수위 관측소: {len(busan_waterlevel)}개")
                for station in busan_waterlevel[:3]:
                    name = station.get("obsnm", "이름 없음")
                    code = station.get("wlobscd", "코드 없음")
                    addr = station.get("addr", "주소 없음")
                    print(f"    * {name} ({code}) - {addr}")
            
            if response2.status_code == 200:
                data2 = response2.json()
                rainfall_stations = data2.get("content", [])
                busan_rainfall = [s for s in rainfall_stations if "부산" in s.get("obsnm", "")]
                print(f"  - 강수량 관측소: {len(busan_rainfall)}개")
                for station in busan_rainfall[:3]:
                    name = station.get("obsnm", "이름 없음")
                    code = station.get("rfobscd", "코드 없음")
                    addr = station.get("addr", "주소 없음")
                    print(f"    * {name} ({code}) - {addr}")
            
            print("\n이러한 관측소들을 통해 실시간으로 수문 상태를 모니터링할 수 있습니다.")
                
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 5: 사용자가 "서버가 정상적으로 작동하고 있나요?"라고 물어봄
    print("\n📋 시나리오 5: 서버 상태 확인")
    print("-" * 40)
    print("사용자: '서버가 정상적으로 작동하고 있나요?'")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            
            print("🤖 Claude 응답:")
            if response.status_code == 200:
                health_data = response.json()
                print("✅ 서버가 정상적으로 작동하고 있습니다.")
                print(f"상태: {health_data.get('status', 'unknown')}")
                print("모든 수문 데이터 조회 기능이 정상적으로 작동합니다.")
            else:
                print("❌ 서버에 문제가 있습니다.")
                print(f"상태 코드: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Claude/AI 챗봇 시나리오 테스트 완료!")
    print("Claude나 AI 챗봇이 이 API를 통해 실시간 수문 정보를 제공할 수 있습니다.")

if __name__ == "__main__":
    asyncio.run(test_claude_scenarios()) 