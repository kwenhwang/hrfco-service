# HRFCO MCP Server

대한민국 수문 데이터터 API를 Claude Desktop과 연동하는 MCP(Model Context Protocol) 서버입니다.

## 🎉 현재 상태

✅ **API 키 테스트 성공**: 실제 HRFCO API 키로 모든 데이터 타입 테스트 완료
✅ **MCP 서버 준비 완료**: Claude Desktop에서 사용 가능
✅ **GitHub Actions 설정**: 자동 배포 워크플로우 구성
✅ **Docker 이미지**: 컨테이너화 완료
✅ **향상된 분석 기능**: 위험 수위 기준 활용 및 종합 분석 기능 추가

## 📊 지원하는 데이터

- **수위 데이터** (waterlevel): 1,000+ 관측소
- **댐 데이터** (dam): 100+ 댐
- **강수량 데이터** (rainfall): 500+ 관측소

## 🚀 빠른 시작

### 1. Claude Desktop에서 사용

1. **MCP 설정 파일 복사**
   ```bash
   # Windows
   copy claude_mcp_config.json "%APPDATA%\Claude\claude_desktop_config.json"
   
   # macOS
   cp claude_mcp_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Claude Desktop 재시작**

3. **사용 예시**
   ```
   Claude: 한강의 현재 수위 데이터를 알려줘
   Claude: 하동군 대석교의 위험 수위 상태를 분석해줘
   Claude: 부산 지역의 수위 관측소 현황을 요약해줘
   ```

### 2. 로컬 개발 환경

```bash
# 저장소 클론
git clone https://github.com/kwenhwang/hrfco-service.git
cd hrfco-service

# 의존성 설치
pip install -r requirements.txt

# API 키 설정
$env:HRFCO_API_KEY = "FE18B23B-A81B-4246-9674-E8D641902A42"

# 테스트 실행
python test_api.py

# 향상된 기능 테스트
python test_mcp_enhanced.py

# MCP 서버 실행
python mcp_server.py
```

### 3. Docker로 실행

```bash
# 이미지 빌드
docker build -t hrfco-mcp-server .

