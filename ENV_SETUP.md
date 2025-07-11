# 환경변수 설정 가이드

## HRFCO_API_KEY 필수 안내
- HRFCO API 키는 반드시 [공식 HRFCO API](https://www.hrfco.go.kr/)에서 발급받아야 합니다.
- 아래 예시의 `your-api-key-here`는 실제로 동작하지 않으며, 반드시 본인 키로 교체해야 합니다.

## .env 파일 생성 예시
```env
HRFCO_API_KEY=your-api-key-here  # 반드시 본인 키로 교체
```

## 환경변수 설정 예시
- Windows (PowerShell):
  ```powershell
  $env:HRFCO_API_KEY="발급받은-API-키"
  ```
- Linux/macOS:
  ```bash
  export HRFCO_API_KEY="발급받은-API-키"
  ```

## Docker/Glama 환경
- 환경변수 또는 Secrets로 반드시 본인 키를 주입해야 정상 동작합니다.

> **주의:** API 키가 없으면 실제 HRFCO 데이터 조회가 불가합니다. 누구나 바로 사용할 수 있는 서비스가 아니며, 반드시 본인 키를 발급받아야 합니다. 