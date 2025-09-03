# Linux 서버 배포 가이드

이 가이드는 HRFCO Service를 Linux 서버에 배포하는 방법을 설명합니다.

## 📋 **배포 방법 선택**

### 1️⃣ **Git Clone (권장)**
가장 깔끔하고 버전 관리가 쉬운 방법입니다.

```bash
# 서버에서 직접 클론
git clone https://github.com/kwenhwang/hrfco-service.git
cd hrfco-service

# 환경변수 설정
cp env.example .env
nano .env  # API 키 입력
```

**장점:**
- 최신 버전 유지 용이 (`git pull`)
- 변경사항 추적 가능
- 브랜치별 배포 가능

### 2️⃣ **rsync 동기화**
개발 환경과 동일한 상태로 배포하고 싶을 때 사용합니다.

```bash
# Windows에서 Linux로 동기화
rsync -avz --exclude '.git' --exclude '__pycache__' /c/Users/20172483/web/hrfco-service/ user@server:/opt/hrfco-service/
```

**장점:**
- 개발 환경과 동일한 파일 구조
- 특정 파일 제외 가능
- 증분 동기화로 효율적

### 3️⃣ **압축 파일 업로드**
간단한 일회성 배포에 적합합니다.

```bash
# Windows에서 압축
tar -czf hrfco-service.tar.gz hrfco-service/

# WinSCP로 업로드 후 서버에서 압축 해제
tar -xzf hrfco-service.tar.gz
```

## 🚀 **Linux 서버 설정**

### 1. Python 환경 준비

```bash
# Python 3.8+ 설치 확인
python3 --version

# pip 업데이트
sudo apt update
sudo apt install python3-pip python3-venv

# 가상환경 생성
cd /opt/hrfco-service
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
cp env.example .env

# API 키 설정 (nano 또는 vi 사용)
nano .env
```

**.env 파일 내용:**
```bash
# API 키 설정 (실제 키로 교체)
HRFCO_API_KEY=your_actual_hrfco_api_key
KMA_API_KEY=your_actual_kma_api_key

# 서버 설정
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
```

### 3. 방화벽 설정

```bash
# MCP 서버 포트 열기 (예: 8000)
sudo ufw allow 8000/tcp

# HTTPS 포트 (443) - 필요한 경우
sudo ufw allow 443/tcp

# 방화벽 활성화
sudo ufw enable
```

## 🔧 **MCP 서버 배포**

### 1. systemd 서비스 생성

```bash
sudo nano /etc/systemd/system/hrfco-mcp.service
```

**서비스 파일 내용:**
```ini
[Unit]
Description=HRFCO MCP Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/hrfco-service
Environment=PATH=/opt/hrfco-service/venv/bin
ExecStart=/opt/hrfco-service/venv/bin/python mcp_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2. 서비스 시작

```bash
# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable hrfco-mcp
sudo systemctl start hrfco-mcp

# 상태 확인
sudo systemctl status hrfco-mcp

# 로그 확인
journalctl -u hrfco-mcp -f
```

## 🌐 **HTTPS 설정 (선택사항)**

### Nginx + Let's Encrypt

```bash
# Nginx 설치
sudo apt install nginx certbot python3-certbot-nginx

# Nginx 설정
sudo nano /etc/nginx/sites-available/hrfco-mcp
```

**Nginx 설정 파일:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/hrfco-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com
```

### Caddy (더 간단한 대안)

```bash
# Caddy 설치
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Caddyfile 설정
sudo nano /etc/caddy/Caddyfile
```

**Caddyfile 내용:**
```
your-domain.com {
    reverse_proxy 127.0.0.1:8000
}
```

```bash
# Caddy 시작
sudo systemctl enable caddy
sudo systemctl start caddy
```

## 📊 **모니터링 설정**

### 1. 로그 관리

```bash
# 로그 로테이션 설정
sudo nano /etc/logrotate.d/hrfco-mcp
```

```
/opt/hrfco-service/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload hrfco-mcp
    endscript
}
```

### 2. 상태 모니터링 스크립트

```bash
# 헬스체크 스크립트 생성
nano /opt/hrfco-service/healthcheck.sh
```

```bash
#!/bin/bash
# HRFCO MCP 서버 헬스체크

URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): MCP Server is healthy"
else
    echo "$(date): MCP Server is down (HTTP $RESPONSE)"
    # 서비스 재시작
    systemctl restart hrfco-mcp
fi
```

