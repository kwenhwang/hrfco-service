# ngrok으로 즉시 HTTPS 도메인 만들기

## 🚀 **ngrok 장점**
- ✅ **설정 1분 완료**
- ✅ **즉시 HTTPS 제공**
- ✅ **무료 플랜 제공**
- ✅ **GUI 대시보드**

## 📋 **설정 방법**

### 1단계: ngrok 설치 및 가입
```bash
# 1. https://ngrok.com 가입 (무료)
# 2. ngrok 다운로드
# Windows: https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip
```

### 2단계: 인증 토큰 설정
```bash
# PowerShell에서 실행
.\ngrok config add-authtoken <YOUR_AUTHTOKEN>
```

### 3단계: 프록시 서버 실행
```bash
# 터미널 1: 프록시 서버 실행
python run_proxy_server.py
```

### 4단계: ngrok 터널 실행
```bash
# 터미널 2: ngrok 실행
.\ngrok http 8000
```

### 5단계: HTTPS URL 확인
```bash
# ngrok 실행 후 출력되는 HTTPS URL 사용
# 예: https://abcd1234.ngrok-free.app
```

## 📊 **사용 예시**

### 실행 결과:
```
Session Status                online
Session Expires               1 hour, 59 minutes
Version                       3.0.0
Region                        Asia Pacific (ap)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### GPT Actions 스키마:
```json
{
  "servers": [
    {
      "url": "https://abc123.ngrok-free.app",
      "description": "HRFCO API HTTPS Proxy via ngrok"
    }
  ]
}
```

## ⚠️ **제한사항**
- 무료 플랜: 2시간마다 재시작 (URL 변경됨)
- 유료 플랜($8/월): 고정 도메인 제공 