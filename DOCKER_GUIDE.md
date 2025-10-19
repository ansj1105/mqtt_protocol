# Docker 배포 가이드 🐳

## 📦 관리 대시보드 추가됨!

이제 웹 기반 관리 대시보드가 포함되어 있습니다:
- **대시보드**: `https://54.234.98.110:8765/admin/`
- 실시간 통계, 연결 관리, TC375 디바이스 관리, 로그 뷰어

## 🎯 Docker 사용 권장!

### Docker의 장점
✅ **환경 일관성**: 로컬과 서버에서 동일하게 작동  
✅ **Python 버전 걱정 없음**: 컨테이너에 모든 것 포함  
✅ **쉬운 배포**: 한 번 빌드, 어디서나 실행  
✅ **빠른 롤백**: 문제 발생 시 이전 버전으로 즉시 복구  
✅ **리소스 격리**: 다른 애플리케이션과 분리  

## 🚀 빠른 시작 (Docker Compose 사용)

### 1단계: Docker 설치

```bash
# EC2 서버에서 실행
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 로그아웃 후 다시 로그인하거나
newgrp docker

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 설치 확인
docker --version
docker-compose --version
```

### 2단계: 프로젝트 업로드

```bash
# 로컬에서 서버로 전송
scp -i your-key.pem -r /Users/an/PycharmProjects/PythonProject/websocket_server ubuntu@54.234.98.110:~/

# 또는 Git 사용
ssh -i your-key.pem ubuntu@54.234.98.110
cd ~
git clone your-repo-url
cd websocket_server
```

### 3단계: .env 파일 설정

```bash
# 서버에서
cd ~/websocket_server

# .env 파일 생성
./create_env.sh
```

### 4단계: Docker로 실행

```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 상태 확인
docker-compose ps
```

**완료!** 서버가 실행 중입니다! 🎉

## 📋 Docker Compose 명령어

```bash
# 시작
docker-compose up -d

# 중지
docker-compose down

# 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f

# 상태 확인
docker-compose ps

# 컨테이너 접속
docker-compose exec websocket-server bash

# 빌드 다시 (코드 변경 시)
docker-compose up -d --build

# 완전 삭제 (볼륨 포함)
docker-compose down -v
```

## 🔧 Docker만 사용 (Compose 없이)

### 빌드

```bash
docker build -t websocket-server:latest .
```

### 실행

```bash
docker run -d \
  --name websocket-server \
  -p 8765:8765 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/certs:/app/certs \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  websocket-server:latest
```

### 관리

```bash
# 로그 확인
docker logs -f websocket-server

# 상태 확인
docker ps

# 중지
docker stop websocket-server

# 시작
docker start websocket-server

# 재시작
docker restart websocket-server

# 삭제
docker rm -f websocket-server

# 컨테이너 접속
docker exec -it websocket-server bash
```

## 🔄 업데이트 방법

### Docker Compose 사용 시

```bash
cd ~/websocket_server

# 최신 코드 가져오기
git pull  # 또는 파일 동기화

# 재빌드 및 재시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f
```

### Docker만 사용 시

```bash
# 기존 컨테이너 중지 및 삭제
docker stop websocket-server
docker rm websocket-server

# 새로 빌드
docker build -t websocket-server:latest .

# 다시 실행
docker run -d \
  --name websocket-server \
  -p 8765:8765 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/certs:/app/certs \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  websocket-server:latest
```

## 🎛️ 환경 변수 관리

Docker 실행 시 환경 변수 직접 전달:

```bash
docker run -d \
  --name websocket-server \
  -p 8765:8765 \
  -e SERVER_HOST=0.0.0.0 \
  -e SERVER_WS_PORT=8765 \
  -e TLS_ENABLED=true \
  -e PQC_ENABLED=true \
  -e LOG_LEVEL=INFO \
  -v $(pwd)/certs:/app/certs \
  -v $(pwd)/logs:/app/logs \
  websocket-server:latest
```

## 📊 리소스 제한

```bash
docker run -d \
  --name websocket-server \
  -p 8765:8765 \
  --cpus="2" \
  --memory="1g" \
  --memory-swap="2g" \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/certs:/app/certs \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  websocket-server:latest
```

## 🔍 모니터링

### 리소스 사용량 확인

