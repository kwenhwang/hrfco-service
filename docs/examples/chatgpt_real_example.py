#!/usr/bin/env python3
"""
실제 API 키로 ChatGPT Function Calling 사용 예시
"""

import asyncio
import json
from chatgpt_functions import CHATGPT_FUNCTIONS, execute_function

async def demo_real_scenarios():
    """실제 데이터로 시나리오 데모"""
    
    print("🌊 실제 API 키로 ChatGPT Function Calling 데모")
    print("=" * 50)
    
    # 시나리오 1: 하동군 대석교 수위 위험도 분석 (실제 데이터)
    print("\n🔍 시나리오 1: 하동군 대석교 실시간 수위 분석")
    print("-" * 40)
    
    try:
        result = await execute_function("get_water_level_data", {
            "obs_code": "4009670",
            "hours": 48,
            "include_thresholds": True
        })
        
        data = json.loads(result)
        print(f"📍 관측소: {data['observatory_info']['name']}")
        print(f"📍 주소: {data['observatory_info']['address']}")
        print(f"🌊 현재 수위: {data['current_water_level']}m")
        print(f"⚠️ 위험도: {data.get('alert_status', '정보 없음')}")
        
        if 'thresholds' in data:
            thresholds = data['thresholds']
            print(f"📊 위험 수위 기준:")
            print(f"   관심: {thresholds.get('interest', 'N/A')}m")
            print(f"   주의보: {thresholds.get('caution', 'N/A')}m")
            print(f"   경보: {thresholds.get('warning', 'N/A')}m")
            print(f"   심각: {thresholds.get('severe', 'N/A')}m")
        
        if 'margin_to_next_level' in data:
            print(f"📏 다음 단계까지 여유: {data['margin_to_next_level']:.2f}m")
        
        print(f"📊 데이터 개수: {data['data_period']['total_records']}개")
        print(f"⏰ 데이터 기간: {data['data_period']['start']} ~ {data['data_period']['end']}")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 2: 진주 지역 실시간 기상 정보
    print("\n🌡️ 시나리오 2: 진주 지역 실시간 기상 정보")
    print("-" * 40)
    
    try:
        # 진주 기상관측소 (162)
        result = await execute_function("get_weather_data", {
            "station_id": "162",
            "hours": 24,
            "data_type": "hourly"
        })
        
        data = json.loads(result)
        current = data['current_weather']
        stats = data['statistics']
        
        print(f"📍 관측소: 진주 (ID: 162)")
        print(f"🌡️ 현재 기온: {current['temperature']}°C")
        print(f"💧 습도: {current['humidity']}%")
        print(f"🌧️ 현재 강수량: {current['rainfall']}mm")
        print(f"💨 풍속: {current['wind_speed']}m/s")
        print(f"📊 24시간 최고/최저 기온: {stats['max_temperature']}°C / {stats['min_temperature']}°C")
        print(f"📊 24시간 총 강수량: {stats['total_rainfall']}mm")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 시나리오 3: 기상관측소 검색
    print("\n🗺️ 시나리오 3: 하동군 주변 기상관측소 검색")
    print("-" * 40)
    
    try:
        result = await execute_function("search_weather_stations", {
            "address": "하동군",
            "radius_km": 50
        })
        
        data = json.loads(result)
        print(f"🎯 검색 위치: {data['search_parameters']['address']}")
        print(f"📊 발견된 기상관측소: {data['total_found']}개")
        
        for i, station in enumerate(data['weather_stations'][:3], 1):
            print(f"   {i}. {station['name']} (ID: {station['station_id']}) - {station['distance_km']}km")
        
    except Exception as e:
        print(f"❌ 오류: {e}")


def print_chatgpt_integration_guide():
    """ChatGPT 통합 사용법 안내"""
    
    print("\n" + "=" * 50)
    print("🤖 ChatGPT Function Calling 사용법")
    print("=" * 50)
    
    guide = """
1️⃣ OpenAI API 설정:
   ```python
   import openai
   from chatgpt_functions import CHATGPT_FUNCTIONS, execute_function
   
   client = openai.OpenAI(api_key="your-openai-api-key")
   ```

2️⃣ ChatGPT에 함수 등록하여 질문:
   ```python
   response = client.chat.completions.create(
       model="gpt-4",
       messages=[
           {"role": "user", "content": "하동군 대석교 수위가 위험한가요?"}
       ],
       functions=CHATGPT_FUNCTIONS,
       function_call="auto"
   )
   ```

3️⃣ 실제 사용 가능한 질문들:
   💬 "하동군 대석교 수위가 위험한가요?"
      → get_water_level_data 함수가 자동 호출되어 실시간 수위와 위험도 분석
   
   💬 "진주 지역 날씨는 어떤가요?"
      → get_weather_data 함수가 호출되어 실시간 기상 정보 제공
   
   💬 "하동군 주변에 어떤 기상관측소가 있나요?"
      → search_weather_stations 함수가 호출되어 주변 관측소 검색
   
   💬 "하동군 수위와 강우량을 종합 분석해주세요"
      → get_comprehensive_flood_analysis 함수가 호출되어 홍수 위험도 분석

4️⃣ 현재 사용 가능한 실제 데이터:
   ✅ 홍수통제소 수위 데이터 (실시간)
   ✅ 기상청 날씨 데이터 (실시간)
   ✅ 기상관측소 검색
   ⚠️ 일부 관측소 검색 기능은 개발 중

5️⃣ 환경 설정:
   - HRFCO_API_KEY: FE18B23B-A81B-4246-9674-E8D641902A42 ✅
   - KMA_API_KEY: bI7VVvskaOdKJGMej%2F2zJzaxEyiCeGn8kLEidNAxHV7%2FRLiWMCAIlqMY08bwU1MqnakQ4ulEirojxHU800l%2BMA%3D%3D ✅
   - OPENAI_API_KEY: 사용자 설정 필요
"""
    
    print(guide)
    
    print("\n💡 추천 ChatGPT 프롬프트:")
    prompts = [
        "하동군 대석교의 현재 수위가 안전한지 알려주세요",
        "진주 지역의 현재 날씨와 24시간 기온 변화를 분석해주세요",
        "하동군 주변 50km 내에 있는 기상관측소를 찾아주세요",
        "수위 4009670 관측소의 최근 48시간 변화 추이를 분석해주세요"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"   {i}. \"{prompt}\"")


async def main():
    # 실제 데이터 데모
    await demo_real_scenarios()
    
    # ChatGPT 통합 가이드
    print_chatgpt_integration_guide()
    
    print(f"\n✨ 실제 API 키가 적용되어 ChatGPT에서 실시간 수위/기상 데이터를 조회할 수 있습니다!")
    print(f"📚 자세한 설정법은 CHATGPT_SETUP.md 파일을 참고하세요.")


if __name__ == "__main__":
    asyncio.run(main()) 