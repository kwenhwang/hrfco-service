# HRFCO Service 배포 가이드

## 🚀 GitHub Codespaces 사용법

### 1. Codespaces 시작
1. GitHub 저장소에서 `Code` 버튼 클릭
2. `Codespaces` 탭 선택
3. `Create codespace on main` 클릭

### 2. 개발 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export HRFCO_API_KEY="your-api-key"

# 테스트 실행
pytest tests/ -v
```

### 3. 로컬 테스트
```bash
# 서버 실행
python -m hrfco_service

# 또는 직접 실행
python main.py
```

## 🔧 KUBE_CONFIG 설정 방법

### 1. Kubernetes 클러스터 설정

#### AWS EKS 사용 시:
```bash
# AWS CLI 설정
aws configure

# EKS 클러스터 생성
eksctl create cluster --name hrfco-cluster --region ap-northeast-2

# kubeconfig 파일 생성
aws eks update-kubeconfig --name hrfco-cluster --region ap-northeast-2
```

#### Google Cloud GKE 사용 시:
```bash
# gcloud 설정
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# GKE 클러스터 생성
gcloud container clusters create hrfco-cluster --zone asia-northeast1-a

# kubeconfig 파일 생성
gcloud container clusters get-credentials hrfco-cluster --zone asia-northeast1-a
```

### 2. GitHub Secrets 설정

1. GitHub 저장소에서 `Settings` → `Secrets and variables` → `Actions`
2. `New repository secret` 클릭
3. 다음 시크릿들 추가:

#### KUBE_CONFIG 설정:
```bash
# kubeconfig 파일을 base64로 인코딩
cat ~/.kube/config | base64 -w 0
```

이 명령어의 출력을 `KUBE_CONFIG` 시크릿에 저장

#### 다른 필요한 시크릿들:
- `HRFCO_API_KEY`: HRFCO API 키
- `DOCKER_USERNAME`: Docker Hub 사용자명 (선택사항)
- `DOCKER_PASSWORD`: Docker Hub 비밀번호 (선택사항)

### 3. GitHub Actions에서 사용

`.github/workflows/deploy.yml`에서 다음과 같이 사용:

```yaml
- name: Configure kubectl
  run: |
    echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
    export KUBECONFIG=kubeconfig
```

## 🌐 클라우드 배포 옵션

### 1. GitHub Codespaces에서 직접 배포
```bash
# 도커 이미지 빌드
docker build -t hrfco-service .

# 로컬 테스트
docker run -p 8000:8000 -e HRFCO_API_KEY=$HRFCO_API_KEY hrfco-service
```

### 2. GitHub Actions 자동 배포
- main 브랜치에 푸시하면 자동으로 배포
- 테스트 → 빌드 → 배포 순서로 진행

### 3. 수동 배포
```bash
# Kubernetes 배포
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/ingress.yaml

# 배포 상태 확인
kubectl get pods -l app=hrfco-service
kubectl get services -l app=hrfco-service
```

## 🔍 문제 해결

### 1. KUBE_CONFIG 오류
```bash
# kubeconfig 파일 확인
kubectl config view

# 클러스터 연결 확인
kubectl cluster-info
```

### 2. 권한 문제
```bash
# RBAC 설정 확인
kubectl auth can-i create deployments
kubectl auth can-i create services
```

### 3. 네트워크 문제
```bash
# 포트 포워딩 확인
kubectl port-forward service/hrfco-service 8000:80
```

## 📊 모니터링

### 1. 로그 확인
```bash
# Pod 로그
kubectl logs -f deployment/hrfco-service

# 서비스 상태
kubectl get endpoints hrfco-service
```

### 2. 메트릭 확인
```bash
# 헬스체크
curl http://localhost:8000/health

# 메트릭
curl http://localhost:8000/metrics
``` 