```bash
# 실행 권한 부여
chmod +x /opt/hrfco-service/healthcheck.sh

# 크론탭 등록 (5분마다 체크)
crontab -e
```

```
*/5 * * * * /opt/hrfco-service/healthcheck.sh >> /var/log/hrfco-healthcheck.log 2>&1
```

## 🔄 **업데이트 및 유지보수**

### Git 기반 업데이트

```bash
cd /opt/hrfco-service

# 백업 생성
cp .env .env.backup

# 최신 코드 가져오기
git pull origin main

# 의존성 업데이트
source venv/bin/activate
pip install -r requirements.txt

# 서비스 재시작
sudo systemctl restart hrfco-mcp
```

### 자동 배포 스크립트

```bash
nano /opt/hrfco-service/deploy.sh
```

```bash
#!/bin/bash
# 자동 배포 스크립트

set -e

echo "=== HRFCO Service 배포 시작 ==="

# 기존 서비스 중지
sudo systemctl stop hrfco-mcp

# 백업 생성
timestamp=$(date +%Y%m%d_%H%M%S)
cp .env .env.backup.$timestamp

# 최신 코드 가져오기
git pull origin main

# 가상환경 활성화 및 의존성 업데이트
source venv/bin/activate
pip install -r requirements.txt

# 서비스 재시작
sudo systemctl start hrfco-mcp

# 상태 확인
sleep 5
if systemctl is-active --quiet hrfco-mcp; then
    echo "✅ 배포 완료! 서비스가 정상 실행 중입니다."
else
    echo "❌ 배포 실패! 서비스 시작에 실패했습니다."
    sudo systemctl status hrfco-mcp
    exit 1
fi

echo "=== 배포 완료 ==="
```

```bash
chmod +x /opt/hrfco-service/deploy.sh
```

## 🐛 **문제 해결**

### 일반적인 오류들

**1. 포트 충돌**
```bash
# 포트 사용 확인
sudo netstat -tlnp | grep :8000

# 프로세스 종료
sudo kill -9 <PID>
```

**2. 권한 문제**
```bash
# 파일 소유권 변경
sudo chown -R ubuntu:ubuntu /opt/hrfco-service

# 실행 권한 부여
chmod +x mcp_server.py
```

**3. 의존성 오류**
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. 메모리 부족**
```bash
# 메모리 사용량 확인
free -h

# 스왑 추가 (필요한 경우)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 로그 분석

```bash
# 서비스 로그 확인
journalctl -u hrfco-mcp -n 100

# 실시간 로그 모니터링
journalctl -u hrfco-mcp -f

# 에러 로그만 필터링
journalctl -u hrfco-mcp -p err
```

## 📈 **성능 최적화**

### 1. 서버 자원 설정

```bash
# CPU 코어 수 확인
nproc

# 메모리 사용량 최적화
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# 파일 디스크립터 제한 증가
echo 'ubuntu soft nofile 65536' | sudo tee -a /etc/security/limits.conf
echo 'ubuntu hard nofile 65536' | sudo tee -a /etc/security/limits.conf
```

### 2. 데이터베이스 최적화 (필요한 경우)

```bash
# Redis 설치 (캐싱용)
sudo apt install redis-server

# Redis 설정
sudo nano /etc/redis/redis.conf
```

## 🔐 **보안 강화**

### 1. 방화벽 설정

```bash
# 기본 정책 설정
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH 포트만 허용
sudo ufw allow ssh

# MCP 서버 포트 (특정 IP에서만)
sudo ufw allow from YOUR_IP to any port 8000
```

### 2. 사용자 권한 제한

```bash
# 전용 사용자 생성
sudo useradd -r -s /bin/false hrfco-service

# 서비스 파일 수정
sudo nano /etc/systemd/system/hrfco-mcp.service
```

```ini
[Service]
User=hrfco-service
Group=hrfco-service
```

### 3. 환경변수 보안

```bash
# .env 파일 권한 제한
chmod 600 .env

# 환경변수 암호화 (선택사항)
sudo apt install gnupg

# 암호화된 환경변수 파일 생성
gpg --cipher-algo AES256 --compress-algo 1 --s2k-cipher-algo AES256 --s2k-digest-algo SHA512 --s2k-mode 3 --s2k-count 65536 --symmetric .env
```

이제 Linux 서버에 HRFCO Service를 안전하고 효율적으로 배포할 수 있습니다! 🚀 