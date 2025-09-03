# 무료 HTTPS 호스팅 대안들

## 🏃‍♂️ **즉시 사용 가능한 솔루션**

### 1. **Serveo** (SSH 터널)
```bash
# 설치 불필요, SSH만 있으면 됨
ssh -R 80:localhost:8000 serveo.net

# 출력: https://random-name.serveo.net
```
**장점:**
- ✅ 설치 불필요
- ✅ 즉시 HTTPS
- ✅ 완전 무료

**단점:**
- ⚠️ 랜덤 도메인 (재시작시 변경)

### 2. **LocalTunnel**
```bash
# Node.js 필요
npm install -g localtunnel

# 실행
lt --port 8000

# 출력: https://random-word.loca.lt
```

### 3. **Bore**
```bash
# Rust 기반, 빠른 터널링
cargo install bore-cli

# 실행
bore local 8000 --to bore.pub

# 출력: https://abc123.bore.pub
```

## 🌐 **클라우드 배포 (완전 무료)**

### 1. **Vercel** (추천!)
```bash
# 1. package.json 생성
echo '{"scripts":{"start":"python gpt_actions_proxy.py"}}' > package.json

# 2. vercel.json 설정
echo '{
  "builds": [{"src": "gpt_actions_proxy.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "gpt_actions_proxy.py"}]
}' > vercel.json

# 3. 배포
npx vercel --prod
```
**결과:** `https://your-project.vercel.app`

### 2. **Railway**
```bash
# 1. railway.json 설정
echo '{
  "build": {"builder": "NIXPACKS"},
  "deploy": {"startCommand": "python gpt_actions_proxy.py"}
}' > railway.json

# 2. 배포
npx @railway/cli up
```
**결과:** `https://your-project.railway.app`

### 3. **Render**
```bash
# 1. GitHub 연동
# 2. Web Service 생성
# 3. Build Command: pip install -r requirements.txt
# 4. Start Command: python gpt_actions_proxy.py
```
**결과:** `https://your-service.onrender.com`

### 4. **Fly.io**
```bash
# 1. Dockerfile 생성
echo 'FROM python:3.9
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "gpt_actions_proxy.py"]' > Dockerfile

# 2. 배포
fly deploy
```
**결과:** `https://your-app.fly.dev`

## 🔧 **Self-Hosted 무료 HTTPS**

### 1. **Cloudflare Origin Certificate**
```bash
# 1. Cloudflare → SSL/TLS → Origin Server
# 2. Create Certificate
# 3. 인증서 다운로드 후 서버에 적용
```

### 2. **Let's Encrypt (자체 서버)**
```bash
# Certbot 설치
sudo apt install certbot

# 인증서 발급
certbot certonly --standalone -d your-domain.com

# 자동 갱신
crontab -e
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. **Caddy Server (자동 HTTPS)**
```bash
# Caddyfile 설정
your-domain.com {
    reverse_proxy localhost:8000
}

# 실행 (자동으로 Let's Encrypt 인증서 발급)
caddy run
```

## 📊 **비교표**

| 솔루션 | 설정시간 | 고정도메인 | 성능 | 제한사항 |
|--------|----------|------------|------|----------|
| **Cloudflare Tunnel** | 5분 | ✅ | ⭐⭐⭐⭐⭐ | 없음 |
| **ngrok** | 1분 | ❌(유료) | ⭐⭐⭐⭐ | 2시간 제한 |
| **Serveo** | 30초 | ❌ | ⭐⭐⭐ | 불안정 |
| **Vercel** | 10분 | ✅ | ⭐⭐⭐⭐⭐ | 서버리스 제약 |
| **Railway** | 5분 | ✅ | ⭐⭐⭐⭐ | 월 500시간 |

## 🎯 **추천 순서**

### 1순위: **Cloudflare Tunnel** 🏆
- 완전 무료 + 고정 도메인
- 설정: `cloudflare_tunnel_setup.md` 참고

### 2순위: **ngrok** (빠른 테스트용)
- 즉시 사용 가능
- 설정: `ngrok_setup.md` 참고

### 3순위: **Vercel** (안정성 중요시)
- 완전 관리형 서비스
- 무료 계정으로도 충분

## 💡 **즉시 실행 가능한 명령어**

### ngrok (가장 빠름):
```bash
# 1. 프록시 서버 실행
python run_proxy_server.py

# 2. 새 터미널에서
ngrok http 8000
```

### Serveo (설치 불필요):
```bash
# 1. 프록시 서버 실행
python run_proxy_server.py

# 2. 새 터미널에서
ssh -R 80:localhost:8000 serveo.net
```

이제 어떤 방법을 선택하시겠나요? 🚀 