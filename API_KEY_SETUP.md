# API 키 설정 가이드

## 🔑 HRFCO API 키 설정

### 1. API 키 발급

1. **한국수자원공사 홍수통제소 API** 접속
   - URL: https://api.hrfco.go.kr
   - 회원가입 및 로그인

2. **API 키 발급**
   - 개발자 센터에서 API 키 신청
   - 승인 후 API 키 발급

### 2. 설정 파일에 API 키 입력

#### 방법 1: .cursor/mcp_servers.json 수정

```json
{
  "mcpServers": {
    "hrfco-service": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "HRFCO_API_KEY": "실제_발급받은_API_키"
      }
    }
  }
}
```

#### 방법 2: 환경 변수 설정

**Windows PowerShell:**
```powershell
$env:HRFCO_API_KEY="실제_발급받은_API_키"
```

**Windows Command Prompt:**
```cmd
set HRFCO_API_KEY=실제_발급받은_API_키
```

**macOS/Linux:**
```bash
export HRFCO_API_KEY="실제_발급받은_API_키"
```

#### 방법 3: .env 파일 사용 (권장)

프로젝트 루트에 `.env` 파일 생성:
```env
HRFCO_API_KEY=실제_발급받은_API_키
```

### 3. 설정 확인

```bash
# 설정 확인 스크립트 실행
python -c "
import os
api_key = os.environ.get('HRFCO_API_KEY')
if api_key and api_key != '실제_API_키_입력_필요':
    print('✅ API 키 설정됨')
else:
    print('❌ API 키 설정 필요')
"
```

### 4. Cursor 재시작

API 키 설정 후 Cursor를 재시작하여 설정을 적용하세요.

### 5. 테스트

Cursor에서 다음 명령으로 테스트:
```
"하동군 대석교 수위 변화 추이를 분석해줘"
```

## 🔒 보안 주의사항

1. **API 키 보안**
   - API 키를 코드에 직접 하드코딩하지 마세요
   - 환경 변수나 설정 파일을 사용하세요
   - .gitignore에 .env 파일 추가

2. **설정 파일 보안**
   ```bash
   # .gitignore에 추가
   echo ".env" >> .gitignore
   echo ".cursor/mcp_servers.json" >> .gitignore
   ```

3. **API 키 관리**
   - 정기적으로 API 키 갱신
   - 사용하지 않는 API 키 삭제
   - API 키 사용량 모니터링

## 🆘 문제 해결

### 문제 1: "API 키가 설정되지 않았습니다" 오류

**해결책:**
1. 환경 변수 설정 확인
2. 설정 파일의 API 키 확인
3. Cursor 재시작

### 문제 2: "API 키가 유효하지 않습니다" 오류

**해결책:**
1. API 키 재발급
2. API 키 형식 확인
3. API 키 권한 확인

### 문제 3: "API 호출 한도 초과" 오류

**해결책:**
1. API 사용량 확인
2. 캐시 활용
3. 요청 빈도 조절

## 📞 지원

- **API 키 발급**: https://api.hrfco.go.kr
- **문서**: [README.md](README.md)
- **설정 가이드**: [CURSOR_SETUP.md](CURSOR_SETUP.md) 