```bash
# 실시간 모니터링
docker stats websocket-server

# 디스크 사용량
docker system df
```

### Health Check

```bash
# 헬스체크 상태
docker inspect --format='{{.State.Health.Status}}' websocket-server

# 로컬에서
curl -k https://54.234.98.110:8765/api/health
```

## 🐛 트러블슈팅

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker logs websocket-server

# 상세 로그
docker logs --tail 100 websocket-server
```

### 포트 충돌

```bash
# 8765 포트 사용 중인 프로세스 확인
sudo lsof -i :8765

# 또는
sudo netstat -tulpn | grep 8765
```

### 볼륨 권한 문제

```bash
# 컨테이너 내부에서
docker exec -it websocket-server bash
ls -la /app/logs
ls -la /app/certs

# 호스트에서 권한 수정
sudo chown -R $USER:$USER logs certs
```

### 네트워크 문제

```bash
# Docker 네트워크 확인
docker network ls

# 컨테이너 네트워크 정보
docker inspect websocket-server | grep -A 10 Networks
```

## 🔐 보안 설정

### 비root 사용자로 실행

Dockerfile에서 이미 설정되어 있습니다.

### 읽기 전용 파일시스템

```bash
docker run -d \
  --name websocket-server \
  -p 8765:8765 \
  --read-only \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/certs:/app/certs:ro \
  -v $(pwd)/logs:/app/logs \
  --tmpfs /tmp \
  websocket-server:latest
```

## 📦 백업 및 복구

### 백업

```bash
# 로그 백업
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# 설정 백업
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env certs/ config.json
```

### 복구

```bash
# 로그 복구
tar -xzf logs-backup-20231019.tar.gz

# 설정 복구
tar -xzf config-backup-20231019.tar.gz
```

## 🌐 Docker Hub에 푸시 (선택)

```bash
# 로그인
docker login

# 태그
docker tag websocket-server:latest yourusername/websocket-server:latest

# 푸시
docker push yourusername/websocket-server:latest

# 다른 서버에서 사용
docker pull yourusername/websocket-server:latest
docker run -d -p 8765:8765 yourusername/websocket-server:latest
```

## ⚡ 성능 최적화

### Multi-stage 빌드 (이미 적용됨)

Dockerfile이 이미 multi-stage 빌드를 사용하여 이미지 크기를 최소화합니다.

### 레이어 캐싱

```bash
# 캐시 없이 빌드 (완전히 새로 빌드)
docker build --no-cache -t websocket-server:latest .

# 캐시 사용 (빠름)
docker build -t websocket-server:latest .
```

## 📊 비교: Docker vs 직접 설치

| 항목 | Docker | 직접 설치 |
|------|--------|----------|
| 설치 난이도 | ⭐⭐ 쉬움 | ⭐⭐⭐⭐ 복잡 |
| 환경 일관성 | ✅ 완벽 | ⚠️ 서버마다 다를 수 있음 |
| Python 버전 | ✅ 자동 포함 | ❌ 수동 설치 필요 |
| 업데이트 | ✅ 매우 쉬움 | ⚠️ 의존성 관리 필요 |
| 롤백 | ✅ 즉시 가능 | ❌ 어려움 |
| 리소스 사용 | ⚠️ 약간 더 많음 | ✅ 최소 |
| 디버깅 | ⚠️ 약간 복잡 | ✅ 직접 접근 |

## 💡 권장 배포 방법

### 개발 환경
```bash
# 직접 설치 (빠른 디버깅)
python main.py
```

### 테스트/스테이징
```bash
# Docker Compose
docker-compose up -d
```

### 프로덕션
```bash
# Docker Compose + 모니터링
docker-compose up -d

# 또는 Kubernetes (대규모)
kubectl apply -f k8s/
```

## 🎉 추천: Docker Compose 사용!

가장 간단하고 관리하기 쉬운 방법입니다:

```bash
# 설치
sudo apt install docker.io docker-compose -y

# 실행
docker-compose up -d

# 끝!
```

## 📞 도움말

문제가 발생하면:
1. `docker-compose logs -f` 로그 확인
2. `docker ps` 컨테이너 상태 확인
3. `https://54.234.98.110:8765/admin/` 대시보드 확인
4. GitHub Issues에 문의

---

**Happy Deploying! 🚀**

