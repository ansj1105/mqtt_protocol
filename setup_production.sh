#!/bin/bash

echo "🚀 프로덕션 서버 설정 스크립트"
echo "================================"
echo ""
echo "서버 IP: 54.234.98.110"
echo "포트: 8765"
echo ""

# .env 파일 생성
if [ -f ".env" ]; then
    echo "⚠️  .env 파일이 이미 존재합니다."
    read -p "덮어쓰시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "취소되었습니다."
        exit 1
    fi
fi

echo "📝 .env 파일 생성 중..."
cp .env.production .env
echo "✅ .env 파일 생성 완료"

# 디렉토리 생성
echo "📁 필요한 디렉토리 생성 중..."
mkdir -p logs certs
echo "✅ 디렉토리 생성 완료"

# 인증서 확인
if [ -f "certs/server.crt" ] && [ -f "certs/server.key" ]; then
    echo "✅ SSL 인증서가 이미 존재합니다."
else
    echo "⚠️  SSL 인증서가 없습니다."
    echo "   ./scripts/generate_certs.sh 를 실행하세요."
fi

# 권한 설정
echo "🔒 파일 권한 설정 중..."
chmod 600 .env 2>/dev/null || true
chmod 600 certs/*.key 2>/dev/null || true
chmod 644 certs/*.crt 2>/dev/null || true
echo "✅ 권한 설정 완료"

echo ""
echo "✅ 프로덕션 설정 완료!"
echo ""
echo "다음 단계:"
echo "1. 가상 환경 활성화: source venv/bin/activate"
echo "2. 의존성 설치: pip install -r requirements.txt"
echo "3. 서버 실행: python main.py"
echo ""
echo "또는:"
echo "  ./scripts/run_prod.sh"
echo ""
echo "접속 URL:"
echo "  - WebSocket: wss://54.234.98.110:8765/ws"
echo "  - API: https://54.234.98.110:8765/api"
echo "  - Docs: https://54.234.98.110:8765/docs"
echo ""
