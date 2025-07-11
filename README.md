[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/kwenhwang-hrfco-service-badge.png)](https://mseep.ai/app/kwenhwang-hrfco-service)

# HRFCO Service

홍수통제소(HRFCO) API를 활용한 수문 데이터 조회 서비스입니다. **API 키 없이도 사용 가능합니다!**

## 🏗️ 서비스 아키텍처

이 서비스는 다양한 방식으로 수문 데이터에 접근할 수 있도록 설계되었습니다:

### 📡 데이터 흐름
```
HRFCO API (공공데이터포털)
    ↓
HRFCO Service (API 키 관리)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   HTTP API      │  MCP Server     │  Function Call  │
│   (REST API)    │  (Claude/Glama) │  (ChatGPT)      │
└─────────────────┴─────────────────┴─────────────────┘
    ↓                ↓                ↓
사용자 애플리케이션  AI 챗봇        ChatGPT 플러그인
```

### 🔌 호출 방식

1. **HTTP REST API**: 직접 API 호출로 수문 데이터 조회
2. **MCP Server**: Model Context Protocol 서버로, Claude, Glama 등 AI 챗봇이 외부 도구를 사용할 수 있게 해주는 인터페이스
3. **Function Calling**: ChatGPT 플러그인으로 함수 호출 방식 데이터 조회

### 🎯 사용 시나리오

- **개발자**: HTTP API로 직접 데이터 조회
- **AI 챗봇 사용자**: MCP Server를 통해 자연어로 질문
- **ChatGPT 사용자**: Function Calling으로 구조화된 데이터 요청
- **일반 사용자**: 미리 빌드된 서비스로 API 키 없이 사용

### 📝 사용 예시

#### 1. HTTP API 호출
```bash
# 관측소 정보 조회
curl "http://localhost:8000/observatories?hydro_type=waterlevel"

# 수문 데이터 조회
curl "http://localhost:8000/hydro?hydro_type=dam&time_type=10M&obs_code=1001210"
```

#### 2. MCP Server (Claude/Glama)
```
사용자: "부산 지역의 수위 관측소 정보를 알려줘"
AI: "부산 지역에는 18개의 수위 관측소가 있습니다. 
     대동낙동강교 관측소의 현재 수위는 3.41m입니다."
```

#### 3. Function Calling (ChatGPT)
```json
{
  "function": "get_hydro_data",
  "parameters": {
    "hydro_type": "waterlevel",
    "time_type": "10M", 
    "obs_code": "1001602"
  }
}
```

## 🌟 주요 특징

- **API 키 불필요**: 사용자는 API 키 발급 없이 바로 사용 가능
- **실시간 수문 데이터**: 수위, 강수량, 댐, 보 데이터 실시간 조회
- **AI 챗봇 통합**: Claude, Glama 등과 자연어로 대화하며 데이터 조회
- **다양한 접근 방식**: HTTP API, MCP 서버, Docker 등 지원
- **자동 배포**: GitHub Actions를 통한 자동 배포 및 관리

## 🚀 빠른 시작 (사용자 타입별)

### 👤 일반 사용자 (가장 간단)
1. **Glama 웹사이트**: https://glama.ai/mcp/servers/@kwenhwang/hrfco-service
   - 회원가입 → 서버 활성화 → 바로 질문
   - 예시: "대전 지역 수위 상황 알려줘"

### 🤖 AI 챗봇 사용자 (Claude Desktop)
1. **Docker 설치** 후 아래 명령어 실행
2. **Claude Desktop 설정** 파일 수정

```bash
# Docker 실행
docker run -p 8080:8080 kwenhwang/hrfco-service:latest

# Claude Desktop 설정
{
  "mcpServers": {
    "hrfco": {
      "command": "docker",
      "args": ["run", "--rm", "-p", "8080:8080", "kwenhwang/hrfco-service:latest"]
    }
  }
}
```

### 👨‍💻 개발자 (HTTP API)
1. **Docker 실행**: `docker run -p 8080:8080 kwenhwang/hrfco-service:latest`
2. **API 호출**: `curl "http://localhost:8000/health"`
3. **테스트**: `curl "http://localhost:8000/hydro?hydro_type=waterlevel&time_type=10M&obs_code=1001602"`

### 🐳 Docker 사용자
```bash
# Linux/Mac
./run-without-api-key.sh

# Windows
.\run-without-api-key.ps1

# 또는 직접 실행
docker pull kwenhwang/hrfco-service:latest
docker run -p 8080:8080 kwenhwang/hrfco-service:latest
```

## 📊 지원 데이터 타입

| 타입 | 설명 | 단위 |
|------|------|------|
| `waterlevel` | 수위 | m |
| `rainfall` | 강수량 | mm |
| `dam` | 댐 | m³/s, m (방류량, 저수위 등) |
| `bo` | 보 | m³/s, m (수위, 방류량 등) |

## 🤖 AI 챗봇 사용 예시

### Glama/Claude에서 자연어로 질문
```
"부산에서 홍수 위험이 있는 지역이 있나요?"
→ 부산 대동낙동강교 관측소의 현재 수위는 3.41m입니다. 홍수 위험도: 보통

"영천댐의 방류량이 얼마나 되나요?"
→ 영천댐의 현재 방류량은 0.704m³/s입니다. 상태: 최소 방류 중

"최근 24시간 동안 비가 많이 온 지역은 어디인가요?"
→ 최근 24시간 강수량 현황: 부산 0.0mm, 기타 지역 0.0mm

"부산 근처에 어떤 수문 관측소들이 있나요?"
→ 부산 지역 수문 관측소 현황: 수위 관측소 18개, 강수량 관측소 3개
```

## 🔧 API 엔드포인트

### 1. 상태 확인
```http
GET /health
```

### 2. 관측소 정보 조회
```http
GET /observatories?hydro_type={type}&document_type={format}
```

**예시:**
```bash
curl "http://localhost:8000/observatories?hydro_type=rainfall&document_type=json"
```

### 3. 수문 데이터 조회
```http
GET /hydro?hydro_type={type}&time_type={time}&obs_code={code}
```

**예시:**
```bash
# 강수량 데이터 조회
curl "http://localhost:8000/hydro?hydro_type=rainfall&time_type=10M&obs_code=10014010"

# 수위 데이터 조회
curl "http://localhost:8000/hydro?hydro_type=waterlevel&time_type=10M&obs_code=1001602"

# 댐 데이터 조회
curl "http://localhost:8000/hydro?hydro_type=dam&time_type=10M&obs_code=1001210"
```

## 🧠 MCP 서버 도구

MCP 서버를 통해 사용할 수 있는 도구들:

- `get_observatory_info`: 관측소 정보 조회
- `get_hydro_data`: 수문 데이터 조회  
- `get_server_health`: 서버 상태 확인
- `get_server_config`: 서버 설정 확인
- `search_observatory`: 관측소 검색
- `get_recent_data`: 최근 수문 데이터 조회
- `analyze_regional_hydro_status`: 지역 수문 상태 분석

## ⚡ 성능 및 제한사항

- **응답 시간**: 일반적으로 1-3초 이내
- **데이터 업데이트**: 실시간 (10분 간격)
- **사용량 제한**: 시간당 100회 요청
- **지원 지역**: 전국 수문 관측소 (약 3,000개소)
- **데이터 보존**: 최근 30일간의 데이터 제공

## 🔧 문제 해결

### 자주 묻는 질문

**Q: Docker 실행 시 포트 오류가 발생해요**
A: 8080 포트가 사용 중일 수 있습니다. `-p 8081:8080`으로 다른 포트 사용

**Q: Claude Desktop에서 연결이 안돼요**
A: Docker 컨테이너가 정상 실행 중인지 `docker ps` 명령어로 확인

**Q: 데이터가 조회되지 않아요**
A: 네트워크 연결과 HRFCO API 서버 상태를 확인해보세요

**Q: API 키가 필요한가요?**
A: 일반 사용자는 API 키 없이도 사용 가능합니다. 개발자만 API 키가 필요합니다.

### 로그 확인
```bash
# Docker 로그 확인
docker logs <container_id>

# 서버 상태 확인
curl "http://localhost:8000/health"
```

## 📁 프로젝트 구조

```
hrfco-service/
├── src/hrfco_service/
│   ├── api.py              # API 클라이언트
│   ├── public_server.py    # 공개 MCP 서버 (API 키 없이 사용)
│   ├── http_server.py      # FastAPI 서버
│   └── ...
├── .github/workflows/      # 자동 배포
├── run-without-api-key.sh  # 사용자 실행 스크립트
├── run-without-api-key.ps1 # Windows 실행 스크립트
└── Dockerfile              # Docker 이미지
```

## 🐳 Docker 실행

```bash
# 가장 간단한 방법
docker pull kwenhwang/hrfco-service:latest
docker run -p 8080:8080 kwenhwang/hrfco-service:latest

# 또는 Docker Compose
docker-compose up -d
```

## 🔧 개발자용 (API 키 필요)

### 로컬 개발 환경
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
python -m src.hrfco_service.http_server
```

### 테스트
```bash
# 전체 테스트
pytest

# AI 챗봇 시나리오 테스트
python test_mcp_scenarios.py
```

## 🌐 배포

### GitHub Actions 자동 배포
- main 브랜치에 push하면 자동으로 배포
- API 키는 GitHub Secrets로 안전하게 관리
- Docker Hub에 자동으로 이미지 업로드

### 클라우드 배포
- Railway, Heroku, AWS 등 지원
- 환경변수로 API 키 설정

## 📖 사용자 가이드

자세한 사용법은 [USER_GUIDE.md](USER_GUIDE.md)를 참조하세요.

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 문의

프로젝트 관련 문의사항은 이슈를 통해 연락주세요.

## 📄 라이센스

MIT License

---

**🎉 이제 누구나 API 키 발급 없이 바로 수문 데이터를 사용할 수 있습니다!**