#!/usr/bin/env python3
"""
연속 메시지 전송 클라이언트
"""

import asyncio
import json
import ssl
import websockets
from datetime import datetime
import random


async def continuous_client():
    """서버에 연결하고 계속 메시지 전송"""
    
    # SSL 설정
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    uri = "wss://54.234.98.110:8765/ws"
    
    print(f"🔌 연결 시도: {uri}")
    print("=" * 60)
    
    try:
        async with websockets.connect(uri, ssl=ssl_context, ping_interval=20) as ws:
            print("✅ 연결 성공!\n")
            
            # Welcome 메시지 받기
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            client_id = welcome_data['payload']['client_id']
            print(f"📨 Welcome!")
            print(f"   클라이언트 ID: {client_id}")
            print(f"   PQC 활성화: {welcome_data['payload']['pqc_enabled']}")
            print("=" * 60)
            
            message_count = 0
            
            # 메시지 수신 태스크
            async def receive_messages():
                while True:
                    try:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        print(f"\n📨 수신: {data['type']}")
                        if data.get('payload'):
                            print(f"   내용: {json.dumps(data['payload'], indent=2, ensure_ascii=False)}")
                    except Exception as e:
                        print(f"❌ 수신 에러: {e}")
                        break
            
            # 수신 태스크 시작
            receive_task = asyncio.create_task(receive_messages())
            
            # 메시지 전송 루프
            while True:
                await asyncio.sleep(3)  # 3초마다
                
                message_count += 1
                
                # 랜덤 메시지 타입
                message_types = [
                    {
                        "type": "ping",
                        "payload": {"timestamp": datetime.now().isoformat()}
                    },
                    {
                        "type": "tc375_data",
                        "payload": {
                            "protocol": "v2",
                            "payload": {
                                "sensor_data": {
                                    "temperature": round(random.uniform(20, 30), 2),
                                    "humidity": round(random.uniform(40, 70), 2),
                                    "pressure": round(random.uniform(1000, 1020), 2)
                                },
                                "device_id": "TC375_001",
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                    },
                    {
                        "type": "status",
                        "payload": {}
                    },
                    {
                        "type": "command",
                        "payload": {
                            "command": "get_stats",
                            "params": {}
                        }
                    }
                ]
                
                # 랜덤하게 선택
                msg = random.choice(message_types)
                
                await ws.send(json.dumps(msg))
                print(f"\n📤 [{message_count}] 전송: {msg['type']}")
                
                # 10개마다 요약
                if message_count % 10 == 0:
                    print(f"\n{'='*60}")
                    print(f"✅ 총 {message_count}개 메시지 전송됨")
                    print(f"{'='*60}")
    
    except KeyboardInterrupt:
        print(f"\n\n중지됨. 총 {message_count}개 메시지 전송")
    except Exception as e:
        print(f"\n❌ 에러: {e}")


if __name__ == "__main__":
    print("💬 연속 메시지 전송 클라이언트")
    print("Ctrl+C로 종료\n")
    asyncio.run(continuous_client())

