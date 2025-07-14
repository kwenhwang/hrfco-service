# Glama MCP 서버 등록 가이드

## 개요
이 가이드는 HRFCO 수문 데이터 조회 서비스를 Glama MCP 서버에 Docker 컨테이너로 등록하는 방법을 설명합니다.

## 사전 준비사항

### 1. Docker 이미지 빌드
```bash
# API 키와 함께 Docker 이미지 빌드
docker build --build-arg HRFCO_API_KEY=your-api-key-here -t hrfco-service:latest .

# 또는 docker-compose 사용
docker-compose build
```

### 2. 이미지 푸시 (선택사항)
```bash
# Docker Hub에 푸시하려면
docker tag hrfco-service:latest your-username/hrfco-service:latest
docker push your-username/hrfco-service:latest
```

## Glama MCP 서버 등록 방법

### 방법 1: 로컬 Docker 실행
```bash
# Glama MCP 서버에서 직접 실행
docker run -d \
  --name hrfco-mcp-server \
  -p 8000:8000 \
  -e HRFCO_API_KEY=your-api-key-here \
  -e LOG_LEVEL=INFO \
  -e CACHE_TTL_SECONDS=300 \
  -e MAX_CONCURRENT_REQUESTS=5 \
  hrfco-service:latest
```

### 방법 2: Glama 설정 파일 사용
1. `glama-mcp-config.json` 파일을 Glama 설정 디렉토리에 복사
2. API 키를 실제 값으로 변경
3. Glama 서버 재시작

### 방법 3: Kubernetes 배포
```bash
# Secret 생성 (API 키를 base64로 인코딩)
echo -n "your-api-key-here" | base64

# Secret 업데이트
kubectl apply -f glama-deployment.yaml

# 배포 확인
kubectl get pods -l app=hrfco-mcp-server
```

## Glama MCP 서버 설정

### 1. Glama 설정 파일 위치
- Linux: `~/.config/glama/`
- Windows: `%APPDATA%\glama\`
- macOS: `~/Library/Application Support/glama/`

### 2. MCP 서버 등록
```json
{
  "mcpServers": {
    "hrfco-service": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-p", "8000:8000",
        "-e", "HRFCO_API_KEY=${HRFCO_API_KEY}",
        "--name", "hrfco-mcp-server",
        "hrfco-service:latest"
      ],
      "env": {
        "HRFCO_API_KEY": "your-actual-api-key"
      }
    }
  }
}
```

## 서비스 테스트

### 1. 헬스체크
```bash
curl http://localhost:8000/health
```

### 2. MCP 서버 연결 테스트
```python
import requests

# MCP 서버 상태 확인
response = requests.get('http://localhost:8000/health')
print(response.json())
```

### 3. 데이터 조회 테스트
```python
# 수문 데이터 조회
response = requests.get('http://localhost:8000/api/water-level?station=HRFCO')
print(response.json())
```

## 모니터링 및 로그

### 1. 컨테이너 로그 확인
```bash
docker logs hrfco-mcp-server
```

### 2. 실시간 로그 모니터링
```bash
docker logs -f hrfco-mcp-server
```

### 3. 리소스 사용량 확인
```bash
docker stats hrfco-mcp-server
```

## 문제 해결

### 1. 컨테이너가 시작되지 않는 경우
```bash
# 컨테이너 상태 확인
docker ps -a

# 상세 로그 확인
docker logs hrfco-mcp-server

# 컨테이너 재시작
docker restart hrfco-mcp-server
```

### 2. 포트 충돌 문제
```bash
# 사용 중인 포트 확인
netstat -tulpn | grep 8000

# 다른 포트 사용
docker run -p 8001:8000 hrfco-service:latest
```

### 3. API 키 문제
- 환경변수 확인: `docker exec hrfco-mcp-server env | grep HRFCO_API_KEY`
- Secret 업데이트: `kubectl patch secret hrfco-secrets --type='json' -p='[{"op": "replace", "path": "/data/api-key", "value":"new-base64-key"}]'`

## 성능 최적화

### 1. 리소스 제한 설정
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 2. 캐시 설정
- `CACHE_TTL_SECONDS`: 캐시 유효 시간 (기본: 300초)
- `MAX_CONCURRENT_REQUESTS`: 동시 요청 제한 (기본: 5개)

### 3. 로그 레벨 조정
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR (기본: INFO)

## 보안 고려사항

### 1. API 키 관리
- 환경변수나 Kubernetes Secret 사용
- Docker 이미지에 API 키를 포함하지 않음
- 정기적인 API 키 로테이션

### 2. 네트워크 보안
- 내부 네트워크에서만 접근 가능하도록 설정
- 방화벽 규칙 적용
- HTTPS 사용 권장

### 3. 컨테이너 보안
- 최신 베이스 이미지 사용
- 불필요한 패키지 제거
- 읽기 전용 파일시스템 사용

## 업데이트 및 유지보수

### 1. 이미지 업데이트
```bash
# 새 이미지 빌드
docker build -t hrfco-service:latest .

# 기존 컨테이너 교체
docker stop hrfco-mcp-server
docker rm hrfco-mcp-server
docker run -d --name hrfco-mcp-server -p 8000:8000 hrfco-service:latest
```

### 2. 설정 변경
- 환경변수 변경 후 컨테이너 재시작
- Kubernetes의 경우 ConfigMap 사용 권장

### 3. 백업 및 복구
```bash
# 설정 백업
docker exec hrfco-mcp-server cat /app/config.json > backup-config.json

# 데이터 백업 (필요시)
docker exec hrfco-mcp-server tar -czf /tmp/backup.tar.gz /app/data
docker cp hrfco-mcp-server:/tmp/backup.tar.gz ./backup.tar.gz
```

## 지원 및 문의

문제가 발생하거나 추가 지원이 필요한 경우:
1. GitHub Issues에 문제 보고
2. 로그 파일 첨부
3. 시스템 환경 정보 제공 