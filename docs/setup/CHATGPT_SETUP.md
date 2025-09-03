# ChatGPT Function Calling 통합 가이드

홍수통제소(HRFCO)와 기상관측소 API를 ChatGPT Function Calling으로 통합하여 사용하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 필요한 패키지 설치
pip install openai httpx python-dotenv

# 환경 변수 설정 (.env 파일)
HRFCO_API_KEY=FE18B23B-A81B-4246-9674-E8D641902A42
KMA_API_KEY=bI7VVvskaOdKJGMej%2F2zJzaxEyiCeGn8kLEidNAxHV7%2FRLiWMCAIlqMY08bwU1MqnakQ4ulEirojxHU800l%2BMA%3D%3D
OPENAI_API_KEY=your_openai_api_key
```

### 2. 기본 사용법

```python
import asyncio
from chatgpt_functions import CHATGPT_FUNCTIONS, execute_function

# ChatGPT에 등록할 함수 정의 확인
print(CHATGPT_FUNCTIONS)

# 개별 함수 테스트
async def test():
    result = await execute_function("get_water_level_data", {
        "obs_code": "4009670",
        "hours": 48
    })
    print(result)

asyncio.run(test())
```

## 📋 사용 가능한 함수들

### 🌊 수위 관련 함수

#### `get_water_level_data`
실시간 수위 데이터와 위험도 분석을 제공합니다.

**매개변수:**
- `obs_code` (필수): 수위 관측소 코드
- `hours` (선택): 조회 시간 범위 (기본값: 48시간)
- `time_type` (선택): 시간 단위 (10M/1H/1D, 기본값: 1H)
- `include_thresholds` (선택): 위험 수위 기준 포함 여부 (기본값: true)

**반환 데이터:**
- 관측소 정보 (이름, 주소, 좌표)
- 현재 수위 및 위험도 평가
- 위험 수위 기준 (관심/주의보/경보/심각)
- 다음 단계까지 여유 수위
- 최근 데이터 목록

**사용 예시:**
```python
result = await execute_function("get_water_level_data", {
    "obs_code": "4009670",  # 하동군(대석교)
    "hours": 72,
    "include_thresholds": True
})
```

### 🌧️ 강우량 관련 함수

#### `get_rainfall_data`
실시간 강우량 데이터와 통계를 제공합니다.

**매개변수:**
- `obs_code` (필수): 강우량 관측소 코드
- `hours` (선택): 조회 시간 범위 (기본값: 48시간)
- `time_type` (선택): 시간 단위 (기본값: 1H)

**반환 데이터:**
- 관측소 정보
- 강우량 통계 (총량, 최대 시간당, 최근 1시간/6시간)
- 최근 데이터 목록

### 🔍 검색 관련 함수

#### `search_nearby_observatories`
특정 지역 주변의 수위, 강우량, 댐 관측소를 검색합니다.

**매개변수:**
- `address` (필수): 검색할 주소 또는 지역명
- `radius_km` (선택): 검색 반경 (기본값: 20km)
- `hydro_type` (선택): 관측소 유형 (waterlevel/rainfall/dam/all, 기본값: all)

**사용 예시:**
```python
result = await execute_function("search_nearby_observatories", {
    "address": "하동군 대석교",
    "radius_km": 15,
    "hydro_type": "all"
})
```

#### `search_weather_stations`
기상관측소를 검색합니다.

**매개변수:**
- `address` (필수): 검색할 주소
- `radius_km` (선택): 검색 반경 (기본값: 30km)

### 📊 종합 분석 함수

#### `get_comprehensive_flood_analysis`
수위와 강우량을 종합하여 홍수 위험도를 분석합니다.

**매개변수:**
- `water_level_obs` (필수): 수위 관측소 코드
- `rainfall_obs` (선택): 강우량 관측소 코드
- `hours` (선택): 분석 기간 (기본값: 72시간)
- `include_forecast` (선택): 예보 정보 포함 여부 (기본값: false)

**반환 데이터:**
- 수위 분석 결과
- 강우량 분석 결과 (제공된 경우)
- 종합 홍수 위험도 평가
- 위험 요소별 점수

### 🌡️ 기상 관련 함수

#### `get_weather_data`
기상관측소의 날씨 데이터를 조회합니다.

**매개변수:**
- `station_id` (필수): 기상관측소 ID
- `hours` (선택): 조회 시간 범위 (기본값: 24시간)
- `data_type` (선택): 데이터 유형 (current/hourly/daily, 기본값: hourly)

## 🤖 ChatGPT 통합 방법

### 1. Function Definitions 등록

```python
import openai
from chatgpt_functions import CHATGPT_FUNCTIONS

