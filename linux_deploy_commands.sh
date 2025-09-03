#!/bin/bash
# HRFCO Service Docker + Cloudflare 배포 스크립트

echo "🚀 HRFCO Service Docker 배포 시작..."

# 1. 시스템 업데이트
echo "📦 시스템 패키지 업데이트..."
sudo apt update && sudo apt upgrade -y

# 2. Docker 설치
echo "🐳 Docker 설치..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker 설치 완료. 다시 로그인 후 계속하세요."
    echo "   logout && ssh user@server 로 다시 접속하세요."
    exit 0
fi

# 3. Docker Compose 설치
echo "🔧 Docker Compose 설치..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 4. 프로젝트 디렉토리 생성 및 이동
echo "📁 프로젝트 디렉토리 설정..."
sudo mkdir -p /opt/hrfco-service
sudo chown $USER:$USER /opt/hrfco-service
cd /opt/hrfco-service

# 5. Git 저장소 클론
echo "📥 프로젝트 다운로드..."
if [ ! -d ".git" ]; then
    git clone https://github.com/kwenhwang/hrfco-service.git .
else
    git pull origin main
fi

# 6. 환경변수 설정
echo "⚙️ 환경변수 설정..."
if [ ! -f ".env" ]; then
    cp env.example .env
fi

echo "🔑 .env 파일을 편집하여 API 키를 입력하세요:"
echo "   nano .env"
echo ""
echo "필수 설정 항목:"
echo "   HRFCO_API_KEY=your_actual_hrfco_api_key"
echo "   KMA_API_KEY=your_actual_kma_api_key"
echo ""
echo "선택 설정 항목:"
echo "   LOG_LEVEL=INFO"
echo "   DEBUG=false"
echo ""

# API 키 설정 확인
nano .env

# 7. 로그 디렉토리 생성
echo "📝 로그 디렉토리 생성..."
mkdir -p logs

# 8. Docker 이미지 빌드 및 실행
echo "🐳 Docker 컨테이너 빌드 및 실행..."
docker-compose build
docker-compose up -d

# 9. 서비스 상태 확인
echo "📊 서비스 상태 확인..."
sleep 10
docker-compose ps
docker-compose logs --tail=20 hrfco-mcp

# 10. Cloudflare Tunnel 설정 안내
echo ""
echo "☁️ Cloudflare Tunnel 설정 (무료 HTTPS + 도메인):"
echo ""
echo "1. Cloudflare 계정 생성: https://dash.cloudflare.com"
echo "2. Zero Trust 대시보드 이동: https://one.dash.cloudflare.com"
echo "3. Networks > Tunnels > Create a tunnel"
echo "4. 터널 이름 입력 (예: hrfco-mcp)"
echo "5. 토큰 복사 후 .env 파일에 추가:"
echo "   CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token"
echo ""
echo "6. Public hostname 설정:"
echo "   - Subdomain: mcp (또는 원하는 이름)"
echo "   - Domain: your-domain.com (Cloudflare에 등록된 도메인)"
echo "   - Service: http://hrfco-mcp:8000"
echo ""

read -p "Cloudflare Tunnel을 지금 설정하시겠습니까? (y/N): " setup_cloudflare
if [[ $setup_cloudflare =~ ^[Yy]$ ]]; then
    echo "🔑 Cloudflare 터널 토큰을 .env 파일에 추가하세요:"
    echo "   nano .env"
    echo "   CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token"
    
    read -p "터널 토큰을 추가했나요? (y/N): " token_added
    if [[ $token_added =~ ^[Yy]$ ]]; then
        echo "🚀 Cloudflare 터널 시작..."
        docker-compose --profile cloudflare up -d
        echo "✅ Cloudflare 터널이 시작되었습니다!"
    fi
fi

# 11. 방화벽 설정 (Docker 사용시 선택사항)
echo "🔥 방화벽 설정..."
read -p "방화벽을 설정하시겠습니까? (y/N): " firewall
if [[ $firewall =~ ^[Yy]$ ]]; then
    sudo ufw allow 8000/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    echo "✅ 방화벽 설정 완료"
fi

# 12. 완료 안내
echo ""
echo "🎉 배포 완료!"
echo ""
echo "📋 유용한 명령어들:"
echo "   컨테이너 상태 확인:     docker-compose ps"
echo "   로그 확인:            docker-compose logs -f"
echo "   서비스 재시작:         docker-compose restart"
echo "   서비스 중지:          docker-compose down"
echo "   이미지 재빌드:         docker-compose build --no-cache"
echo ""
echo "🔧 업데이트 방법:"
echo "   cd /opt/hrfco-service"
echo "   git pull origin main"
echo "   docker-compose build"
echo "   docker-compose up -d"
echo ""
echo "🌐 MCP 서버 주소:"
echo "   로컬: http://$(hostname -I | awk '{print $1}'):8000"
if [[ $setup_cloudflare =~ ^[Yy]$ && $token_added =~ ^[Yy]$ ]]; then
    echo "   Cloudflare: https://your-subdomain.your-domain.com"
fi
echo ""
echo "📚 Cloudflare 설정 가이드: docs/setup/cloudflare_tunnel_setup.md" 