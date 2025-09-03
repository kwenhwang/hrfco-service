# Cloudflare Tunnel 무료 HTTPS 설정 가이드

이 가이드는 Cloudflare Tunnel을 사용하여 무료로 HTTPS + 사용자 정의 도메인을 설정하는 방법을 설명합니다.

## 🌟 **Cloudflare Tunnel의 장점**

- ✅ **완전 무료**: SSL 인증서, CDN, DDoS 보호 무료
- ✅ **설정 간단**: 복잡한 방화벽/포트포워딩 불필요
- ✅ **자동 갱신**: SSL 인증서 자동 관리
- ✅ **보안 강화**: 서버 IP 숨김, Zero Trust 보안
- ✅ **글로벌 CDN**: 전세계 빠른 접속 속도

## 📋 **사전 준비사항**

1. **Cloudflare 계정** (무료): https://dash.cloudflare.com
2. **도메인** (무료 도메인 가능):
   - Freenom: .tk, .ml, .ga, .cf 도메인 무료
   - 또는 기존 소유 도메인
3. **Docker가 설치된 Linux 서버**

## 🚀 **1단계: Cloudflare 계정 및 도메인 설정**

### A. Cloudflare 계정 생성
```bash
# 1. https://dash.cloudflare.com 접속
# 2. 계정 생성 (이메일 인증)
# 3. 무료 플랜 선택
```

### B. 도메인 연결
```bash
# 1. Cloudflare 대시보드에서 "Add a Site" 클릭
# 2. 도메인 입력 (예: example.com)
# 3. Free 플랜 선택
# 4. DNS 레코드 스캔 완료 대기
# 5. Cloudflare 네임서버로 변경:
#    - 도메인 등록업체에서 NS 레코드 변경
#    - Cloudflare에서 제공하는 네임서버 2개 입력
```

### C. DNS 설정 확인
```bash
# 네임서버 변경 확인 (시간이 걸릴 수 있음)
nslookup your-domain.com

# Cloudflare 네임서버가 보이면 성공
```

## 🔧 **2단계: Cloudflare Tunnel 생성**

### A. Zero Trust 대시보드 접속
```bash
# 1. https://one.dash.cloudflare.com 접속
# 2. 팀 이름 설정 (처음 접속시)
# 3. 무료 플랜 선택
```

### B. 터널 생성
```bash
# 1. Networks > Tunnels 메뉴 선택
# 2. "Create a tunnel" 클릭
# 3. "Cloudflared" 선택
# 4. 터널 이름 입력 (예: hrfco-mcp-server)
# 5. "Save tunnel" 클릭
```

### C. 터널 토큰 복사
```bash
# 설치 방법에서 "Docker" 선택
# 표시되는 토큰 복사 (eyJ... 형태)
# 예시: eyJhIjoiYWJjZGVmZyIsInQiOiJoaWprbG1ubyIsInMiOiJwcXJzdHV2dyJ9
```

## 🐳 **3단계: Docker 설정 업데이트**

### A. 환경변수 설정
```bash
# .env 파일 편집
nano /opt/hrfco-service/.env

# 다음 라인 추가
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiYWJjZGVmZyIsInQiOiJoaWprbG1ubyIsInMiOiJwcXJzdHV2dyJ9
```

### B. Cloudflare 터널 시작
```bash
cd /opt/hrfco-service

# Cloudflare 프로필과 함께 컨테이너 시작
docker-compose --profile cloudflare up -d

# 터널 상태 확인
docker-compose logs cloudflared
```

## 🌐 **4단계: Public Hostname 설정**

### A. Cloudflare 대시보드에서 설정
```bash
# 1. Tunnels 페이지에서 생성한 터널 클릭
# 2. "Public Hostname" 탭 선택
# 3. "Add a public hostname" 클릭
```

### B. 호스트명 설정
```bash
# Subdomain: mcp (또는 원하는 이름)
# Domain: your-domain.com (선택)
# Path: (비워둠)
# Service Type: HTTP
# URL: hrfco-mcp:8000
```

### C. 고급 설정 (선택사항)
```bash
# TLS 탭:
# - Origin Server Name: hrfco-mcp
# - No TLS Verify: 체크

# HTTP Settings 탭:
# - HTTP Host Header: hrfco-mcp
# - Origin Server Name: hrfco-mcp
```

