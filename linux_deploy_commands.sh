#!/bin/bash
# HRFCO Service Linux 서버 배포 스크립트

echo "🚀 HRFCO Service Linux 배포 시작..."

# 1. 시스템 업데이트
echo "📦 시스템 패키지 업데이트..."
sudo apt update && sudo apt upgrade -y

# 2. Python 환경 설치
echo "🐍 Python 환경 설치..."
sudo apt install -y python3 python3-pip python3-venv git curl

# 3. 프로젝트 디렉토리 생성 및 이동
echo "📁 프로젝트 디렉토리 설정..."
sudo mkdir -p /opt/hrfco-service
sudo chown $USER:$USER /opt/hrfco-service
cd /opt/hrfco-service

# 4. Git 저장소 클론
echo "📥 프로젝트 다운로드..."
git clone https://github.com/kwenhwang/hrfco-service.git .

# 5. Python 가상환경 생성 및 활성화
echo "🔧 Python 가상환경 설정..."
python3 -m venv venv
source venv/bin/activate

# 6. 의존성 설치
echo "📦 의존성 패키지 설치..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. 환경변수 설정
echo "⚙️ 환경변수 설정..."
cp env.example .env
echo "🔑 .env 파일을 편집하여 API 키를 입력하세요:"
echo "   nano .env"
echo ""
echo "설정해야 할 항목:"
echo "   HRFCO_API_KEY=your_actual_hrfco_api_key"
echo "   KMA_API_KEY=your_actual_kma_api_key"
echo ""

# 환경변수 설정 대기
read -p "API 키 설정을 완료했나요? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    echo "✅ API 키 설정 완료"
else
    echo "⚠️ API 키를 먼저 설정해주세요: nano .env"
    exit 1
fi

# 8. systemd 서비스 파일 생성
echo "🔧 systemd 서비스 설정..."
sudo tee /etc/systemd/system/hrfco-mcp.service > /dev/null << EOF
[Unit]
Description=HRFCO MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/hrfco-service
Environment=PATH=/opt/hrfco-service/venv/bin
ExecStart=/opt/hrfco-service/venv/bin/python mcp_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 9. 서비스 등록 및 시작
echo "🚀 서비스 시작..."
sudo systemctl daemon-reload
sudo systemctl enable hrfco-mcp
sudo systemctl start hrfco-mcp

# 10. 서비스 상태 확인
echo "📊 서비스 상태 확인..."
sleep 3
sudo systemctl status hrfco-mcp

# 11. 방화벽 설정 (선택사항)
echo "🔥 방화벽 설정..."
read -p "방화벽을 설정하시겠습니까? (y/N): " firewall
if [[ $firewall =~ ^[Yy]$ ]]; then
    sudo ufw allow 8000/tcp
    sudo ufw --force enable
    echo "✅ 포트 8000 열림"
fi

# 12. 로그 확인 명령어 안내
echo ""
echo "🎉 배포 완료!"
echo ""
echo "📋 유용한 명령어들:"
echo "   서비스 상태 확인:    sudo systemctl status hrfco-mcp"
echo "   서비스 재시작:      sudo systemctl restart hrfco-mcp"
echo "   서비스 중지:        sudo systemctl stop hrfco-mcp"
echo "   실시간 로그 확인:    journalctl -u hrfco-mcp -f"
echo "   최근 로그 확인:      journalctl -u hrfco-mcp -n 50"
echo ""
echo "🔧 업데이트 방법:"
echo "   cd /opt/hrfco-service"
echo "   git pull origin main"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   sudo systemctl restart hrfco-mcp"
echo ""
echo "🌐 MCP 서버 주소: http://$(hostname -I | awk '{print $1}'):8000" 