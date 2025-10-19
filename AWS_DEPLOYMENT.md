# AWS EC2 배포 가이드

## 📋 사전 준비

### 서버 정보
- **IP**: 54.234.98.110
- **포트**: 8765
- **OS**: Ubuntu 20.04/22.04 LTS 권장

## 🔧 1. AWS EC2 보안 그룹 설정

### 인바운드 규칙 추가

| 타입 | 프로토콜 | 포트 범위 | 소스 | 설명 |
|------|----------|----------|------|------|
| SSH | TCP | 22 | My IP | SSH 접속 |
| Custom TCP | TCP | 8765 | 0.0.0.0/0 | WebSocket 서버 |
| Custom TCP | TCP | 8765 | ::/0 | WebSocket 서버 (IPv6) |

### AWS Console에서 설정
1. EC2 Dashboard → Security Groups
2. 해당 보안 그룹 선택
3. Inbound rules → Edit inbound rules
4. Add rule:
   - Type: Custom TCP
   - Port: 8765
   - Source: Anywhere-IPv4 (0.0.0.0/0)
5. Save rules

### CLI로 설정 (선택)
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 8765 \
  --cidr 0.0.0.0/0
```

## 🖥️ 2. EC2 서버 접속

```bash
# SSH로 서버 접속
ssh -i your-key.pem ubuntu@54.234.98.110

# 또는 사용자가 다르다면
ssh -i your-key.pem ec2-user@54.234.98.110
```

## 📦 3. 시스템 패키지 설치

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    openssl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# Python 버전 확인 (3.9 이상 필요)
python3 --version
```

### Python 3.11 설치 (Ubuntu 20.04인 경우)

```bash
# deadsnakes PPA 추가
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Python 3.11 설치
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# python3.11을 기본으로 설정 (선택)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

## 📁 4. 프로젝트 배포

### 방법 1: Git으로 배포 (권장)

```bash
# 작업 디렉토리 생성
mkdir -p ~/apps
cd ~/apps

# Git clone (GitHub에 푸시한 경우)
git clone https://github.com/your-username/websocket_server.git
cd websocket_server

# 또는 직접 업로드한 경우 해당 디렉토리로 이동
```

### 방법 2: SCP로 파일 전송

로컬에서 실행:
```bash
# 전체 프로젝트 압축
cd /Users/an/PycharmProjects/PythonProject
tar -czf websocket_server.tar.gz websocket_server/

# 서버로 전송
scp -i your-key.pem websocket_server.tar.gz ubuntu@54.234.98.110:~/

# 서버에서 압축 해제
ssh -i your-key.pem ubuntu@54.234.98.110
cd ~
tar -xzf websocket_server.tar.gz
cd websocket_server
```

### 방법 3: rsync로 동기화

```bash
# 로컬에서 실행
rsync -avz -e "ssh -i your-key.pem" \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  /Users/an/PycharmProjects/PythonProject/websocket_server/ \
  ubuntu@54.234.98.110:~/websocket_server/
```

## 🐍 5. Python 환경 설정

```bash
cd ~/websocket_server  # 또는 프로젝트 경로

# 가상 환경 생성
python3.11 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt

# 설치 확인
pip list
```

## 🔐 6. SSL 인증서 설정

인증서는 이미 생성되어 있으므로 확인만:

```bash
# 인증서 확인
ls -lh certs/

# 인증서 정보 확인
openssl x509 -in certs/server.crt -noout -text | head -20
```

## ⚙️ 7. 환경 설정

.env 파일이 이미 있으므로 확인:

```bash
# .env 파일 확인
cat .env

# 필요시 수정
nano .env
```

## 🔥 8. 방화벽 설정 (Ubuntu UFW)

```bash
# UFW 상태 확인
sudo ufw status

# UFW가 비활성화되어 있다면
sudo ufw enable

# 8765 포트 열기
sudo ufw allow 8765/tcp

# SSH 포트도 열기 (안전을 위해)
sudo ufw allow 22/tcp

# 규칙 확인
sudo ufw status numbered
```

## 🚀 9. 서버 실행

### 테스트 실행 (포그라운드)

```bash
# 가상 환경 활성화 확인
source venv/bin/activate

# 서버 실행
python main.py

# 또는
uvicorn main:app --host 0.0.0.0 --port 8765
```

다른 터미널에서 테스트:
```bash
curl http://localhost:8765/api/health
```

### 프로덕션 실행 (백그라운드)

#### 방법 1: nohup 사용

```bash
# 백그라운드 실행
nohup python main.py > logs/server.log 2>&1 &

# 프로세스 확인
ps aux | grep python

# 로그 확인
tail -f logs/server.log

# 종료
pkill -f "python main.py"
```

#### 방법 2: systemd 서비스 (권장)

서비스 파일 생성:
```bash
sudo nano /etc/systemd/system/websocket-server.service
```

내용:
```ini
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
```

서비스 실행:
```bash
# systemd 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start websocket-server

