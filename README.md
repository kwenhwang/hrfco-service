# HRFCO MCP Server

대한민국 수문 데이터터 API를 Claude Desktop과 연동하는 MCP(Model Context Protocol) 서버입니다.

## 🎉 현재 상태

✅ **API 키 테스트 성공**: 실제 HRFCO API 키로 모든 데이터 타입 테스트 완료
✅ **MCP 서버 준비 완료**: Claude Desktop에서 사용 가능
✅ **GitHub Actions 설정**: 자동 배포 워크플로우 구성
✅ **Docker 이미지**: 컨테이너화 완료

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

### Docker 빌드

```bash
docker build -t hrfco-mcp-server .
docker run --rm hrfco-mcp-server python test_api.py
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
- MCP 서버가 실행 중인지 확인

### Docker 빌드 실패
- Dockerfile 문법 확인
- 빌드 컨텍스트 확인

## 📝 라이선스

MIT License

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 지원

- GitHub Issues: [문제 보고](https://github.com/kwenhwang/hrfco-service/issues)
- Email: kwenhwang@gmail.com

---

**🎉 HRFCO MCP Server가 성공적으로 설정되었습니다! Claude Desktop에서 한국수자원공사 데이터를 활용해보세요!**