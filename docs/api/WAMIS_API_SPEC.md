# WAMIS API 명세서

## 개요
WAMIS(Water Management Information System)는 한국수자원공사에서 제공하는 수자원 관리 정보 시스템의 공개 API입니다.

## 기본 정보
- **Base URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/`
- **출력 형식**: JSON (기본값), XML
- **인코딩**: UTF-8

---

## 1. 댐검색 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_dammain`
- **메소드**: GET
- **설명**: 댐 정보를 검색하는 API

### 요청 파라미터

| 변수명 | 타입 | 필수 | 설명 | 범위 |
|--------|------|------|------|------|
| `basin` | String | ❌ | 권역 | 1: 한강<br>2: 낙동강<br>3: 금강<br>4: 섬진강<br>5: 영산강<br>6: 제주도 |
| `mngorg` | String | ❌ | 관할기관 | 1: 환경부<br>2: 한국수자원공사<br>3: 한국농어촌공사<br>9: 한국수력원자력<br>12: 기타 |
| `damdvcd` | String | ❌ | 관측방법 | 1: 다목적<br>2: 생공전용<br>3: 발전지용<br>4: 조정지댐<br>5: 기타 |
| `keynm` | String | ❌ | 관측소명 | - |
| `sort` | String | ❌ | 정렬방법 | 1: 관측소코드<br>2: 관측소명<br>**기본값**: 1 |

### 응답 필드

| 필드명 | 타입 | 설명 | 비고 |
|--------|------|------|------|
| `damcd` | String | 댐코드 | - |
| `damnm` | String | 댐명 | - |
| `bbsncd` | String | 권역코드 | - |
| `sbsncd` | String | 표준유역코드 | - |
| `bbsnnm` | String | 대권역명 | - |
| `mggvnm` | String | 관할기관 | - |

### 사용 예시
```bash
# 모든 댐 검색
GET /mn_dammain

# 한강 권역 댐 검색
GET /mn_dammain?basin=1

# 한국수자원공사 관할 댐 검색
GET /mn_dammain?mngorg=2&basin=1
```

---

## 2. 댐수문정보 일자료 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_dtdata`
- **메소드**: GET
- **설명**: 댐의 일별 수문 정보를 조회하는 API

### 요청 파라미터

| 변수명 | 타입 | 필수 | 설명 | 범위 |
|--------|------|------|------|------|
| `damcd` | String | ✅ | 관측소코드 | - |
| `startdt` | String | ❌ | 관측기간-시작일 | YYYYMMDD |
| `enddt` | String | ❌ | 관측기간-종료일 | YYYYMMDD |
| `output` | String | ❌ | 출력 포맷 | xml, json<br>**기본값**: json |

### 응답 필드

| 필드명 | 타입 | 설명 | 단위 |
|--------|------|------|------|
| `obsymd` | String | 관측년월일 | - |
| `rwl` | String | 저수위 | EL.m |
| `iqty` | String | 유입량 | ㎥/s |
| `tdqty` | String | 총 방류량 | ㎥/s |
| `edqty` | String | 발전방류량 | ㎥/s |
| `spdqty` | String | 여수로방류량 | ㎥/s |
| `otltdqty` | String | 기타방류량 | ㎥/s |
| `itqty` | String | 용수공급량 | ㎥/s |
| `rf` | String | 댐유역평균강우량 | ㎜ |

### 사용 예시
```bash
# 특정 댐의 일자료 조회
GET /mn_dtdata?damcd=5002201&startdt=20240101&enddt=20240131

# JSON 형식으로 출력
GET /mn_dtdata?damcd=5002201&output=json
```

---

## 3. 댐수문정보 시자료 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_hrdata`
- **메소드**: GET
- **설명**: 댐의 시간별 수문 정보를 조회하는 API

### 요청 파라미터

| 변수명 | 타입 | 필수 | 설명 | 범위 |
|--------|------|------|------|------|
| `damcd` | String | ✅ | 관측소코드 | - |
| `startdt` | String | ❌ | 관측기간-시작일 | YYYYMMDD |
| `enddt` | String | ❌ | 관측기간-종료일 | YYYYMMDD |
| `output` | String | ❌ | 출력 포맷 | xml, json<br>**기본값**: json |

### 응답 필드

