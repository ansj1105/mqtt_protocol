#!/usr/bin/env python3
"""
빠른 연결 테스트
"""

import asyncio
import json
import ssl
import websockets


async def test_connection():
    """서버 연결 테스트"""
    
    # SSL 컨텍스트 (Self-signed 인증서용)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # TLS로 연결 (wss://)
    uri = "wss://54.234.98.110:8765/ws"
    
    print(f"🔌 연결 시도: {uri}")
    print(f"🔐 TLS/SSL 활성화")
    
    try:
        async with websockets.connect(uri, ssl=ssl_context, ping_timeout=10) as ws:
            print("✅ 연결 성공!")
            
            # Welcome 메시지 받기
            print("⏳ Welcome 메시지 대기 중...")
            welcome = await asyncio.wait_for(ws.recv(), timeout=30.0)
            print(f"\n📨 Welcome 메시지:")
            welcome_data = json.loads(welcome)
            print(json.dumps(welcome_data, indent=2, ensure_ascii=False))
            
            # 클라이언트 ID 저장
            client_id = welcome_data.get('payload', {}).get('client_id', 'unknown')
            print(f"\n🆔 클라이언트 ID: {client_id}")
            
            # Ping 보내기
            ping_msg = {
                "type": "ping",
                "payload": {"timestamp": "2024-10-19T12:00:00"}
            }
            await ws.send(json.dumps(ping_msg))
            print(f"\n📤 Ping 전송")
            
            # Pong 받기
            print("⏳ Pong 대기 중...")
            pong = await asyncio.wait_for(ws.recv(), timeout=30.0)
            print(f"\n📨 Pong 수신:")
            print(json.dumps(json.loads(pong), indent=2, ensure_ascii=False))
            
            # 연결 유지하며 대기
            print("\n✅ 테스트 성공! 10초간 연결 유지...")
            await asyncio.sleep(10)
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ 연결 실패: {e}")
        print("서버가 실행 중인지 확인하세요.")
    except asyncio.TimeoutError:
        print(f"❌ 타임아웃: 서버 응답 없음")
    except Exception as e:
        print(f"❌ 에러: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())

