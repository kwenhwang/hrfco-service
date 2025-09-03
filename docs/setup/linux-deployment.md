# 윈도우 → 리눅스 서버 배포 가이드

## 🎯 **추천 방법 순위**

### 🥇 **1순위: Git 사용 (최고 추천!)**

#### **장점:**
- ✅ **버전 관리** - 변경 이력 추적
- ✅ **자동 동기화** - push/pull로 간편 업데이트  
- ✅ **안전성** - 백업 및 롤백 가능
- ✅ **협업 용이** - 팀 작업 가능
- ✅ **무료** - GitHub, GitLab 등 무료 서비스

#### **설정 방법:**

##### A. GitHub 사용 (공개 저장소)
```bash
# 윈도우에서
git add .
git commit -m "HRFCO API 프록시 서버 추가"
git push origin main

# 리눅스 서버에서
git clone https://github.com/username/hrfco-service.git
cd hrfco-service
```

##### B. GitLab 사용 (비공개 가능)
```bash
# 윈도우에서
git remote add gitlab https://gitlab.com/username/hrfco-service.git
git push gitlab main

# 리눅스 서버에서
git clone https://gitlab.com/username/hrfco-service.git
```

##### C. 자체 Git 서버 (완전 비공개)
```bash
# 리눅스 서버에서 bare 저장소 생성
git init --bare hrfco-service.git

# 윈도우에서
git remote add server user@server:/path/to/hrfco-service.git
git push server main

# 리눅스 서버에서
git clone /path/to/hrfco-service.git
```

### 🥈 **2순위: rsync (직접 동기화)**

#### **장점:**
- ✅ **차분 전송** - 변경된 파일만 전송
- ✅ **빠른 속도** - 압축 및 최적화
- ✅ **실시간 동기화** 가능

#### **설정 방법:**
```bash
# WSL 또는 Git Bash에서
rsync -avz --progress . user@server:/path/to/hrfco-service/

# 제외 파일 설정
rsync -avz --progress --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' . user@server:/path/to/hrfco-service/
```

### 🥉 **3순위: SCP/SFTP (간단한 복사)**

#### **장점:**
- ✅ **단순함** - 명령어 하나로 전송
- ✅ **안전성** - SSH 암호화

#### **설정 방법:**
```bash
# 전체 폴더 압축 후 전송
tar -czf hrfco-service.tar.gz .
scp hrfco-service.tar.gz user@server:/tmp/

# 리눅스 서버에서 압축 해제
ssh user@server "cd /path/to/destination && tar -xzf /tmp/hrfco-service.tar.gz"
```

### 📁 **4순위: WinSCP (GUI 방식)**

#### **장점:**
- ✅ **직관적 GUI** - 드래그앤드롭
- ✅ **동기화 기능** - 폴더 동기화 가능

#### **설정 방법:**
1. WinSCP 실행
2. 서버 연결 설정
3. **Commands → Synchronize** 선택
4. 로컬과 원격 폴더 동기화

## 🚀 **권장 워크플로우**

### **초기 설정 (Git 추천)**

```bash
# 1. 현재 프로젝트 Git 초기화 (윈도우)
git init
git add .
git commit -m "Initial commit: HRFCO API 프록시 서버"

# 2. GitHub/GitLab에 저장소 생성 후 푸시
git remote add origin https://github.com/username/hrfco-service.git
git push -u origin main

# 3. 리눅스 서버에서 클론
git clone https://github.com/username/hrfco-service.git
cd hrfco-service
```

### **지속적 업데이트**

```bash
# 윈도우에서 변경 사항 푸시
git add .
git commit -m "프록시 서버 기능 추가"
git push

# 리눅스 서버에서 풀
git pull
```

## 🐧 **리눅스 서버 설정**

### **1. Python 환경 설정**

```bash
# Python 3.9+ 설치 확인
python3 --version

# pip 업그레이드
python3 -m pip install --upgrade pip

# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### **2. 환경 변수 설정**

```bash
# .env 파일 생성
cat > .env << EOF
HRFCO_API_KEY=FE18B23B-A81B-4246-9674-E8D641902A42
KMA_API_KEY=bI7VVvskaOdKJGMej%2F2zJzaxEyiCeGn8kLEidNAxHV7%2FRLiWMCAIlqMY08bwU1MqnakQ4ulEirojxHU800l%2BMA%3D%3D
HOST=0.0.0.0
PORT=8000
DEBUG=False
EOF

# 권한 설정
chmod 600 .env
```

### **3. 서비스 실행**

```bash
# 직접 실행
python gpt_actions_proxy.py

# 백그라운드 실행
nohup python gpt_actions_proxy.py > proxy.log 2>&1 &

# systemd 서비스 등록 (권장)
sudo tee /etc/systemd/system/hrfco-proxy.service << EOF
[Unit]
Description=HRFCO API Proxy Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/hrfco-service
Environment=PATH=/path/to/hrfco-service/venv/bin
ExecStart=/path/to/hrfco-service/venv/bin/python gpt_actions_proxy.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 서비스 시작
sudo systemctl enable hrfco-proxy
sudo systemctl start hrfco-proxy
sudo systemctl status hrfco-proxy
```

## 🔒 **HTTPS 설정 (리눅스)**

### **1. Nginx + Let's Encrypt**

```bash
# Nginx 설치
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# Nginx 설정
sudo tee /etc/nginx/sites-available/hrfco-proxy << EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 설정 활성화
sudo ln -s /etc/nginx/sites-available/hrfco-proxy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL 인증서 설치
sudo certbot --nginx -d your-domain.com
```

### **2. Caddy (자동 HTTPS)**

```bash
# Caddy 설치
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Caddyfile 설정
sudo tee /etc/caddy/Caddyfile << EOF
your-domain.com {
    reverse_proxy localhost:8000
}
EOF

# Caddy 시작
sudo systemctl enable caddy
sudo systemctl start caddy
```

## 📊 **방법별 비교**

| 방법 | 복잡도 | 속도 | 버전관리 | 협업 | 보안 |
|------|--------|------|----------|------|------|
| **Git** | ⭐⭐ | ⭐⭐⭐⭐ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **rsync** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ❌ | ⭐⭐⭐⭐ |
| **SCP** | ⭐ | ⭐⭐⭐ | ❌ | ❌ | ⭐⭐⭐⭐ |
| **WinSCP** | ⭐ | ⭐⭐ | ❌ | ❌ | ⭐⭐⭐ |

## 🎯 **최종 추천**

### **개발/테스트 환경:**
```bash
# Git을 사용한 지속적 배포
git push  # 윈도우에서
git pull  # 리눅스에서
```

### **프로덕션 환경:**
```bash
# Git + 자동화 스크립트
git pull && pip install -r requirements.txt && sudo systemctl restart hrfco-proxy
```

**Git을 사용하면 코드 관리, 배포, 협업이 모두 쉬워집니다!** 🚀 