# 컨테이너 실행
docker run -p 8000:8000 hrfco-mcp-server
```

## 🔧 설정

### 환경 변수

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `HRFCO_API_KEY` | HRFCO API 키 | ✅ |

### API 키 발급

1. [한국수자원공사 API](https://www.data.go.kr/data/15000581/openapi.do) 접속
2. API 키 신청 및 발급
3. 환경 변수로 설정

## 📁 프로젝트 구조

```
hrfco-service/
├── src/hrfco_service/     # 핵심 서비스 코드
├── mcp_server.py          # MCP 서버 메인
├── test_api.py           # API 테스트
├── test_mcp_enhanced.py  # 향상된 기능 테스트
├── Dockerfile            # Docker 설정
├── requirements.txt      # Python 의존성
└── .github/workflows/    # GitHub Actions
```

## 🛠️ 개발

### API 테스트

```bash
python test_api.py
```

### MCP 서버 테스트

```bash
python test_mcp_direct.py
```

### 향상된 기능 테스트

```bash
python test_mcp_enhanced.py
```

### Docker 빌드

```bash
docker build -t hrfco-mcp-server .
docker run --rm hrfco-mcp-server python test_api.py
```

## 🆕 새로운 기능

### 📊 데이터 양 최적화

Claude 사용량을 최적화하기 위해 데이터 양을 지능적으로 조절합니다:

### 🎯 기본 분석 (적은 데이터)
- **기본 데이터 개수**: 24개 (기존 48개에서 감소)
- **기본 시간 범위**: 48시간 (기존 72시간에서 감소)
- **최근 데이터**: 최근 5개만 포함
- **상세 분석**: 기본적으로 비활성화

### 🔍 상세 분석 (많은 데이터)
- **상세 분석 요청 시**: 최소 72개 데이터, 최소 168시간(7일)
- **최근 데이터**: 최근 10개 포함
- **통계 정보**: 상세 통계 및 상관관계 분석 포함
- **상관관계 분석**: 강우량-수위 상관관계 분석 포함

### 📈 사용 예시
```
"하동군 대석교 수위 분석해줘"  # 기본 분석 (적은 데이터)
"하동군 대석교 수위 상세 분석해줘"  # 상세 분석 (많은 데이터)
```

## 📊 데이터 가용성 개선

기존의 데이터 제한 문제를 해결하여 더 많은 시간 범위의 데이터를 조회할 수 있습니다:

- **시간 범위 확장**: 기본 48시간에서 최대 720시간(30일)까지 조회 가능
- **자동 날짜 계산**: 요청된 시간 범위에 따라 자동으로 시작/종료 날짜 계산
- **데이터 밀도 정보**: 실제 사용 가능한 데이터 개수와 요청된 데이터 개수 비교 제공
- **유연한 파라미터**: `hours` 파라미터로 조회 시간 범위 조정 가능

**개선된 응답 예시:**
```json
{
  "summary": {
    "total_records": 72,
    "total_available": 168,
    "hours_requested": 72,
    "data_count_requested": 48
  },
  "statistics": {
    "max_water_level": 4.25,
    "min_water_level": 0.90,
    "avg_water_level": 2.15,
    "current_water_level": 4.25,
    "analysis_period": {
      "start_time": "202507180900",
      "end_time": "202507251400",
      "hours": 168.0,
      "days": 7.0,
      "data_count": 168
    }
  }
}
```

### 1. 위험 수위 기준 활용

수위 관측소의 관심, 주의보, 경보, 심각 단계별 위험 수위 기준을 자동으로 분석합니다.

**사용 예시:**
```
"하동군 대석교의 위험 수위 상태를 분석해줘"
```

**응답 예시:**
```json
{
  "observatory_info": {
    "obs_code": "4009670",
    "obs_name": "하동군 대석교",
    "location": {"lat": 35.123, "lon": 127.456}
  },
  "thresholds": {
    "attention": 2.2,
    "warning": 4.0,
    "alert": 5.0,
    "serious": 5.9
  },
  "alert_analysis": {
    "attention": {
      "status": "exceeded",
      "threshold": 2.2,
      "current": 4.25,
      "margin": 2.05
    },
    "warning": {
      "status": "exceeded", 
      "threshold": 4.0,
      "current": 4.25,
      "margin": 0.25
    },
    "alert": {
      "status": "safe",
      "threshold": 5.0,
      "current": 4.25,
      "margin": 0.75
    }
  },
  "summary": {
    "total_records": 72,
    "total_available": 168,
    "hours_requested": 72,
    "data_count_requested": 48
  }
}
```

### 2. 종합 수문 분석

수위와 강우량 데이터를 함께 분석하여 상관관계와 위험도를 종합적으로 평가합니다.

**사용 예시:**
```
"하동군 대석교와 하동군(읍내리) 강우량 관측소의 종합 분석을 해줘"
```

**주요 기능:**
- 관측소 간 거리 계산
- 강우량-수위 상관관계 분석
- 위험 수위 기준 적용
- 변화 추세 분석

### 3. 지역별 위험 수위 상태 요약

지정된 지역의 모든 수위 관측소 상태를 한눈에 파악할 수 있습니다.

**사용 예시:**
```
"부산 지역의 수위 관측소 현황을 요약해줘"
"전국의 위험 수위 상태를 확인해줘"
```

### 4. 수계 종합 분석

같은 수계의 근접 시설들(수위, 강우량, 댐, 보)을 거리 기반으로 찾아 통합 분석합니다.

**사용 예시:**
```
"하동군 대석교 주변 20km 내의 모든 수문 시설을 종합 분석해줘"
"부산 지역의 수계별 종합 분석을 해줘"
```

**주요 기능:**
- 거리 기반 근접 시설 검색
- 수위, 강우량, 댐, 보 통합 분석
- 시설별 통계 및 위험도 평가
- 수계별 분포 통계 제공

**응답 예시:**
```json
{
  "region": "부산",
  "hydro_type": "waterlevel",
  "total_stations_checked": 15,
  "alert_statistics": {
    "normal": 10,
    "attention": 3,
    "warning": 2,
    "alert": 0,
    "serious": 0
  }
}
```

### 5. WAMIS API 수계 시설 검색

WAMIS API를 사용하여 특정 수계의 모든 수문 시설을 검색합니다.

**사용 예시:**
```
"낙동강 수계의 모든 수위 관측소를 찾아줘"
"한강 수계의 한국수자원공사 댐들을 검색해줘"
```

**주요 기능:**
- 수계별 시설 검색 (한강, 낙동강, 금강, 섬진강, 영산강, 제주도)
- 시설 타입별 필터링 (수위, 강우량, 기상, 댐)
- 관할기관별 필터링 (환경부, 한국수자원공사, 한국농어촌공사, 기상청, 한국수력원자력)
- 운영상태별 필터링 (운영중, 폐쇄)
- 시설 개수 통계 제공

**응답 예시:**
```json
{
  "search_parameters": {
    "basin": "낙동강",
    "basin_code": "2",
    "facility_types": ["waterlevel", "rainfall"],
    "management_org": "한국수자원공사",
    "operation_status": "y"
  },
  "facility_counts": {
    "waterlevel": 45,
    "rainfall": 32
  },
  "total_facilities": 77
}
```

### 6. 통합 온톨로지 기반 분석

홍수통제소, WAMIS, 기상청 API의 정보를 통합하여 정확한 수계 관계를 분석합니다.

**사용 예시:**
```
"하동군 대석교의 상류/하류 관측소들을 찾아줘"
"낙동강 수계의 모든 관측소 현황을 알려줘"
"4009670 관측소의 수계 관계를 분석해줘"
```

**주요 기능:**
- 3개 API 정보 통합 (홍수통제소, WAMIS, 기상청)
- 표준유역코드 기반 상류/하류 관계 분석
- 수계별 관측소 분포 및 통계
- 관측소 타입별 필터링 (수위, 강우량, 댐, 기상)
- 데이터 소스별 필터링 (hrfco, wamis, weather)

**응답 예시:**
```json
{
  "type": "water_system_analysis",
  "target_station": {
    "obs_code": "4009670",
    "obs_name": "하동군(대석교)",
    "obs_type": "waterlevel",
    "source": "hrfco"
  },
  "relationships": {
    "upstream": [
      {"obs_code": "40094090", "obs_name": "하동군(읍내리)", "obs_type": "rainfall"}
    ],
    "downstream": [
      {"obs_code": "4009680", "obs_name": "하동군(하동교)", "obs_type": "waterlevel"}
    ],
    "same_basin": [
      {"obs_code": "4009675", "obs_name": "하동군(횡천초교)", "obs_type": "rainfall"}
    ]
  },
  "summary": {
    "upstream_count": 1,
    "downstream_count": 1,
    "same_basin_count": 1
  }
}
```

## 🚀 배포

### GitHub Actions 자동 배포

1. **GitHub Secrets 설정**
   - `HRFCO_API_KEY`: API 키
   - `DOCKER_USERNAME`: Docker Hub 사용자명
   - `DOCKER_PASSWORD`: Docker Hub 액세스 토큰
   - `GLAMA_HOST`: 배포 서버 호스트
   - `GLAMA_USERNAME`: SSH 사용자명
   - `GLAMA_SSH_KEY`: SSH 개인키

2. **자동 배포**
   - main 브랜치에 push하면 자동 실행
   - Docker 이미지 빌드 및 푸시
   - Glama 서버에 자동 배포

### 수동 배포

```bash
# Docker Hub에 푸시
docker build -t your-username/hrfco-mcp-server .
docker push your-username/hrfco-mcp-server

