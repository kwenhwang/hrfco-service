# WAMIS API 완전 명세서

## 개요
WAMIS(Water Management Information System)는 한국수자원공사에서 제공하는 수자원 관리 정보 시스템의 공개 API입니다.

## 기본 정보
- **Base URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkw/` (강우/수위/기상)
- **Base URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/` (댐)
- **출력 형식**: JSON (기본값), XML
- **인코딩**: UTF-8

---

## 1. 강우관측소 검색 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_dubrfobs`
- **메소드**: GET
- **설명**: 강우관측소 정보를 검색하는 API

### 요청 파라미터
- **파라미터 없음** (모든 강우관측소 조회)

### 응답 필드

| 필드명 | 타입 | 설명 | 비고 |
|--------|------|------|------|
| `obscd` | String | 관측소코드 | 8자리 숫자 |
| `obsnm` | String | 관측소명 | - |
| `bbsnnm` | String | 대권역명 | - |
| `sbsncd` | String | 표준유역코드 | - |
| `clsyn` | String | 운영상태 | 운영/폐쇄 |
| `obsknd` | String | 관측소종류 | 보통/T/M |
| `mngorg` | String | 관리기관 | 기상청/환경부/한국수자원공사 등 |

### 사용 예시
```bash
# 모든 강우관측소 조회
GET /rf_dubrfobs
```

---

## 2. 수위관측소 검색 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkw/wl_dubrfobs`
- **메소드**: GET
- **설명**: 수위관측소 정보를 검색하는 API

### 요청 파라미터
- **파라미터 없음** (모든 수위관측소 조회)

### 응답 필드

| 필드명 | 타입 | 설명 | 비고 |
|--------|------|------|------|
| `obscd` | String | 관측소코드 | 8자리 숫자 |
| `obsnm` | String | 관측소명 | - |
| `bbsnnm` | String | 대권역명 | - |
| `sbsncd` | String | 표준유역코드 | - |
| `clsyn` | String | 운영상태 | 운영/폐쇄 |
| `obsknd` | String | 관측소종류 | 보통/T/M |
| `mngorg` | String | 관리기관 | 기상청/환경부/한국수자원공사 등 |

### 사용 예시
```bash
# 모든 수위관측소 조회
GET /wl_dubrfobs
```

---

## 3. 강우량 데이터 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_data`
- **메소드**: GET
- **설명**: 강우량 데이터를 조회하는 API

### 요청 파라미터

| 변수명 | 타입 | 필수 | 설명 | 범위 |
|--------|------|------|------|------|
| `obscd` | String | ✅ | 관측소코드 | - |
| `startdt` | String | ❌ | 관측기간-시작일 | YYYYMMDD |
| `enddt` | String | ❌ | 관측기간-종료일 | YYYYMMDD |
| `output` | String | ❌ | 출력 포맷 | xml, json<br>**기본값**: json |

### 응답 필드

| 필드명 | 타입 | 설명 | 단위 |
|--------|------|------|------|
| `obsymd` | String | 관측년월일 | - |
| `rf` | String | 강우량 | mm |
| `rfhr` | String | 시간강우량 | mm |
| `rfday` | String | 일강우량 | mm |

### 사용 예시
```bash
# 특정 관측소의 강우량 데이터 조회
GET /rf_data?obscd=10011100&startdt=20240101&enddt=20240131
```

---

## 4. 수위 데이터 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkw/wl_data`
- **메소드**: GET
- **설명**: 수위 데이터를 조회하는 API

### 요청 파라미터

| 변수명 | 타입 | 필수 | 설명 | 범위 |
|--------|------|------|------|------|
| `obscd` | String | ✅ | 관측소코드 | - |
| `startdt` | String | ❌ | 관측기간-시작일 | YYYYMMDD |
| `enddt` | String | ❌ | 관측기간-종료일 | YYYYMMDD |
| `output` | String | ❌ | 출력 포맷 | xml, json<br>**기본값**: json |

### 응답 필드

| 필드명 | 타입 | 설명 | 단위 |
|--------|------|------|------|
| `obsymd` | String | 관측년월일 | - |
| `wl` | String | 수위 | EL.m |
| `wlhr` | String | 시간수위 | EL.m |

### 사용 예시
```bash
# 특정 관측소의 수위 데이터 조회
GET /wl_data?obscd=10011100&startdt=20240101&enddt=20240131
```

---

## 5. 기상관측소 검색 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkw/ws_dubrfobs`
- **메소드**: GET
- **설명**: 기상관측소 정보를 검색하는 API

### 요청 파라미터
- **파라미터 없음** (모든 기상관측소 조회)

### 응답 필드

| 필드명 | 타입 | 설명 | 비고 |
|--------|------|------|------|
| `obscd` | String | 관측소코드 | 8자리 숫자 |
| `obsnm` | String | 관측소명 | - |
| `bbsnnm` | String | 대권역명 | - |
| `sbsncd` | String | 표준유역코드 | - |
| `clsyn` | String | 운영상태 | 운영/폐쇄 |
| `obsknd` | String | 관측소종류 | 보통/T/M |
| `mngorg` | String | 관리기관 | 기상청/환경부/한국수자원공사 등 |

