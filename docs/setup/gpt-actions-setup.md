# GPT Actions HTTPS 문제 해결 가이드

## ❌ **문제 상황**

GPT Actions에서 홍수통제소 API를 직접 호출할 때 발생하는 오류들:

1. **잘못된 API 키**: 기상청 API 키를 홍수통제소 API에 사용
2. **잘못된 URL 패턴**: 존재하지 않는 엔드포인트 호출
3. **HTTPS 요구사항**: GPT Actions는 HTTPS만 허용하지만 홍수통제소 API는 HTTP만 지원

### 오류 메시지:
```
None of the provided servers is under the root origin https://api.hrfco.go.kr
Server URL http://api.hrfco.go.kr is not under the root origin https://api.hrfco.go.kr; ignoring it
```

## ✅ **해결 방법: HTTPS 프록시 서버**

### 1. 프록시 서버 아키텍처

```
GPT Actions (HTTPS) → Proxy Server (HTTPS) → HRFCO API (HTTP)
```

### 2. 생성된 파일들

#### `gpt_actions_proxy.py` - FastAPI 프록시 서버
- **기능**: HTTP 홍수통제소 API를 HTTPS로 래핑
- **엔드포인트**:
  - `/waterlevel/data` - 수위 데이터 조회
  - `/waterlevel/observatories` - 수위 관측소 정보
  - `/rainfall/data` - 강우량 데이터 조회
  - `/analysis/water_level/{obscd}` - 종합 수위 분석

#### `gpt_actions_proxy_schema.json` - GPT Actions 스키마
- **기능**: GPT Actions에서 사용할 OpenAPI 스키마
- **서버 URL**: `https://your-proxy-domain.com`

## 🚀 **배포 방법**

### 옵션 1: 클라우드 배포 (권장)

#### **Vercel 배포**
```bash
# 1. Vercel CLI 설치
npm i -g vercel

# 2. 프로젝트 배포
vercel --prod

# 3. 환경 변수 설정
vercel env add HRFCO_API_KEY
# 값: FE18B23B-A81B-4246-9674-E8D641902A42
```

#### **Heroku 배포**
```bash
# 1. 프로젝트 생성
heroku create hrfco-proxy

# 2. 환경 변수 설정
heroku config:set HRFCO_API_KEY=FE18B23B-A81B-4246-9674-E8D641902A42

# 3. 배포
git push heroku main
```

#### **Railway 배포**
```bash
# 1. Railway CLI 설치
npm install -g @railway/cli

# 2. 프로젝트 연결
railway login
railway link

# 3. 환경 변수 설정
railway variables set HRFCO_API_KEY=FE18B23B-A81B-4246-9674-E8D641902A42

# 4. 배포
railway up
```

### 옵션 2: 로컬 테스트

```bash
# 1. 서버 실행
python run_proxy_server.py

# 2. 테스트
curl "http://localhost:8000/waterlevel/data?obscd=4009670&hours=24"

# 3. API 문서 확인
# 브라우저에서 http://localhost:8000/docs 접속
```

## 📋 **GPT Actions 설정**

### 1. 배포 완료 후 스키마 업데이트

`gpt_actions_proxy_schema.json`에서 서버 URL 수정:

```json
{
  "servers": [
    {
      "url": "https://your-actual-domain.com",
      "description": "HRFCO API HTTPS Proxy Server"
    }
  ]
}
```

### 2. ChatGPT GPT에 Actions 등록

1. ChatGPT GPT 설정 페이지에서 "Actions" 탭 선택
2. "Create new action" 클릭
3. `gpt_actions_proxy_schema.json` 내용을 Schema에 붙여넣기
4. Authentication을 "None"으로 설정
5. "Test" 버튼으로 동작 확인

### 3. 사용 가능한 질문들

✅ **"하동군 대석교 수위가 위험한가요?"**
- `analyzeWaterLevel` 액션 호출
- 실시간 수위와 위험도 분석 제공

✅ **"관측소 4009670의 최근 48시간 수위 데이터를 조회해주세요"**
- `getWaterLevelData` 액션 호출
- 상세 수위 데이터 반환

✅ **"모든 수위 관측소 목록을 보여주세요"**
- `getWaterLevelObservatories` 액션 호출
- 전국 수위 관측소 정보 제공

## 🔧 **프록시 서버 주요 기능**

### 1. 자동 날짜 범위 계산
```python
# hours 파라미터로 자동 계산
# hours=24 → 최근 24시간 데이터 조회
```

### 2. 통계 계산
```python
# 강우량 통계 자동 계산
"statistics": {
    "total_rainfall": 15.2,
    "max_rainfall": 5.0,
    "data_points": 48
}
```

### 3. 위험도 분석
```python
# 수위 위험도 자동 평가
"alert_status": "안전",
"margin_to_next_level": 1.38
```

## 🛠️ **문제 해결**

### 1. CORS 오류
프록시 서버에 CORS 미들웨어가 설정되어 있음:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. SSL 인증서 (프로덕션용)
클라우드 배포 시 자동으로 HTTPS 인증서가 제공됨
- Vercel: 자동 HTTPS
- Heroku: 자동 HTTPS  
- Railway: 자동 HTTPS

### 3. API 키 보안
환경 변수로 API 키 관리:
```bash
HRFCO_API_KEY=FE18B23B-A81B-4246-9674-E8D641902A42
```

## 📊 **테스트 예시**

### 수위 데이터 조회
```bash
curl "https://your-domain.com/waterlevel/data?obscd=4009670&hours=48"
```

### 수위 종합 분석
```bash
curl "https://your-domain.com/analysis/water_level/4009670?hours=72&include_thresholds=true"
```

### 관측소 정보 조회
```bash
curl "https://your-domain.com/waterlevel/observatories"
```

## 🎯 **장점**

1. **HTTPS 호환**: GPT Actions에서 바로 사용 가능
2. **API 키 숨김**: 프론트엔드에 API 키 노출 없음
3. **데이터 가공**: 원본 API보다 사용하기 쉬운 형태로 응답
4. **오류 처리**: 안정적인 오류 처리 및 응답
5. **문서화**: FastAPI 자동 문서 생성 (`/docs`)

## 🔄 **업데이트 및 유지보수**

### 새로운 기능 추가
1. `gpt_actions_proxy.py`에 새 엔드포인트 추가
2. `gpt_actions_proxy_schema.json`에 스키마 업데이트
3. 클라우드 서비스에 재배포
4. GPT Actions 스키마 업데이트

### 모니터링
- 클라우드 서비스의 로그 확인
- API 응답 시간 모니터링
- 오류율 추적

이제 GPT Actions에서 안정적으로 홍수통제소 데이터를 조회할 수 있습니다! 🌊 