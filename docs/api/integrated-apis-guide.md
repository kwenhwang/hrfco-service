# 기상청, 홍수통제소, WAMIS 제원정보 통합 가이드

## 개요

이 문서는 기상청, 홍수통제소, WAMIS의 제원정보를 통합하여 관리하기 위한 가이드입니다. 각 기관의 관측소 정보를 체계적으로 정리하고 통합 방안을 제시합니다.

## 1. 기상청 지점정보

### 1.1 API 정보

#### 관측소 정보 조회 API
- **API 엔드포인트**: `https://apihub.kma.go.kr/api/typ01/url/stn_inf.php`
- **파라미터**:
  - `inf=SFC`: 지상관측 메타
  - `stn=0`: 지점번호 (0은 전체, 특정 지점번호 입력 가능)
  - `authKey=aTZ7pNU3TqW2e6TVNw6liA`: 인증키

#### 일별 관측 데이터 조회 API
- **API 엔드포인트**: `https://apihub.kma.go.kr/api/typ01/url/sfc_aws_day.php`
- **파라미터**:
  - `tm2=YYYYMMDD`: 날짜 (예: 20150406)
  - `obs=ta_max`: 관측 요소 (ta_max: 최고기온, ta_min: 최저기온, rn_day: 일강수량)
  - `stn=0`: 지점번호 (0은 전체, 특정 지점번호 입력 가능)
  - `disp=0`: 표시 옵션
  - `help=1`: 도움말 표시
  - `authKey=aTZ7pNU3TqW2e6TVNw6liA`: 인증키

#### 시간별 관측 데이터 조회 API
- **API 엔드포인트**: `https://apihub.kma.go.kr/api/typ01/url/awsh.php`
- **파라미터**:
  - `var=TA`: 관측 변수 (TA: 기온, RN: 강수량, WS: 풍속, WD: 풍향, HM: 습도, PA: 기압)
  - `tm=YYYYMMDDHHMM`: 시간 (예: 201508121500)
  - `stn=108`: 지점번호 (108: 서울, 0: 전체)
  - `help=1`: 도움말 표시
  - `authKey=aTZ7pNU3TqW2e6TVNw6liA`: 인증키

#### 데이터 형식
```
#START7777
# 지상 관측소 일자료
# 1. TM : 관측일시 (KST)
# 2. STN : 지점 지점번호
# 3. LON : 경도 (deg)
# 4. LAT : 위도 (deg)
# 5. HT : 지점 해발고도 (m)
# 6. VAL : 관측값
# YYMMDD STN LON LAT HT VAL
# KST ID (deg) (deg) (m)
20150406 90 128.56472000 38.25085000 18.06 10.1 강릉
```

#### API 사용 예시
```bash
# 관측소 정보 조회 (전체)
curl "https://apihub.kma.go.kr/api/typ01/url/stn_inf.php?inf=SFC&stn=0&authKey=aTZ7pNU3TqW2e6TVNw6liA"

# 관측소 정보 조회 (특정 지점)
curl "https://apihub.kma.go.kr/api/typ01/url/stn_inf.php?inf=SFC&stn=108&authKey=aTZ7pNU3TqW2e6TVNw6liA"

# 일별 최고기온 데이터 (전체)
curl "https://apihub.kma.go.kr/api/typ01/url/sfc_aws_day.php?tm2=20150406&obs=ta_max&stn=0&disp=0&help=1&authKey=aTZ7pNU3TqW2e6TVNw6liA"

# 시간별 기온 데이터 (서울)
curl "https://apihub.kma.go.kr/api/typ01/url/awsh.php?var=TA&tm=201508121500&help=1&authKey=aTZ7pNU3TqW2e6TVNw6liA&stn=108"
```

### 1.2 관측소 유형

#### ASOS (자동기상관측소)
- **파일**: `asos 지점정보.csv`
- **특징**: 
  - 지점번호: 90~296
  - 관측 항목: 기온, 습도, 강수량, 풍속, 풍향, 기압 등
  - 운영 기간: 1904년~현재
  - 총 관측소 수: 약 149개

