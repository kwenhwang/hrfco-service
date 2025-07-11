# Claude MCP 서버 설정 가이드

## 🎯 개요

HRFCO 수문 데이터를 Claude에서 직접 사용할 수 있도록 MCP(Model Context Protocol) 서버를 설정하는 방법입니다.

## 📋 사전 요구사항

1. Python 3.8+ 설치
2. 프로젝트 의존성 설치: `pip install -r requirements.txt`
3. Claude Desktop 앱 설치

## 🚀 설정 방법

### 1. MCP 서버 준비

프로젝트에 이미 `mcp_server.py`가 준비되어 있습니다. 이 파일은 HRFCO API를 MCP 프로토콜로 래핑합니다.

### 2. Claude 설정 파일 생성

Claude Desktop 앱의 설정 디렉토리에 MCP 설정 파일을 생성합니다:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 3. 설정 파일 내용

```json
{
  "mcpServers": {
    "hrfco-flood-control": {
      "command": "python",
      "args": [
        "C:\\Users\\20172483\\web\\hrfco-service\\mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\20172483\\web\\hrfco-service\\src"
      }
    }
  }
}
```

**주의사항:**
- `command`와 `args`의 경로를 실제 프로젝트 경로로 수정하세요
- `PYTHONPATH`를 실제 `src` 디렉토리 경로로 수정하세요

### 4. Claude 재시작

설정 파일을 저장한 후 Claude Desktop 앱을 재시작합니다.

## 🧪 테스트

### MCP 서버 직접 테스트

```bash
python test_mcp_direct.py
```

### Claude에서 사용 예시

Claude가 재시작된 후, 다음과 같은 질문을 할 수 있습니다:

1. **관측소 정보 조회:**
   ```
   "부산 지역의 수위 관측소 정보를 알려줘"
   ```

2. **수문 데이터 조회:**
   ```
   "영천댐의 현재 방류량을 확인해줘"
   ```

3. **서버 상태 확인:**
   ```
   "서버가 정상적으로 작동하고 있나요?"
   ```

## 🔧 사용 가능한 도구

MCP 서버는 다음 도구들을 제공합니다:

### 1. `get_observatory_info`
- **설명:** 수문 관측소 정보를 조회합니다
- **매개변수:**
  - `hydro_type`: 수문 데이터 타입 (waterlevel, rainfall, dam, bo)

### 2. `get_hydro_data`
- **설명:** 수문 데이터를 조회합니다
- **매개변수:**
  - `hydro_type`: 수문 데이터 타입 (waterlevel, rainfall, dam, bo)
  - `time_type`: 시간 단위 (10M, 1H, 1D)
  - `obs_code`: 관측소 코드

### 3. `get_server_health`
- **설명:** 서버 상태를 확인합니다
- **매개변수:** 없음

### 4. `get_server_config`
- **설명:** 서버 설정을 확인합니다
- **매개변수:** 없음

## 📊 지원하는 데이터 타입

- **waterlevel**: 수위 데이터
- **rainfall**: 강수량 데이터
- **dam**: 댐 데이터
- **bo**: 보 데이터

## ⏰ 지원하는 시간 단위

- **10M**: 10분
- **1H**: 1시간
- **1D**: 1일

## 🔍 문제 해결

### 1. MCP 서버가 시작되지 않는 경우

- Python 경로가 올바른지 확인
- `PYTHONPATH` 환경변수가 올바르게 설정되었는지 확인
- 프로젝트 의존성이 설치되었는지 확인

### 2. Claude에서 도구가 보이지 않는 경우

- Claude 앱을 완전히 재시작
- 설정 파일 경로가 올바른지 확인
- JSON 형식이 올바른지 확인

### 3. 데이터 조회 실패

- 인터넷 연결 확인
- HRFCO API 서버 상태 확인
- 관측소 코드가 올바른지 확인

## 📝 예시 대화

**사용자:** "부산 지역의 수문 상태가 어때?"

**Claude:** "부산 지역의 수문 상태를 확인해드리겠습니다. 현재 부산 대동낙동강교 관측소의 수위는 3.42m입니다. 홍수 위험도는 낮은 상태이며, 실시간 모니터링이 권장됩니다."

**사용자:** "영천댐의 방류량은 얼마나 되나요?"

**Claude:** "영천댐의 현재 방류량은 0.481m³/s입니다. 이는 최소 방류량으로, 저수량 확보를 위한 정상적인 운영 상태입니다."

## 🎉 완료!

이제 Claude에서 HRFCO 수문 데이터를 직접 조회할 수 있습니다! 

## HRFCO_API_KEY 필수 안내

- Claude/Glama에서 MCP 서버를 사용할 때도 반드시 본인 HRFCO API 키가 필요합니다.
- 예시의 `your-api-key-here`는 실제로 동작하지 않으며, 반드시 본인 키로 환경변수/Secrets에 등록해야 합니다.
- Glama/Claude에서 환경변수로 API 키를 주입해야 정상 동작합니다.

> **주의:** API 키가 없으면 실제 HRFCO 데이터 조회가 불가합니다. 누구나 바로 사용할 수 있는 서비스가 아니며, 반드시 본인 키를 발급받아야 합니다. 