## ✅ **5단계: 설정 확인 및 테스트**

### A. DNS 전파 확인
```bash
# 설정한 서브도메인 확인
nslookup mcp.your-domain.com

# Cloudflare IP가 보이면 성공
```

### B. HTTPS 접속 테스트
```bash
# 브라우저에서 접속
https://mcp.your-domain.com

# 또는 curl로 테스트
curl -I https://mcp.your-domain.com
```

### C. SSL 인증서 확인
```bash
# SSL 인증서 정보 확인
openssl s_client -connect mcp.your-domain.com:443 -servername mcp.your-domain.com
```

## 🔧 **추가 설정 및 최적화**

### A. Cloudflare SSL/TLS 설정
```bash
# 1. Cloudflare 대시보드 > SSL/TLS
# 2. Overview에서 "Full" 모드 선택
# 3. Edge Certificates에서 "Always Use HTTPS" 활성화
```

### B. 보안 강화 설정
```bash
# 1. Security > WAF
# 2. Managed Rules 활성화
# 3. Rate Limiting 설정 (선택사항)

# Firewall Rules 예시:
# - Block countries (필요시)
# - IP Access Rules
```

### C. 성능 최적화
```bash
# 1. Speed > Optimization
# 2. Auto Minify 활성화 (JS, CSS, HTML)
# 3. Brotli 압축 활성화
# 4. Rocket Loader 활성화 (선택사항)
```

## 🚨 **문제 해결**

### A. 터널 연결 실패
```bash
# 로그 확인
docker-compose logs cloudflared

# 터널 재시작
docker-compose restart cloudflared

# 토큰 재확인
echo $CLOUDFLARE_TUNNEL_TOKEN
```

### B. 도메인 접속 불가
```bash
# DNS 전파 상태 확인
dig mcp.your-domain.com

# Cloudflare DNS 직접 확인
dig @1.1.1.1 mcp.your-domain.com

# 캐시 클리어
# Cloudflare 대시보드 > Caching > Purge Everything
```

### C. SSL 인증서 오류
```bash
# SSL 모드 확인 및 변경
# Cloudflare 대시보드 > SSL/TLS > Overview
# "Flexible" → "Full" 로 변경

# Edge Certificate 강제 갱신
# SSL/TLS > Edge Certificates > "Delete Certificate"
```

## 📊 **모니터링 및 관리**

### A. 터널 상태 모니터링
```bash
# 실시간 로그 확인
docker-compose logs -f cloudflared

# 터널 메트릭 확인
# Cloudflare 대시보드 > Zero Trust > Networks > Tunnels
```

### B. 트래픽 분석
```bash
# Cloudflare Analytics 확인
# 대시보드 > Analytics & Logs > Web Analytics
```

### C. 자동 업데이트 설정
```bash
# Cloudflared 이미지 자동 업데이트
# docker-compose.yml에 이미 latest 태그 사용

# 정기적 업데이트 크론잡 (선택사항)
crontab -e

# 매일 새벽 3시 업데이트
0 3 * * * cd /opt/hrfco-service && docker-compose pull && docker-compose up -d
```

## 🎯 **완료 체크리스트**

- [ ] Cloudflare 계정 생성 및 도메인 연결
- [ ] 네임서버 변경 및 DNS 전파 확인
- [ ] Cloudflare Tunnel 생성 및 토큰 획득
- [ ] Docker 환경변수 설정 및 터널 실행
- [ ] Public Hostname 설정
- [ ] HTTPS 접속 테스트 성공
- [ ] SSL 인증서 정상 작동 확인

## 🌟 **최종 결과**

설정 완료 후:
- ✅ **무료 HTTPS**: https://mcp.your-domain.com
- ✅ **자동 SSL**: 인증서 자동 갱신
- ✅ **CDN 가속**: 전세계 빠른 접속
- ✅ **DDoS 보호**: Cloudflare 보안
- ✅ **숨겨진 IP**: 서버 IP 노출 방지

완전 무료로 프로덕션급 HTTPS 서비스 운영이 가능합니다! 🚀 