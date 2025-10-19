# 프로덕션 배포 가이드

## 🌐 서버 정보

- **IP**: 54.234.98.110
- **포트**: 8765
- **프로토콜**: WSS (WebSocket Secure)

## ✅ SSL 인증서 생성 완료

SSL 인증서가 성공적으로 생성되었습니다:

```
certs/
├── ca.crt          (CA 인증서)
├── ca.key          (CA 비밀키)
├── server.crt      (서버 인증서) ← CN=54.234.98.110
└── server.key      (서버 비밀키)
```

**인증서 정보**:
- Subject: CN=54.234.98.110
- 유효기간: 365일
- 키 길이: RSA 4096bit
- 해시: SHA-256

⚠️ **중요**: 이것은 Self-signed 인증서입니다. 프로덕션에서는 Let's Encrypt나 상용 CA의 인증서를 권장합니다.

## 🚀 배포 방법

### 방법 1: 직접 실행

```bash
# 1. .env 파일 생성
cp .env.production .env

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 서버 실행
python main.py

# 또는 uvicorn으로 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8765 --workers 4
```

### 방법 2: 프로덕션 스크립트 사용

```bash
# .env.production을 .env로 복사 후
./scripts/run_prod.sh
```

### 방법 3: Docker

```bash
# Docker 이미지 빌드
docker build -t websocket-server .

# 컨테이너 실행
docker run -d \
  --name websocket-server \
  -p 8765:8765 \
  -v $(pwd)/.env.production:/app/.env \
  -v $(pwd)/certs:/app/certs \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  websocket-server
```

### 방법 4: Docker Compose

```bash
# .env.production을 .env로 복사 후
cp .env.production .env

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 🔌 접속 URL

### WebSocket
```
wss://54.234.98.110:8765/ws
```

### REST API
```
https://54.234.98.110:8765/api
```

### API 문서 (Swagger)
```
https://54.234.98.110:8765/docs
```

### Health Check
```
https://54.234.98.110:8765/api/health
```

## 🧪 테스트

### 1. 로컬에서 테스트

```bash
# WebSocket 테스트 클라이언트 실행
python scripts/test_client.py --host 54.234.98.110 --port 8765 --tls

# 또는 curl로 Health Check
curl -k https://54.234.98.110:8765/api/health
```

### 2. 브라우저 테스트

브라우저에서 접속:
```
https://54.234.98.110:8765/docs
```

⚠️ Self-signed 인증서이므로 브라우저에서 보안 경고가 나타납니다. "고급" → "계속 진행" 선택

## 🔐 방화벽 설정

서버에서 다음 포트를 열어야 합니다:

```bash
# Ubuntu/Debian
sudo ufw allow 8765/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8765/tcp
sudo firewall-cmd --reload

# AWS Security Group
Inbound Rules:
- Type: Custom TCP
- Port: 8765
- Source: 0.0.0.0/0 (또는 특정 IP)
```

## 📊 모니터링

### 로그 확인

```bash
# 실시간 로그
tail -f logs/server.log

# JSON 로그 파싱
tail -f logs/server.log | jq '.'
```

### 서버 상태 확인

```bash
# API로 상태 확인
curl -k https://54.234.98.110:8765/api/status

# 통계 확인
curl -k https://54.234.98.110:8765/api/statistics

# 활성 연결 확인
curl -k https://54.234.98.110:8765/api/connections
```

## 🔄 systemd 서비스 설정 (Linux)

```bash
# /etc/systemd/system/websocket-server.service 생성
sudo nano /etc/systemd/system/websocket-server.service
```

내용:
```ini
[Unit]
Description=WebSocket Server with TC375 Litekit Support
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/websocket_server
Environment="PATH=/path/to/websocket_server/venv/bin"
ExecStart=/path/to/websocket_server/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

실행:
```bash
sudo systemctl daemon-reload
sudo systemctl enable websocket-server
sudo systemctl start websocket-server
sudo systemctl status websocket-server
```

## 🔒 Let's Encrypt 인증서 (권장)

Self-signed 인증서 대신 Let's Encrypt 무료 인증서 사용:

```bash
# Certbot 설치
sudo apt-get install certbot

# 인증서 발급 (도메인이 있는 경우)
sudo certbot certonly --standalone -d your-domain.com

# .env 파일 수정
TLS_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
TLS_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem

# 자동 갱신
sudo certbot renew --dry-run
```

## 📝 환경 변수 설명

| 변수 | 값 | 설명 |
|------|-----|------|
| SERVER_HOST | 0.0.0.0 | 모든 인터페이스에서 수신 |
| SERVER_WS_PORT | 8765 | WebSocket 포트 |
| TLS_ENABLED | true | TLS 암호화 활성화 |
| PQC_ENABLED | true | PQC 하이브리드 활성화 |
| MAX_CONNECTIONS | 5000 | 최대 동시 연결 (서버 스펙에 맞게 조정) |
| LOG_LEVEL | INFO | 프로덕션 로그 레벨 |

## ⚠️ 보안 체크리스트

- [x] SSL/TLS 인증서 생성 완료
- [ ] 방화벽 설정 확인
- [ ] Let's Encrypt 인증서로 교체 (도메인 있는 경우)
- [ ] 환경 변수 파일 권한 설정 (chmod 600 .env)
- [ ] 로그 로테이션 설정
- [ ] 모니터링 도구 설정 (Prometheus, Grafana 등)
- [ ] 백업 정책 수립
- [ ] Rate Limiting 설정 확인

## 🐞 트러블슈팅

### 포트가 이미 사용 중

```bash
# 8765 포트 사용 중인 프로세스 확인
sudo lsof -i :8765
sudo netstat -tulpn | grep 8765

# 프로세스 종료
sudo kill -9 <PID>
```

### 인증서 오류

```bash
# 인증서 확인
openssl x509 -in certs/server.crt -noout -text

# 인증서 재생성
./scripts/generate_certs.sh
```

### 연결 안됨

```bash
# 서버 실행 확인
ps aux | grep python

# 포트 리스닝 확인
sudo netstat -tulpn | grep 8765

# 방화벽 확인
sudo ufw status
```

## 📞 지원

문제가 발생하면:
1. 로그 파일 확인: `logs/server.log`
2. 서버 상태 확인: `curl https://54.234.98.110:8765/api/health`
3. GitHub Issues 제출

---

**배포 완료!** 🎉

서버 접속: `wss://54.234.98.110:8765/ws`