| 필드명 | 타입 | 설명 | 단위 |
|--------|------|------|------|
| `obsdh` | String | 관측일시 | - |
| `rwl` | String | 저수위 | EL.m |
| `ospilwl` | String | 방수로수위 | EL.m |
| `rsqty` | String | 저수량 | M㎥ |
| `rsrt` | String | 저수율 | % |
| `iqty` | String | 유입량 | ㎥/s |
| `etqty` | String | 공용량 | 백만㎥ |
| `tdqty` | String | 총 방류량 | ㎥/s |
| `edqty` | String | 발전방류량 | ㎥/s |
| `spdqty` | String | 여수로방류량 | ㎥/s |
| `otltdqty` | String | 기타방류량 | ㎥/s |
| `itqty` | String | 취수량 | ㎥/s |
| `dambsarf` | String | 댐유역평균우량 | mm |

### 사용 예시
```bash
# 특정 댐의 시자료 조회
GET /mn_hrdata?damcd=5002201&startdt=20240101&enddt=20240102

# XML 형식으로 출력
GET /mn_hrdata?damcd=5002201&output=xml
```

---

## 4. 댐수문정보 월자료 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_mndata`
- **메소드**: GET
- **설명**: 댐의 월별 수문 정보를 조회하는 API

### 요청 파라미터

| 변수명 | 타입 | 필수 | 설명 | 범위 |
|--------|------|------|------|------|
| `damcd` | String | ✅ | 관측소코드 | - |
| `startyear` | String | ❌ | 관측기간-시작년 | YYYY |
| `endyear` | String | ❌ | 관측기간-종료년 | YYYY |
| `output` | String | ❌ | 출력 포맷 | xml, json<br>**기본값**: json |

### 응답 필드

| 필드명 | 타입 | 설명 | 단위 |
|--------|------|------|------|
| `obsymd` | String | 관측년월 | - |
| `mnwl` | String | 저수위 최저 | EL.m |
| `avwl` | String | 저수위 평균 | EL.m |
| `mxwl` | String | 저수위 최고 | EL.m |
| `mniqty` | String | 유입량 최저 | ㎥/s |
| `aviqty` | String | 유입량 평균 | ㎥/s |
| `mxiqty` | String | 유입량 최고 | ㎥/s |
| `mntdqty` | String | 총방류량 최저 | ㎥/s |
| `avtdqty` | String | 총방류량 평균 | ㎥/s |
| `mxtdqty` | String | 총방류량 최고 | ㎥/s |
| `mnsqty` | String | 수문방류량 최저 | ㎥/s |
| `avsqty` | String | 수문방류량 평균 | ㎥/s |
| `mxsqty` | String | 수문방류량 최고 | ㎥/s |
| `mnrf` | String | 유역평균우량 최저 | ㎜ |
| `avrf` | String | 유역평균우량 평균 | ㎜ |
| `mxrf` | String | 유역평균우량 최고 | ㎜ |

### 사용 예시
```bash
# 특정 댐의 월자료 조회
GET /mn_mndata?damcd=5002201&startyear=2023&endyear=2024

# JSON 형식으로 출력
GET /mn_mndata?damcd=5002201&output=json
```

---

## 권역 코드 매핑

### 대권역 (basin)
| 코드 | 권역명 |
|------|--------|
| 1 | 한강 |
| 2 | 낙동강 |
| 3 | 금강 |
| 4 | 섬진강 |
| 5 | 영산강 |
| 6 | 제주도 |

### 관할기관 (mngorg)
| 코드 | 기관명 |
|------|--------|
| 1 | 환경부 |
| 2 | 한국수자원공사 |
| 3 | 한국농어촌공사 |
| 9 | 한국수력원자력 |
| 12 | 기타 |

### 관측방법 (damdvcd)
| 코드 | 방법 |
|------|------|
| 1 | 다목적 |
| 2 | 생공전용 |
| 3 | 발전지용 |
| 4 | 조정지댐 |
| 5 | 기타 |

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| 200 | 정상 처리 |
| 400 | 잘못된 요청 |
| 404 | 리소스를 찾을 수 없음 |
| 500 | 서버 내부 오류 |

---

## 주의사항

1. **API 호출 제한**: 과도한 API 호출은 제한될 수 있습니다.
2. **데이터 지연**: 실시간 데이터는 최대 1시간 지연될 수 있습니다.
3. **인증**: 현재 버전은 인증이 필요하지 않습니다.
4. **CORS**: 웹 브라우저에서 직접 호출 시 CORS 정책을 확인하세요.

---

## 연락처

- **개발자**: 한국수자원공사
- **문서 버전**: 1.0
- **최종 업데이트**: 2024년 1월

---

*이 문서는 WAMIS API의 공식 명세를 기반으로 작성되었습니다.* 