# 부팅 시 자동 시작 설정
sudo systemctl enable websocket-server

# 상태 확인
sudo systemctl status websocket-server

# 로그 확인
sudo journalctl -u websocket-server -f

# 재시작
sudo systemctl restart websocket-server

# 중지
sudo systemctl stop websocket-server
```

#### 방법 3: screen 사용

```bash
# screen 설치
sudo apt install screen -y

# screen 세션 시작
screen -S websocket

# 서버 실행
source venv/bin/activate
python main.py

# screen에서 나가기 (Ctrl+A, D)

# screen 목록 확인
screen -ls

# screen 재접속
screen -r websocket

# screen 종료
screen -X -S websocket quit
```

## 📊 10. 모니터링 및 확인

### 서버 상태 확인

```bash
# 포트 리스닝 확인
sudo netstat -tulpn | grep 8765
# 또는
sudo ss -tulpn | grep 8765

# 프로세스 확인
ps aux | grep python

# 로그 확인
tail -f logs/server.log

# 실시간 로그 (JSON 파싱)
tail -f logs/server.log | jq '.'
```

### 외부에서 접근 테스트

로컬 컴퓨터에서:
```bash
# Health check
curl -k https://54.234.98.110:8765/api/health

# WebSocket 테스트
python scripts/test_client.py --host 54.234.98.110 --port 8765 --tls

# 브라우저에서
# https://54.234.98.110:8765/docs
```

## 🔧 11. 트러블슈팅

### 포트가 이미 사용 중

```bash
# 8765 포트 사용 프로세스 확인
sudo lsof -i :8765

# 프로세스 종료
sudo kill -9 <PID>
```

### 연결이 안됨

```bash
# 1. 서버가 실행 중인지 확인
sudo systemctl status websocket-server

# 2. 포트가 열려있는지 확인
sudo netstat -tulpn | grep 8765

# 3. 방화벽 확인
sudo ufw status

# 4. AWS 보안 그룹 확인
# AWS Console에서 확인

# 5. 로그 확인
tail -50 logs/server.log
```

### Permission Denied

```bash
# 파일 권한 확인
ls -la

# 소유자 변경
sudo chown -R ubuntu:ubuntu ~/websocket_server

# 실행 권한 추가
chmod +x scripts/*.sh
```

### Python 모듈 없음

```bash
# 가상 환경 활성화 확인
which python
# /home/ubuntu/websocket_server/venv/bin/python 이어야 함

# 의존성 재설치
pip install -r requirements.txt

# 특정 패키지 설치
pip install fastapi uvicorn websockets
```

## 🔄 12. 업데이트 방법

```bash
# Git 사용 시
cd ~/websocket_server
git pull

# 파일 직접 업데이트 시
# rsync로 동기화

# 의존성 업데이트
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 서버 재시작
sudo systemctl restart websocket-server
```

## 📈 13. 성능 최적화

### Uvicorn Workers 사용

```bash
# 4개의 워커로 실행 (CPU 코어 수에 맞게)
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8765 \
  --workers 4 \
  --log-level info
```

systemd 서비스 파일 수정:
```ini
ExecStart=/home/ubuntu/websocket_server/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8765 --workers 4
```

### 시스템 리소스 모니터링

```bash
# CPU/메모리 사용량
htop

# 디스크 사용량
df -h

# 네트워크 트래픽
sudo iftop -i eth0
```

## 🔐 14. 보안 강화

```bash
# SSH 보안 설정
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no

# 자동 보안 업데이트
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades

# fail2ban 설치 (무차별 대입 공격 방지)
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## ✅ 배포 체크리스트

- [ ] EC2 인스턴스 생성 완료
- [ ] 보안 그룹 8765 포트 오픈
- [ ] Python 3.11 설치
- [ ] 프로젝트 파일 업로드
- [ ] 가상 환경 생성 및 의존성 설치
- [ ] .env 파일 확인
- [ ] SSL 인증서 확인
- [ ] UFW 방화벽 설정
- [ ] systemd 서비스 등록
- [ ] 서버 실행 및 테스트
- [ ] 자동 시작 설정
- [ ] 로그 확인
- [ ] 외부 접속 테스트

## 📞 빠른 명령어 참고

```bash
# 서버 시작
sudo systemctl start websocket-server

# 서버 중지
sudo systemctl stop websocket-server

# 서버 재시작
sudo systemctl restart websocket-server

# 상태 확인
sudo systemctl status websocket-server

# 로그 확인
tail -f logs/server.log
sudo journalctl -u websocket-server -f

# 포트 확인
sudo netstat -tulpn | grep 8765
```

## 🎉 완료!

서버가 정상적으로 실행되면:

- **WebSocket**: `wss://54.234.98.110:8765/ws`
- **API**: `https://54.234.98.110:8765/api`
- **API Docs**: `https://54.234.98.110:8765/docs`
- **Health Check**: `https://54.234.98.110:8765/api/health`

---

문제 발생 시 로그를 확인하고 GitHub Issues에 문의하세요!

