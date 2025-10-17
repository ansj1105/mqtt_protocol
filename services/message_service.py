"""
Message service for handling WebSocket messages.
"""

import json
from typing import Dict, Any, Optional, Set
from datetime import datetime

from models.message import Message, MessageType
from services.connection_service import ConnectionService
from utils.logger import LoggerMixin
from utils.validators import validate_message_size
from config import Config


class MessageService(LoggerMixin):
    """Service for handling messages."""
    
    def __init__(self, connection_service: ConnectionService, config: Config):
        self.connection_service = connection_service
        self.config = config
    
    async def send_message(
        self,
        connection_id: str,
        message: Message
    ) -> bool:
        """
        Send message to a specific connection.
        
        Args:
            connection_id: Target connection ID
            message: Message to send
        
        Returns:
            True if sent successfully
        """
        websocket = self.connection_service.get_websocket(connection_id)
        if not websocket:
            self.logger.warning(f"WebSocket not found for connection: {connection_id}")
            return False
        
        try:
            # Serialize message
            message_dict = message.to_dict()
            message_str = json.dumps(message_dict)
            
            # Validate size
            validate_message_size(message_str, self.config.security.max_message_size)
            
            # Send
            await websocket.send(message_str)
            
            # Update connection statistics
            connection = self.connection_service.get_connection(connection_id)
            if connection:
                connection.increment_sent(len(message_str))
                self.connection_service.repository.update(connection_id, connection)
            
            self.logger.debug(
                f"Message sent",
                extra={
                    "connection_id": connection_id,
                    "message_type": message.type.value,
                    "message_id": message.id,
                    "size": len(message_str)
                }
            )
            
            return True
        
        except Exception as e:
            self.logger.error(
                f"Error sending message",
                extra={
                    "connection_id": connection_id,
                    "error": str(e)
                }
            )
            return False
    
    async def broadcast_message(
        self,
        message: Message,
        exclude: Optional[Set[str]] = None
    ) -> int:
        """
        Broadcast message to all active connections.
        
        Args:
            message: Message to broadcast
            exclude: Set of connection IDs to exclude
        
        Returns:
            Number of recipients
        """
        exclude = exclude or set()
        connections = self.connection_service.get_active_connections()
        
        count = 0
        for connection in connections:
            if connection.id not in exclude:
                success = await self.send_message(connection.id, message)
                if success:
                    count += 1
        
        self.logger.info(
            f"Message broadcast",
            extra={
                "message_type": message.type.value,
                "recipients": count,
                "total_connections": len(connections)
            }
        )
        
        return count
    
    async def process_incoming_message(
        self,
        connection_id: str,
        raw_message: str
    ) -> Optional[Message]:
        """
        Process incoming message from client.
        
        Args:
            connection_id: Source connection ID
            raw_message: Raw message string
        
        Returns:
            Parsed message or None if invalid
        """
        try:
            # Validate size
            validate_message_size(raw_message, self.config.security.max_message_size)
            
            # Parse JSON
            data = json.loads(raw_message)
            
            # Create message
            message = Message.from_dict(data, connection_id)
            
            # Update connection activity
            await self.connection_service.update_activity(
                connection_id,
                increment_received=len(raw_message)
            )
            
            self.logger.debug(
                f"Message received",
                extra={
                    "connection_id": connection_id,
                    "message_type": message.type.value,
                    "message_id": message.id,
                    "size": len(raw_message)
                }
            )
            
            return message
        
        except json.JSONDecodeError as e:
            self.logger.error(
                f"Invalid JSON message",
                extra={
                    "connection_id": connection_id,
                    "error": str(e)
                }
            )
            return None
        
        except Exception as e:
            self.logger.error(
                f"Error processing message",
                extra={
                    "connection_id": connection_id,
                    "error": str(e)
                }
            )
            return None
    
    async def send_welcome(self, connection_id: str, pqc_enabled: bool) -> bool:
        """Send welcome message to new connection."""
        message = Message(
            type=MessageType.WELCOME,
            payload={
                "client_id": connection_id,
                "server_time": datetime.utcnow().isoformat(),
                "pqc_enabled": pqc_enabled,
                "supported_pqc_algorithms": self.config.pqc.supported_algorithms
            }
        )
        return await self.send_message(connection_id, message)
    
    async def send_error(self, connection_id: str, error_message: str) -> bool:
        """Send error message to connection."""
        message = Message(
            type=MessageType.ERROR,
            payload={"message": error_message}
        )
        return await self.send_message(connection_id, message)
    
    async def send_pong(self, connection_id: str, client_timestamp: Optional[str] = None) -> bool:
        """Send pong response to ping."""
        message = Message(
            type=MessageType.PONG,
            payload={
                "timestamp": client_timestamp,
                "server_time": datetime.utcnow().isoformat()
            }
        )
        return await self.send_message(connection_id, message)