#### AWS (자동기상관측소)
- **파일**: `aws 지점정보.csv`
- **특징**:
  - 지점번호: 12~661
  - 관측 항목: 기온, 습도, 강수량, 풍속, 풍향, 기압 등
  - 운영 기간: 1990년~현재
  - 총 관측소 수: 약 2,466개

### 1.3 데이터 구조
```csv
지점번호,시작일,종료일,지점명,상세주소,관할기관,위도,경도,고도,기준고도,관측고도,심층고도,지반고도
```

## 2. 홍수통제소 수문관측소

### 2.1 관측소 유형
- **수위관측소**: 하천 수위 측정
- **강우관측소**: 강수량 측정
- **댐관측소**: 댐 수위 및 방류량 측정
- **보관측소**: 보 수위 및 방류량 측정

### 2.2 API 정보
- **기본 URL**: 홍수통제소 API
- **데이터 타입**: waterlevel, rainfall, dam, bo
- **시간 단위**: 10M, 1H, 1D

### 2.3 주요 기능
- 실시간 수문 데이터 조회
- 관측소 정보 조회
- 위험 수위 분석
- 종합 수문 분석

## 3. WAMIS (Water Management Information System)

### 3.1 시스템 개요
- **목적**: 수자원 관리 정보 시스템
- **관리기관**: 환경부, 한국수자원공사, 한국농어촌공사 등
- **수계**: 한강, 낙동강, 금강, 섬진강, 영산강, 제주도

### 3.2 관측소 유형
- **수위관측소**: 하천 수위 측정
- **강우관측소**: 강수량 측정
- **기상관측소**: 기상 데이터 측정
- **댐관측소**: 댐 운영 데이터

### 3.3 API 기능
- 수계별 시설 검색
- 관측소 정보 조회
- 실시간 데이터 제공
- 통계 분석 기능

## 4. 통합 관리 방안

### 4.1 데이터 표준화

#### 공통 필드 정의
```json
{
  "obs_code": "관측소 코드",
  "obs_name": "관측소명",
  "obs_type": "관측소 유형",
  "latitude": "위도",
  "longitude": "경도",
  "elevation": "고도",
  "basin": "수계",
  "management_org": "관리기관",
  "start_date": "시작일",
  "end_date": "종료일",
  "status": "운영상태"
}
```

#### 관측소 유형 분류
- **기상**: ASOS, AWS, 기상관측소
- **수문**: 수위관측소, 강우관측소
- **댐보**: 댐관측소, 보관측소
- **종합**: 다중 관측 기능

### 4.2 통합 API 설계

#### 기본 엔드포인트
```
GET /api/observatories
GET /api/observatories/{obs_code}
GET /api/observatories/search
GET /api/observatories/nearby
```

#### 데이터 조회 엔드포인트
```
GET /api/data/{obs_code}
GET /api/data/nearby
GET /api/data/basin/{basin}
```

### 4.3 데이터 매핑 규칙

#### 기상청 → 통합 시스템
- 지점번호 → obs_code
- 지점명 → obs_name
- 위도/경도 → latitude/longitude
- 고도 → elevation
- 관할기관 → management_org

#### 홍수통제소 → 통합 시스템
- 관측소코드 → obs_code
- 관측소명 → obs_name
- 관측소유형 → obs_type
- 위도/경도 → latitude/longitude

#### WAMIS → 통합 시스템
- 시설코드 → obs_code
- 시설명 → obs_name
- 시설유형 → obs_type
- 수계 → basin

## 5. 구현 가이드

### 5.1 데이터베이스 스키마

```sql
-- 관측소 기본 정보
CREATE TABLE observatories (
    obs_code VARCHAR(20) PRIMARY KEY,
    obs_name VARCHAR(100) NOT NULL,
    obs_type VARCHAR(20) NOT NULL,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    elevation DECIMAL(8,2),
    basin VARCHAR(20),
    management_org VARCHAR(50),
    start_date DATE,
    end_date DATE,
    status VARCHAR(10) DEFAULT 'ACTIVE',
    source VARCHAR(20) NOT NULL, -- KMA, HRFCO, WAMIS
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 관측 데이터
CREATE TABLE observation_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    obs_code VARCHAR(20),
    obs_time DATETIME,
    data_type VARCHAR(20), -- water_level, rainfall, temperature, etc.
    value DECIMAL(10,3),
    unit VARCHAR(10),
    quality_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (obs_code) REFERENCES observatories(obs_code)
);
```

