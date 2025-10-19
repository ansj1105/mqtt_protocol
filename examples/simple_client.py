#!/usr/bin/env python3
"""
간단한 WebSocket 클라이언트
"""

import asyncio
import json
import ssl
import websockets


async def simple_connect():
    """간단한 연결 예제"""
    
    # SSL 설정
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # 연결
    uri = "wss://54.234.98.110:8765/ws"
    
    async with websockets.connect(uri, ssl=ssl_context) as ws:
        print("✅ Connected!")
        
        # Welcome 메시지 받기
        welcome = await ws.recv()
        print(f"Welcome: {welcome}")
        
        # Ping 보내기
        await ws.send(json.dumps({
            "type": "ping",
            "payload": {"timestamp": "2024-01-01T00:00:00"}
        }))
        
        # Pong 받기
        pong = await ws.recv()
        print(f"Pong: {pong}")


if __name__ == "__main__":
    asyncio.run(simple_connect())