# Glama에 배포
ssh user@glama-server
cd /opt/hrfco-service
docker-compose pull
docker-compose up -d
```

## 📊 API 응답 예시

### 수위 데이터
```json
{
  "wlobscd": "2201614",
  "ymdhm": "202507161450",
  "wl": "0.64",
  "fw": "2.42"
}
```

### 댐 데이터
```json
{
  "dmobscd": "1001210",
  "ymdhm": "2025071613",
  "swl": "669.480",
  "inf": "0.380",
  "sfw": "6.790"
}
```

### 강수량 데이터
```json
{
  "rfobscd": "10014010",
  "ymdhm": "20250715",
  "rf": 22.0
}
```

## 🔍 문제 해결

### API 키 인증 실패
- API 키가 올바르게 설정되었는지 확인
- API 키가 유효한지 확인

### MCP 서버 연결 실패
- Claude Desktop 설정 파일 경로 확인
- Python 환경 및 의존성 확인

### 새로운 기능 테스트
```bash
# 향상된 기능 테스트
python test_mcp_enhanced.py

# 특정 관측소 분석
python -c "
import asyncio
from mcp_server import HRFCOMCPServer

async def test():
    server = HRFCOMCPServer()
    result = await server._analyze_water_level_with_thresholds({
        'obs_code': '4009670',
        'time_type': '1H',
        'count': 24
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))

