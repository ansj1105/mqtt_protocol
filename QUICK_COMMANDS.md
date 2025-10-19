# 빠른 명령어 모음 ⚡

## 🚀 서버 재배포 (완전판)

### 로컬에서:
```bash
cd /Users/an/PycharmProjects/PythonProject
tar --exclude='venv' --exclude='__pycache__' --exclude='.git' -czf ws.tar.gz websocket_server/
scp -i /Users/an/Downloads/bmbit.pem ws.tar.gz ubuntu@54.234.98.110:~/
```

### 서버에서:
```bash
ssh -i /Users/an/Downloads/bmbit.pem ubuntu@54.234.98.110
cd ~ && rm -rf mqtt_protocol && tar -xzf ws.tar.gz && mv websocket_server mqtt_protocol && cd mqtt_protocol
docker compose down --rmi all && docker compose build --no-cache && docker compose up -d
docker compose logs -f
```

## 📊 연결 확인

```bash
# 연결된 클라이언트 목록
curl -k https://54.234.98.110:8765/api/connections | jq '.connections[] | {id, remote_address, status}'

# 연결 수
curl -k https://54.234.98.110:8765/api/connections | jq '.count'

# 서버 상태
curl -k https://54.234.98.110:8765/api/status | jq '.'
```

## 💬 메시지 전송

```bash
# 모든 클라이언트에 브로드캐스트
curl -k -X POST https://54.234.98.110:8765/api/broadcast \
  -H "Content-Type: application/json" \
  -d '{"message": {"type": "notification", "text": "안녕하세요!"}}'

# 특정 클라이언트에 전송 (client_id는 /api/connections에서 확인)
curl -k -X POST https://54.234.98.110:8765/api/send \
  -H "Content-Type: application/json" \
  -d '{"client_id": "클라이언트_ID", "message": {"text": "Hello!"}}'

# 클라이언트 연결 해제
curl -k -X POST https://54.234.98.110:8765/api/disconnect \
  -H "Content-Type: application/json" \
  -d '{"client_id": "클라이언트_ID"}'
```

## 🧪 클라이언트 테스트

```bash
# 간단한 테스트
cd /Users/an/PycharmProjects/PythonProject/websocket_server
python3 test_connection.py

# 상세한 테스트
python3 examples/client_example.py

# 프로젝트 내장 테스트 클라이언트
python3 scripts/test_client.py --host 54.234.98.110 --port 8765 --tls
```

## 🐳 Docker 관리

```bash
# 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f

# 재시작
docker compose restart

# 완전 삭제 후 재빌드
docker compose down --rmi all
docker compose build --no-cache
docker compose up -d

# 컨테이너 접속
docker exec -it websocket-server bash

# 리소스 사용량
docker stats websocket-server
```

## 🌐 대시보드 접속

```
https://54.234.98.110:8765/admin/         # 메인 대시보드
https://54.234.98.110:8765/admin/messages # 메시지 관리 ⭐ 신규!
https://54.234.98.110:8765/admin/connections # 연결 관리
https://54.234.98.110:8765/admin/devices  # 디바이스 관리
https://54.234.98.110:8765/docs          # API 문서
```

## 📋 서버 로그

```bash
# 서버 접속
ssh -i /Users/an/Downloads/bmbit.pem ubuntu@54.234.98.110

# 로그 확인
cd ~/mqtt_protocol
docker compose logs --tail=50

# 실시간 로그
docker compose logs -f

# 에러만 보기
docker compose logs | grep -i error

# WebSocket 관련만 보기
docker compose logs | grep -i websocket
```

## 🔥 원라이너 모음

```bash
# 서버 상태 빠른 확인
curl -k https://54.234.98.110:8765/api/health

# 연결 수 확인
curl -k -s https://54.234.98.110:8765/api/connections | jq '.count'

# 통계
curl -k -s https://54.234.98.110:8765/api/statistics | jq '.connections.active_connections'

# 브로드캐스트 (한 줄)
curl -k -X POST https://54.234.98.110:8765/api/broadcast -H "Content-Type: application/json" -d '{"message":{"text":"Hi"}}'
```

## ⚡ 별칭 설정 (선택)

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
alias ws-status='curl -k -s https://54.234.98.110:8765/api/status | jq .'
alias ws-connections='curl -k -s https://54.234.98.110:8765/api/connections | jq .'
alias ws-stats='curl -k -s https://54.234.98.110:8765/api/statistics | jq .'
alias ws-logs='ssh -i /Users/an/Downloads/bmbit.pem ubuntu@54.234.98.110 "cd mqtt_protocol && docker compose logs --tail=50"'

# 사용
ws-status
ws-connections
```

저장하고 사용하세요! 📝

