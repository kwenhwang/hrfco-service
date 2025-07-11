# 사용자 가이드 - API 키 없이 HRFCO 데이터 사용하기

## 🎯 개요

이 가이드는 **API 키를 발급받지 않아도** HRFCO 수문 데이터를 사용할 수 있는 방법을 설명합니다.

## 📋 사용자 유형별 가이드

### 1. 일반 사용자 (API 키 없이 사용)

#### Glama에서 사용하기
1. **Glama 접속**: https://glama.ai
2. **MCP 서버**: https://glama.ai/mcp/servers/@kwenhwang/hrfco-service
3. **서버 활성화**: 클릭하여 활성화
4. **질문하기**: 자연어로 수문 데이터 요청

**예시 질문:**
```
"부산 지역의 수위 관측소 정보를 알려줘"
"영천댐의 현재 방류량을 확인해줘"
"최근 강수량 현황을 보여줘"
"홍수 위험이 있는 지역이 있나요?"
```

#### Claude Desktop에서 사용하기
1. **Claude Desktop 설치**: https://claude.ai
2. **MCP 설정**: `claude_desktop_config.json` 파일 생성
3. **서버 연결**: 설정 파일에 MCP 서버 정보 추가
4. **질문하기**: 자연어로 수문 데이터 요청

**설정 파일 예시:**
```json
{
  "mcpServers": {
    "hrfco-flood-control": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

#### HTTP API 사용하기
서버가 배포된 경우 HTTP API로 직접 호출 가능:

```bash
# 관측소 정보 조회
curl "http://localhost:8000/observatories?hydro_type=waterlevel"

# 수문 데이터 조회
curl "http://localhost:8000/hydro?hydro_type=dam&time_type=10M&obs_code=1001210"

# 서버 상태 확인
curl "http://localhost:8000/health"
```

### 2. 개발자/운영자 (API 키 필요)

#### 로컬 개발 환경
```bash
# 환경변수 설정
export HRFCO_API_KEY="your-api-key"

# 서버 실행
python -m src.hrfco_service.http_server

# MCP 서버 실행
python mcp_server.py
```

#### Docker 배포
```bash
# 환경변수와 함께 실행
docker run -p 8000:8000 -e HRFCO_API_KEY="your-api-key" hrfco-service
```

#### Kubernetes 배포
```yaml
# deployment.yaml
env:
- name: HRFCO_API_KEY
  valueFrom:
    secretKeyRef:
      name: hrfco-secrets
      key: api-key
```

### 3. Docker로 로컬 실행 (API 키 없이)
사용자는 API 키 없이 미리 빌드된 Docker 이미지를 실행할 수 있습니다:

```bash
# 미리 빌드된 이미지 실행 (API 키는 이미 포함됨)
docker pull kwenhwang/hrfco-service:latest
docker run -p 8080:8080 kwenhwang/hrfco-service:latest

# 또는 직접 빌드 (개발자용)
docker build --build-arg HRFCO_API_KEY="your-api-key" -t hrfco-service .
docker run -p 8080:8080 hrfco-service
```

#### Claude Desktop 설정
```json
{
  "mcpServers": {
    "hrfco": {
      "command": "docker",
      "args": ["run", "--rm", "-p", "8080:8080", "kwenhwang/hrfco-service:latest"]
    }
  }
}
```

#### Glama에서 사용
1. https://glama.ai 접속
2. https://glama.ai/mcp/servers/@kwenhwang/hrfco-service 접속
3. 서버 활성화
4. "부산 수위 정보 알려줘" 질문

## 🔧 사용 가능한 도구

### MCP 서버 도구
| 도구명 | 설명 | 매개변수 |
|--------|------|----------|
| `get_observatory_info` | 관측소 정보 조회 | `hydro_type` (waterlevel/rainfall/dam/bo) |
| `get_hydro_data` | 수문 데이터 조회 | `hydro_type`, `time_type`, `obs_code` |
| `get_server_health` | 서버 상태 확인 | 없음 |
| `get_server_config` | 서버 설정 확인 | 없음 |

### HTTP API 엔드포인트
| 엔드포인트 | 설명 | 매개변수 |
|------------|------|----------|
| `GET /observatories` | 관측소 정보 | `hydro_type`, `document_type` |
| `GET /hydro` | 수문 데이터 | `hydro_type`, `time_type`, `obs_code` |
| `GET /health` | 서버 상태 | 없음 |
| `GET /config` | 서버 설정 | 없음 |

## 📊 데이터 타입

### 지원하는 수문 데이터
- **waterlevel**: 수위 데이터
- **rainfall**: 강수량 데이터  
- **dam**: 댐 데이터
- **bo**: 보 데이터

### 지원하는 시간 단위
- **10M**: 10분
- **1H**: 1시간
- **1D**: 1일

## 🚀 빠른 시작

### 1. Glama에서 바로 사용
1. https://glama.ai 접속
2. https://glama.ai/mcp/servers/@kwenhwang/hrfco-service 접속
3. 서버 활성화
4. "부산 수위 정보 알려줘" 질문

### 2. Claude에서 사용
1. Claude Desktop 설치
2. MCP 설정 파일 생성
3. 서버 연결
4. 자연어로 질문

### 3. HTTP API 사용
```bash
# 서버가 실행 중인 경우
curl "http://localhost:8000/hydro?hydro_type=waterlevel&time_type=10M&obs_code=2022678"
```

## ❓ 자주 묻는 질문

**Q: API 키가 없어도 정말 사용할 수 있나요?**
A: 네! Glama나 Claude에서 MCP 서버를 통해 사용하면 API 키 입력 없이도 데이터를 조회할 수 있습니다.

**Q: 개인정보나 API 키가 노출되나요?**
A: 아니요. API 키는 서버 내부에서만 사용되며, 사용자에게는 노출되지 않습니다.

**Q: 어떤 데이터를 조회할 수 있나요?**
A: 수위, 강수량, 댐, 보 데이터를 실시간으로 조회할 수 있습니다.

**Q: 사용량 제한이 있나요?**
A: HRFCO API 정책에 따라 제한이 있을 수 있습니다. 과도한 사용은 피해주세요.

## 🆘 문제 해결

### 서버 연결 실패
- 인터넷 연결 확인
- 서버 상태 확인: `GET /health`
- 방화벽 설정 확인

### 데이터 조회 실패
- 관측소 코드 확인
- 시간 단위 확인 (10M, 1H, 1D)
- API 서버 상태 확인

### MCP 서버 오류
- Python 환경 확인
- 의존성 설치 확인: `pip install -r requirements.txt`
- 로그 확인

## 📞 지원

- **이슈 리포트**: GitHub Issues
- **문서**: README.md 참조
- **예제**: `test_mcp_scenarios.py` 참조

---

**즐거운 수문 데이터 활용하세요! 🌊** 