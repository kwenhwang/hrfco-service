# Cursor MCP 서버 설정 가이드

## 📋 개요

이 가이드는 Cursor에서 HRFCO MCP 서버를 사용할 수 있도록 설정하는 방법을 안내합니다.

## 🚀 설정 방법

### 방법 1: 프로젝트별 설정 (권장)

1. **프로젝트 루트에 설정 파일 생성**
   ```bash
   # 프로젝트 루트에 .cursor/mcp_servers.json 파일 생성
   mkdir -p .cursor
   ```

2. **설정 파일 내용**
   ```json
   {
     "mcpServers": {
       "hrfco-service": {
         "command": "python",
         "args": ["mcp_server.py"],
         "env": {
           "HRFCO_API_KEY": "실제_API_키_입력_필요"
         }
       }
     }
   }
   ```

### 방법 2: 전역 설정

1. **전역 설정 파일 위치**
   ```bash
   # Windows
   %USERPROFILE%\.cursor\mcp_servers.json
   
   # macOS/Linux
   ~/.cursor/mcp_servers.json
   ```

2. **설정 파일 내용**
   ```json
   {
     "mcpServers": {
       "hrfco-service": {
         "command": "python",
         "args": ["/path/to/your/project/mcp_server.py"],
         "env": {
           "HRFCO_API_KEY": "실제_API_키_입력_필요"
         }
       }
     }
   }
   ```

## 🔧 API 키 설정

### 1. 환경 변수 설정

**Windows (PowerShell):**
```powershell
$env:HRFCO_API_KEY="your-actual-api-key"
```

**Windows (Command Prompt):**
```cmd
set HRFCO_API_KEY=your-actual-api-key
```

**macOS/Linux:**
```bash
export HRFCO_API_KEY="your-actual-api-key"
```

### 2. .env 파일 사용 (권장)

프로젝트 루트에 `.env` 파일 생성:
```env
HRFCO_API_KEY=your-actual-api-key
```

## 📝 사용 예시

### 1. Cursor에서 MCP 서버 연결 확인

Cursor에서 다음 명령을 실행하여 서버가 정상적으로 연결되었는지 확인:

```
"하동군 대석교 수위 변화 추이를 분석해줘"
```

### 2. 사용 가능한 도구들

- `get_hydro_data_nearby`: 주변 수문 데이터 조회
- `analyze_water_level_with_thresholds`: 수위 위험 수위 분석
- `get_comprehensive_hydro_analysis`: 수위+강우량 종합 분석
- `get_basin_comprehensive_analysis`: 수계 종합 분석
- `search_basin_facilities`: WAMIS API 수계 시설 검색
- `get_integrated_ontology_info`: 통합 온톨로지 정보 조회

## 🔍 문제 해결

### 1. 서버 연결 실패

**문제**: MCP 서버가 연결되지 않음
**해결책**:
1. Python 경로 확인: `python --version`
2. 의존성 설치: `pip install -r requirements.txt`
3. API 키 설정 확인

### 2. API 키 오류

**문제**: "API 키가 설정되지 않았습니다" 오류
**해결책**:
1. 환경 변수 설정 확인
2. .env 파일 생성 및 API 키 입력
3. Cursor 재시작

### 3. 모듈 오류

**문제**: "ModuleNotFoundError" 오류
**해결책**:
1. 프로젝트 루트에서 실행 확인
2. PYTHONPATH 설정: `export PYTHONPATH="${PYTHONPATH}:/path/to/your/project/src"`

## 📊 테스트

### 1. 서버 상태 확인
```
"서버 상태를 확인해줘"
```

### 2. 관측소 정보 조회
```
"하동군 대석교 주변 관측소들을 찾아줘"
```

### 3. 수위 분석
```
"하동군 대석교 수위 변화 추이를 분석해줘"
```

## 🎯 고급 설정

### 1. 로그 레벨 설정

환경 변수에 로그 레벨 추가:
```json
{
  "mcpServers": {
    "hrfco-service": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "HRFCO_API_KEY": "your-api-key-here",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 2. 캐시 설정

캐시 디렉토리 설정:
```json
{
  "mcpServers": {
    "hrfco-service": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "HRFCO_API_KEY": "your-api-key-here",
        "CACHE_DIR": "./cache"
      }
    }
  }
}
```

## 📚 추가 정보

- **프로젝트 문서**: [README.md](README.md)
- **사용자 가이드**: [USER_GUIDE.md](USER_GUIDE.md)
- **API 문서**: [API_DOCS.md](API_DOCS.md)

## 🆘 지원

문제가 발생하면 다음을 확인하세요:

1. **로그 확인**: Cursor 개발자 도구에서 로그 확인
2. **서버 상태**: `python mcp_server.py` 직접 실행
3. **의존성**: `pip list`로 필요한 패키지 설치 확인
4. **API 키**: 환경 변수 설정 확인

---

**참고**: 이 설정은 Cursor의 MCP 기능을 사용하여 HRFCO API에 접근할 수 있게 해줍니다. API 키는 보안을 위해 환경 변수로 관리하세요. 