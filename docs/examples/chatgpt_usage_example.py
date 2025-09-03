"""
ChatGPT Function Calling 사용 예시
"""

import json
import asyncio
from chatgpt_functions import CHATGPT_FUNCTIONS, execute_function

# 1. ChatGPT에 제공할 Function Definitions
print("=== ChatGPT에 등록할 Function Definitions ===")
print(json.dumps(CHATGPT_FUNCTIONS, ensure_ascii=False, indent=2))

# 2. 실제 사용 시나리오
async def demo_scenarios():
    """다양한 사용 시나리오 데모"""
    
    print("\n" + "="*50)
    print("🌊 홍수통제소 & 기상관측소 API Function Calling 데모")
    print("="*50)
    
    # 시나리오 1: 수위 위험도 분석
    print("\n🔍 시나리오 1: 하동군 대석교 수위 위험도 분석")
    print("-" * 40)
    
    result = await execute_function("get_water_level_data", {
        "obs_code": "4009670",
        "hours": 48,
        "include_thresholds": True
    })
    
    data = json.loads(result)
    print(f"📍 관측소: {data['observatory_info']['name']}")
    print(f"🌊 현재 수위: {data['current_water_level']}m")
    print(f"⚠️ 위험도: {data.get('alert_status', '정보 없음')}")
    if 'margin_to_next_level' in data:
        print(f"📏 다음 단계까지: {data['margin_to_next_level']:.2f}m")
    
    # 시나리오 2: 주변 관측소 종합 검색
    print("\n🔍 시나리오 2: 하동군 주변 관측소 종합 검색")
    print("-" * 40)
    
    result = await execute_function("search_nearby_observatories", {
        "address": "하동군 대석교",
        "radius_km": 20,
        "hydro_type": "all"
    })
    
    data = json.loads(result)
    print(f"🎯 검색 위치: {data['search_parameters']['address']}")
    print(f"📊 발견된 관측소: {data['total_found']}개")
    
    for obs in data['observatories'][:5]:
        print(f"  - {obs['name']} ({obs['type']}) - {obs['distance_km']}km")
    
    # 시나리오 3: 강우량 분석
    print("\n🔍 시나리오 3: 강우량 상세 분석")
    print("-" * 40)
    
    result = await execute_function("get_rainfall_data", {
        "obs_code": "4009665",
        "hours": 72
    })
    
    data = json.loads(result)
    stats = data['rainfall_statistics']
    print(f"🌧️ 관측소: {data['observatory_info']['name']}")
    print(f"📈 총 강우량: {stats['total_rainfall']}mm")
    print(f"⚡ 최대 시간당: {stats['max_hourly_rainfall']}mm")
    print(f"🕐 최근 1시간: {stats['recent_1hour']}mm")
    print(f"🕕 최근 6시간: {stats['recent_6hours']}mm")
    
    # 시나리오 4: 종합 홍수 위험 분석
    print("\n🔍 시나리오 4: 종합 홍수 위험 분석")
    print("-" * 40)
    
    result = await execute_function("get_comprehensive_flood_analysis", {
        "water_level_obs": "4009670",
        "rainfall_obs": "4009665",
        "hours": 72
    })
    
    data = json.loads(result)
    if 'flood_risk_assessment' in data:
        risk = data['flood_risk_assessment']
        print(f"🚨 종합 위험도: {risk['overall_risk_level']}")
        print(f"🌊 현재 수위: {risk['factors']['current_water_level']}m")
        print(f"🌧️ 6시간 강우량: {risk['factors']['recent_6h_rainfall']}mm")
        print(f"⚠️ 경보 상태: {risk['factors']['alert_status']}")
    
    # 시나리오 5: 기상관측소 검색 및 데이터 조회
    print("\n🔍 시나리오 5: 기상관측소 정보")
    print("-" * 40)
    
    # 기상관측소 검색
    result = await execute_function("search_weather_stations", {
        "address": "하동군",
        "radius_km": 50
    })
    
    data = json.loads(result)
    print(f"🌡️ 주변 기상관측소: {data['total_found']}개")
    
    if data['weather_stations']:
        closest_station = data['weather_stations'][0]
        print(f"📍 가장 가까운 관측소: {closest_station['name']} ({closest_station['distance_km']}km)")
        
        # 해당 기상관측소 데이터 조회
        weather_result = await execute_function("get_weather_data", {
            "station_id": closest_station['station_id'],
            "hours": 24
        })
        
        weather_data = json.loads(weather_result)
        current = weather_data['current_weather']
        stats = weather_data['statistics']
        
        print(f"🌡️ 현재 기온: {current['temperature']}°C")
        print(f"💧 습도: {current['humidity']}%")
        print(f"🌧️ 강수량: {current['rainfall']}mm")
        print(f"💨 풍속: {current['wind_speed']}m/s")
        print(f"📊 24시간 최고/최저: {stats['max_temperature']}°C / {stats['min_temperature']}°C")


