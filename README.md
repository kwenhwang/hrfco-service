# HRFCO Service - 홍수통제소 API 통합 서비스

한국수자원공사 홍수통제소(HRFCO) API와 WAMIS API를 통합하여 실시간 수문 정보를 제공하는 MCP(Model Context Protocol) 서버입니다.

## 🌟 주요 기능

- **MCP 서버**: Claude/Cursor에서 직접 사용 가능한 수문 데이터 조회
- **ChatGPT Function Calling**: ChatGPT에서 자연어로 수문 정보 조회
- **통합 온톨로지**: HRFCO, WAMIS, 기상청 API 통합 관리
- **실시간 분석**: 수위 위험도, 강우량 통계 자동 분석

## 📊 지원 데이터

- 🌊 **수위 데이터**: 전국 수위 관측소 실시간 수위 정보
- 🌧️ **강우량 데이터**: 강우량 관측소 실시간 강우 정보  
- 🏗️ **댐/보 데이터**: 댐 수위, 방류량 정보
- 🌡️ **기상 데이터**: 기상청 날씨 정보 (온도, 습도, 풍속)
- ⚠️ **위험도 분석**: 수위 기준별 위험도 평가 및 예측

## 🚀 빠른 시작

### MCP 서버 (Claude/Cursor)
```bash
# 의존성 설치
pip install -r requirements.txt

# API 키 설정
cp env.example .env
# .env 파일에서 API 키 설정

# MCP 서버 실행
python mcp_server.py
```

## 📚 문서

### 📋 설정 가이드 (`docs/setup/`)
- [ChatGPT Function Calling 설정](docs/setup/CHATGPT_SETUP.md)
- [Linux 서버 배포](docs/setup/linux-deployment.md)
- [Cloudflare 터널링](docs/setup/cloudflare_tunnel_setup.md)
- [ngrok 터널링](docs/setup/ngrok_setup.md)
- [무료 호스팅 대안](docs/setup/free_hosting_alternatives.md)

### 📖 API 문서 (`docs/api/`)
- [WAMIS API 명세](docs/api/wamis-api-spec.md)
- [WAMIS 완전 API 명세](docs/api/wamis-complete-spec.md)
- [통합 API 가이드](docs/api/integrated-apis-guide.md)

### 💻 사용 예시 (`docs/examples/`)
- [ChatGPT Function Calling](docs/examples/chatgpt_functions.py)
- [ChatGPT 사용법](docs/examples/chatgpt_usage.py)
- [함수 테스트](docs/examples/test_chatgpt_functions.py)

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

### ChatGPT에서
```python
# Function Calling으로 자동 호출
"진주 지역 날씨와 수위 상황을 종합해서 알려주세요"
"하동군 주변 관측소들의 실시간 데이터를 비교 분석해주세요"
```

## 🔧 도구 (`tools/`)

- **`setup_api_keys.py`**: API 키 설정 도구
- **`test_wamis_complete_api.py`**: WAMIS API 테스트

## 🏗️ 프로젝트 구조

```
hrfco-service/
├── docs/                    # 문서
│   ├── setup/              # 설정 가이드
│   ├── api/                # API 문서
│   └── examples/           # 사용 예시
├── src/hrfco_service/      # 핵심 라이브러리
├── tools/                  # 유틸리티 도구
├── mcp_server.py          # MCP 서버 메인
└── requirements.txt       # 의존성
```

## 🌐 배포

### 로컬 테스트
```bash
# MCP 서버
python mcp_server.py
```

### 클라우드 배포
- **Vercel**: 서버리스 배포
- **Railway**: 컨테이너 배포  
- **Render**: 웹 서비스 배포
- **Linux 서버**: Docker 또는 직접 배포

자세한 내용은 [docs/setup/linux-deployment.md](docs/setup/linux-deployment.md) 참고

## 🔐 보안

- ✅ API 키는 환경변수로 관리
- ✅ .env 파일 Git 제외
- ✅ 하드코딩된 인증정보 없음
- ✅ 최소 권한 원칙 적용

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

- 한국수자원공사 홍수통제소 API
- 국가수자원관리종합정보시스템(WAMIS) API
- 기상청 날씨 API