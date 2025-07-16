# GitHub Secrets 설정 가이드

이 프로젝트를 GitHub Actions로 배포하기 위해 필요한 시크릿들을 설정해야 합니다.

## 필수 시크릿

### 1. HRFCO_API_KEY
한국수자원공사 API 키입니다.

**설정 방법:**
1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. Name: `HRFCO_API_KEY`
4. Value: `FE18B23B-A81B-4246-9674-E8D641902A42`

### 2. DOCKER_USERNAME
Docker Hub 사용자명입니다.

**설정 방법:**
1. "New repository secret" 클릭
2. Name: `DOCKER_USERNAME`
3. Value: `your-dockerhub-username`

### 3. DOCKER_PASSWORD
Docker Hub 액세스 토큰입니다.

**설정 방법:**
1. Docker Hub → Account Settings → Security → New Access Token
2. 토큰 생성 후 복사
3. "New repository secret" 클릭
4. Name: `DOCKER_PASSWORD`
5. Value: `your-dockerhub-access-token`

### 4. GLAMA_HOST
Glama 서버의 호스트 주소입니다.

**설정 방법:**
1. "New repository secret" 클릭
2. Name: `GLAMA_HOST`
3. Value: `your-glama-server-ip`

### 5. GLAMA_USERNAME
Glama 서버의 SSH 사용자명입니다.

**설정 방법:**
1. "New repository secret" 클릭
2. Name: `GLAMA_USERNAME`
3. Value: `your-glama-username`

### 6. GLAMA_SSH_KEY
Glama 서버 접속용 SSH 개인키입니다.

**설정 방법:**
1. SSH 키 생성 (없는 경우): `ssh-keygen -t rsa -b 4096 -C "your-email@example.com"`
2. 개인키 내용 복사: `cat ~/.ssh/id_rsa`
3. "New repository secret" 클릭
4. Name: `GLAMA_SSH_KEY`
5. Value: `-----BEGIN OPENSSH PRIVATE KEY-----
your-private-key-content
-----END OPENSSH PRIVATE KEY-----`

## 시크릿 확인

모든 시크릿이 설정되면 다음과 같이 표시됩니다:

```
✅ HRFCO_API_KEY (32 characters)
✅ DOCKER_USERNAME (your-username)
✅ DOCKER_PASSWORD (your-access-token)
✅ GLAMA_HOST (your-server-ip)
✅ GLAMA_USERNAME (your-username)
✅ GLAMA_SSH_KEY (your-private-key)
```

## 워크플로우 테스트

시크릿 설정 후:
1. main 브랜치에 푸시하거나
2. Pull Request를 생성하면
3. GitHub Actions가 자동으로 실행됩니다

## 문제 해결

### API 키 인증 실패
- HRFCO_API_KEY가 올바르게 설정되었는지 확인
- API 키가 유효한지 확인

### Docker Hub 인증 실패
- DOCKER_USERNAME과 DOCKER_PASSWORD가 올바른지 확인
- Docker Hub 액세스 토큰이 유효한지 확인

### SSH 연결 실패
- GLAMA_SSH_KEY가 올바른 형식인지 확인
- GLAMA_HOST와 GLAMA_USERNAME이 올바른지 확인
- 서버의 authorized_keys에 공개키가 등록되어 있는지 확인 