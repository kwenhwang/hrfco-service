# Cloudflare Tunnel로 무료 HTTPS 도메인 만들기

## 🌟 **Cloudflare Tunnel 장점**
- ✅ **완전 무료** (도메인 + HTTPS)
- ✅ **즉시 사용 가능** (5분 내 설정)
- ✅ **안정적인 성능**
- ✅ **방화벽 통과** (포트 열기 불필요)

## 🚀 **설정 방법**

### 1단계: Cloudflare 가입 및 도메인 연결
```bash
# 1. https://cloudflare.com 가입 (무료)
# 2. 무료 도메인 서비스 이용하거나 기존 도메인 연결
```

**무료 도메인 옵션:**
- **Freenom** (`.tk`, `.ml`, `.ga` 등)
- **DuckDNS** (Dynamic DNS)
- **No-IP** (Dynamic DNS)

### 2단계: Cloudflare Tunnel 설정

#### A. Cloudflare Dashboard에서 설정
```bash
# 1. Cloudflare Dashboard → Zero Trust → Networks → Tunnels
# 2. "Create a tunnel" 클릭
# 3. 터널 이름 입력 (예: hrfco-proxy)
# 4. Connector 설치 명령어 복사
```

#### B. 로컬 서버에서 Connector 설치
```bash
# Windows PowerShell
# 1. Cloudflared 다운로드
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"

# 2. 인증 (Cloudflare에서 제공한 토큰 사용)
.\cloudflared.exe service install <YOUR_TOKEN>

# 3. 터널 실행
.\cloudflared.exe tunnel run
```

#### C. Public Hostname 설정
```bash
# Cloudflare Dashboard에서:
# 1. Public Hostname 탭
# 2. Subdomain: hrfco-api (원하는 이름)
# 3. Domain: your-domain.com
# 4. Service: HTTP → localhost:8000
# 5. Save 클릭
```

### 3단계: 프록시 서버 실행
```bash
# 로컬에서 프록시 서버 실행
python run_proxy_server.py
```

### 4단계: 테스트
```bash
# 이제 HTTPS로 접근 가능!
curl "https://hrfco-api.your-domain.com/waterlevel/data?obscd=4009670&hours=24"
```

## 📋 **완전한 예시**

### 1. 무료 도메인 생성 (DuckDNS 사용)
```bash
# 1. https://duckdns.org 접속
# 2. GitHub/Google 로그인
# 3. 도메인 생성: hrfco-proxy.duckdns.org
# 4. Cloudflare에 도메인 추가
```

### 2. Cloudflare Tunnel 명령어
```bash
# Windows에서 실행
cloudflared tunnel --name hrfco-tunnel --hostname hrfco-api.hrfco-proxy.duckdns.org --url http://localhost:8000
```

### 3. 최종 GPT Actions 스키마 업데이트
```json
{
  "servers": [
    {
      "url": "https://hrfco-api.hrfco-proxy.duckdns.org",
      "description": "HRFCO API HTTPS Proxy via Cloudflare Tunnel"
    }
  ]
}
``` 