# OpenAI 클라이언트 설정
client = openai.OpenAI(api_key="your-api-key")

# ChatGPT 호출 시 functions 매개변수에 전달
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "하동군 대석교 수위 상황을 알려주세요"}
    ],
    functions=CHATGPT_FUNCTIONS,
    function_call="auto"
)
```

### 2. 완전한 통합 예시

```python
import openai
import json
import asyncio
from chatgpt_functions import CHATGPT_FUNCTIONS, execute_function

async def ask_chatgpt_with_functions(user_message):
    client = openai.OpenAI(api_key="your-api-key")
    
    # 첫 번째 ChatGPT 호출
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 홍수 및 기상 정보 전문가입니다."},
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

# 사용 예시
async def main():
    answer = await ask_chatgpt_with_functions("하동군 대석교 수위가 위험한가요?")
    print(answer)

asyncio.run(main())
```

## 💡 실제 사용 시나리오

### 시나리오 1: 수위 위험도 문의
**사용자:** "하동군 대석교 수위가 위험한가요?"

**ChatGPT 동작:**
1. `get_water_level_data` 함수 호출
2. 실시간 수위와 위험 기준 비교
3. 위험도 평가 및 설명 제공

### 시나리오 2: 주변 관측소 검색
**사용자:** "하동군 주변에 어떤 관측소들이 있나요?"

**ChatGPT 동작:**
1. `search_nearby_observatories` 함수 호출
2. 반경 내 수위, 강우량, 댐 관측소 검색
3. 거리순으로 정렬하여 목록 제공

### 시나리오 3: 종합 홍수 분석
**사용자:** "최근 강우량이 수위에 미치는 영향을 분석해주세요"

**ChatGPT 동작:**
1. `get_comprehensive_flood_analysis` 함수 호출
2. 수위와 강우량 데이터 종합 분석
3. 상관관계 및 홍수 위험도 평가

## 🔧 고급 설정

### 데모 모드 사용
API 키가 없어도 데모 데이터로 테스트 가능합니다:

```python
# .env 파일에서 API 키를 주석처리하거나 제거
# HRFCO_API_KEY=your_api_key

# 함수 호출 시 자동으로 데모 데이터 사용
result = await execute_function("get_water_level_data", {
    "obs_code": "4009670"
})
```

### 커스텀 함수 추가
새로운 함수를 추가하려면:

1. `chatgpt_functions.py`에서 `CHATGPT_FUNCTIONS` 리스트에 함수 정의 추가
2. 함수 구현 후 `FUNCTION_ROUTER`에 등록
3. ChatGPT가 새 함수를 인식하고 사용 가능

### 오류 처리
```python
async def safe_execute_function(function_name, arguments):
    try:
        result = await execute_function(function_name, arguments)
        return result
    except Exception as e:
        return f"함수 실행 중 오류 발생: {str(e)}"
```

## 📊 테스트 및 검증

### 개별 함수 테스트
```bash
# 데모 실행
python chatgpt_usage_example.py
```

### ChatGPT 통합 테스트
```python
# 실제 ChatGPT API와 통합 테스트
python -c "
import asyncio
from chatgpt_usage_example import demo_scenarios
asyncio.run(demo_scenarios())
"
```

## ⚠️ 주의사항

1. **API 키 보안**: API 키는 환경 변수로 관리하고 코드에 직접 포함하지 마세요
2. **API 제한**: 각 API의 호출 제한을 확인하고 적절히 사용하세요
3. **데이터 신뢰성**: 실시간 데이터는 네트워크 상황에 따라 지연될 수 있습니다
4. **비용 관리**: OpenAI API 사용료를 모니터링하세요

## 🆘 문제 해결

### 자주 발생하는 오류

**1. API 키 오류**
```
⚠️ HRFCO_API_KEY가 설정되지 않았습니다.
```
→ `.env` 파일에 올바른 API 키를 설정하세요

**2. 네트워크 오류**
```
API 오류: Connection timeout
```
→ 네트워크 연결을 확인하고 재시도하세요

**3. 함수 호출 오류**
```
지원하지 않는 함수입니다: function_name
```
→ 함수명이 올바른지 확인하세요

### 지원 및 문의

- 이슈 리포팅: GitHub Issues
- 문서 업데이트: Pull Request 환영
- 추가 기능 요청: Feature Request 작성

## 📈 향후 계획

- [ ] 더 많은 기상 데이터 소스 통합
- [ ] 예보 정보 제공
- [ ] 실시간 알림 기능
- [ ] 데이터 시각화 통합
- [ ] 다국어 지원 