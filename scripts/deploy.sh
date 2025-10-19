#!/bin/bash

# AWS EC2 자동 배포 스크립트
# 사용법: ./scripts/deploy.sh ubuntu@54.234.98.110 your-key.pem

set -e

if [ "$#" -ne 2 ]; then
    echo "사용법: $0 <user@host> <ssh-key>"
    echo "예제: $0 ubuntu@54.234.98.110 ~/.ssh/my-key.pem"
    exit 1
fi

SERVER=$1
SSH_KEY=$2
PROJECT_DIR="websocket_server"

echo "🚀 AWS EC2 배포 시작"
echo "====================="
echo "서버: $SERVER"
echo "SSH 키: $SSH_KEY"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 서버 연결 테스트
echo "📡 서버 연결 테스트..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$SERVER" "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 서버 연결 성공${NC}"
else
    echo -e "${RED}❌ 서버 연결 실패${NC}"
    exit 1
fi

# 2. 프로젝트 디렉토리 생성
echo ""
echo "📁 프로젝트 디렉토리 생성..."
ssh -i "$SSH_KEY" "$SERVER" "mkdir -p ~/$PROJECT_DIR"

# 3. 파일 전송
echo ""
echo "📦 파일 전송 중..."
rsync -avz -e "ssh -i $SSH_KEY" \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude '*.log' \
    --exclude '.env' \
    --progress \
    ./ "$SERVER:~/$PROJECT_DIR/"

echo -e "${GREEN}✅ 파일 전송 완료${NC}"

# 4. 서버에서 설정 실행
echo ""
echo "⚙️  서버 설정 중..."

ssh -i "$SSH_KEY" "$SERVER" /bin/bash << 'ENDSSH'
set -e

cd ~/websocket_server

echo "📦 시스템 패키지 업데이트..."
sudo apt update -qq

echo "🐍 Python 확인..."
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 설치 중..."
    sudo apt install -y python3.11 python3.11-venv python3-pip
fi

python3.11 --version

echo "📁 필요한 디렉토리 생성..."
mkdir -p logs certs

echo "🔧 가상 환경 생성..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

echo "📚 의존성 설치..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "🔐 SSL 인증서 확인..."
if [ ! -f "certs/server.crt" ]; then
    echo "SSL 인증서 생성 중..."
    ./scripts/generate_certs.sh
fi

echo "⚙️  .env 파일 확인..."
if [ ! -f ".env" ]; then
    echo ".env 파일 생성 중..."
    ./create_env.sh
fi

echo "✅ 서버 설정 완료!"
ENDSSH

echo -e "${GREEN}✅ 서버 설정 완료${NC}"

# 5. systemd 서비스 생성 (선택)
echo ""
read -p "systemd 서비스를 생성하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 systemd 서비스 생성 중..."
    
    ssh -i "$SSH_KEY" "$SERVER" /bin/bash << 'ENDSSH'
    set -e
    
    # 서비스 파일 생성
    cat > /tmp/websocket-server.service << 'EOF'
[Unit]
Description=WebSocket Server with TC375 Litekit Support
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/websocket_server
Environment="PATH=/home/ubuntu/websocket_server/venv/bin"
ExecStart=/home/ubuntu/websocket_server/venv/bin/python /home/ubuntu/websocket_server/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/ubuntu/websocket_server/logs/server.log
StandardError=append:/home/ubuntu/websocket_server/logs/server.log

[Install]
WantedBy=multi-user.target
EOF

    # 서비스 파일 이동
    sudo mv /tmp/websocket-server.service /etc/systemd/system/
    
    # systemd 리로드
    sudo systemctl daemon-reload
    
    # 서비스 활성화
    sudo systemctl enable websocket-server
    
    echo "✅ systemd 서비스 생성 완료"
ENDSSH
    
    echo -e "${GREEN}✅ systemd 서비스 생성 완료${NC}"
fi

# 6. 서버 시작
echo ""
read -p "서버를 시작하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 서버 시작 중..."
    
    ssh -i "$SSH_KEY" "$SERVER" /bin/bash << 'ENDSSH'
    set -e
    
    # systemd 서비스가 있으면 그것으로 시작
    if systemctl list-unit-files | grep -q websocket-server.service; then
        sudo systemctl restart websocket-server
        sleep 2
        sudo systemctl status websocket-server --no-pager
    else
        # 없으면 백그라운드로 실행
        cd ~/websocket_server
        source venv/bin/activate
        nohup python main.py > logs/server.log 2>&1 &
        sleep 2
        echo "서버가 백그라운드로 시작되었습니다."
    fi
ENDSSH
    
    echo -e "${GREEN}✅ 서버 시작 완료${NC}"
fi

# 7. 완료 메시지
echo ""
echo "================================"
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo "================================"
echo ""
echo "접속 정보:"
echo "  - WebSocket: wss://54.234.98.110:8765/ws"
echo "  - API: https://54.234.98.110:8765/api"
echo "  - API Docs: https://54.234.98.110:8765/docs"
echo ""
echo "서버 관리 명령어:"
echo "  - 상태 확인: ssh -i $SSH_KEY $SERVER 'sudo systemctl status websocket-server'"
echo "  - 로그 확인: ssh -i $SSH_KEY $SERVER 'tail -f ~/websocket_server/logs/server.log'"
echo "  - 재시작: ssh -i $SSH_KEY $SERVER 'sudo systemctl restart websocket-server'"
echo ""
echo "테스트:"
echo "  curl -k https://54.234.98.110:8765/api/health"
echo ""

