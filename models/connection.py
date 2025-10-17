"""
Connection domain model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class ConnectionStatus(str, Enum):
    """Connection status enumeration."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class Connection:
    """Domain model for a WebSocket connection."""
    
    id: str
    remote_address: tuple
    status: ConnectionStatus = ConnectionStatus.CONNECTING
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    disconnected_at: Optional[datetime] = None
    
    # Statistics
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    
    # Metadata
    user_agent: Optional[str] = None
    protocol_version: Optional[str] = None
    pqc_session_id: Optional[str] = None
    tc375_device_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if connection is active."""
        return self.status in [ConnectionStatus.CONNECTED, ConnectionStatus.AUTHENTICATED]
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def increment_sent(self, size: int = 0):
        """Increment sent message counter."""
        self.messages_sent += 1
        self.bytes_sent += size
        self.update_activity()
    
    def increment_received(self, size: int = 0):
        """Increment received message counter."""
        self.messages_received += 1
        self.bytes_received += size
        self.update_activity()
    
    def disconnect(self):
        """Mark connection as disconnected."""
        self.status = ConnectionStatus.DISCONNECTED
        self.disconnected_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "remote_address": f"{self.remote_address[0]}:{self.remote_address[1]}",
            "status": self.status.value,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "disconnected_at": self.disconnected_at.isoformat() if self.disconnected_at else None,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "protocol_version": self.protocol_version,
            "pqc_session_id": self.pqc_session_id,
            "tc375_device_id": self.tc375_device_id,
            "metadata": self.metadata,
        }