asyncio.run(test())
"
```

## 📝 사용 예시

### 1. 기본 데이터 조회
```
사용자: "부산 지역의 수문 상태가 어때?"
Claude: "부산 지역의 수문 상태를 확인해드리겠습니다. 현재 부산 대동낙동강교 관측소의 수위는 3.42m입니다. 홍수 위험도는 낮은 상태이며, 실시간 모니터링이 권장됩니다."
```

### 2. 위험 수위 분석
```
사용자: "하동군 대석교의 위험 수위 상태를 분석해줘"
Claude: "하동군 대석교의 위험 수위 상태를 분석해드리겠습니다. 현재 수위는 4.25m로 주의보 기준(4.0m)을 초과하고 있습니다. 경보 기준(5.0m)까지 0.75m 여유가 있으며, 지속적인 모니터링이 필요합니다."
```

### 3. 종합 분석
```
사용자: "하동군 대석교와 주변 강우량 관측소의 종합 분석을 해줘"
Claude: "하동군 대석교와 하동군(읍내리) 강우량 관측소의 종합 분석 결과입니다. 두 관측소는 0.95km 거리에 있어 매우 근접합니다. 최근 48시간 동안 총 272mm의 강우가 있었으며, 이로 인해 수위가 1.25m에서 4.25m로 급상승했습니다. 현재 주의보 단계에 있으며, 지속적인 강우 시 경보 단계로 상승할 가능성이 있습니다."
```

### 4. 지역 현황 요약
```
사용자: "부산 지역의 수위 관측소 현황을 요약해줘"
Claude: "부산 지역의 수위 관측소 현황입니다. 총 15개 관측소를 확인했으며, 정상 상태 10개, 관심 단계 3개, 주의보 단계 2개입니다. 경보나 심각 단계는 없어 전반적으로 안정적인 상태입니다."
```

## 🆘 지원

### 문제 해결

**API 키 오류:**
```
"API 키가 설정되지 않았습니다"
```
→ `HRFCO_API_KEY` 환경변수를 설정하세요.

**관측소를 찾을 수 없음:**
```
"관측소를 찾을 수 없습니다"
```
→ 관측소 코드를 확인하거나 지역명으로 검색해보세요.

**hours 파라미터 오류:**
```
"HRFCOAPI.fetch_observatory_data() got an unexpected keyword argument 'hours'"
```
→ 최신 버전으로 업데이트하세요. 이 오류는 수정되었습니다.

**데이터 제한 문제:**
```
"데이터가 제한적입니다"
```
→ `hours` 파라미터를 사용하여 더 많은 시간 범위를 요청하세요.

### 지원 채널

- **이슈 리포트**: GitHub Issues
- **문서**: README.md 참조
- **예제**: `test_mcp_enhanced.py` 참조

---

**즐거운 수문 데이터 활용하세요! 🌊**