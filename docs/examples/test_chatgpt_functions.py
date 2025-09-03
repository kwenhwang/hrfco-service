#!/usr/bin/env python3
"""
ChatGPT Function Calling 테스트 스크립트
"""

import asyncio
import json
import sys
import os

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatgpt_functions import CHATGPT_FUNCTIONS, execute_function

async def test_water_level_function():
    """수위 데이터 함수 테스트"""
    print("🌊 수위 데이터 함수 테스트")
    print("-" * 40)
    
    try:
        result = await execute_function("get_water_level_data", {
            "obs_code": "4009670",
            "hours": 24,
            "include_thresholds": True
        })
        
        data = json.loads(result)
        print(f"✅ 성공: {data['observatory_info']['name']}")
        print(f"   현재 수위: {data['current_water_level']}m")
        print(f"   위험도: {data.get('alert_status', '정보 없음')}")
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

async def test_search_function():
    """관측소 검색 함수 테스트"""
    print("\n🔍 관측소 검색 함수 테스트")
    print("-" * 40)
    
    try:
        result = await execute_function("search_nearby_observatories", {
            "address": "하동군",
            "radius_km": 20,
            "hydro_type": "all"
        })
        
        data = json.loads(result)
        print(f"✅ 성공: {data['total_found']}개 관측소 발견")
        if data['observatories']:
            obs = data['observatories'][0]
            print(f"   가장 가까운 관측소: {obs['name']} ({obs['distance_km']}km)")
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

async def test_rainfall_function():
    """강우량 함수 테스트"""
    print("\n🌧️ 강우량 함수 테스트")
    print("-" * 40)
    
    try:
        result = await execute_function("get_rainfall_data", {
            "obs_code": "4009665",
            "hours": 48
        })
        
        data = json.loads(result)
        print(f"✅ 성공: {data['observatory_info']['name']}")
        stats = data['rainfall_statistics']
        print(f"   총 강우량: {stats['total_rainfall']}mm")
        print(f"   최근 1시간: {stats['recent_1hour']}mm")
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

async def test_comprehensive_analysis():
    """종합 분석 함수 테스트"""
    print("\n📊 종합 분석 함수 테스트")
    print("-" * 40)
    
    try:
        result = await execute_function("get_comprehensive_flood_analysis", {
            "water_level_obs": "4009670",
            "rainfall_obs": "4009665",
            "hours": 72
        })
        
        data = json.loads(result)
        print(f"✅ 성공: 종합 홍수 위험 분석 완료")
        if 'flood_risk_assessment' in data:
            risk = data['flood_risk_assessment']
            print(f"   종합 위험도: {risk['overall_risk_level']}")
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

async def test_weather_functions():
    """기상 함수 테스트"""
    print("\n🌡️ 기상 함수 테스트")
    print("-" * 40)
    
    try:
        # 기상관측소 검색
        search_result = await execute_function("search_weather_stations", {
            "address": "하동군",
            "radius_km": 50
        })
        
        search_data = json.loads(search_result)
        print(f"✅ 기상관측소 검색 성공: {search_data['total_found']}개 발견")
        
        if search_data['weather_stations']:
            station_id = search_data['weather_stations'][0]['station_id']
            station_name = search_data['weather_stations'][0]['name']
            
            # 기상 데이터 조회
            weather_result = await execute_function("get_weather_data", {
                "station_id": station_id,
                "hours": 24
            })
            
            weather_data = json.loads(weather_result)
            current = weather_data['current_weather']
            print(f"✅ 기상 데이터 조회 성공: {station_name}")
            print(f"   현재 기온: {current['temperature']}°C")
            print(f"   습도: {current['humidity']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 ChatGPT Function Calling 테스트 시작")
    print("=" * 50)
    
    # Function Definitions 출력
    print(f"\n📋 등록된 함수 개수: {len(CHATGPT_FUNCTIONS)}")
    for i, func in enumerate(CHATGPT_FUNCTIONS, 1):
        print(f"   {i}. {func['name']}: {func['description'][:50]}...")
    
    # 각 함수 테스트
    tests = [
        test_water_level_function,
        test_search_function,
        test_rainfall_function,
        test_comprehensive_analysis,
        test_weather_functions
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ 테스트 실행 오류: {e}")
            results.append(False)
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("-" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 성공: {passed}/{total}")
    print(f"❌ 실패: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("   ChatGPT Function Calling 구현이 정상 작동합니다.")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("   API 키 설정을 확인하거나 네트워크 연결을 점검해주세요.")
        print("   데모 모드에서도 기본 기능은 작동합니다.")

if __name__ == "__main__":
    asyncio.run(main()) 