### 5.2 API 구현 예시

```python
# 통합 관측소 정보 조회
def get_observatory_info(obs_code):
    # 1. 기상청 데이터 확인
    kma_data = get_kma_observatory(obs_code)
    if kma_data:
        return map_kma_to_unified(kma_data)
    
    # 2. 홍수통제소 데이터 확인
    hrfco_data = get_hrfco_observatory(obs_code)
    if hrfco_data:
        return map_hrfco_to_unified(hrfco_data)
    
    # 3. WAMIS 데이터 확인
    wamis_data = get_wamis_observatory(obs_code)
    if wamis_data:
        return map_wamis_to_unified(wamis_data)
    
    return None

# 근처 관측소 검색
def get_nearby_observatories(lat, lon, radius_km=10):
    observatories = []
    
    # 각 소스에서 근처 관측소 검색
    kma_nearby = get_kma_nearby(lat, lon, radius_km)
    hrfco_nearby = get_hrfco_nearby(lat, lon, radius_km)
    wamis_nearby = get_wamis_nearby(lat, lon, radius_km)
    
    # 결과 통합 및 중복 제거
    all_observatories = kma_nearby + hrfco_nearby + wamis_nearby
    return deduplicate_observatories(all_observatories)
```

## 6. 데이터 품질 관리

### 6.1 중복 데이터 처리
- **위치 기반 중복 검사**: 위도/경도 기준으로 근접한 관측소 식별
- **이름 기반 중복 검사**: 관측소명 유사도 분석
- **코드 매핑**: 기관별 코드 간 매핑 테이블 구축

### 6.2 데이터 검증
- **위치 검증**: 위도/경도 범위 검사
- **시간 검증**: 시작일/종료일 일관성 검사
- **코드 검증**: 관측소 코드 형식 검증

### 6.3 데이터 업데이트
- **정기 업데이트**: 일/주/월 단위 데이터 동기화
- **변경 감지**: 관측소 정보 변경 시 알림
- **버전 관리**: 데이터 변경 이력 추적

## 7. 활용 방안

### 7.1 종합 수문 분석
- 기상 데이터와 수문 데이터 연계 분석
- 강우-유출 관계 분석
- 홍수 예측 모델 개발

### 7.2 실시간 모니터링
- 전국 관측소 실시간 상태 모니터링
- 이상 데이터 자동 감지
- 알림 시스템 구축

### 7.3 공간 분석
- 관측소 분포 분석
- 관측망 밀도 분석
- 관측 빈도 분석

## 8. 향후 계획

### 8.1 단기 계획 (3개월)
- [ ] 통합 데이터베이스 구축
- [ ] 기본 API 개발
- [ ] 데이터 매핑 규칙 확정

### 8.2 중기 계획 (6개월)
- [ ] 실시간 데이터 연동
- [ ] 웹 대시보드 개발
- [ ] 데이터 품질 관리 시스템 구축

### 8.3 장기 계획 (1년)
- [ ] AI 기반 데이터 분석
- [ ] 예측 모델 개발
- [ ] 모바일 앱 개발

## 9. 참고 자료

### 9.1 API 문서
- [기상청 API 가이드](https://apihub.kma.go.kr/)
- [홍수통제소 API 문서](https://www.hrfco.go.kr/)
- [WAMIS API 문서](https://www.wamis.go.kr/)

### 9.2 데이터 사전
- [기상청 관측소 목록](asos 지점정보.csv)
- [AWS 관측소 목록](aws 지점정보.csv)
- [수문관측소 목록](수문관측소_목록.csv)

### 9.3 관련 프로젝트
- [HRFCO Service](https://github.com/your-repo/hrfco-service)
- [통합 수문 시스템](https://github.com/your-repo/integrated-hydro-system)

---

**문서 버전**: 1.0  
**최종 업데이트**: 2024년 12월  
**작성자**: AI Assistant  
**검토자**: 개발팀 