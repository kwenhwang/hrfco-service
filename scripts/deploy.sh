#!/bin/bash

# HRFCO Service Deployment Script
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 확인
check_environment() {
    log_info "환경 변수 확인 중..."
    
    if [ -z "$HRFCO_API_KEY" ]; then
        log_error "HRFCO_API_KEY 환경 변수가 설정되지 않았습니다."
        exit 1
    fi
    
    log_info "환경 변수 확인 완료"
}

# 도커 이미지 빌드
build_image() {
    log_info "도커 이미지 빌드 중..."
    
    docker build -t hrfco-service:latest .
    
    if [ $? -eq 0 ]; then
        log_info "도커 이미지 빌드 완료"
    else
        log_error "도커 이미지 빌드 실패"
        exit 1
    fi
}

# 로컬 테스트
test_local() {
    log_info "로컬 테스트 실행 중..."
    
    # 도커 컴포즈로 테스트
    docker-compose up -d
    
    # 헬스체크 대기
    sleep 10
    
    # 헬스체크 확인
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "로컬 테스트 성공"
    else
        log_error "로컬 테스트 실패"
        docker-compose down
        exit 1
    fi
    
    docker-compose down
}

# Kubernetes 배포
deploy_k8s() {
    log_info "Kubernetes 배포 중..."
    
    # 네임스페이스 생성 (없는 경우)
    kubectl create namespace hrfco-service --dry-run=client -o yaml | kubectl apply -f -
    
    # Secret 생성
    kubectl create secret generic hrfco-secrets \
        --from-literal=api-key="$HRFCO_API_KEY" \
        --namespace=hrfco-service \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # 배포 적용
    kubectl apply -f kubernetes/deployment.yaml -n hrfco-service
    
    # 배포 상태 확인
    kubectl rollout status deployment/hrfco-service -n hrfco-service --timeout=300s
    
    if [ $? -eq 0 ]; then
        log_info "Kubernetes 배포 완료"
    else
        log_error "Kubernetes 배포 실패"
        exit 1
    fi
}

# 메인 함수
main() {
    log_info "HRFCO Service 배포 시작"
    
    check_environment
    build_image
    test_local
    
    if [ "$1" = "--k8s" ]; then
        deploy_k8s
    fi
    
    log_info "배포 완료!"
}

# 스크립트 실행
main "$@" 