# ChatGPT Integration 예시 코드
def chatgpt_integration_example():
    """ChatGPT와 실제 통합할 때 사용하는 코드 예시"""
    
    print("\n" + "="*50)
    print("💡 ChatGPT Integration 예시 코드")
    print("="*50)
    
    example_code = '''
import openai
import json
import asyncio
from chatgpt_functions import CHATGPT_FUNCTIONS, execute_function

# 1. OpenAI 클라이언트 설정
client = openai.OpenAI(api_key="your-api-key")

# 2. ChatGPT에 Function Calling으로 질문
async def ask_chatgpt_with_functions(user_message):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 홍수 및 기상 정보 전문가입니다. 사용자의 질문에 대해 제공된 함수들을 활용하여 정확한 정보를 제공해주세요."},
            {"role": "user", "content": user_message}
        ],
        functions=CHATGPT_FUNCTIONS,
        function_call="auto"
    )
    
    message = response.choices[0].message
    
    # Function call이 있는 경우 실행
    if message.function_call:
        function_name = message.function_call.name
        function_args = json.loads(message.function_call.arguments)
        
        # 실제 함수 실행
        function_result = await execute_function(function_name, function_args)
        
        # 결과와 함께 다시 ChatGPT에 질문
        second_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 홍수 및 기상 정보 전문가입니다."},
                {"role": "user", "content": user_message},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_result
                }
            ]
        )
        
        return second_response.choices[0].message.content
    
    return message.content

# 3. 사용 예시
async def main():
    # 예시 질문들
    questions = [
        "하동군 대석교 수위가 위험한가요?",
        "하동군 주변에 어떤 관측소들이 있나요?",
        "최근 강우량이 수위에 미치는 영향을 분석해주세요",
        "진주 지역 날씨는 어떤가요?"
    ]
    
    for question in questions:
        print(f"질문: {question}")
        answer = await ask_chatgpt_with_functions(question)
        print(f"답변: {answer}")
        print("-" * 50)

# 실행
asyncio.run(main())
'''
    
    print(example_code)


# 사용법 가이드
def usage_guide():
    """사용법 가이드"""
    
    print("\n" + "="*50)
    print("📖 사용법 가이드")
    print("="*50)
    
    guide = """
🚀 ChatGPT Function Calling 통합 단계:

1️⃣ 환경 설정:
   - pip install openai httpx python-dotenv
   - .env 파일에 API 키 설정:
     HRFCO_API_KEY=your_hrfco_api_key
     KMA_API_KEY=your_kma_api_key

2️⃣ Function Definitions 등록:
   - CHATGPT_FUNCTIONS를 ChatGPT에 등록
   - 총 6개 함수 사용 가능

3️⃣ 주요 함수들:
   🌊 get_water_level_data: 수위 데이터 + 위험도 분석
   🌧️ get_rainfall_data: 강우량 데이터 + 통계
   🔍 search_nearby_observatories: 주변 관측소 검색
   📊 get_comprehensive_flood_analysis: 종합 홍수 위험 분석
   🌡️ get_weather_data: 기상 데이터
   🗺️ search_weather_stations: 기상관측소 검색

4️⃣ 실제 활용 예시:
   "하동군 대석교 수위 상황은?" 
   → get_water_level_data 호출 → 위험도 분석 결과 제공
   
   "주변 관측소 정보를 알려줘"
   → search_nearby_observatories 호출 → 관측소 목록 제공
   
   "홍수 위험도를 종합 분석해줘"
   → get_comprehensive_flood_analysis 호출 → 수위+강우량 종합 분석

5️⃣ 데모 모드:
   - API 키가 없어도 데모 데이터로 테스트 가능
   - 실제 사용시에는 API 키 필수

6️⃣ 확장 가능:
   - 새로운 함수 추가 시 CHATGPT_FUNCTIONS와 FUNCTION_ROUTER에 등록
   - 더 많은 기상/수문 데이터 소스 통합 가능
"""
    
    print(guide)


if __name__ == "__main__":
    # 데모 실행
    asyncio.run(demo_scenarios())
    
    # ChatGPT 통합 예시
    chatgpt_integration_example()
    
    # 사용법 가이드
    usage_guide() 