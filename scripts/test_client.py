#!/usr/bin/env python3
"""
Simple WebSocket test client for testing the server.
"""

import asyncio
import json
import websockets
import argparse
from datetime import datetime


async def test_client(uri: str, use_tls: bool = False):
    """
    Test WebSocket client.
    
    Args:
        uri: WebSocket URI
        use_tls: Use TLS (wss://)
    """
    # Prepare SSL context for self-signed certificates
    ssl_context = None
    if use_tls:
        import ssl
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print("✅ Connected!")
            
            # Receive welcome message
            welcome = await websocket.recv()
            print(f"\n📨 Received: {welcome}")
            welcome_data = json.loads(welcome)
            print(f"   Client ID: {welcome_data['payload']['client_id']}")
            print(f"   PQC Enabled: {welcome_data['payload']['pqc_enabled']}")
            
            # Send ping
            print("\n📤 Sending ping...")
            ping_message = {
                "type": "ping",
                "payload": {
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await websocket.send(json.dumps(ping_message))
            
            # Receive pong
            pong = await websocket.recv()
            print(f"📨 Received: {pong}")
            
            # Send status request
            print("\n📤 Sending status request...")
            status_message = {
                "type": "status",
                "payload": {}
            }
            await websocket.send(json.dumps(status_message))
            
            # Receive status
            status = await websocket.recv()
            print(f"📨 Received: {status}")
            status_data = json.loads(status)
            print(f"   Active connections: {status_data['payload']['active_connections']}")
            
            # Test PQC handshake
            if welcome_data['payload']['pqc_enabled']:
                print("\n📤 Testing PQC handshake...")
                pqc_message = {
                    "type": "pqc_handshake",
                    "payload": {
                        "algorithm": "kyber768_x25519",
                        "public_key": "test_public_key_" + ("a" * 100)
                    }
                }
                await websocket.send(json.dumps(pqc_message))
                
                # Receive response
                pqc_response = await websocket.recv()
                print(f"📨 Received: {pqc_response}")
                pqc_data = json.loads(pqc_response)
                if pqc_data['payload']['success']:
                    print(f"   ✅ PQC handshake successful!")
                    print(f"   Session ID: {pqc_data['payload']['session_id']}")
            
            # Test TC375 data
            print("\n📤 Sending TC375 test data...")
            tc375_message = {
                "type": "tc375_data",
                "payload": {
                    "protocol": "v2",
                    "payload": {
                        "data": "test_data_from_tc375",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            }
            await websocket.send(json.dumps(tc375_message))
            
            # Receive response
            tc375_response = await websocket.recv()
            print(f"📨 Received: {tc375_response}")
            
            print("\n✅ All tests completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="WebSocket test client")
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Server port (default: 8765)"
    )
    parser.add_argument(
        "--tls",
        action="store_true",
        help="Use TLS (wss://)"
    )
    
    args = parser.parse_args()
    
    protocol = "wss" if args.tls else "ws"
    uri = f"{protocol}://{args.host}:{args.port}/ws"
    
    await test_client(uri, args.tls)


if __name__ == "__main__":
    asyncio.run(main())

