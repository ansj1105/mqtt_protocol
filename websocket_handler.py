"""
WebSocket handler for TC375 Litekit communication.
Handles WebSocket connections with TLS and PQC hybrid support.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Set, Optional, Any
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol
from config import get_config


logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocketServerProtocol] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self.config = get_config()
    
    async def connect(self, websocket: WebSocketServerProtocol, client_id: str) -> bool:
        """Register a new connection."""
        async with self._lock:
            if len(self.active_connections) >= self.config.security.max_connections:
                logger.warning(f"Max connections reached. Rejecting client: {client_id}")
                return False
            
            self.active_connections[client_id] = websocket
            self.connection_metadata[client_id] = {
                "connected_at": datetime.utcnow().isoformat(),
                "remote_address": websocket.remote_address,
                "messages_sent": 0,
                "messages_received": 0,
                "last_activity": time.time()
            }
            logger.info(f"Client connected: {client_id} from {websocket.remote_address}")
            return True
    
    async def disconnect(self, client_id: str):
        """Unregister a connection."""
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                metadata = self.connection_metadata.pop(client_id, {})
                logger.info(f"Client disconnected: {client_id}, Stats: {metadata}")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific client."""
        if client_id not in self.active_connections:
            logger.warning(f"Client not found: {client_id}")
            return False
        
        try:
            websocket = self.active_connections[client_id]
            await websocket.send(json.dumps(message))
            
            # Update metadata
            if client_id in self.connection_metadata:
                self.connection_metadata[client_id]["messages_sent"] += 1
                self.connection_metadata[client_id]["last_activity"] = time.time()
            
            return True
        except Exception as e:
            logger.error(f"Error sending message to {client_id}: {e}")
            await self.disconnect(client_id)
            return False
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set[str]] = None):
        """Broadcast a message to all connected clients."""
        exclude = exclude or set()
        tasks = []
        
        for client_id in list(self.active_connections.keys()):
            if client_id not in exclude:
                tasks.append(self.send_message(client_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_active_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active connections."""
        return {
            client_id: {
                **metadata,
                "is_active": client_id in self.active_connections
            }
            for client_id, metadata in self.connection_metadata.items()
        }


class WebSocketHandler:
    """Main WebSocket handler for processing messages."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.config = get_config()
        self.message_handlers = {
            "ping": self._handle_ping,
            "pqc_handshake": self._handle_pqc_handshake,
            "tc375_data": self._handle_tc375_data,
            "command": self._handle_command,
            "status": self._handle_status,
        }
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new WebSocket connection."""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        
        # Register connection
        if not await self.connection_manager.connect(websocket, client_id):
            await websocket.close(1008, "Max connections reached")
            return
        
        try:
            # Send welcome message
            await self.connection_manager.send_message(client_id, {
                "type": "welcome",
                "client_id": client_id,
                "server_time": datetime.utcnow().isoformat(),
                "pqc_enabled": self.config.pqc.enabled,
                "supported_pqc_algorithms": self.config.pqc.supported_algorithms
            })
            
            # Message processing loop
            async for message in websocket:
                try:
                    await self._process_message(client_id, message)
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}")
                    await self.connection_manager.send_message(client_id, {
                        "type": "error",
                        "message": str(e)
                    })
        
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Connection closed for {client_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {client_id}: {e}")
        finally:
            await self.connection_manager.disconnect(client_id)
    
    async def _process_message(self, client_id: str, message: str):
        """Process incoming message."""
        # Check message size
        if len(message) > self.config.security.max_message_size:
            raise ValueError(f"Message size exceeds limit: {len(message)} bytes")
        
        # Update metadata
        if client_id in self.connection_manager.connection_metadata:
            metadata = self.connection_manager.connection_metadata[client_id]
            metadata["messages_received"] += 1
            metadata["last_activity"] = time.time()
        
        # Parse message
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON message")
        
        message_type = data.get("type")
        if not message_type:
            raise ValueError("Message type not specified")
        
        # Route to appropriate handler
        handler = self.message_handlers.get(message_type)
        if handler:
            await handler(client_id, data)
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await self.connection_manager.send_message(client_id, {
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            })
    
    async def _handle_ping(self, client_id: str, data: Dict[str, Any]):
        """Handle ping message."""
        await self.connection_manager.send_message(client_id, {
            "type": "pong",
            "timestamp": data.get("timestamp"),
            "server_time": datetime.utcnow().isoformat()
        })
    
    async def _handle_pqc_handshake(self, client_id: str, data: Dict[str, Any]):
        """Handle PQC handshake for hybrid key exchange."""
        logger.info(f"PQC handshake from {client_id}")
        
        requested_algorithm = data.get("algorithm")
        client_public_key = data.get("public_key")
        
        if not self.config.pqc.enabled:
            await self.connection_manager.send_message(client_id, {
                "type": "pqc_handshake_response",
                "success": False,
                "message": "PQC not enabled on server"
            })
            return
        
        if requested_algorithm not in self.config.pqc.supported_algorithms:
            await self.connection_manager.send_message(client_id, {
                "type": "pqc_handshake_response",
                "success": False,
                "message": f"Algorithm not supported: {requested_algorithm}"
            })
            return
        
        # In production, perform actual PQC key exchange here
        # For MVP, simulate the handshake
        server_public_key = "simulated_server_public_key_" + requested_algorithm
        shared_secret = "simulated_shared_secret"
        
        await self.connection_manager.send_message(client_id, {
            "type": "pqc_handshake_response",
            "success": True,
            "algorithm": requested_algorithm,
            "server_public_key": server_public_key,
            "session_id": f"pqc_session_{client_id}_{int(time.time())}"
        })
        
        logger.info(f"PQC handshake completed for {client_id} with {requested_algorithm}")
    
    async def _handle_tc375_data(self, client_id: str, data: Dict[str, Any]):
        """Handle data from TC375 Litekit."""
        logger.info(f"TC375 data from {client_id}")
        
        protocol_version = data.get("protocol", self.config.tc375.default_protocol)
        payload = data.get("payload")
        
        if not payload:
            raise ValueError("Payload is required")
        
        # Process TC375 data
        # In production, parse and validate TC375-specific data format
        response_payload = {
            "status": "received",
            "protocol": protocol_version,
            "data_size": len(str(payload)),
            "processed_at": datetime.utcnow().isoformat()
        }
        
        await self.connection_manager.send_message(client_id, {
            "type": "tc375_data_response",
            "success": True,
            "payload": response_payload
        })
    
    async def _handle_command(self, client_id: str, data: Dict[str, Any]):
        """Handle command from client."""
        command = data.get("command")
        params = data.get("params", {})
        
        logger.info(f"Command from {client_id}: {command}")
        
        # Execute command (implement specific commands as needed)
        result = await self._execute_command(command, params)
        
        await self.connection_manager.send_message(client_id, {
            "type": "command_response",
            "command": command,
            "success": result.get("success", True),
            "result": result
        })
    
    async def _handle_status(self, client_id: str, data: Dict[str, Any]):
        """Handle status request."""
        await self.connection_manager.send_message(client_id, {
            "type": "status_response",
            "server_status": "running",
            "active_connections": len(self.connection_manager.active_connections),
            "pqc_enabled": self.config.pqc.enabled,
            "tls_enabled": self.config.tls.enabled
        })
    
    async def _execute_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command."""
        # Implement specific command logic here
        if command == "echo":
            return {"success": True, "echo": params}
        elif command == "get_config":
            return {
                "success": True,
                "config": {
                    "pqc_enabled": self.config.pqc.enabled,
                    "supported_algorithms": self.config.pqc.supported_algorithms
                }
            }
        else:
            return {"success": False, "error": f"Unknown command: {command}"}