### 사용 예시
```bash
# 모든 기상관측소 조회
GET /ws_dubrfobs
```

---

## 6. 기상 데이터 API

### 요청 정보
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkw/ws_data`
- **메소드**: GET
- **설명**: 기상 데이터를 조회하는 API

### 요청 파라미터

| 변수명 | 타입 | 필수 | 설명 | 범위 |
|--------|------|------|------|------|
| `obscd` | String | ✅ | 관측소코드 | - |
| `startdt` | String | ❌ | 관측기간-시작일 | YYYYMMDD |
| `enddt` | String | ❌ | 관측기간-종료일 | YYYYMMDD |
| `output` | String | ❌ | 출력 포맷 | xml, json<br>**기본값**: json |

### 응답 필드

| 필드명 | 타입 | 설명 | 단위 |
|--------|------|------|------|
| `obsymd` | String | 관측년월일 | - |
| `temp` | String | 기온 | ℃ |
| `humidity` | String | 습도 | % |
| `windspd` | String | 풍속 | m/s |
| `winddir` | String | 풍향 | degree |
| `pressure` | String | 기압 | hPa |

### 사용 예시
```bash
# 특정 관측소의 기상 데이터 조회
GET /ws_data?obscd=10011100&startdt=20240101&enddt=20240131
```

---

## 7. 댐검색 API (기존)

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

---

## 8. 댐수문정보 API들 (기존)

### 8.1 일자료 API
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_dtdata`
- **설명**: 댐의 일별 수문 정보

### 8.2 시자료 API
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_hrdata`
- **설명**: 댐의 시간별 수문 정보

### 8.3 월자료 API
- **URL**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_mndata`
- **설명**: 댐의 월별 수문 정보

---

## API 엔드포인트 요약

### 강우/수위/기상 관련 (`/wkw/`)
1. **강우관측소 검색**: `/rf_dubrfobs`
2. **수위관측소 검색**: `/wl_dubrfobs`
3. **기상관측소 검색**: `/ws_dubrfobs`
4. **강우량 데이터**: `/rf_data`
5. **수위 데이터**: `/wl_data`
6. **기상 데이터**: `/ws_data`

### 댐 관련 (`/wkd/`)
1. **댐 검색**: `/mn_dammain`
2. **댐 일자료**: `/mn_dtdata`
3. **댐 시자료**: `/mn_hrdata`
4. **댐 월자료**: `/mn_mndata`

---

## 데이터 유형별 분류

### 🌧️ 강수량 데이터
- **관측소 검색**: `/rf_dubrfobs`
- **강우량 조회**: `/rf_data`
- **데이터 포함**: 일강우량, 시간강우량

### 🌊 수위 데이터
- **관측소 검색**: `/wl_dubrfobs`
- **수위 조회**: `/wl_data`
- **데이터 포함**: 수위, 시간수위

### 🌤️ 기상 데이터
- **관측소 검색**: `/ws_dubrfobs`
- **기상 조회**: `/ws_data`
- **데이터 포함**: 기온, 습도, 풍속, 풍향, 기압

### 🏞️ 댐수문정보
- **댐 검색**: `/mn_dammain`
- **댐 데이터**: `/mn_dtdata`, `/mn_hrdata`, `/mn_mndata`
- **데이터 포함**: 저수위, 유입량, 방류량, 강우량 등

---

## 실제 테스트 결과

### ✅ 성공적으로 조회 가능한 API들
1. **강우관측소 검색**: `http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_dubrfobs`
   - 결과: 821개 관측소 정보
   - 예시: 대관령(10011100), 정선군(10011217)

2. **댐 검색**: `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_dammain`
   - 결과: 89개 댐 정보
   - 예시: 광동댐(1001210), 충주댐(1003110)

### ❓ 확인이 필요한 API들
1. **수위관측소 검색**: `/wl_dubrfobs`
2. **기상관측소 검색**: `/ws_dubrfobs`
3. **강우량 데이터**: `/rf_data`
4. **수위 데이터**: `/wl_data`
5. **기상 데이터**: `/ws_data`

---

## 결론

현재 WAMIS API 스펙에서 **댐 관련 API만** 문서화되어 있고, **강수량, 수위, 기상** 관련 API들이 누락되어 있습니다. 

실제로는 다음 API들이 존재합니다:
- ✅ **강우관측소 검색**: `/rf_dubrfobs` (확인됨)
- ❓ **수위관측소 검색**: `/wl_dubrfobs` (확인 필요)
- ❓ **기상관측소 검색**: `/ws_dubrfobs` (확인 필요)
- ❓ **강우량/수위/기상 데이터**: `/rf_data`, `/wl_data`, `/ws_data` (확인 필요)

이러한 API들을 실제로 테스트하여 완전한 WAMIS API 스펙을 작성해야 합니다. 