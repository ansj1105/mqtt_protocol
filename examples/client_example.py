#!/usr/bin/env python3
"""
WebSocket 클라이언트 예제
"""

import asyncio
import json
import ssl
import websockets
from datetime import datetime


async def connect_to_server():
    """서버에 연결하고 메시지 송수신"""
    
    # SSL 컨텍스트 (Self-signed 인증서용)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # 또는 CA 인증서 사용
    # ssl_context.load_verify_locations('ca.crt')
    
    # 서버 URI
    uri = "wss://54.234.98.110:8765/ws"
    # TLS 없이: uri = "ws://54.234.98.110:8765/ws"
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print("✅ Connected!")
            
            # 1. Welcome 메시지 수신
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"\n📨 Welcome: {json.dumps(welcome_data, indent=2)}")
            
            # 2. Ping 전송
            ping_msg = {
                "type": "ping",
                "payload": {
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await websocket.send(json.dumps(ping_msg))
            print(f"\n📤 Sent: {ping_msg}")
            
            # Pong 수신
            pong = await websocket.recv()
            print(f"📨 Received: {pong}")
            
            # 3. PQC Handshake (선택)
            if welcome_data.get('payload', {}).get('pqc_enabled'):
                pqc_msg = {
                    "type": "pqc_handshake",
                    "payload": {
                        "algorithm": "kyber768_x25519",
                        "public_key": "client_public_key_" + ("a" * 100)
                    }
                }
                await websocket.send(json.dumps(pqc_msg))
                print(f"\n📤 PQC Handshake sent")
                
                pqc_response = await websocket.recv()
                print(f"📨 PQC Response: {pqc_response}")
            
            # 4. TC375 데이터 전송
            tc375_msg = {
                "type": "tc375_data",
                "payload": {
                    "protocol": "v2",
                    "payload": {
                        "sensor_data": {
                            "temperature": 25.5,
                            "humidity": 60.2,
                            "pressure": 1013.25
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            }
            await websocket.send(json.dumps(tc375_msg))
            print(f"\n📤 TC375 Data sent")
            
            tc375_response = await websocket.recv()
            print(f"📨 TC375 Response: {tc375_response}")
            
            # 5. 커스텀 명령 실행
            command_msg = {
                "type": "command",
                "payload": {
                    "command": "get_stats",
                    "params": {}
                }
            }
            await websocket.send(json.dumps(command_msg))
            print(f"\n📤 Command sent")
            
            command_response = await websocket.recv()
            print(f"📨 Command Response: {command_response}")
            
            # 6. 연결 유지 (실시간 메시지 수신)
            print("\n⏳ Waiting for messages... (Press Ctrl+C to exit)")
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    print(f"📨 Received: {message}")
                except asyncio.TimeoutError:
                    # 30초마다 ping 전송 (연결 유지)
                    await websocket.send(json.dumps({
                        "type": "ping",
                        "payload": {"timestamp": datetime.utcnow().isoformat()}
                    }))
                    print("💓 Ping sent")
    
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # 실행
    asyncio.run(connect_to_server())

