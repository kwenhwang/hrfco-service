# HRFCO Service - 홍수통제소 API 통합 서비스

홍수통제소(HRFCO) API와 WAMIS API를 통합하여 실시간 수문 정보를 제공하는 MCP(Model Context Protocol) 서버입니다.

## 🌟 주요 기능

- **MCP 서버**: Claude/Cursor에서 직접 사용 가능한 수문 데이터 조회
- **통합 온톨로지**: HRFCO, WAMIS, 기상청 API 통합 관리
- **실시간 분석**: 수위 위험도, 강우량 통계 자동 분석
- **Docker 배포**: 컨테이너 기반 안정적 운영
- **무료 HTTPS**: Cloudflare Tunnel로 SSL + 도메인 제공

## 📊 지원 데이터

- 🌊 **수위 데이터**: 전국 수위 관측소 실시간 수위 정보
- 🌧️ **강우량 데이터**: 강우량 관측소 실시간 강우 정보  
- 🏗️ **댐/보 데이터**: 댐 수위, 방류량 정보
- 🌡️ **기상 데이터**: 기상청 날씨 정보 (온도, 습도, 풍속)
- ⚠️ **위험도 분석**: 수위 기준별 위험도 평가 및 예측

## 🚀 빠른 시작

### 로컬 개발
```bash
# 의존성 설치
pip install -r requirements.txt

# API 키 설정
cp env.example .env
# .env 파일에서 API 키 설정

# MCP 서버 실행
python mcp_server.py
```

### Docker 배포 (권장)
```bash
# 1. 서버 접속
ssh user@your-server

# 2. 원클릭 배포 스크립트 실행
curl -fsSL https://raw.githubusercontent.com/kwenhwang/hrfco-service/main/linux_deploy_commands.sh | bash

# 3. Cloudflare 무료 HTTPS 설정 (선택사항)
# 스크립트 실행 시 안내에 따라 설정
```

## 📚 문서

### 📋 설정 가이드 (`docs/setup/`)
- [Linux Docker 배포](docs/setup/linux-deployment.md)
- [Cloudflare 무료 HTTPS](docs/setup/cloudflare_tunnel_setup.md)
- [ngrok 터널링](docs/setup/ngrok_setup.md)
- [무료 호스팅 대안](docs/setup/free_hosting_alternatives.md)

### 📖 API 문서 (`docs/api/`)
- [WAMIS API 명세](docs/api/wamis-api-spec.md)
- [WAMIS 완전 API 명세](docs/api/wamis-complete-spec.md)
- [통합 API 가이드](docs/api/integrated-apis-guide.md)

## 🛠️ 개발

### 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 개발 의존성 설치
pip install -r requirements.txt
```

### API 키 설정
```bash
# .env 파일 생성 (env.example 참고)
HRFCO_API_KEY=your_hrfco_api_key
KMA_API_KEY=your_kma_api_key
```

자세한 API 키 설정은 [tools/setup_api_keys.py](tools/setup_api_keys.py)를 사용하세요.

## 📈 사용 예시

### Claude/Cursor에서
```
"하동군 대석교 수위가 위험한가요?"
"최근 48시간 강우량 추이를 분석해주세요"
"수계별 관측소 정보를 조회해주세요"
```

## 🔧 도구 (`tools/`)

- **`setup_api_keys.py`**: API 키 설정 도구
- **`test_wamis_complete_api.py`**: WAMIS API 테스트

## 🏗️ 프로젝트 구조

```
hrfco-service/
├── 📁 docs/                    # 문서
│   ├── 📁 setup/              # 설정 가이드
│   └── 📁 api/                # API 문서
├── 📁 src/hrfco_service/      # 핵심 라이브러리
├── 📁 tools/                  # 유틸리티 도구
├── 🚀 mcp_server.py          # MCP 서버 메인
├── 🐳 Dockerfile             # Docker 이미지
├── 🐳 docker-compose.yml     # Docker Compose 설정
├── 🐧 linux_deploy_commands.sh # 원클릭 배포 스크립트
└── 📋 requirements.txt       # 의존성
```

## 🌐 배포

### 로컬 테스트
```bash
# MCP 서버
python mcp_server.py

# Docker 테스트
docker-compose up -d
```

### Linux 서버 배포 (Docker + Cloudflare)
```bash
# 원클릭 배포
curl -fsSL https://raw.githubusercontent.com/kwenhwang/hrfco-service/main/linux_deploy_commands.sh | bash
```

**배포 과정:**
1. 🐳 Docker & Docker Compose 자동 설치
2. 📥 프로젝트 자동 다운로드
3. ⚙️ 환경변수 설정 (.env 파일 편집)
4. 🚀 Docker 컨테이너 빌드 및 실행
5. ☁️ Cloudflare Tunnel 설정 (무료 HTTPS)
6. 🔥 방화벽 설정 (선택사항)

**최종 결과:**
- ✅ **로컬 접속**: `http://server-ip:8000`
- ✅ **HTTPS 도메인**: `https://mcp.your-domain.com`
- ✅ **자동 SSL**: 인증서 자동 갱신
- ✅ **글로벌 CDN**: 전세계 빠른 접속

자세한 내용은 [docs/setup/linux-deployment.md](docs/setup/linux-deployment.md) 참고

## 🔐 보안

- ✅ API 키는 환경변수로 관리
- ✅ .env 파일 Git 제외
- ✅ 하드코딩된 인증정보 없음
- ✅ Docker 컨테이너 격리
- ✅ Cloudflare 보안 및 DDoS 보호

**⚠️ 중요**: API 키를 코드에 직접 포함하지 마세요!

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 감사의 말

- 홍수통제소(HRFCO) API
- 국가수자원관리종합정보시스템(WAMIS) API  
- 기상청 날씨 API