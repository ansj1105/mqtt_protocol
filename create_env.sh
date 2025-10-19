#!/bin/bash
cat > .env << 'ENVEOF'
# Production Server Configuration for 54.234.98.110
SERVER_HOST=0.0.0.0
SERVER_WS_PORT=8765
SERVER_API_PORT=8080

# TLS Configuration
TLS_ENABLED=true
TLS_CERT_PATH=./certs/server.crt
TLS_KEY_PATH=./certs/server.key

# PQC Configuration
PQC_ENABLED=true
PQC_ALGORITHM=kyber768_x25519

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security (Production settings)
MAX_MESSAGE_SIZE=2097152
CONNECTION_TIMEOUT=600
MAX_CONNECTIONS=5000

# TC375 Litekit Configuration
TC375_CLIENT_TIMEOUT=30
TC375_MAX_RETRIES=3
ENVEOF

echo "✅ .env 파일이 생성되었습니다!"
echo ""
echo "접속 정보:"
echo "  - IP: 54.234.98.110"
echo "  - WebSocket: wss://54.234.98.110:8765/ws"
echo "  - API: https://54.234.98.110:8765/api"
echo "  - Docs: https://54.234.98.110:8765/docs"
