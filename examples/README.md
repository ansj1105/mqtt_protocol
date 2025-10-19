# 클라이언트 연결 예제

## 📁 파일 목록

- `client_example.py` - 완전한 Python 클라이언트 예제
- `simple_client.py` - 간단한 Python 클라이언트
- `javascript_client.html` - 브라우저 기반 클라이언트

## 🚀 사용 방법

### Python 클라이언트

```bash
# 의존성 설치
pip install websockets

# 실행
python examples/client_example.py
# 또는
python examples/simple_client.py
```

### JavaScript 클라이언트

```bash
# 브라우저에서 열기
open examples/javascript_client.html

# 또는 간단한 웹 서버로
python -m http.server 8000
# 브라우저에서 http://localhost:8000/examples/javascript_client.html
```

## 📡 메시지 타입

### 1. Ping/Pong

```json
{
  "type": "ping",
  "payload": {
    "timestamp": "2024-01-01T00:00:00"
  }
}
```

### 2. PQC Handshake

```json
{
  "type": "pqc_handshake",
  "payload": {
    "algorithm": "kyber768_x25519",
    "public_key": "your_public_key_here"
  }
}
```

### 3. TC375 Data

```json
{
  "type": "tc375_data",
  "payload": {
    "protocol": "v2",
    "payload": {
      "sensor_data": {
        "temperature": 25.5
      }
    }
  }
}
```

### 4. Command

```json
{
  "type": "command",
  "payload": {
    "command": "get_stats",
    "params": {}
  }
}
```

### 5. Status

```json
{
  "type": "status",
  "payload": {}
}
```

## 🔐 TLS 설정

### Python (Self-signed)

```python
import ssl
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

### Python (CA 인증서)

```python
import ssl
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations('ca.crt')
```

### JavaScript

브라우저는 자동으로 처리하지만, self-signed 인증서는 경고가 표시됩니다.

## 📊 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/connections` | GET | 연결 목록 |
| `/api/status` | GET | 서버 상태 |
| `/api/broadcast` | POST | 브로드캐스트 |
| `/api/send` | POST | 특정 클라이언트에 전송 |

## 🎯 테스트

```bash
# 제공된 테스트 클라이언트
python scripts/test_client.py --host 54.234.98.110 --port 8765 --tls
```

