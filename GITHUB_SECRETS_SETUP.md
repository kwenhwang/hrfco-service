# GitHub Secrets를 사용한 API 키 관리

## 개요
이 가이드는 GitHub Secrets를 사용하여 HRFCO API 키를 안전하게 관리하고, Docker 빌드 시 자동으로 주입하는 방법을 설명합니다.

## 🔐 GitHub Secrets 설정

### 1. GitHub 저장소에서 Secrets 설정

1. **GitHub 저장소 접속**
   - https://github.com/kwenhwang/hrfco-service

2. **Settings → Secrets and variables → Actions**
   - 저장소 설정 → Secrets and variables → Actions

3. **New repository secret 추가**
   - **Name**: `HRFCO_API_KEY`
   - **Value**: 실제 HRFCO API 키
   - **Add secret** 클릭

### 2. 필요한 Secrets 목록

| Secret Name | 설명 | 예시 |
|-------------|------|------|
| `HRFCO_API_KEY` | HRFCO API 키 | `your-actual-api-key-here` |
| `GLAMA_API_KEY` | Glama API 키 (선택사항) | `glama-api-key` |
| `DOCKER_USERNAME` | Docker Hub 사용자명 | `kwenhwang` |
| `DOCKER_PASSWORD` | Docker Hub 토큰 | `docker-hub-token` |

## 🚀 자동 배포 워크플로우

### 워크플로우 동작 방식

1. **main 브랜치에 push** → 자동 트리거
2. **GitHub Secrets에서 API 키 가져오기**
3. **Docker 이미지 빌드** (API 키 포함)
4. **Docker Hub에 푸시**
5. **Glama MCP 서버에 배포**

### 빌드 과정

```yaml
# .github/workflows/build-and-deploy.yml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    build-args: |
      HRFCO_API_KEY=${{ secrets.HRFCO_API_KEY }}  # ← 여기서 API 키 주입
```

## 🔧 수동 배포 방법

### 1. GitHub Actions에서 수동 실행

1. **Actions 탭 접속**
2. **"Build and Deploy with API Key" 워크플로우 선택**
3. **"Run workflow" 클릭**
4. **main 브랜치 선택 후 실행**

### 2. 로컬에서 Secrets 확인 (개발용)

```bash
# GitHub CLI 사용
gh secret list

# 특정 Secret 확인 (값은 마스킹됨)
gh secret view HRFCO_API_KEY
```

## 🛡️ 보안 고려사항

### 1. API 키 보안
- ✅ **GitHub Secrets 사용**: API 키가 코드에 노출되지 않음
- ✅ **빌드 시 주입**: 런타임에만 API 키 사용
- ✅ **로그 마스킹**: GitHub Actions 로그에서 API 키 자동 마스킹

### 2. 접근 제어
- ✅ **저장소 권한**: Secrets는 저장소 관리자만 수정 가능
- ✅ **워크플로우 권한**: 최소 권한 원칙 적용
- ✅ **감사 로그**: Secrets 접근 기록 유지

### 3. 정기 관리
- 🔄 **API 키 로테이션**: 3-6개월마다 갱신
- 🔄 **Secrets 검토**: 정기적으로 불필요한 Secrets 제거
- 🔄 **접근 권한 검토**: 팀원 권한 정기 검토

## 📊 배포 상태 확인

### 1. GitHub Actions 상태
```bash
# 워크플로우 실행 상태 확인
gh run list --workflow="Build and Deploy with API Key"
```

### 2. Docker 이미지 확인
```bash
# 빌드된 이미지 확인
docker pull kwenhwang/hrfco-service:latest
docker run --rm kwenhwang/hrfco-service:latest python -c "
import os
print(f'API 키 설정됨: {bool(os.getenv(\"HRFCO_API_KEY\"))}')
"
```

### 3. Glama 배포 확인
```bash
# Glama에서 서비스 상태 확인
curl https://glama.ai/api/mcp-servers/@kwenhwang/hrfco-service/status
```

## 🔍 문제 해결

### 1. Secrets 접근 오류
```yaml
# 워크플로우에서 Secrets 사용 확인
- name: Debug Secrets
  run: |
    echo "API 키 길이: ${#HRFCO_API_KEY}"
    echo "API 키 설정됨: ${{ secrets.HRFCO_API_KEY != '' }}"
```

### 2. Docker 빌드 실패
```bash
# 로컬에서 빌드 테스트
docker build --build-arg HRFCO_API_KEY=test-key -t test-image .
```

### 3. API 키 유효성 검증
```python
# API 키 테스트 스크립트
import requests
import os

api_key = os.getenv('HRFCO_API_KEY')
url = f'http://api.hrfco.go.kr/{api_key}/waterlevel/info.json'

response = requests.get(url)
print(f'API 응답: {response.status_code}')
```

## 📝 설정 예시

### 1. GitHub Secrets 설정 예시
```
Repository: kwenhwang/hrfco-service
Settings → Secrets and variables → Actions

Secrets:
- HRFCO_API_KEY: your-actual-hrfco-api-key
- GLAMA_API_KEY: your-glama-api-key (선택사항)
```

### 2. 워크플로우 실행 예시
```bash
# main 브랜치에 push하면 자동 실행
git add .
git commit -m "Update with API key support"
git push origin main

# 또는 수동 실행
gh workflow run "Build and Deploy with API Key"
```

### 3. 배포 결과 확인
```bash
# Docker Hub에서 이미지 확인
docker pull kwenhwang/hrfco-service:latest

# 로컬에서 테스트
docker run -p 8000:8000 kwenhwang/hrfco-service:latest
curl http://localhost:8000/health
```

## 🎯 장점

### 1. **보안성**
- API 키가 코드에 노출되지 않음
- GitHub Secrets로 안전하게 관리
- 빌드 시에만 API 키 주입

### 2. **자동화**
- main 브랜치 push 시 자동 배포
- 수동 개입 없이 완전 자동화
- 배포 상태 실시간 모니터링

### 3. **사용자 편의성**
- 사용자는 API 키 신경 쓸 필요 없음
- 미리 빌드된 이미지로 바로 사용
- Glama에서 즉시 활성화 가능

## 📞 지원

문제가 발생하거나 추가 설정이 필요한 경우:
1. GitHub Issues에 문제 보고
2. 워크플로우 로그 첨부
3. Secrets 설정 상태 확인

---

**🎉 이제 GitHub Secrets를 사용하여 API 키를 안전하게 관리하고 자동 배포할 수 있습니다!** 