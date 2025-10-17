"""
Connection service for managing WebSocket connections.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from websockets.server import WebSocketServerProtocol

from models.connection import Connection, ConnectionStatus
from repositories.connection import ConnectionRepository
from utils.logger import LoggerMixin
from utils.validators import validate_connection_limit
from config import Config


class ConnectionService(LoggerMixin):
    """Service for managing connections."""
    
    def __init__(self, repository: ConnectionRepository, config: Config):
        self.repository = repository
        self.config = config
        self._websockets: Dict[str, WebSocketServerProtocol] = {}
    
    async def create_connection(
        self,
        websocket: WebSocketServerProtocol,
        user_agent: Optional[str] = None,
        protocol_version: Optional[str] = None
    ) -> Connection:
        """
        Create a new connection.
        
        Args:
            websocket: WebSocket connection
            user_agent: Client user agent
            protocol_version: Protocol version
        
        Returns:
            Created connection
        
        Raises:
            ValidationError: If connection limit reached
        """
        # Validate connection limit
        current_count = len(self.repository.get_active_connections())
        validate_connection_limit(current_count, self.config.security.max_connections)
        
        # Create connection ID
        remote_addr = websocket.remote_address
        connection_id = f"{remote_addr[0]}:{remote_addr[1]}:{int(datetime.utcnow().timestamp())}"
        
        # Create connection model
        connection = Connection(
            id=connection_id,
            remote_address=remote_addr,
            status=ConnectionStatus.CONNECTED,
            user_agent=user_agent,
            protocol_version=protocol_version
        )
        
        # Save to repository
        self.repository.create(connection_id, connection)
        self._websockets[connection_id] = websocket
        
        self.logger.info(
            f"Connection created",
            extra={
                "connection_id": connection_id,
                "remote_address": f"{remote_addr[0]}:{remote_addr[1]}",
                "total_connections": current_count + 1
            }
        )
        
        return connection
    
    async def disconnect(self, connection_id: str) -> bool:
        """
        Disconnect a connection.
        
        Args:
            connection_id: Connection ID
        
        Returns:
            True if disconnected successfully
        """
        connection = self.repository.get(connection_id)
        if not connection:
            self.logger.warning(f"Connection not found: {connection_id}")
            return False
        
        # Mark as disconnected
        connection.disconnect()
        self.repository.update(connection_id, connection)
        
        # Remove websocket
        if connection_id in self._websockets:
            del self._websockets[connection_id]
        
        self.logger.info(
            f"Connection disconnected",
            extra={
                "connection_id": connection_id,
                "duration": (connection.disconnected_at - connection.connected_at).total_seconds()
                if connection.disconnected_at else 0,
                "messages_sent": connection.messages_sent,
                "messages_received": connection.messages_received
            }
        )
        
        return True
    
    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get connection by ID."""
        return self.repository.get(connection_id)
    
    def get_active_connections(self) -> List[Connection]:
        """Get all active connections."""
        return self.repository.get_active_connections()
    
    def get_websocket(self, connection_id: str) -> Optional[WebSocketServerProtocol]:
        """Get WebSocket by connection ID."""
        return self._websockets.get(connection_id)
    
    async def update_activity(self, connection_id: str, increment_received: int = 0):
        """Update connection activity."""
        connection = self.repository.get(connection_id)
        if connection:
            if increment_received > 0:
                connection.increment_received(increment_received)
            else:
                connection.update_activity()
            self.repository.update(connection_id, connection)
    
    async def cleanup_inactive(self) -> int:
        """Clean up inactive connections."""
        timeout = self.config.security.connection_timeout
        inactive = self.repository.get_inactive_connections(timeout)
        
        count = 0
        for connection in inactive:
            await self.disconnect(connection.id)
            count += 1
        
        if count > 0:
            self.logger.info(f"Cleaned up {count} inactive connections")
        
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get connection statistics."""
        all_connections = self.repository.get_all()
        active = self.repository.get_active_connections()
        
        total_messages_sent = sum(c.messages_sent for c in all_connections)
        total_messages_received = sum(c.messages_received for c in all_connections)
        total_bytes_sent = sum(c.bytes_sent for c in all_connections)
        total_bytes_received = sum(c.bytes_received for c in all_connections)
        
        return {
            "total_connections": len(all_connections),
            "active_connections": len(active),
            "total_messages_sent": total_messages_sent,
            "total_messages_received": total_messages_received,
            "total_bytes_sent": total_bytes_sent,
            "total_bytes_received": total_bytes_received,
        }

