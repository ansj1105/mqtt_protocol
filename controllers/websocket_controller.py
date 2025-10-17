"""
WebSocket controller for handling WebSocket connections.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any

from models.message import Message, MessageType
from services.connection_service import ConnectionService
from services.message_service import MessageService
from services.tc375_service import TC375Service
from services.pqc_service import PQCService
from utils.logger import LoggerMixin


class WebSocketController(LoggerMixin):
    """Controller for WebSocket connections."""
    
    def __init__(
        self,
        connection_service: ConnectionService,
        message_service: MessageService,
        tc375_service: TC375Service,
        pqc_service: PQCService
    ):
        self.connection_service = connection_service
        self.message_service = message_service
        self.tc375_service = tc375_service
        self.pqc_service = pqc_service
        
        # Message handlers
        self.message_handlers = {
            MessageType.PING: self._handle_ping,
            MessageType.PQC_HANDSHAKE: self._handle_pqc_handshake,
            MessageType.TC375_DATA: self._handle_tc375_data,
            MessageType.COMMAND: self._handle_command,
            MessageType.STATUS: self._handle_status,
        }
    
    async def handle_connection(self, websocket: WebSocket):
        """
        Handle a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
        """
        # Accept connection
        await websocket.accept()
        
        # Create connection
        try:
            connection = await self.connection_service.create_connection(websocket)
            connection_id = connection.id
            
            self.logger.info(f"WebSocket connection established: {connection_id}")
            
            # Send welcome message
            await self.message_service.send_welcome(
                connection_id,
                pqc_enabled=self.pqc_service.config.pqc.enabled
            )
            
            # Message processing loop
            try:
                while True:
                    # Receive message
                    raw_message = await websocket.receive_text()
                    
                    # Process message
                    message = await self.message_service.process_incoming_message(
                        connection_id,
                        raw_message
                    )
                    
                    if message:
                        await self._route_message(connection_id, message)
            
            except WebSocketDisconnect:
                self.logger.info(f"WebSocket disconnected: {connection_id}")
            
            except Exception as e:
                self.logger.error(
                    f"Error in WebSocket connection",
                    extra={"connection_id": connection_id, "error": str(e)}
                )
                await self.message_service.send_error(connection_id, str(e))
        
        except Exception as e:
            self.logger.error(f"Error establishing WebSocket connection: {e}")
        
        finally:
            # Cleanup
            if 'connection_id' in locals():
                await self.connection_service.disconnect(connection_id)
    
    async def _route_message(self, connection_id: str, message: Message):
        """Route message to appropriate handler."""
        handler = self.message_handlers.get(message.type)
        
        if handler:
            try:
                await handler(connection_id, message)
            except Exception as e:
                self.logger.error(
                    f"Error handling message",
                    extra={
                        "connection_id": connection_id,
                        "message_type": message.type.value,
                        "error": str(e)
                    }
                )
                await self.message_service.send_error(connection_id, str(e))
        else:
            self.logger.warning(
                f"Unknown message type: {message.type.value}",
                extra={"connection_id": connection_id}
            )
            await self.message_service.send_error(
                connection_id,
                f"Unknown message type: {message.type.value}"
            )
    
    async def _handle_ping(self, connection_id: str, message: Message):
        """Handle ping message."""
        timestamp = message.payload.get("timestamp")
        await self.message_service.send_pong(connection_id, timestamp)
    
    async def _handle_pqc_handshake(self, connection_id: str, message: Message):
        """Handle PQC handshake."""
        algorithm = message.payload.get("algorithm")
        client_public_key = message.payload.get("public_key")
        
        if not algorithm or not client_public_key:
            await self.message_service.send_error(
                connection_id,
                "Algorithm and public_key are required for PQC handshake"
            )
            return
        
        # Initiate handshake
        result = await self.pqc_service.initiate_handshake(
            connection_id,
            algorithm,
            client_public_key
        )
        
        # Send response
        response = Message(
            type=MessageType.PQC_HANDSHAKE_RESPONSE,
            payload=result,
            correlation_id=message.id
        )
        await self.message_service.send_message(connection_id, response)
    
    async def _handle_tc375_data(self, connection_id: str, message: Message):
        """Handle TC375 data."""
        payload = message.payload.get("payload")
        
        if not payload:
            await self.message_service.send_error(connection_id, "Payload is required")
            return
        
        # Process TC375 data
        tc375_response = await self.tc375_service.process_tc375_data(
            connection_id,
            payload
        )
        
        # Send response
        response = Message(
            type=MessageType.TC375_DATA_RESPONSE,
            payload={
                "success": tc375_response.success,
                "payload": tc375_response.to_dict()
            },
            correlation_id=message.id
        )
        await self.message_service.send_message(connection_id, response)
    
    async def _handle_command(self, connection_id: str, message: Message):
        """Handle command."""
        command = message.payload.get("command")
        params = message.payload.get("params", {})
        
        if not command:
            await self.message_service.send_error(connection_id, "Command is required")
            return
        
        # Execute command
        result = await self._execute_command(command, params)
        
        # Send response
        response = Message(
            type=MessageType.COMMAND_RESPONSE,
            payload={
                "command": command,
                "success": result.get("success", True),
                "result": result
            },
            correlation_id=message.id
        )
        await self.message_service.send_message(connection_id, response)
    
    async def _handle_status(self, connection_id: str, message: Message):
        """Handle status request."""
        stats = self.connection_service.get_statistics()
        
        response = Message(
            type=MessageType.STATUS_RESPONSE,
            payload={
                "server_status": "running",
                "active_connections": stats["active_connections"],
                "pqc_enabled": self.pqc_service.config.pqc.enabled,
                "tls_enabled": self.pqc_service.config.tls.enabled
            },
            correlation_id=message.id
        )
        await self.message_service.send_message(connection_id, response)
    
    async def _execute_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command."""
        if command == "echo":
            return {"success": True, "echo": params}
        
        elif command == "get_config":
            return {
                "success": True,
                "config": self.pqc_service.get_info()
            }
        
        elif command == "get_stats":
            conn_stats = self.connection_service.get_statistics()
            pqc_stats = self.pqc_service.get_statistics()
            tc375_stats = self.tc375_service.get_statistics()
            
            return {
                "success": True,
                "statistics": {
                    "connections": conn_stats,
                    "pqc": pqc_stats,
                    "tc375": tc375_stats
                }
            }
        
        else:
            return {"success": False, "error": f"Unknown command: {command}"}

