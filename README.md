# TC375 Litekit WebSocket Server

비동기 WebSocket 서버 with TLS 및 PQC (Post-Quantum Cryptography) Hybrid 지원

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [아키텍처](#아키텍처)
- [시작하기](#시작하기)
- [설정](#설정)
- [API 문서](#api-문서)
- [배포](#배포)
- [개발](#개발)
- [보안](#보안)

## 🎯 개요

TC375 Litekit과 통신하는 고성능 비동기 WebSocket 서버입니다. TLS 암호화 및 양자 내성 암호(PQC) 하이브리드 키 교환을 지원합니다.

### 기술 스택

- **Framework**: FastAPI + Uvicorn
- **WebSocket**: websockets 라이브러리
- **비동기 처리**: asyncio
- **검증**: Pydantic v2
- **암호화**: cryptography, pyOpenSSL
- **로깅**: python-json-logger

## ✨ 주요 기능

### 🔐 보안
- ✅ TLS/SSL 암호화 통신
- ✅ PQC Hybrid 키 교환 (Kyber + X25519/X448)
- ✅ Self-signed 인증서 자동 생성
- ✅ 연결 제한 및 타임아웃

### 🚀 성능
- ✅ 비동기 I/O 처리
- ✅ 다중 워커 지원 (프로덕션)
- ✅ 연결 풀링 및 관리
- ✅ 백그라운드 작업 (cleanup)

### 📡 TC375 Litekit
- ✅ 프로토콜 v1/v2 지원
- ✅ 디바이스 등록 및 관리
- ✅ Heartbeat 모니터링
- ✅ 명령 전송 및 응답 처리

### 🔌 API
- ✅ RESTful API (FastAPI)
- ✅ WebSocket 연결
- ✅ 자동 API 문서 (Swagger UI)
- ✅ 실시간 통계

## 🏗️ 아키텍처

### 계층형 아키텍처 (Layered Architecture)

```
┌─────────────────────────────────────────┐
│         Controllers Layer               │
│  (WebSocket & REST API Endpoints)       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Services Layer                 │
│  (Business Logic & Orchestration)       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Repositories Layer               │
│  (Data Access & Persistence)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Models Layer                   │
│  (Domain Models & Entities)             │
└─────────────────────────────────────────┘
```

### 디렉토리 구조

```
websocket_server/
├── main.py                 # 애플리케이션 엔트리 포인트
├── dependencies.py         # Dependency Injection 컨테이너
├── config.py              # 설정 관리
├── config.json            # JSON 설정 파일
├── env.example            # 환경 변수 예제
│
├── controllers/           # 🎮 Controller Layer
│   ├── websocket_controller.py
│   └── api_controller.py
│
├── services/             # 🔧 Service Layer
│   ├── connection_service.py
│   ├── message_service.py
│   ├── tc375_service.py
│   └── pqc_service.py
│
├── repositories/         # 💾 Repository Layer
│   ├── base.py
│   ├── connection.py
│   ├── tc375.py
│   └── pqc.py
│
├── models/              # 📦 Domain Models
│   ├── connection.py
│   ├── message.py
│   ├── tc375.py
│   └── pqc.py
│
├── schemas/             # 📋 Pydantic Schemas
│   ├── connection.py
│   ├── message.py
│   ├── tc375.py
│   ├── pqc.py
│   └── api.py
│
├── utils/               # 🛠️ Utilities
│   ├── logger.py
│   ├── crypto.py
│   ├── validators.py
│   └── formatters.py
│
├── scripts/             # 📜 Scripts
│   ├── generate_certs.sh
│   ├── run_dev.sh
│   ├── run_prod.sh
│   └── test_client.py
│
├── certs/              # 🔐 TLS Certificates
├── logs/               # 📊 Log Files
└── requirements.txt    # 📦 Dependencies
```

## 🚀 시작하기

### 1. 사전 요구사항

- Python 3.9+
- OpenSSL (인증서 생성용)

### 2. 설치

```bash
# 저장소 클론 (또는 디렉토리로 이동)
cd websocket_server

# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3. 설정

#### 방법 1: 환경 변수 (.env)

```bash
cp env.example .env
# .env 파일을 편집하여 설정 수정
```

#### 방법 2: JSON 설정 (config.json)

```json
{
  "server": {
    "host": "0.0.0.0",
    "websocket_port": 8765,
    "api_port": 8080
  },
  "tls": {
    "enabled": true,
    "cert_path": "./certs/server.crt",
    "key_path": "./certs/server.key"
  },
  "pqc": {
    "enabled": true,
    "algorithms": {
      "kem": "kyber768",
      "kex": "x25519",
      "hybrid_mode": true
    }
  }
}
```

### 4. TLS 인증서 생성

```bash
# Self-signed 인증서 생성
./scripts/generate_certs.sh
```

### 5. 서버 실행

#### 개발 모드 (Hot Reload)

```bash
./scripts/run_dev.sh
# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8765
```

#### 프로덕션 모드

```bash
./scripts/run_prod.sh
# 또는
uvicorn main:app --host 0.0.0.0 --port 8765 --workers 4
```

### 6. 테스트

```bash
# WebSocket 테스트 클라이언트 실행
python scripts/test_client.py

# TLS 사용 시
python scripts/test_client.py --tls

# 다른 호스트/포트
python scripts/test_client.py --host example.com --port 8765
```

## ⚙️ 설정

### 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `SERVER_HOST` | 서버 호스트 | `0.0.0.0` |
| `SERVER_WS_PORT` | WebSocket 포트 | `8765` |
| `TLS_ENABLED` | TLS 활성화 | `true` |
| `TLS_CERT_PATH` | 인증서 경로 | `./certs/server.crt` |
| `TLS_KEY_PATH` | 키 경로 | `./certs/server.key` |
| `PQC_ENABLED` | PQC 활성화 | `true` |
| `PQC_ALGORITHM` | PQC 알고리즘 | `kyber768_x25519` |
| `MAX_MESSAGE_SIZE` | 최대 메시지 크기 | `1048576` (1MB) |
| `MAX_CONNECTIONS` | 최대 연결 수 | `1000` |
| `LOG_LEVEL` | 로그 레벨 | `INFO` |

### PQC 지원 알고리즘

- `kyber512` - Kyber-512 (NIST Level 1)
- `kyber768` - Kyber-768 (NIST Level 3) ⭐ 권장
- `kyber1024` - Kyber-1024 (NIST Level 5)
- `kyber768_x25519` - Hybrid (Kyber-768 + X25519) ⭐ 권장
- `kyber1024_x448` - Hybrid (Kyber-1024 + X448)

## 📚 API 문서

### WebSocket API

#### 연결

```
ws://localhost:8765/ws
wss://localhost:8765/ws  (TLS 사용 시)
```

#### 메시지 형식

```json
{
  "type": "message_type",
  "payload": {
    "key": "value"
  }
}
```

#### 메시지 타입

| 타입 | 설명 | 방향 |
|------|------|------|
| `welcome` | 환영 메시지 | Server → Client |
| `ping` | Ping 요청 | Client → Server |
| `pong` | Pong 응답 | Server → Client |
| `pqc_handshake` | PQC 핸드셰이크 요청 | Client → Server |
| `pqc_handshake_response` | PQC 핸드셰이크 응답 | Server → Client |
| `tc375_data` | TC375 데이터 | Client → Server |
| `tc375_data_response` | TC375 응답 | Server → Client |
| `command` | 명령 실행 | Client → Server |
| `status` | 상태 요청 | Client → Server |

### REST API

서버 실행 후 다음 URL에서 자동 생성된 API 문서 확인:

- Swagger UI: `http://localhost:8765/docs`
- ReDoc: `http://localhost:8765/redoc`
- OpenAPI JSON: `http://localhost:8765/openapi.json`

#### 주요 엔드포인트

```bash
# Health Check
GET /api/health

# 서버 상태
GET /api/status

# 활성 연결 목록
GET /api/connections

# 브로드캐스트
POST /api/broadcast
{
  "message": {"text": "Hello everyone"}
}

# 특정 클라이언트에 메시지 전송
POST /api/send
{
  "client_id": "client_id",
  "message": {"text": "Hello"}
}

# TC375 명령 전송
POST /api/tc375/command
{
  "device_id": "device_123",
  "command_type": "read",
  "parameters": {}
}

# PQC 정보
GET /api/pqc/info
```

## 🐳 배포

### Docker

```bash
# Docker 이미지 빌드
docker build -t websocket-server .

# 컨테이너 실행
docker run -p 8765:8765 \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/certs:/app/certs \
  websocket-server
```

### Docker Compose

```bash
docker-compose up -d
```

### Linux 서비스 (systemd)

```bash
# /etc/systemd/system/websocket-server.service 생성
sudo systemctl enable websocket-server
sudo systemctl start websocket-server
```

## 👨‍💻 개발

### 프로젝트 구조

이 프로젝트는 **계층형 아키텍처 (Layered Architecture)** 를 사용합니다:

1. **Controller Layer**: HTTP/WebSocket 요청 처리
2. **Service Layer**: 비즈니스 로직
3. **Repository Layer**: 데이터 접근
4. **Model Layer**: 도메인 모델

### 디자인 패턴

- **Dependency Injection**: 느슨한 결합
- **Repository Pattern**: 데이터 접근 추상화
- **Service Pattern**: 비즈니스 로직 캡슐화
- **Singleton**: 전역 컨테이너 관리

### 코드 스타일

```bash
# 포매팅
black .

# 린팅
flake8 .

# 테스트
pytest
```

## 🔒 보안

### 프로덕션 체크리스트

- [ ] 신뢰할 수 있는 CA의 인증서 사용
- [ ] 강력한 TLS 설정 (TLS 1.3 권장)
- [ ] 연결 제한 및 Rate Limiting 설정
- [ ] 로그 모니터링 구성
- [ ] 방화벽 설정
- [ ] 환경 변수로 민감 정보 관리
- [ ] 정기적인 보안 업데이트

### PQC 보안 노트

⚠️ **중요**: 현재 PQC 구현은 **MVP용 시뮬레이션**입니다.

프로덕션 환경에서는 다음을 사용하세요:
- [liboqs-python](https://github.com/open-quantum-safe/liboqs-python)
- [PQClean](https://github.com/PQClean/PQClean)

## 📊 모니터링

### 로그

로그는 다음 위치에 저장됩니다:
- 파일: `./logs/server.log`
- 콘솔: stdout

JSON 형식 로그 예시:
```json
{
  "timestamp": "2025-10-17T12:00:00.000Z",
  "level": "INFO",
  "service": "websocket_server",
  "message": "Connection created",
  "connection_id": "192.168.1.100:54321:1697544000",
  "remote_address": "192.168.1.100:54321"
}
```

### 통계 API

```bash
# 전체 통계
curl http://localhost:8765/api/statistics
```

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📝 라이선스

This project is licensed under the MIT License.

## 📞 지원

문의사항이나 이슈가 있으시면 GitHub Issues를 이용해주세요.

---

**Made with ❤️ for TC375 Litekit**

