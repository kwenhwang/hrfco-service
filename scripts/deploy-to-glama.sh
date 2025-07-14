#!/bin/bash

# Glama MCP 서버 배포 스크립트
# 사용법: ./scripts/deploy-to-glama.sh [API_KEY]

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

# API 키 확인
if [ -z "$1" ]; then
    log_error "API 키가 필요합니다."
    echo "사용법: $0 <API_KEY>"
    exit 1
fi

API_KEY=$1
IMAGE_NAME="hrfco-service"
CONTAINER_NAME="hrfco-mcp-server"
PORT=8000

log_info "HRFCO 서비스를 Glama MCP 서버에 배포합니다..."

# 1. 기존 컨테이너 정리
log_info "기존 컨테이너 정리 중..."
if docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    log_info "기존 컨테이너가 제거되었습니다."
fi

# 2. Docker 이미지 빌드
log_info "Docker 이미지 빌드 중..."
docker build \
    --build-arg HRFCO_API_KEY="$API_KEY" \
    -t "$IMAGE_NAME:latest" \
    .

if [ $? -eq 0 ]; then
    log_info "Docker 이미지 빌드가 완료되었습니다."
else
    log_error "Docker 이미지 빌드에 실패했습니다."
    exit 1
fi

# 3. 컨테이너 실행
log_info "MCP 서버 컨테이너를 시작합니다..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$PORT:$PORT" \
    -e HRFCO_API_KEY="$API_KEY" \
    -e LOG_LEVEL=INFO \
    -e CACHE_TTL_SECONDS=300 \
    -e MAX_CONCURRENT_REQUESTS=5 \
    --restart unless-stopped \
    "$IMAGE_NAME:latest"

if [ $? -eq 0 ]; then
    log_info "컨테이너가 성공적으로 시작되었습니다."
else
    log_error "컨테이너 시작에 실패했습니다."
    exit 1
fi

# 4. 헬스체크
log_info "서비스 헬스체크 중..."
sleep 10

for i in {1..30}; do
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        log_info "서비스가 정상적으로 실행되고 있습니다."
        break
    else
        if [ $i -eq 30 ]; then
            log_error "서비스 시작 시간이 초과되었습니다."
            docker logs "$CONTAINER_NAME"
            exit 1
        fi
        log_warn "서비스 시작 대기 중... ($i/30)"
        sleep 2
    fi
done

# 5. 서비스 정보 출력
log_info "=== 배포 완료 ==="
echo "서비스 URL: http://localhost:$PORT"
echo "헬스체크: http://localhost:$PORT/health"
echo "API 문서: http://localhost:$PORT/docs"
echo ""
echo "컨테이너 관리 명령어:"
echo "  로그 확인: docker logs $CONTAINER_NAME"
echo "  실시간 로그: docker logs -f $CONTAINER_NAME"
echo "  컨테이너 중지: docker stop $CONTAINER_NAME"
echo "  컨테이너 재시작: docker restart $CONTAINER_NAME"
echo "  컨테이너 제거: docker rm -f $CONTAINER_NAME"

# 6. Glama 설정 파일 생성
log_info "Glama 설정 파일을 생성합니다..."
GLAMA_CONFIG_DIR="$HOME/.config/glama"
mkdir -p "$GLAMA_CONFIG_DIR"

cat > "$GLAMA_CONFIG_DIR/mcp-servers.json" << EOF
{
  "mcpServers": {
    "hrfco-service": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-p", "$PORT:$PORT",
        "-e", "HRFCO_API_KEY=$API_KEY",
        "-e", "LOG_LEVEL=INFO",
        "-e", "CACHE_TTL_SECONDS=300",
        "-e", "MAX_CONCURRENT_REQUESTS=5",
        "--name", "$CONTAINER_NAME",
        "$IMAGE_NAME:latest"
      ],
      "env": {
        "HRFCO_API_KEY": "$API_KEY"
      }
    }
  }
}
EOF

log_info "Glama 설정 파일이 생성되었습니다: $GLAMA_CONFIG_DIR/mcp-servers.json"

# 7. 테스트 실행
log_info "서비스 테스트를 실행합니다..."
if curl -s http://localhost:$PORT/health | grep -q "status.*ok"; then
    log_info "헬스체크 테스트 통과"
else
    log_warn "헬스체크 테스트 실패"
fi

# API 테스트
if curl -s "http://localhost:$PORT/api/water-level?station=HRFCO" > /dev/null 2>&1; then
    log_info "API 테스트 통과"
else
    log_warn "API 테스트 실패 (API 키 확인 필요)"
fi

log_info "배포가 완료되었습니다!"
log_info "Glama에서 MCP 서버를 사용할 수 있습니다." 