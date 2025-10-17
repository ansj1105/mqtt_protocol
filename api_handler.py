"""
REST API handler for server management and control.
Provides HTTP endpoints for monitoring and control.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from aiohttp import web
from config import get_config


logger = logging.getLogger(__name__)


class APIHandler:
    """REST API handler for server management."""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.config = get_config()
        self.app = web.Application()
        self._setup_routes()
        self.rate_limiter = {}  # Simple rate limiting
    
    def _setup_routes(self):
        """Setup API routes."""
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/health", self.handle_health)
        self.app.router.add_get("/status", self.handle_status)
        self.app.router.add_get("/connections", self.handle_connections)
        self.app.router.add_post("/broadcast", self.handle_broadcast)
        self.app.router.add_post("/send", self.handle_send)
        self.app.router.add_get("/config", self.handle_config)
        self.app.router.add_post("/disconnect", self.handle_disconnect)
        
        # TC375 specific endpoints
        self.app.router.add_post("/tc375/command", self.handle_tc375_command)
        self.app.router.add_get("/tc375/status", self.handle_tc375_status)
        
        # PQC endpoints
        self.app.router.add_get("/pqc/info", self.handle_pqc_info)
    
    async def handle_index(self, request: web.Request) -> web.Response:
        """Root endpoint with API documentation."""
        api_info = {
            "name": "WebSocket Server API",
            "version": "1.0.0",
            "description": "REST API for TC375 Litekit WebSocket Server",
            "endpoints": {
                "GET /": "API documentation",
                "GET /health": "Health check",
                "GET /status": "Server status",
                "GET /connections": "List active connections",
                "POST /broadcast": "Broadcast message to all clients",
                "POST /send": "Send message to specific client",
                "GET /config": "Get server configuration",
                "POST /disconnect": "Disconnect a client",
                "POST /tc375/command": "Send command to TC375 device",
                "GET /tc375/status": "Get TC375 device status",
                "GET /pqc/info": "Get PQC configuration info"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        return web.json_response(api_info)
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_status(self, request: web.Request) -> web.Response:
        """Server status endpoint."""
        status = {
            "status": "running",
            "active_connections": len(self.connection_manager.active_connections),
            "max_connections": self.config.security.max_connections,
            "uptime": "N/A",  # Implement uptime tracking if needed
            "tls_enabled": self.config.tls.enabled,
            "pqc_enabled": self.config.pqc.enabled,
            "timestamp": datetime.utcnow().isoformat()
        }
        return web.json_response(status)
    
    async def handle_connections(self, request: web.Request) -> web.Response:
        """List all active connections."""
        connections = self.connection_manager.get_active_connections()
        return web.json_response({
            "count": len(connections),
            "connections": connections,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_broadcast(self, request: web.Request) -> web.Response:
        """Broadcast message to all connected clients."""
        try:
            data = await request.json()
            message = data.get("message")
            
            if not message:
                return web.json_response(
                    {"error": "Message is required"},
                    status=400
                )
            
            await self.connection_manager.broadcast({
                "type": "broadcast",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return web.json_response({
                "success": True,
                "recipients": len(self.connection_manager.active_connections)
            })
        
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def handle_send(self, request: web.Request) -> web.Response:
        """Send message to specific client."""
        try:
            data = await request.json()
            client_id = data.get("client_id")
            message = data.get("message")
            
            if not client_id or not message:
                return web.json_response(
                    {"error": "client_id and message are required"},
                    status=400
                )
            
            success = await self.connection_manager.send_message(client_id, {
                "type": "message",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if success:
                return web.json_response({"success": True})
            else:
                return web.json_response(
                    {"error": "Client not found or message failed"},
                    status=404
                )
        
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def handle_config(self, request: web.Request) -> web.Response:
        """Get server configuration (non-sensitive parts)."""
        config_data = {
            "server": {
                "websocket_port": self.config.server.websocket_port,
                "api_port": self.config.server.api_port
            },
            "tls": {
                "enabled": self.config.tls.enabled
            },
            "pqc": {
                "enabled": self.config.pqc.enabled,
                "supported_algorithms": self.config.pqc.supported_algorithms,
                "algorithms": {
                    "kem": self.config.pqc.algorithms.kem,
                    "kex": self.config.pqc.algorithms.kex,
                    "hybrid_mode": self.config.pqc.algorithms.hybrid_mode
                }
            },
            "security": {
                "max_message_size": self.config.security.max_message_size,
                "max_connections": self.config.security.max_connections
            },
            "tc375": {
                "supported_protocols": self.config.tc375.supported_protocols,
                "default_protocol": self.config.tc375.default_protocol
            }
        }
        return web.json_response(config_data)
    
    async def handle_disconnect(self, request: web.Request) -> web.Response:
        """Disconnect a specific client."""
        try:
            data = await request.json()
            client_id = data.get("client_id")
            
            if not client_id:
                return web.json_response(
                    {"error": "client_id is required"},
                    status=400
                )
            
            if client_id in self.connection_manager.active_connections:
                websocket = self.connection_manager.active_connections[client_id]
                await websocket.close(1000, "Disconnected by server")
                await self.connection_manager.disconnect(client_id)
                return web.json_response({"success": True})
            else:
                return web.json_response(
                    {"error": "Client not found"},
                    status=404
                )
        
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error disconnecting client: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def handle_tc375_command(self, request: web.Request) -> web.Response:
        """Send command to TC375 device through WebSocket."""
        try:
            data = await request.json()
            client_id = data.get("client_id")
            command = data.get("command")
            params = data.get("params", {})
            
            if not client_id or not command:
                return web.json_response(
                    {"error": "client_id and command are required"},
                    status=400
                )
            
            # Send command to TC375 client
            success = await self.connection_manager.send_message(client_id, {
                "type": "tc375_command",
                "command": command,
                "params": params,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if success:
                return web.json_response({
                    "success": True,
                    "message": f"Command '{command}' sent to {client_id}"
                })
            else:
                return web.json_response(
                    {"error": "Client not found or command failed"},
                    status=404
                )
        
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error sending TC375 command: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def handle_tc375_status(self, request: web.Request) -> web.Response:
        """Get TC375 devices status."""
        # Filter connections from TC375 devices
        # In production, you'd have a way to identify TC375 devices
        tc375_connections = {}
        for client_id, metadata in self.connection_manager.connection_metadata.items():
            if client_id in self.connection_manager.active_connections:
                tc375_connections[client_id] = metadata
        
        return web.json_response({
            "tc375_devices": len(tc375_connections),
            "devices": tc375_connections,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_pqc_info(self, request: web.Request) -> web.Response:
        """Get PQC configuration information."""
        pqc_info = {
            "enabled": self.config.pqc.enabled,
            "algorithms": {
                "kem": self.config.pqc.algorithms.kem,
                "kex": self.config.pqc.algorithms.kex,
                "hybrid_mode": self.config.pqc.algorithms.hybrid_mode
            },
            "supported_algorithms": self.config.pqc.supported_algorithms,
            "description": "Post-Quantum Cryptography hybrid key exchange support"
        }
        return web.json_response(pqc_info)


async def create_api_server(connection_manager, host: str, port: int) -> web.AppRunner:
    """Create and start the API server."""
    api_handler = APIHandler(connection_manager)
    runner = web.AppRunner(api_handler.app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"API server started on http://{host}:{port}")
    return runner

